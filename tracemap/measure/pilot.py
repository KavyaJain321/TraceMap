"""Batch runner for the pilot (and later the full corpus).

    python -m tracemap pilot data/corpus/pilot_50.csv [--quick] [--no-leak] [--limit N]

CSV columns: url, sector[, name]. One site at a time with a politeness delay.
Resumable: sites already completed in this run directory are skipped. Writes
var/pilot/<run>/results.csv (one row per site) and summary.json (per-sector stats).
"""

from __future__ import annotations

import asyncio
import csv
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from ..config import settings
from ..detect.classify import default_classifier
from ..pipeline import run_scan
from ..storage import Store

FIELDS = ["url", "sector", "name", "scan_id", "status", "blocked", "pages", "requests", "third_parties", "trackers",
          "companies", "tracking_cookies", "leak_tested", "fields_filled", "leaks", "leak_recipients",
          "shared_id_edges", "risky_scripts", "consent_banner", "seconds", "error"]


def load_sites(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("url") and not r["url"].startswith("#")]
    return rows


def summarize(rows: list[dict]) -> dict:
    by: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by[r["sector"]].append(r)
    out = {}
    for sector, rs in sorted(by.items()):
        ok = [r for r in rs if r["status"] == "done" and r["blocked"] != "True"]
        nums = lambda k: [float(r[k]) for r in ok if r[k] != ""]  # noqa: E731
        tested = [r for r in ok if r["leak_tested"] == "True" and int(r["fields_filled"] or 0) > 0]
        out[sector] = {
            "sites": len(rs), "completed": len(ok), "blocked": sum(r["blocked"] == "True" for r in rs),
            "errors": sum(r["status"] != "done" for r in rs),
            "median_trackers": statistics.median(nums("trackers")) if ok else None,
            "median_third_parties": statistics.median(nums("third_parties")) if ok else None,
            "forms_tested": len(tested),
            "sites_with_leak": sum(int(r["leaks"] or 0) > 0 for r in tested),
            "sites_with_shared_id": sum(int(r["shared_id_edges"] or 0) > 0 for r in ok),
            "banner_rate": round(sum(r["consent_banner"] == "True" for r in ok) / len(ok), 2) if ok else None,
            "median_seconds": statistics.median(nums("seconds")) if ok else None,
        }
    return out


async def run(sites: list[dict], run_dir: Path, mode: str, leak: bool, delay: float) -> list[dict]:
    store = Store(settings.data_dir)
    classifier = default_classifier()
    out_csv = run_dir / "results.csv"
    done: dict[str, dict] = {}
    if out_csv.exists():
        with open(out_csv, encoding="utf-8") as f:
            done = {r["url"]: r for r in csv.DictReader(f)}
    new_file = not out_csv.exists()
    with open(out_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for i, site in enumerate(sites, 1):
            url = site["url"].strip()
            if url in done:
                continue
            print(f"[{i}/{len(sites)}] {site.get('sector', '?'):12} {url}", flush=True)
            t0 = time.time()
            res = await run_scan(url, store, mode=mode, leak_test=leak, classifier=classifier)
            s = res.summary
            row = {"url": url, "sector": site.get("sector", ""), "name": site.get("name", ""), "scan_id": res.scan_id,
                   "status": res.status, "blocked": s.blocked, "pages": s.pages_visited, "requests": s.requests,
                   "third_parties": s.third_parties, "trackers": s.trackers, "companies": s.companies,
                   "tracking_cookies": s.tracking_cookies, "leak_tested": res.leaks.tested,
                   "fields_filled": len(res.leaks.fields), "leaks": s.leaks, "leak_recipients": s.leak_recipients,
                   "shared_id_edges": s.shared_id_edges, "risky_scripts": s.risky_scripts,
                   "consent_banner": s.consent_banner, "seconds": round(time.time() - t0, 1), "error": res.error or ""}
            w.writerow(row)
            f.flush()
            done[url] = {k: str(v) for k, v in row.items()}
            print(f"      -> {res.status}{' BLOCKED' if s.blocked else ''}: {s.trackers} trackers, "
                  f"{s.leaks} leaks, {s.shared_id_edges} ID links ({row['seconds']}s)", flush=True)
            await asyncio.sleep(delay)
    return list(done.values())


def main(args) -> None:
    sites = load_sites(args.csv)
    if args.limit:
        sites = sites[: args.limit]
    run_dir = settings.data_dir / "pilot" / Path(args.csv).stem
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Pilot: {len(sites)} sites -> {run_dir}")
    rows = asyncio.run(run(sites, run_dir, "quick" if args.quick else "full", not args.no_leak, args.delay))
    summary = summarize(rows)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
