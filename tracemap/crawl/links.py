"""Choose which same-site subpages to visit.

Deterministic: profiles A, B and A2 must see the same pages, so the choice is made
once (from profile A's landing page) and reused. We prefer variety: one link per
first path segment before taking a second from the same section.
"""

from __future__ import annotations

from urllib.parse import urldefrag, urlsplit

from ..util.domains import etld1, is_http

SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".zip", ".rar", ".exe", ".apk",
            ".mp4", ".mp3", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".xml", ".json")
SKIP_WORDS = ("logout", "log-out", "signout", "sign-out", "unsubscribe", "delete", "remove", "cart/add",
              "mailto:", "tel:", "javascript:", "whatsapp:")


def _norm(url: str) -> str:
    u, _ = urldefrag(url)
    return u.rstrip("/") or u


def choose_subpages(landing_url: str, hrefs: list[str], n: int, site: str | None = None) -> list[str]:
    site = site or etld1(landing_url)
    landing = _norm(landing_url)
    seen: set[str] = {landing}
    candidates: list[str] = []
    for h in hrefs:
        if not h or not is_http(h):
            continue
        u = _norm(h)
        low = u.lower()
        if u in seen or etld1(u) != site:
            continue
        path = urlsplit(low).path
        if path.endswith(SKIP_EXT) or any(w in low for w in SKIP_WORDS):
            continue
        seen.add(u)
        candidates.append(u)

    picked: list[str] = []
    used_sections: set[str] = set()
    for u in candidates:  # first pass: one per section
        section = (urlsplit(u).path.strip("/").split("/") or [""])[0]
        if section not in used_sections:
            used_sections.add(section)
            picked.append(u)
        if len(picked) >= n:
            return picked
    for u in candidates:  # second pass: fill up
        if u not in picked:
            picked.append(u)
        if len(picked) >= n:
            break
    return picked
