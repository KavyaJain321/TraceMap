"""API tests without a browser: validation, listing, proof lookup, SSRF guard."""

import pytest
from fastapi.testclient import TestClient

from tracemap.api.app import create_app
from tracemap.api.scans import TargetRejected, validate_target
from tracemap.contracts import CrawlRecord, Request, ScanResult, Visit, PageVisit
from tracemap.storage import Store


@pytest.mark.parametrize("url", ["http://localhost:8000", "http://shop.localhost:8765/", "http://127.0.0.1/",
                                 "http://10.0.0.5/", "http://[::1]/", "ftp://example.com/", "http://user:pw@example.com/"])
def test_ssrf_guard_rejects(url):
    with pytest.raises(TargetRejected):
        validate_target(url, allow_local=False)


def test_ssrf_guard_allows_local_when_enabled():
    assert validate_target("shop.localhost:8765", allow_local=True) == "https://shop.localhost:8765"


@pytest.fixture
def client(tmp_path):
    store = Store(tmp_path)
    sid = "20260101-000000-abcdef"
    rec = CrawlRecord(crawl_id=sid, input_url="https://x.in", site="x.in", started_at=100.0, visits=[
        Visit(profile="L", started_at=100.0, pages=[PageVisit(index=0, url="https://x.in/")],
              requests=[Request(request_id="L:1:0", url="https://t.com/c?em=abc", t=2.5)])])
    store.save_doc(sid, "crawl", rec)
    store.save_doc(sid, "result", ScanResult(scan_id=sid, url="https://x.in", site="x.in", mode="quick",
                                             status="done", created_at=100.0))
    store.upsert_scan(sid, url="https://x.in", status="done", created_at=100.0, summary={"trackers": 0})
    store.append_event(sid, {"stage": "done", "message": "Scan complete", "t": 1})
    return TestClient(create_app(store)), sid


def test_list_get_and_proof(client):
    c, sid = client
    assert c.get("/api/health").json()["ok"]
    assert c.get("/api/scans").json()[0]["scan_id"] == sid
    assert c.get(f"/api/scans/{sid}").json()["status"] == "done"
    proof = c.get(f"/api/scans/{sid}/requests/L:1:0").json()
    assert proof["url"].startswith("https://t.com/c") and proof["absolute_time"] == 102.5
    assert c.get(f"/api/scans/{sid}/requests/nope").status_code == 404
    assert c.get("/api/scans/..%2F..%2Fescape").status_code == 404


def test_events_replay_for_finished_scan(client):
    c, sid = client
    body = c.get(f"/api/scans/{sid}/events").text
    assert "Scan complete" in body and "event: end" in body


def test_rejects_local_target(client):
    c, _ = client
    r = c.post("/api/scans", json={"url": "http://127.0.0.1:9/"})
    assert r.status_code == 400
