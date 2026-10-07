"""Leak test visit (profile "L") and matching.

Ethics guarantees enforced in code:
  * forms are never submitted (no Enter key, submit events cancelled, form.submit() disabled)
  * password, OTP, card, Aadhaar/PAN-like fields are never touched
  * only synthetic canaries; phone only if the team configured its own number
"Before submit" therefore means: any request carrying the canary after it was typed.
"""

from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

from playwright.async_api import Error as PWError

from ..config import CrawlConfig
from ..contracts import Canary, FieldFilled, LeakEvent, LeakReport, Visit
from ..util.domains import etld1, hostname
from ..crawl.crawler import Progress, Visitor, emit, new_context
from .canary import make_email, make_phone
from .encodings import CanaryPool
from .fields import FIND_FIELDS_JS, FORM_LINKS_JS, NO_SUBMIT_JS

if TYPE_CHECKING:
    from playwright.async_api import Browser, Playwright

    from ..detect.classify import Classifier
    from ..storage import Store

SKIP_HEADERS = {"user-agent", "accept", "accept-language", "accept-encoding", "content-type", "origin", "host",
                "content-length", "cache-control", "pragma", "connection", "upgrade-insecure-requests", "priority",
                "referer", "cookie", "if-none-match", "if-modified-since", "range", "dnt"}


async def run_leak_test(pw: "Playwright", browser: "Browser", site: str, landing_url: str, config: CrawlConfig,
                        store: "Store | None", progress: Progress | None, email_domain: str,
                        phones: list[str] | None, max_form_pages: int = 2, max_pages: int = 5,
                        max_fields_per_page: int = 6) -> tuple[Visit, LeakReport]:
    report = LeakReport(tested=True)
    email = make_email(site, email_domain)
    report.canaries.append(email)
    phone = None
    if phones:
        phone = make_phone(site, phones[0])
        report.canaries.append(phone)
    else:
        report.notes.append("No team-owned phone number configured; phone fields were not filled.")
    by_kind = {"email": email, "phone": phone}

    lcfg = CrawlConfig(**{**config.__dict__, "screenshot": False, "dwell_ms": 1500})
    ctx, bridge = await new_context(pw, browser, lcfg)
    await ctx.add_init_script(NO_SUBMIT_JS)
    visitor = await Visitor(ctx, bridge, "L", lcfg, store, progress).open()
    try:
        queue = [landing_url]
        form_pages = 0
        i = 0
        while i < len(queue) and i < max_pages and form_pages < max_form_pages:
            url = queue[i]
            await emit(progress, "leak", f"[L] looking for form fields on {url}")
            pv = await visitor.load(url, i)
            report.pages_tried.append(url)
            if pv.status == "blocked":
                report.notes.append(f"blocked on {url}")
                break
            if i == 0:
                try:
                    links = await visitor.page.evaluate(FORM_LINKS_JS)
                except PWError:
                    links = []
                queue += [u for u in links if etld1(u) == site and u not in queue][: max_pages - 1]
            filled = await _fill_page(visitor, by_kind, report, max_fields_per_page, progress)
            if filled:
                form_pages += 1
                await visitor.page.wait_for_timeout(4000)  # let beacons / batched recorders fire
                await visitor.harvest(i)
            i += 1
        if not report.fields:
            report.notes.append("No email/phone fields found on the pages tried.")
    finally:
        visit = await visitor.close()
        await ctx.close()
    return visit, report


