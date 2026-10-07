"""Fast unit tests (no browser)."""

import base64
import hashlib
import json
import time
from urllib.parse import quote

import pytest

from tracemap.collusion.ids import id_like
from tracemap.contracts import Canary, CrawlRecord, Request, Visit
from tracemap.crawl.blocks import detect_block
from tracemap.crawl.consent import filter_compact_rules
from tracemap.crawl.links import choose_subpages
from tracemap.leak.canary import make_email, make_phone
from tracemap.leak.encodings import CanaryPool
from tracemap.storage import Store
from tracemap.util.domains import etld1, is_third_party


# ---------------------------------------------------------------- domains

@pytest.mark.parametrize("url,expected", [
    ("https://www.sbi.co.in/web/personal", "sbi.co.in"),
    ("https://onlinesbi.sbi/", "onlinesbi.sbi"),
    ("https://a.b.uidai.gov.in/x", "uidai.gov.in"),
    ("http://shop.localhost:8765/", "shop.localhost"),
    ("http://127.0.0.1:8000/", "127.0.0.1"),
    ("https://d2r1yp2w7bby2u.cloudfront.net/js/a.js", "cloudfront.net"),
])
def test_etld1(url, expected):
    assert etld1(url) == expected


def test_third_party():
    assert is_third_party("https://www.google-analytics.com/g/collect", "flipkart.com")
    assert not is_third_party("https://rukminim1.flipkart.com/x.jpg", "flipkart.com")


# ---------------------------------------------------------------- subpage choice

def test_choose_subpages_prefers_variety_and_same_site():
    hrefs = ["https://x.in/", "https://x.in/a/1", "https://x.in/a/2", "https://x.in/b", "https://y.com/c",
             "https://x.in/terms.pdf", "https://x.in/logout", "mailto:a@b.c", "https://x.in/c#top", "https://x.in/d"]
    got = choose_subpages("https://x.in/", hrefs, 4)
    assert got == ["https://x.in/a/1", "https://x.in/b", "https://x.in/c", "https://x.in/d"]
    assert choose_subpages("https://x.in/", hrefs, 4) == got  # deterministic


# ---------------------------------------------------------------- bot walls

def test_block_detection():
    assert detect_block(403, "Just a moment...", "Checking your browser", [])
    assert detect_block(200, "Home", "x" * 100, ["https://challenges.cloudflare.com/turnstile/v0"])
    assert detect_block(200, "SBI - Home", "Welcome to State Bank of India " * 200, []) is None


# ---------------------------------------------------------------- consent rule filter (port of autoconsent)

def test_compact_rule_filter():
    main = filter_compact_rules("https://www.example.in/", True)
    frame = filter_compact_rules("https://cmp.example.net/frame", False)
    assert main["r"] and isinstance(main["s"], list)
    assert len(frame["r"]) < len(main["r"])


# ---------------------------------------------------------------- canary encodings

def _pool():
    email = Canary(canary_id="em-1", kind="email", value="tm.abcdefghjk@example.com", site="x.in", created_at=0)
    phone = Canary(canary_id="ph-1", kind="phone", value="9876543210", site="x.in", created_at=0)
    return CanaryPool([email, phone]), email, phone


def test_pool_finds_plain_hashed_and_nested():
    pool, email, phone = _pool()
    sha = hashlib.sha256(email.value.encode()).hexdigest()
    cases = {
        f"https://t.com/p?em={sha}": "sha256(email)",
        f"https://t.com/p?em={sha.upper()}": "sha256(email) [upper]",
        "https://t.com/p?e=" + base64.b64encode(hashlib.md5(email.value.encode()).hexdigest().encode()).decode(): "base64(md5(email))",
        "d=" + quote(json.dumps([{"v": email.value}])): "url(email)",
        json.dumps({"ph": base64.b64encode(b"+919876543210").decode()}): "base64(+91 phone)",
    }
    for text, enc in cases.items():
        hits = pool.search(text)
        assert any(m.encoding == enc and w == "raw" for _n, m, w in hits), (text, [(m.encoding, w) for _n, m, w in hits])


def test_pool_finds_inside_encoded_payload():
    pool, email, _ = _pool()
    blob = base64.b64encode(json.dumps({"user": {"email": email.value}, "x": 1}).encode()).decode()
    hits = pool.search(f"payload={blob}")
    assert any(m.canary.kind == "email" and w.startswith("base64") for _n, m, w in hits)


def test_pool_no_false_positive_on_other_values():
    pool, _, _ = _pool()
    noise = "https://t.com/p?em=" + hashlib.sha256(b"someone.else@example.com").hexdigest() + "&ph=9876543211&ts=1700000000"
    assert pool.search(noise) == []


def test_canary_rules():
    e = make_email("x.in", "example.com")
    assert e.value.startswith("tm.") and e.value.endswith("@example.com")
    assert make_email("x.in", "example.com").value != e.value  # unique per run
    assert make_phone("x.in", "+91 98765 43210").value == "9876543210"
    with pytest.raises(ValueError):
        make_phone("x.in", "12345")


# ---------------------------------------------------------------- identifier heuristics

@pytest.mark.parametrize("v,ok", [
    ("714dbf54fc0aa8df998a3d7d", True), ("v=1&p=2", False), ("af3bl55j12v64vfyprrsrn", True),
    ("products", False), (str(int(time.time())), False), (str(int(time.time() * 1000)), False),
    ("aaaaaaaaaaaa1", False), ("x" * 120, False),
])
def test_id_like(v, ok):
    assert id_like(v) is ok


# ---------------------------------------------------------------- storage

def test_ga_cookie_tokens():
    from tracemap.collusion.ids import _tokens
    toks = [t for t in _tokens("GA1.2.1234567890.1700000000") if id_like(t)]
    assert toks == ["1234567890"]  # the random client-id part; the timestamp part is rejected


def test_store_roundtrip(tmp_path):
    s = Store(tmp_path)
    sid = s.new_scan_id()
    rec = CrawlRecord(crawl_id=sid, input_url="https://x.in", site="x.in", started_at=1.0,
                      visits=[Visit(profile="A", started_at=1.0, requests=[Request(request_id="A:1:0", url="https://x.in/")])])
    s.save_doc(sid, "crawl", rec)
    assert s.load_doc(sid, "crawl", CrawlRecord).visits[0].requests[0].url == "https://x.in/"
    sha = s.put_blob(b"hello")
    assert s.get_blob(sha) == b"hello" and s.get_blob("../etc") is None
    s.upsert_scan(sid, url="https://x.in", status="done", created_at=1.0, summary={"trackers": 3})
    assert s.list_scans()[0]["summary"]["trackers"] == 3
    with pytest.raises(ValueError):
        s.scan_dir("../escape")
