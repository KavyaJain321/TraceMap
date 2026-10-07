"""Pilot / study report: per-sector numbers, company prevalence, list-coverage gap.

Built from results.csv plus each scan's stored ScanResult, so it can be regenerated
at any time (also after `tracemap analyze` improves a detector).
"""

from __future__ import annotations

import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from ..contracts import ScanResult
from ..storage import Store

SECTOR_ORDER = ["government", "banking", "health", "ecommerce", "edtech"]


def _median(xs: list[float]) -> float | None:
    return round(statistics.median(xs), 1) if xs else None


def build_report(run_dir: Path, store: Store) -> dict:
    rows_path = run_dir / "results.csv"
    if not rows_path.exists():
        return {"name": run_dir.name, "sites": [], "sectors": [], "companies": [], "unlisted": [], "totals": {}}
    with open(rows_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    sites, results = [], {}
    for r in rows:
        res = store.load_doc(r["scan_id"], "result", ScanResult) if r.get("scan_id") else None
        if res is not None:
            results[r["scan_id"]] = res
        sites.append({
            "url": r["url"], "name": r.get("name") or "", "sector": r["sector"], "scan_id": r["scan_id"],
            "status": "blocked" if r["blocked"] == "True" else ("done" if r["status"] == "done" else "error"),
            "third_parties": int(r["third_parties"] or 0), "trackers": int(r["trackers"] or 0),
            "companies": int(r["companies"] or 0), "shared_id_edges": int(r["shared_id_edges"] or 0),
            "consent_banner": r["consent_banner"] == "True", "leaks": int(r["leaks"] or 0),
            "seconds": float(r["seconds"] or 0),
        })

    ok = [s for s in sites if s["status"] == "done"]
    by_sector: dict[str, list[dict]] = defaultdict(list)
    for s in sites:
        by_sector[s["sector"]].append(s)

    company_sites: dict[str, set[str]] = defaultdict(set)
    company_sectors: dict[str, Counter] = defaultdict(Counter)
    unlisted: dict[str, set[str]] = defaultdict(set)
    third_total = unlisted_total = 0
    for s in ok:
        res = results.get(s["scan_id"])
        if res is None:
            continue
        for p in res.parties:
            if p.first_party or p.same_owner_as_site:
                continue
            third_total += 1
            if p.is_tracker:
                name = p.owner or p.domain
                if s["url"] not in company_sites[name]:
                    company_sector_key = s["sector"]
                    company_sectors[name][company_sector_key] += 1
                company_sites[name].add(s["url"])
            if not p.sources:
                unlisted_total += 1
                unlisted[p.domain].add(s["url"])

    sectors = []
    for sec in sorted(by_sector, key=lambda x: SECTOR_ORDER.index(x) if x in SECTOR_ORDER else 99):
        ss = by_sector[sec]
        done = [s for s in ss if s["status"] == "done"]
        sectors.append({
            "sector": sec, "sites": len(ss), "completed": len(done),
            "blocked": sum(s["status"] == "blocked" for s in ss), "errors": sum(s["status"] == "error" for s in ss),
            "median_trackers": _median([s["trackers"] for s in done]),
            "median_third_parties": _median([s["third_parties"] for s in done]),
            "max_trackers": max((s["trackers"] for s in done), default=None),
            "sites_with_id_sharing": sum(s["shared_id_edges"] > 0 for s in done),
            "banner_rate": round(sum(s["consent_banner"] for s in done) / len(done), 2) if done else None,
        })

    companies = sorted(({"company": c, "sites": len(u), "by_sector": dict(company_sectors[c])}
                        for c, u in company_sites.items()), key=lambda x: (-x["sites"], x["company"]))
    unlisted_rows = sorted(({"domain": d, "sites": len(u)} for d, u in unlisted.items()),
                           key=lambda x: (-x["sites"], x["domain"]))
    totals = {
        "sites": len(sites), "completed": len(ok), "blocked": sum(s["status"] == "blocked" for s in sites),
        "errors": sum(s["status"] == "error" for s in sites),
        "median_trackers": _median([s["trackers"] for s in ok]),
        "sites_with_trackers": sum(s["trackers"] > 0 for s in ok),
        "sites_with_id_sharing": sum(s["shared_id_edges"] > 0 for s in ok),
        "banner_rate": round(sum(s["consent_banner"] for s in ok) / len(ok), 2) if ok else None,
        "third_party_observations": third_total, "unlisted_observations": unlisted_total,
        "unlisted_share": round(unlisted_total / third_total, 3) if third_total else None,
        "median_seconds": _median([s["seconds"] for s in ok]),
    }
    return {"name": run_dir.name, "totals": totals, "sectors": sectors, "companies": companies[:25],
            "unlisted": unlisted_rows[:30], "sites": sites}
