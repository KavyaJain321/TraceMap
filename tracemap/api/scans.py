"""Background scan runner.

Scans run one at a time in a worker thread with its own asyncio loop (Playwright
needs a subprocess-capable loop, and browsers are heavy). Progress events are
kept in memory for live streaming and also persisted to events.jsonl.
"""

from __future__ import annotations

import asyncio
import ipaddress
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from ..config import settings
from ..crawl.crawler import normalize_url
from ..detect.classify import default_classifier
from ..pipeline import run_scan
from ..storage import Store


class TargetRejected(ValueError):
    pass


def validate_target(url: str, allow_local: bool) -> str:
    """http(s) only; refuse private/loopback/link-local targets unless explicitly allowed (SSRF guard)."""
    url = normalize_url(url)
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise TargetRejected("Only http(s) URLs with a hostname can be scanned.")
    if parts.username or parts.password:
        raise TargetRejected("URLs with credentials are not allowed.")
    host = parts.hostname
    if allow_local:
        return url
    if host == "localhost" or host.endswith(".localhost"):
        raise TargetRejected("Local addresses are not allowed (set TRACEMAP_ALLOW_LOCAL=1 for the testbed).")
    try:
        infos = socket.getaddrinfo(host, parts.port or (443 if parts.scheme == "https" else 80), proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise TargetRejected(f"Could not resolve {host}.")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            raise TargetRejected(f"{host} resolves to a non-public address ({ip}).")
    return url


@dataclass
class LiveScan:
    scan_id: str
    events: list[dict] = field(default_factory=list)
    done: bool = False


class ScanManager:
    def __init__(self, store: Store):
        self.store = store
        self.live: dict[str, LiveScan] = {}
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="scan")

    def submit(self, url: str, mode: str, leak_test: bool, consent: str, device: str) -> str:
        url = validate_target(url, settings.allow_local_targets)
        scan_id = self.store.new_scan_id()
        live = LiveScan(scan_id)
        with self._lock:
            self.live[scan_id] = live
        queued = sum(1 for s in self.live.values() if not s.done) - 1
        live.events.append({"stage": "queued", "message": "Queued" + (f" behind {queued} scan(s)" if queued else ""),
                            "t": time.time(), "pct": 0})
        self.store.upsert_scan(scan_id, url=url, mode=mode, status="queued", created_at=time.time())
        self._pool.submit(self._run, scan_id, url, mode, leak_test, consent, device)
        return scan_id

    def _run(self, scan_id: str, url: str, mode: str, leak_test: bool, consent: str, device: str) -> None:
        live = self.live[scan_id]

        def progress(ev: dict) -> None:
            live.events.append(ev)

        try:
            asyncio.run(run_scan(url, self.store, mode=mode, leak_test=leak_test, consent_mode=consent, device=device,
                                 scan_id=scan_id, progress=progress, classifier=default_classifier()))
        except Exception as e:  # run_scan already records errors; this is a last resort
            live.events.append({"stage": "error", "message": f"{type(e).__name__}: {e}", "t": time.time(), "pct": 100})
        finally:
            live.done = True

    def events_since(self, scan_id: str, n: int) -> tuple[list[dict], bool]:
        live = self.live.get(scan_id)
        if live is None:  # scan from an earlier server run: replay the persisted log
            return (self.store.load_events(scan_id)[n:], True)
        return live.events[n:], live.done