async def _fill_page(visitor: Visitor, by_kind: dict[str, Canary | None], report: LeakReport,
                     max_fields: int, progress: Progress | None) -> int:
    page = visitor.page
    filled = 0
    for frame in list(page.frames):
        try:
            fields = await frame.evaluate(FIND_FIELDS_JS)
        except PWError:
            continue
        for f in fields:
            if filled >= max_fields:
                return filled
            canary = by_kind.get(f["kind"])
            if canary is None:
                continue
            loc = frame.locator(f'[data-tm-field="{f["idx"]}"]').first
            try:
                await loc.scroll_into_view_if_needed(timeout=2500)
                try:
                    await loc.click(timeout=2500)
                except PWError:
                    await loc.focus(timeout=2500)
                typed_at = time.time()
                await loc.press_sequentially(canary.value, delay=random.randint(50, 110))
                await loc.press("Tab")
            except PWError as e:
                report.notes.append(f"could not type into {f['desc'][:40]!r}: {str(e).splitlines()[0][:80]}")
                continue
            filled += 1
            report.fields.append(FieldFilled(canary_id=canary.canary_id, kind=canary.kind, page_url=page.url,
                                             frame_url=frame.url, descriptor=f["desc"], typed_at=typed_at,
                                             in_iframe=frame != page.main_frame))
            await emit(progress, "leak", f"[L] typed test {canary.kind} into '{f['desc'][:40]}'"
                                         + (" (inside an iframe)" if frame != page.main_frame else ""),
                       kind=canary.kind)
            await page.wait_for_timeout(600)
    return filled


def _channels(r) -> list[tuple[str, str]]:
    out = [("url", r.url)]
    if r.headers.get("referer"):
        out.append(("referer", r.headers["referer"]))
    if r.headers.get("cookie"):
        out.append(("cookie", r.headers["cookie"]))
    for k, v in r.headers.items():
        if k not in SKIP_HEADERS and not k.startswith("sec-") and not k.startswith(":"):
            out.append((f"header:{k}", v))
    if r.post_data:
        out.append(("post_body", r.post_data))
    return out


def match_leaks(visit: Visit, report: LeakReport, site: str, classifier: "Classifier | None" = None,
                cloaked_hosts: set[str] | None = None) -> list[LeakEvent]:
    """Search every request of the leak visit for any encoding of any canary."""
    if not report.canaries or not report.fields:
        return []
    pool = CanaryPool(report.canaries)
    typed = {}
    for f in report.fields:
        typed.setdefault(f.canary_id, f)
    best: dict[tuple, LeakEvent] = {}
    for r in visit.requests:
        if not r.url.startswith("http"):
            continue
        rdom, rhost = etld1(r.url), hostname(r.url)
        first_party = rdom == site and rhost not in (cloaked_hosts or set())
        owner = classifier.owner_category(rhost)[0] if classifier else None
        for channel, text in _channels(r):
            # One event per (canary, request, channel): prefer what was literally on the
            # wire (raw before decoded), then the most transformed form (longest chain).
            per_canary: dict[str, tuple] = {}
            for needle, m, where in pool.search(text):
                rank = (where != "raw", -m.encoding.count("("), -len(needle))
                cur = per_canary.get(m.canary.canary_id)
                if cur is None or rank < cur[0]:
                    per_canary[m.canary.canary_id] = (rank, m, where)
            for cid, (_rank, m, where) in per_canary.items():
                f = typed.get(cid)
                if f is None:
                    continue
                ms = max(0, int((visit.started_at + r.t - f.typed_at) * 1000))
                conf = 0.9 if channel == "referer" else (0.95 if m.canary.kind == "phone" and m.encoding == "plain" else 0.99)
                enc = m.encoding if where == "raw" else f"{m.encoding} inside {where} payload"
                ev = LeakEvent(canary_id=cid, kind=m.canary.kind, field=f.descriptor,
                               recipient_domain=rdom, recipient_host=rhost, recipient_owner=owner, channel=channel,
                               encoding=enc, request_id=r.request_id, request_url=r.url[:600],
                               ms_after_typing=ms, first_party=first_party, confidence=conf)
                key = (cid, rdom, channel, enc)
                if key not in best or best[key].ms_after_typing > ms:
                    best[key] = ev
    return sorted(best.values(), key=lambda e: (e.first_party, e.ms_after_typing))
