"""End-to-end against the local testbed: precision/recall vs planted ground truth.

Needs a Chromium browser (installed Chrome or Playwright's build). ~2-3 minutes.
Run only these with:  pytest -m browser
"""

import asyncio
import json
from pathlib import Path

import pytest

from testbed.server import TestbedServer
from tracemap.config import CrawlConfig
from tracemap.contracts import Canary
from tracemap.detect.classify import Classifier
from tracemap.leak.tracer import match_leaks
from tracemap.pipeline import run_scan
from tracemap.storage import Store

pytestmark = pytest.mark.browser
GT = json.loads((Path(__file__).parent.parent / "testbed" / "ground_truth.json").read_text(encoding="utf-8"))
PORT = 8766
PHONE = "9876543210"  # testbed only (local, nothing leaves this machine)


@pytest.fixture(scope="module")
def testbed():
    with TestbedServer(PORT) as tb:
        yield tb


@pytest.fixture(scope="module")
def classifier():
    return Classifier.load(filter_lists=False)


@pytest.fixture(scope="module")
def shop_result(testbed, classifier, tmp_path_factory):
    store = Store(tmp_path_factory.mktemp("scans"))
    res = asyncio.run(run_scan(testbed.url("shop"), store, mode="full", phones=[PHONE], classifier=classifier))
    return res, store


def test_shop_scan_completes(shop_result):
    res, _ = shop_result
    assert res.status == "done", res.error


def test_third_parties_exact(shop_result):
    res, _ = shop_result
    found = {p.domain for p in res.parties if not p.first_party}
    assert found == set(GT["shop.localhost"]["third_parties"])


def test_leak_recall_and_precision(shop_result):
    res, _ = shop_result
    third = [e for e in res.leaks.leaks if not e.first_party]
    for exp in GT["shop.localhost"]["leaks"]:  # recall = 1.0
        assert any(e.recipient_domain == exp["recipient"] and e.kind == exp["kind"]
                   and exp["encoding_contains"] in e.encoding for e in third), exp
    expected_recipients = {x["recipient"] for x in GT["shop.localhost"]["leaks"]}
    assert {e.recipient_domain for e in third} <= expected_recipients  # precision: no unexpected recipient
    assert all(e.before_submit for e in third)
    fp = [e for e in res.leaks.leaks if e.first_party]
    assert all(e.recipient_domain == "shop.localhost" for e in fp)


def test_negative_control_other_canary_finds_nothing(shop_result):
    """Matching the same traffic against canaries that were never typed must give zero hits."""
    res, store = shop_result
    from tracemap.contracts import CrawlRecord
    rec = store.load_doc(res.scan_id, "crawl", CrawlRecord)
    report = res.leaks.model_copy(deep=True)
    report.canaries = [Canary(canary_id=c.canary_id, kind=c.kind, site=c.site, created_at=c.created_at,
                              value="tm.zzzzzzzzzz@example.com" if c.kind == "email" else "9123456780")
                       for c in report.canaries]
    assert match_leaks(rec.visit("L"), report, rec.site) == []


def test_cookie_sync_edge(shop_result):
    res, _ = shop_result
    shared = {(e.a, e.b) for e in res.graph.edges if e.kind == "shared_id" and e.confidence >= 0.8}
    for a, b in GT["shop.localhost"]["shared_id_pairs"]:
        assert tuple(sorted((a, b))) in shared


def test_behaviour_flags(shop_result):
    res, _ = shop_result
    flags = {s.domain: set(s.flags) for s in res.risky_scripts}
    for dom, expected in GT["shop.localhost"]["fingerprinting"].items():
        assert set(expected) <= flags.get(dom, set())
    for dom in GT["shop.localhost"]["reads_form"]:
        assert "reads_form" in flags.get(dom, set())


def test_clean_site_is_clean(testbed, classifier, tmp_path):
    res = asyncio.run(run_scan(testbed.url("clean"), Store(tmp_path), mode="quick", phones=[PHONE],
                               classifier=classifier))
    assert res.status == "done"
    assert [p for p in res.parties if not p.first_party] == []
    assert res.leaks.fields and not [e for e in res.leaks.leaks if not e.first_party]


def test_blocked_site_detected(testbed, classifier, tmp_path):
    res = asyncio.run(run_scan(testbed.url("blocked"), Store(tmp_path), mode="quick", classifier=classifier,
                               config=CrawlConfig.quick(dwell_ms=500)))
    assert res.summary.blocked
    assert any(f.code == "SCAN_BLOCKED" for f in res.findings)
