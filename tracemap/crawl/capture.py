"""Network capture over a raw Chrome DevTools Protocol session.

Playwright's high-level request events don't expose initiator call stacks or the
raw Set-Cookie headers, so we listen to CDP Network events directly. With site
isolation disabled (see CrawlConfig) one page-level session sees every frame.
"""

from __future__ import annotations

import asyncio
import base64
import time
from typing import TYPE_CHECKING

from ..contracts import Initiator, Request, Script

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, CDPSession, Page

    from ..storage import Store

MAX_SCRIPT_BYTES = 5_000_000
MAX_POST_CHARS = 200_000


def _stack_urls(stack: dict | None) -> list[str]:
    """Script URLs on the initiator stack, innermost first, de-duplicated."""
    out: list[str] = []
    while stack:
        for f in stack.get("callFrames", []):
            u = f.get("url")
            if u and u not in out:
                out.append(u)
        stack = stack.get("parent")
    return out


def _lower_headers(h: dict | None) -> dict[str, str]:
    return {str(k).lower(): str(v) for k, v in (h or {}).items()}


class NetworkCapture:
    def __init__(self, session: "CDPSession", visit_start: float, store: "Store | None", tag: str):
        self.session = session
        self.visit_start = visit_start
        self.store = store
        self.tag = tag  # prefix for request ids (profile name), unique within a crawl
        self.page_index = 0
        self.requests: list[Request] = []
        self.scripts: list[Script] = []
        self._current: dict[str, Request] = {}  # CDP requestId -> latest hop
        self._hops: dict[str, int] = {}
        self._pending_extra: dict[str, dict] = {}
        self._tasks: set[asyncio.Task] = set()
        self._seen_script_urls: set[str] = set()

    @classmethod
    async def attach(cls, context: "BrowserContext", page: "Page", visit_start: float,
                     store: "Store | None", tag: str) -> "NetworkCapture":
        session = await context.new_cdp_session(page)
        cap = cls(session, visit_start, store, tag)
        session.on("Network.requestWillBeSent", cap._on_request)
        session.on("Network.requestWillBeSentExtraInfo", cap._on_request_extra)
        session.on("Network.responseReceived", cap._on_response)
        session.on("Network.responseReceivedExtraInfo", cap._on_response_extra)
        session.on("Network.loadingFinished", cap._on_finished)
        session.on("Network.loadingFailed", cap._on_failed)
        await session.send("Network.enable", {"maxPostDataSize": MAX_POST_CHARS})
        return cap

    # ------------------------------------------------------------------ helpers

    def _spawn(self, coro) -> None:
        t = asyncio.ensure_future(coro)
        self._tasks.add(t)
        t.add_done_callback(self._tasks.discard)

    async def drain(self, timeout: float = 10.0) -> None:
        """Wait for pending body/post-data fetches."""
        if self._tasks:
            await asyncio.wait(list(self._tasks), timeout=timeout)

    def mark_time(self) -> float:
        return time.time() - self.visit_start

    # ------------------------------------------------------------------ CDP handlers

    def _on_request(self, e: dict) -> None:
        rid = e["requestId"]
        req = e["request"]
        prev = self._current.get(rid)
        redirect_from = None
        if prev is not None and e.get("redirectResponse"):
            rr = e["redirectResponse"]
            prev.status = rr.get("status")
            prev.response_headers = prev.response_headers or _lower_headers(rr.get("headers"))
            prev.remote_ip = rr.get("remoteIPAddress")
            redirect_from = prev.request_id

        hop = self._hops.get(rid, -1) + 1
        self._hops[rid] = hop
        init = e.get("initiator") or {}
        initiator = Initiator(
            type="redirect" if redirect_from else init.get("type", "other"),
            # For a redirect hop the meaningful initiator is the URL that redirected.
            url=prev.url if redirect_from else init.get("url"),
            stack_urls=_stack_urls(init.get("stack")),
        )

        post = req.get("postData")
        if post is None and req.get("postDataEntries"):
            chunks = []
            for entry in req["postDataEntries"]:
                try:
                    chunks.append(base64.b64decode(entry.get("bytes", "")).decode("utf-8", "replace"))
                except Exception:
                    pass
            post = "".join(chunks) or None

        wall = e.get("wallTime") or time.time()
        r = Request(
            request_id=f"{self.tag}:{rid}:{hop}",
            url=req["url"],
            method=req.get("method", "GET"),
            resource_type=e.get("type", "Other"),
            page_index=self.page_index,
            frame_url=e.get("documentURL"),
            initiator=initiator,
            headers=_lower_headers(req.get("headers")),
            post_data=post[:MAX_POST_CHARS] if post else None,
            t=round(wall - self.visit_start, 3),
            redirect_from=redirect_from,
        )
        self.requests.append(r)
        self._current[rid] = r
        extra = self._pending_extra.pop(rid, None)
        if extra:
            r.headers.update(extra)
        if r.post_data is None and req.get("hasPostData"):
            self._spawn(self._fetch_post(rid, r))

    def _on_request_extra(self, e: dict) -> None:
        headers = _lower_headers(e.get("headers"))
        r = self._current.get(e["requestId"])
        if r is None:
            self._pending_extra[e["requestId"]] = headers
        else:
            r.headers.update(headers)  # includes the real Cookie header

    def _on_response(self, e: dict) -> None:
        r = self._current.get(e["requestId"])
        if r is None:
            return
        resp = e.get("response", {})
        r.status = resp.get("status")
        r.remote_ip = resp.get("remoteIPAddress")
        if not r.response_headers:
            r.response_headers = _lower_headers(resp.get("headers"))

    def _on_response_extra(self, e: dict) -> None:
        r = self._current.get(e["requestId"])
        if r is None:
            return
        raw = _lower_headers(e.get("headers"))
        r.response_headers.update(raw)
        sc = raw.get("set-cookie")
        if sc:
            r.set_cookies.extend(line for line in sc.split("\n") if line.strip())
        if e.get("statusCode") and r.status is None:
            r.status = e["statusCode"]

    def _on_finished(self, e: dict) -> None:
        r = self._current.get(e["requestId"])
        if r is not None and r.resource_type == "Script" and self.store is not None:
            if r.url not in self._seen_script_urls:
                self._seen_script_urls.add(r.url)
                self._spawn(self._fetch_script(e["requestId"], r))

    def _on_failed(self, e: dict) -> None:
        r = self._current.get(e["requestId"])
        if r is not None:
            r.failed = e.get("blockedReason") or e.get("errorText") or "failed"

    # ------------------------------------------------------------------ async fetches

    async def _fetch_post(self, rid: str, r: Request) -> None:
        try:
            res = await self.session.send("Network.getRequestPostData", {"requestId": rid})
            r.post_data = (res.get("postData") or "")[:MAX_POST_CHARS] or None
        except Exception:
            pass

    async def _fetch_script(self, rid: str, r: Request) -> None:
        try:
            res = await self.session.send("Network.getResponseBody", {"requestId": rid})
        except Exception:
            return
        body = res.get("body") or ""
        data = base64.b64decode(body) if res.get("base64Encoded") else body.encode("utf-8", "replace")
        if len(data) > MAX_SCRIPT_BYTES:
            return
        sha = self.store.put_blob(data)
        self.scripts.append(Script(url=r.url, sha256=sha, size=len(data), page_index=r.page_index))
