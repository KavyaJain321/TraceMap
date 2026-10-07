"""Full scan: crawl -> detect -> leak test -> graph -> findings. One call, one ScanResult."""

from __future__ import annotations

import time
import traceback

from .collusion.graph import build_graph
from .config import CrawlConfig, settings
from .contracts import LeakReport, ScanResult
from .crawl.crawler import Progress, crawl, emit, normalize_url
from .detect.behaviour import risky_scripts
from .detect.classify import Classifier, default_classifier
from .findings import build_findings
from .leak.tracer import match_leaks, run_leak_test
from .storage import Store
from .util.domains import etld1


async def run_scan(url: str, store: Store, *, mode: str = "full", leak_test: bool = True,
                   consent_mode: str = "none", device: str = "mobile", phones: list[str] | None = None,
                   email_domain: str | None = None, scan_id: str | None = None,
                   progress: Progress | None = None, classifier: Classifier | None = None,
                   config: CrawlConfig | None = None) -> ScanResult:
    url = normalize_url(url)
    scan_id = scan_id or store.new_scan_id()
    config = config or (CrawlConfig.quick() if mode == "quick" else CrawlConfig())
    config.consent_mode, config.device = consent_mode, device
    phones = settings.canary_phones if phones is None else phones
    email_domain = email_domain or settings.canary_email_domain
    result = ScanResult(scan_id=scan_id, url=url, site=etld1(url), mode=mode, created_at=time.time())
    store.upsert_scan(scan_id, url=url, site=result.site, mode=mode, status="running", created_at=result.created_at)

    async def prog(ev: dict) -> None:
        store.append_event(scan_id, ev)
        if progress:
            r = progress(ev)
            if hasattr(r, "__await__"):
                await r

    leak_holder: dict = {}

    async def leak_hook(pw, browser, record, urls):
        if not leak_test or record.status == "blocked" or not record.visits or not record.visits[0].pages \
                or record.visits[0].pages[0].status == "blocked":
            return
        await emit(prog, "leak", "Starting leak test with a fresh profile (forms are never submitted)")
        landing = record.visits[0].pages[0].final_url or url
        visit, report = await run_leak_test(pw, browser, record.site, landing, config, store, prog,
                                            email_domain, phones)
        record.visits.append(visit)
        leak_holder["report"] = report

    try:
        await emit(prog, "start", f"Scanning {url} ({mode} mode, {device}, consent={consent_mode})", pct=2)
        record = await crawl(url, config, store, prog, crawl_id=scan_id, after_profiles=leak_hook)
        result.site = record.site
        store.save_doc(scan_id, "crawl", record)
        await emit(prog, "detect", "Classifying third parties", pct=80)
        classifier = classifier or default_classifier()
        parties = classifier.classify(record)
        scripts = risky_scripts(record)
        await emit(prog, "detect", f"{sum(p.is_tracker for p in parties)} trackers among "
                                   f"{sum(not p.first_party for p in parties)} third parties", pct=85)
        report: LeakReport = leak_holder.get("report") or LeakReport(tested=False)
        lvisit = record.visit("L")
        if lvisit is not None:
            cloaked = {e.split(" ")[1] for p in parties if p.cloaked for e in p.evidence if e.startswith("cname:")}
            report.leaks = match_leaks(lvisit, report, record.site, classifier, cloaked)
            n = sum(not e.first_party for e in report.leaks)
            await emit(prog, "leak", f"{n} leak event(s) to other companies found", pct=90, leaks=n)
        graph = build_graph(record, parties)
        await emit(prog, "graph", f"Identifier-flow graph: {len(graph.nodes)} nodes, "
                                  f"{sum(e.kind == 'shared_id' for e in graph.edges)} shared-ID links", pct=94)
        findings, summary = build_findings(record, parties, scripts, report, graph)
        a = record.visit("A") or (record.visits[0] if record.visits else None)
        result.screenshot_sha256 = a.pages[0].screenshot_sha256 if a and a.pages else None
        result.parties, result.risky_scripts, result.leaks, result.graph = parties, scripts, report, graph
        result.findings, result.summary = findings, summary
        result.status = "done"
    except Exception as e:  # keep the scan record, surface the error
        result.status, result.error = "error", f"{type(e).__name__}: {e}"
        store.append_event(scan_id, {"stage": "error", "message": result.error, "trace": traceback.format_exc()[-2000:],
                                     "t": time.time()})
    result.finished_at = time.time()
    store.save_doc(scan_id, "result", result)
    store.upsert_scan(scan_id, url=url, site=result.site, mode=mode, status=result.status, created_at=result.created_at,
                      finished_at=result.finished_at, summary=result.summary.model_dump())
    await emit(prog, "done" if result.status == "done" else "error",
               "Scan complete" if result.status == "done" else f"Scan failed: {result.error}", pct=100)
    return result
