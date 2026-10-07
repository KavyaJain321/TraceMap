"""Stage 1: instrumented crawl of one site.

Sequence per site (see PANEL_REVIEW.md B5):
    A   fresh profile: landing page, pick subpages, visit them
    B   second fresh profile: the same pages (a different "user")
    A2  profile A again after B (same cookies/storage): the "revisit"
A value that is stable across A/A2 but different in B is a user identifier.
The leak test (profile L) lives in tracemap.leak and reuses Visitor.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from pathlib import Path
from typing import Awaitable, Callable

from playwright.async_api import Browser, BrowserContext, Error as PWError, Page, Playwright, async_playwright

from ..config import CrawlConfig
from ..contracts import APICall, ConsentInfo, Cookie, CrawlRecord, PageVisit, Script, StorageItem, Visit
from ..storage import Store
from ..util.domains import etld1, hostname
from .blocks import detect_block
from .capture import NetworkCapture
from .consent import ConsentBridge
from .links import choose_subpages

INSTRUMENT_JS = (Path(__file__).parent / "instrument.js").read_text(encoding="utf-8")
MOBILE_DEVICE = "Pixel 7"

Progress = Callable[[dict], Awaitable[None] | None]
CALL_TIMEOUT = 10.0  # seconds for any single in-page call; a frozen page must not stall the crawl


async def bounded(aw, default=None, timeout: float = CALL_TIMEOUT):
    """Await with a hard timeout. Playwright's evaluate/title/mouse calls have no timeout of their
    own and hang forever on a page whose main thread is blocked."""
    try:
        return await asyncio.wait_for(aw, timeout)
    except (asyncio.TimeoutError, PWError):
        return default


async def emit(progress: Progress | None, stage: str, message: str, **data) -> None:
    if progress is None:
        return
    res = progress({"stage": stage, "message": message, "t": time.time(), **data})
    if asyncio.iscoroutine(res):
        await res


# ---------------------------------------------------------------------- browser


async def launch_browser(pw: Playwright, config: CrawlConfig) -> Browser:
    args = []
    if config.disable_site_isolation:
        args += ["--disable-features=IsolateOrigins,site-per-process", "--disable-site-isolation-trials"]
    if config.channel == "auto":
        channels = ["chrome", None]  # installed Google Chrome first, then Playwright's build
    elif config.channel == "bundled":
        channels = [None]
    else:
        channels = [config.channel]
    last: Exception | None = None
    for ch in channels:
        try:
            kw = {"headless": config.headless, "args": args}
            if ch:
                kw["channel"] = ch
            return await pw.chromium.launch(**kw)
        except PWError as e:
            last = e
    raise RuntimeError(f"could not launch Chromium: {last}")


async def new_context(pw: Playwright, browser: Browser, config: CrawlConfig) -> tuple[BrowserContext, ConsentBridge]:
    if config.device == "mobile":
        dev = dict(pw.devices[MOBILE_DEVICE])
        dev.pop("default_browser_type", None)
    else:
        dev = {"viewport": {"width": 1366, "height": 768}}
    ctx = await browser.new_context(**dev, locale=config.locale, timezone_id=config.timezone_id,
                                    ignore_https_errors=False)
    ctx.set_default_navigation_timeout(config.page_timeout_ms)
    await ctx.add_init_script(INSTRUMENT_JS)
    bridge = ConsentBridge(config.consent_mode)
    await bridge.install(ctx)
    return ctx, bridge


# ---------------------------------------------------------------------- one visit


class Visitor:
    """Drives one page through a list of URLs while capturing everything."""

    def __init__(self, ctx: BrowserContext, bridge: ConsentBridge, profile: str, config: CrawlConfig,
                 store: Store | None, progress: Progress | None = None):
        self.ctx, self.bridge, self.profile, self.config = ctx, bridge, profile, config
        self.store, self.progress = store, progress
        self.started_at = time.time()
        self.visit = Visit(profile=profile, started_at=self.started_at)
        self.page: Page | None = None
        self.cap: NetworkCapture | None = None
        self._storage: dict[tuple, StorageItem] = {}
        self._api: dict[tuple, APICall] = {}
        self._js_cookie_setters: dict[str, str] = {}

    async def open(self) -> "Visitor":
        self.page = await self.ctx.new_page()
        self.cap = await NetworkCapture.attach(self.ctx, self.page, self.started_at, self.store, self.profile)
        return self

    async def load(self, url: str, index: int) -> PageVisit:
        assert self.page and self.cap
        self.cap.page_index = index
        pv = PageVisit(index=index, url=url)
        t0 = time.time()
        try:
            resp = await self.page.goto(url, wait_until="load", timeout=self.config.page_timeout_ms)
            pv.http_status = resp.status if resp else None
        except PWError as e:
            msg = str(e).splitlines()[0]
            pv.status, pv.error = ("timeout", msg) if "Timeout" in msg else ("error", msg)
            if "Timeout" not in msg:
                self.visit.pages.append(pv)
                return pv
        await bounded(self.page.wait_for_load_state("networkidle", timeout=self.config.settle_ms),
                      timeout=self.config.settle_ms / 1000 + 5)
        if self.config.scroll:
            await bounded(self._scroll(), timeout=CALL_TIMEOUT)
        await asyncio.sleep(self.config.dwell_ms / 1000)
        pv.load_ms = int((time.time() - t0) * 1000)
        pv.final_url = self.page.url
        pv.title = ((await bounded(self.page.title(), "")) or "")[:300]
        body = await bounded(self.page.evaluate("() => (document.body && document.body.innerText || '').slice(0, 5000)"), "")
        if pv.title == "" and body == "" and pv.status == "ok":
            pv.error = "page did not respond to inspection (frozen main thread?)"
        reason = detect_block(pv.http_status, pv.title, body, [f.url for f in self.page.frames])
        if reason:
            pv.status, pv.block_reason = "blocked", reason
        if self.config.screenshot and index == 0 and self.store is not None:
            shot = await bounded(self.page.screenshot(type="jpeg", quality=60, timeout=5000), timeout=8)
            if shot:
                pv.screenshot_sha256 = self.store.put_blob(shot)
        await bounded(self.harvest(index), timeout=30)
        self.visit.pages.append(pv)
        return pv

    async def _scroll(self) -> None:
        try:
            for _ in range(6):
                await self.page.mouse.wheel(0, 700)
                await self.page.wait_for_timeout(250)
            await self.page.evaluate("() => window.scrollTo(0, 0)")
        except PWError:
            pass

    async def harvest(self, index: int) -> None:
        """Collect API calls, storage and inline scripts from every frame of the current page."""
        assert self.page
        for frame in self.page.frames:
            data = await bounded(frame.evaluate("() => window.__tm ? window.__tm.collect() : null"), timeout=5)
            if data:
                for c in data.get("calls", []):
                    key = (c["api"], c["script_url"])
                    if key in self._api:
                        a = self._api[key]
                        a.count += c["count"]
                        a.sample_args = (a.sample_args + [x for x in c["sample_args"] if x not in a.sample_args])[:6]
                    else:
                        self._api[key] = APICall(api=c["api"], script_url=c["script_url"], count=c["count"],
                                                 sample_args=c["sample_args"], page_index=index)
                for jc in data.get("cookies", []):
                    self._js_cookie_setters.setdefault(jc["name"], jc["script"])
            st = await bounded(frame.evaluate("""() => {
                    const out = {origin: location.origin, local: [], session: []};
                    try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i);
                          out.local.push([k, String(localStorage.getItem(k)).slice(0, 2000)]); } } catch (e) {}
                    try { for (let i = 0; i < sessionStorage.length; i++) { const k = sessionStorage.key(i);
                          out.session.push([k, String(sessionStorage.getItem(k)).slice(0, 2000)]); } } catch (e) {}
                    return out; }"""), timeout=5)
            if st:
                for kind in ("local", "session"):
                    for k, v in st[kind]:
                        self._storage[(st["origin"], k, kind)] = StorageItem(origin=st["origin"], key=k, value=v, kind=kind)
        if self.store is not None:
            inline = await bounded(self.page.evaluate(
                "() => Array.from(document.scripts).filter(s => !s.src).map(s => s.textContent || '')"), [], timeout=5)
            for i, text in enumerate(inline):
                if text.strip():
                    data = text.encode("utf-8", "replace")
                    self.visit.scripts.append(Script(url=f"inline:{self.page.url}#{i}", sha256=self.store.put_blob(data),
                                                     size=len(data), inline=True, page_index=index))

    async def close(self) -> Visit:
        assert self.page and self.cap
        await self.cap.drain()
        self.visit.requests = self.cap.requests
        self.visit.scripts = self.cap.scripts + self.visit.scripts
        self.visit.api_calls = list(self._api.values())
        self.visit.storage = list(self._storage.values())
        self.visit.cookies = await bounded(self._cookies(), [], timeout=15)
        self.visit.consent = self.bridge.info.model_copy(deep=True)
        self.visit.finished_at = time.time()
        await bounded(self.page.close(), timeout=10)
        return self.visit

    async def _cookies(self) -> list[Cookie]:
        http_setters: dict[str, str] = {}
        for r in self.cap.requests:
            for line in r.set_cookies:
                name = line.split("=", 1)[0].strip()
                if name:
                    http_setters.setdefault(name, r.url)
        out = []
        for c in await self.ctx.cookies():
            name = c["name"]
            if name in http_setters:
                set_by, setter = "http", http_setters[name]
            elif name in self._js_cookie_setters:
                set_by, setter = "js", self._js_cookie_setters[name] or None
            else:
                set_by, setter = "unknown", None
            out.append(Cookie(name=name, value=c["value"], domain=c["domain"], path=c.get("path", "/"),
                              expires=c.get("expires", -1), http_only=c.get("httpOnly", False),
                              secure=c.get("secure", False), same_site=c.get("sameSite"),
                              set_by=set_by, setter_url=setter))
        return out


# ---------------------------------------------------------------------- whole crawl


async def visit_pages(visitor: Visitor, urls: list[str], progress: Progress | None,
                      choose_from_landing: int = 0) -> list[str]:
    """Visit urls in order. If choose_from_landing > 0, pick that many subpages from
    the landing page and append them. Returns the full URL list actually used."""
    urls = list(urls)
    i = 0
    while i < len(urls):
        url = urls[i]
        await emit(progress, "crawl", f"[{visitor.profile}] opening {url}", profile=visitor.profile, page=i)
        pv = await visitor.load(url, i)
        if pv.status == "blocked":
            await emit(progress, "crawl", f"[{visitor.profile}] blocked: {pv.block_reason}", level="warn")
            break
        if i == 0 and choose_from_landing and pv.status in ("ok", "timeout"):
            hrefs = await bounded(visitor.page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)"), [])
            subs = choose_subpages(pv.final_url or url, hrefs, choose_from_landing, etld1(pv.final_url or url))
            urls += subs
            await emit(progress, "crawl", f"chose {len(subs)} subpages", subpages=subs)
        n_third = len({etld1(r.url) for r in visitor.cap.requests} - {etld1(url)})
        await emit(progress, "crawl", f"[{visitor.profile}] page {i + 1}: {len(visitor.cap.requests)} requests, "
                                      f"{n_third} other domains so far", requests=len(visitor.cap.requests),
                   third_parties=n_third)
        i += 1
    return urls


def normalize_url(url: str) -> str:
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    return url


async def crawl(url: str, config: CrawlConfig | None = None, store: Store | None = None,
                progress: Progress | None = None, crawl_id: str | None = None,
                after_profiles: Callable[[Playwright, Browser, CrawlRecord, list[str]], Awaitable[None]] | None = None,
                ) -> CrawlRecord:
    """Crawl one site. `after_profiles` lets the pipeline run the leak test in the same browser."""
    config = config or CrawlConfig()
    url = normalize_url(url)
    record = CrawlRecord(crawl_id=crawl_id or uuid.uuid4().hex[:12], input_url=url, site=etld1(url),
                         started_at=time.time())
    async with async_playwright() as pw:
        browser = await launch_browser(pw, config)
        record.config = {**config.__dict__, "browser_version": browser.version,
                         "browser": browser.browser_type.name}
        await emit(progress, "crawl", f"browser ready ({browser.version}, {config.device})")
        urls: list[str] = [url]
        contexts: dict[str, tuple[BrowserContext, ConsentBridge]] = {}
        try:
            for profile in config.profiles:
                base = "A" if profile == "A2" else profile
                if base not in contexts:
                    contexts[base] = await new_context(pw, browser, config)
                ctx, bridge = contexts[base]
                bridge.info = ConsentInfo(mode=config.consent_mode)  # per-visit consent outcome
                visitor = await Visitor(ctx, bridge, profile, config, store, progress).open()
                first = profile == config.profiles[0]
                urls = await visit_pages(visitor, urls if not first else [url],
                                         progress, choose_from_landing=config.subpages if first else 0)
                record.visits.append(await visitor.close())
                if record.visits[-1].pages and record.visits[-1].pages[0].final_url:
                    record.site = etld1(record.visits[-1].pages[0].final_url) or record.site
            if after_profiles is not None:
                await after_profiles(pw, browser, record, urls)
        finally:
            for ctx, _ in contexts.values():
                await ctx.close()
            await browser.close()
    record.finished_at = time.time()
    record.status = crawl_status(record)
    return record


def crawl_status(record: CrawlRecord) -> str:
    pages = [p for v in record.visits for p in v.pages]
    if not pages:
        return "error"
    first = record.visits[0].pages[0] if record.visits[0].pages else pages[0]
    if first.status in ("blocked", "error"):
        return first.status
    if any(p.status != "ok" for p in pages):
        return "partial"
    return "ok"
