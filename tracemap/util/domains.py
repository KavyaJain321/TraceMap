"""Hostname -> registrable domain (eTLD+1) helpers.

Uses tldextract's bundled Public Suffix List snapshot (no network fetch) so results
are reproducible. "localhost" is added as a suffix so the local testbed can simulate
many distinct sites (shop.localhost, adnet-a.localhost, ...).
"""

from __future__ import annotations

import ipaddress
from functools import lru_cache
from urllib.parse import urlsplit

import tldextract

_extract = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None, extra_suffixes=["localhost"])


def hostname(url_or_host: str) -> str:
    s = url_or_host.strip()
    if "://" in s:
        s = urlsplit(s).hostname or ""
    return s.lower().rstrip(".")


@lru_cache(maxsize=65536)
def etld1(url_or_host: str) -> str:
    """Registrable domain, e.g. https://a.b.example.co.in/x -> example.co.in."""
    host = hostname(url_or_host)
    if not host:
        return ""
    try:
        ipaddress.ip_address(host.strip("[]"))
        return host
    except ValueError:
        pass
    ext = _extract(host)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    return host


def is_third_party(url: str, site: str) -> bool:
    d = etld1(url)
    return bool(d) and d != site


def is_http(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")
