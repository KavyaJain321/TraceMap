"""User-identifier detection across profiles A / B / A2.

Criteria adapted from Englehardt & Narayanan (CCS 2016, sec. 4), applied to every
place a value can travel (cookie jar, storage, URL params/path, Cookie header,
POST body), which also covers the POST channel that Fouad et al. 2020 did not:
  * length 8..100 after splitting on characters outside [A-Za-z0-9_=-]
  * looks random (has digits or mixed case, entropy >= 2.5 bits/char), not a timestamp
  * stable for the same user: same value seen in A and in A2 (the revisit)
  * different between users: the same slot in B holds a value with
    Ratcliff-Obershelp similarity < 0.66 (difflib.SequenceMatcher)
The paper's ">90 day cookie expiry" rule is reported as a sensitivity variant
later; here expiry is not required because values also travel outside cookies.

Edge confidence is a transparent heuristic in this phase; Phase 6 replaces it with
a calibrated model trained on hand-labelled edges.
"""

from __future__ import annotations

import json
import math
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, unquote, urlsplit

from ..contracts import CrawlRecord, Visit
from ..util.domains import etld1

_SPLIT = re.compile(r"[^A-Za-z0-9_=\-]+")
_NOW = time.time()


def _entropy(s: str) -> float:
    counts = defaultdict(int)
    for ch in s:
        counts[ch] += 1
    return -sum(c / len(s) * math.log2(c / len(s)) for c in counts.values())


def id_like(v: str) -> bool:
    if not (8 <= len(v) <= 100):
        return False
    if v.isdigit():
        n = int(v[:13])
        if len(v) in (10, 13) and abs((n / (1000 if len(v) == 13 else 1)) - _NOW) < 10 * 365 * 86400:
            return False  # unix timestamp
    has_digit = any(c.isdigit() for c in v)
    mixed = any(c.islower() for c in v) and any(c.isupper() for c in v)
    if not (has_digit or mixed):
        return False
    return _entropy(v) >= 2.5


@dataclass
class Sighting:
    value: str
    slot: str  # where it sits, e.g. "adnet-a.localhost|q:uid"
    holder: str  # eTLD+1 of the party that received/stores it
    channel: str  # url_param | path | cookie | post_body | storage | cookie_jar | redirect
    request_id: str | None = None
    page_index: int = 0


def _tokens(value: str) -> list[str]:
    value = unquote(value)
    toks = [t for t in _SPLIT.split(value) if t]
    out = []
    for t in toks:  # also split "name=value" pieces
        out.extend(p for p in t.split("=") if p) if "=" in t else out.append(t)
    return out


def _flatten_json(obj, prefix="") -> list[tuple[str, str]]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += _flatten_json(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            out += _flatten_json(v, f"{prefix}[{i}]")
    elif obj is not None:
        out.append((prefix, str(obj)))
    return out


def sightings(visit: Visit, site: str) -> list[Sighting]:
    out: list[Sighting] = []

    def add(raw: str, slot: str, holder: str, channel: str, rid=None, page=0):
        for t in _tokens(raw):
            if id_like(t):
                out.append(Sighting(t, slot, holder, channel, rid, page))

    for r in visit.requests:
        if not r.url.startswith("http"):
            continue
        d = etld1(r.url)
        parts = urlsplit(r.url)
        channel_q = "redirect" if r.redirect_from else "url_param"
        for k, v in parse_qsl(parts.query, keep_blank_values=False):
            add(v, f"{d}|q:{k}", d, channel_q, r.request_id, r.page_index)
        for i, seg in enumerate(p for p in parts.path.split("/") if p):
            add(seg, f"{d}|path:{i}", d, "path", r.request_id, r.page_index)
        if r.headers.get("cookie"):
            for pair in r.headers["cookie"].split(";"):
                k, _, v = pair.strip().partition("=")
                add(v, f"{d}|c:{k}", d, "cookie", r.request_id, r.page_index)
        if r.post_data:
            body = r.post_data.strip()
            pairs: list[tuple[str, str]] = []
            try:
                pairs = _flatten_json(json.loads(body))
            except (ValueError, TypeError):
                if "=" in body:
                    pairs = parse_qsl(body, keep_blank_values=False)
            if not pairs:
                pairs = [("body", body[:2000])]
            for k, v in pairs[:200]:
                add(v, f"{d}|p:{k}", d, "post_body", r.request_id, r.page_index)
    for c in visit.cookies:
        holder = etld1(c.domain.lstrip("."))
        add(c.value, f"{holder}|jar:{c.name}", holder, "cookie_jar")
    for s in visit.storage:
        holder = etld1(s.origin)
        add(s.value, f"{holder}|{s.kind}:{s.key}", holder, "storage")
    return out


@dataclass
class IdValue:
    value: str
    status: str  # "confirmed" (passes A/B/A2) | "unconfirmed" (no B comparison) | "single_profile"
    holders: dict[str, list[Sighting]] = field(default_factory=dict)  # party -> sightings in profile A


def find_ids(record: CrawlRecord) -> list[IdValue]:
    site = record.site
    a, b, a2 = record.visit("A"), record.visit("B"), record.visit("A2")
    if a is None:
        return []
    sa = sightings(a, site)
    vals_a2 = {s.value for s in sightings(a2, site)} if a2 else None
    slots_b: dict[str, set[str]] = defaultdict(set)
    vals_b: set[str] = set()
    if b is not None:
        for s in sightings(b, site):
            slots_b[s.slot].add(s.value)
            vals_b.add(s.value)

    by_value: dict[str, list[Sighting]] = defaultdict(list)
    for s in sa:
        by_value[s.value].append(s)

    out = []
    for v, ss in by_value.items():
        if b is None or vals_a2 is None:
            status = "single_profile"
        else:
            if v not in vals_a2 or v in vals_b:
                continue  # not stable for the user, or identical for another user
            comparable = [x for s in ss for x in slots_b.get(s.slot, ())]
            if comparable and any(SequenceMatcher(None, v, x).ratio() >= 0.66 for x in comparable):
                continue  # B holds a near-identical value: not a per-user identifier
            status = "confirmed" if comparable else "unconfirmed"
        holders: dict[str, list[Sighting]] = defaultdict(list)
        for s in ss:
            holders[s.holder].append(s)
        out.append(IdValue(v, status, dict(holders)))
    return out
