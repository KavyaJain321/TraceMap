"""Pilot report: sector aggregation, company prevalence, unlisted third parties."""

import csv

from tracemap.contracts import DetectedParty, ScanResult
from tracemap.measure.pilot import FIELDS
from tracemap.measure.report import build_report
from tracemap.storage import Store


def _scan(store, sid, url, parties):
    store.save_doc(sid, "result", ScanResult(scan_id=sid, url=url, site=url, mode="quick", status="done",
                                             created_at=0, parties=parties))


def test_build_report(tmp_path):
    store = Store(tmp_path)
    run = tmp_path / "pilot" / "p"
    run.mkdir(parents=True)
    g = DetectedParty(domain="google-analytics.com", owner="Google", category="analytics", is_tracker=True, sources=["ddg-tds"])
    unk = DetectedParty(domain="mystery.in", category="unknown", sources=[])
    own = DetectedParty(domain="cdn-of-site.com", owner="Site", same_owner_as_site=True)
    _scan(store, "s1", "a.gov.in", [DetectedParty(domain="a.gov.in", first_party=True), g, unk])
    _scan(store, "s2", "b.com", [DetectedParty(domain="b.com", first_party=True), g, own])
    rows = [
        {"url": "a.gov.in", "sector": "government", "scan_id": "s1", "status": "done", "blocked": "False", "trackers": 1,
         "third_parties": 2, "companies": 2, "shared_id_edges": 1, "consent_banner": "True", "leaks": 0, "seconds": 10},
        {"url": "b.com", "sector": "ecommerce", "scan_id": "s2", "status": "done", "blocked": "False", "trackers": 1,
         "third_parties": 2, "companies": 2, "shared_id_edges": 0, "consent_banner": "False", "leaks": 0, "seconds": 20},
        {"url": "c.bank", "sector": "banking", "scan_id": "s3", "status": "done", "blocked": "True", "trackers": 0,
         "third_parties": 0, "companies": 0, "shared_id_edges": 0, "consent_banner": "False", "leaks": 0, "seconds": 5},
    ]
    with open(run / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, restval="")
        w.writeheader()
        w.writerows(rows)
    rep = build_report(run, store)
    assert rep["totals"]["completed"] == 2 and rep["totals"]["blocked"] == 1
    assert rep["companies"][0] == {"company": "Google", "sites": 2, "by_sector": {"government": 1, "ecommerce": 1}}
    assert rep["unlisted"] == [{"domain": "mystery.in", "sites": 1}]
    assert rep["totals"]["third_party_observations"] == 3  # same-owner CDN excluded
    assert [s["sector"] for s in rep["sectors"]] == ["government", "banking", "ecommerce"]
