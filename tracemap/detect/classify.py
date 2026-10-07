"""Classify every third party seen in a crawl: owner, category, tracker or not.

Owner/category sources, in priority order (first hit wins):
    1. our supplements (data/lists/supplement/*.json: India vendors, testbed)
    2. DuckDuckGo TDS            (owner + categories, CC BY-NC-SA)
    3. Ghostery TrackerDB        (owner + category + country, CC BY-NC-SA)
    4. Disconnect services.json  (org + category, CC BY-NC-SA)
    5. third-party-web           (company + category, MIT)
URL-level filter lists (EasyPrivacy, EasyList, IndianList, AdGuard Tracking) are
matched per request with one engine per list, so evidence names the list + rule.
Missing list files are skipped (the classifier still works with what it has).
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import adblock

from ..config import settings
from ..contracts import CrawlRecord, DetectedParty, Request
from ..util.domains import etld1, hostname

TRACKING = {"ad", "analytics", "social", "session_replay", "fingerprinting"}
FILTER_LISTS = {"easyprivacy": "easyprivacy.txt", "easylist": "easylist.txt", "indianlist": "indianlist.txt",
                "adguard_tracking": "adguard-tracking.txt"}

TDS_CATS = [  # (TDS category, ours) in priority order
    ("Session Replay", "session_replay"), ("Advertising", "ad"), ("Ad Motivated Tracking", "ad"),
    ("Action Pixels", "ad"), ("Ad Fraud", "ad"), ("Analytics", "analytics"), ("Audience Measurement", "analytics"),
    ("Third-Party Analytics Marketing", "analytics"), ("Social Network", "social"), ("Social - Share", "social"),
    ("Social - Comment", "social"), ("Tag Manager", "tag_manager"), ("Content Delivery", "functional"),
    ("Embedded Content", "functional"), ("Online Payment", "functional"), ("Federated Login", "functional"),
    ("SSO", "functional"), ("Support Chat Widget", "functional"), ("Badge", "functional"),
]
GHOSTERY_CATS = {"advertising": "ad", "pornvertising": "ad", "site_analytics": "analytics", "social_media": "social",
                 "comments": "social", "customer_interaction": "functional", "essential": "functional",
                 "audio_video_player": "functional", "cdn": "functional", "hosting": "functional",
                 "consent": "functional", "email": "functional", "extensions": "functional", "utilities": "functional",
                 "misc": "unknown"}
DISCONNECT_CATS = {"Advertising": "ad", "Analytics": "analytics", "Social": "social",
                   "FingerprintingInvasive": "fingerprinting", "FingerprintingGeneral": "fingerprinting",
                   "Email": "ad", "EmailAggressive": "ad", "Content": "functional", "Anti-fraud": "functional",
                   "ConsentManagers": "functional", "Cryptomining": "unknown"}
TPW_CATS = {"ad": "ad", "analytics": "analytics", "marketing": "analytics", "social": "social",
            "tag-manager": "tag_manager", "other": "unknown"}
ADBLOCK_TYPES = {"Document": "sub_frame", "Stylesheet": "stylesheet", "Image": "image", "Media": "media",
                 "Font": "font", "Script": "script", "XHR": "xmlhttprequest", "Fetch": "xmlhttprequest",
                 "Ping": "ping", "WebSocket": "websocket"}


@dataclass
class Label:
    owner: str | None = None
    category: str | None = None
    country: str | None = None
    source: str = ""


@dataclass
class Classifier:
    lists_dir: Path
    domains: dict[str, list[Label]] = field(default_factory=dict)  # domain -> labels from each source
    engines: dict[str, adblock.Engine] = field(default_factory=dict)
    cnames: dict[str, str] = field(default_factory=dict)  # cloaked host -> tracker host (TDS)
    cname_hosts: set[str] = field(default_factory=set)  # AdGuard disguised hostnames
    loaded: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ loading

    @classmethod
    def load(cls, lists_dir: Path | None = None, filter_lists: bool = True) -> "Classifier":
        c = cls(Path(lists_dir or settings.lists_dir))
        c._load_supplements()
        c._load_tds()
        c._load_trackerdb()
        c._load_disconnect()
        c._load_tpw()
        c._load_cname()
        if filter_lists:
            c._load_filters()
        return c

    def _add(self, domain: str, label: Label) -> None:
        if domain:
            self.domains.setdefault(domain.lower().lstrip("*."), []).append(label)

    def _json(self, rel: str):
        p = self.lists_dir / rel
        if not p.exists():
            return None
        self.loaded.append(rel)
        return json.loads(p.read_text(encoding="utf-8"))

    def _load_supplements(self) -> None:
        sup = self.lists_dir / "supplement"
        for p in sorted(sup.glob("*.json")) if sup.exists() else []:
            data = json.loads(p.read_text(encoding="utf-8"))
            self.loaded.append(f"supplement/{p.name}")
            for owner, e in data.get("entities", {}).items():
                for d in e.get("domains", []):
                    self._add(d, Label(owner, e.get("category"), e.get("country"), f"supplement:{p.stem}"))

    def _load_tds(self) -> None:
        tds = self._json("nc-sa/ddg-tds.json")
        if not tds:
            return
        ents = tds.get("entities", {})
        parent = {n: e["ownedBy"] for n, e in ents.items() if e.get("ownedBy")}
        for t in tds.get("trackers", {}).values():
            o = t.get("owner") or {}
            if o.get("ownedBy") and o.get("name"):
                parent.setdefault(o["name"], o["ownedBy"])

        def top_owner(name: str | None) -> str | None:
            seen = set()
            while name and name in parent and name not in seen:
                seen.add(name)
                name = parent[name]
            return (ents.get(name, {}).get("displayName") or name) if name else None

        def tds_cat(t: dict | None) -> str | None:
            cats = set((t or {}).get("categories") or [])
            return next((ours for theirs, ours in TDS_CATS if theirs in cats), None)

        for dom, ent in tds.get("domains", {}).items():
            self._add(dom, Label(top_owner(ent), tds_cat(tds["trackers"].get(dom)), None, "ddg-tds"))
        for dom, t in tds.get("trackers", {}).items():
            if dom not in tds.get("domains", {}):
                owner = t.get("owner") or {}
                self._add(dom, Label(top_owner(owner.get("ownedBy") or owner.get("name")) or owner.get("displayName"),
                                     tds_cat(t), None, "ddg-tds"))
        self.cnames = {k.lower(): v.lower() for k, v in tds.get("cnames", {}).items()}

    def _load_trackerdb(self) -> None:
        db = self._json("nc-sa/ghostery-trackerdb.json")
        if not db:
            return
        orgs, pats = db.get("organizations", {}), db.get("patterns", {})
        for dom, pid in db.get("domains", {}).items():
            p = pats.get(pid, {})
            org = orgs.get(p.get("organization") or "", {})
            self._add(dom, Label(org.get("name") or p.get("name"), GHOSTERY_CATS.get(p.get("category", ""), "unknown"),
                                 org.get("country"), "ghostery"))

    def _load_disconnect(self) -> None:
        d = self._json("nc-sa/disconnect-services.json")
        if not d:
            return
        for cat, entries in d.get("categories", {}).items():
            ours = DISCONNECT_CATS.get(cat, "unknown")
            for entry in entries:
                for org, sites in entry.items():
                    for _home, doms in sites.items():
                        if isinstance(doms, list):
                            for dom in doms:
                                self._add(dom, Label(org, ours, None, "disconnect"))

    def _load_tpw(self) -> None:
        tpw = self._json("third-party-web.json")
        if not tpw:
            return
        for e in tpw:
            for dom in e.get("domains", []):
                self._add(dom, Label(e.get("company") or e.get("name"), TPW_CATS.get(e.get("category"), "functional"),
                                     None, "third-party-web"))

    def _load_cname(self) -> None:
        p = self.lists_dir / "adguard-cname.txt"
        if p.exists():
            self.loaded.append("adguard-cname.txt")
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    self.cname_hosts.add(line.lower())

    def _load_filters(self) -> None:
        for name, fn in FILTER_LISTS.items():
            p = self.lists_dir / fn
            if not p.exists():
                continue
            fs = adblock.FilterSet(debug=True)
            fs.add_filter_list(p.read_text(encoding="utf-8"))
            self.engines[name] = adblock.Engine(fs, optimize=False)
            self.loaded.append(fn)

    # ------------------------------------------------------------------ lookups

    def labels(self, host: str) -> list[Label]:
        """Labels for the most specific matching domain (host, then parents)."""
        host = hostname(host)
        parts = host.split(".")
        for i in range(len(parts) - 1):
            d = ".".join(parts[i:])
            if d in self.domains:
                return self.domains[d]
        return []

    def owner_category(self, host: str) -> tuple[str | None, str | None, list[str]]:
        """Owner = first source in priority order. Category = our supplement if present,
        otherwise a majority vote across sources (ties broken by source priority),
        because lists disagree (e.g. TDS tags Google Analytics 'Advertising')."""
        labels = self.labels(host)
        owner = next((l.owner for l in labels if l.owner), None)
        sup = next((l.category for l in labels if l.source.startswith("supplement") and l.category), None)
        if sup:
            return owner, sup, sorted({l.source for l in labels})
        if any(l.category == "session_replay" for l in labels):  # highest-risk capability wins
            return owner, "session_replay", sorted({l.source for l in labels})
        votes: dict[str, int] = {}
        first_seen: dict[str, int] = {}
        voted_sources: set[tuple[str, str]] = set()
        for i, l in enumerate(labels):
            c = l.category
            if not c or c in ("unknown", "fingerprinting") or (l.source, c) in voted_sources:
                continue
            voted_sources.add((l.source, c))
            votes[c] = votes.get(c, 0) + 1
            first_seen.setdefault(c, i)
        cat = max(votes, key=lambda c: (votes[c], -first_seen[c])) if votes else None
        if cat is None and any(l.category == "fingerprinting" for l in labels):
            cat = "fingerprinting"
        return owner, cat, sorted({l.source for l in labels})

    def match_filters(self, r: Request, source_url: str) -> list[str]:
        hits = []
        rtype = ADBLOCK_TYPES.get(r.resource_type, "other")
        for name, eng in self.engines.items():
            try:
                res = eng.check_network_urls(r.url, source_url, rtype)
            except Exception:
                continue
            if res.matched and not res.exception:
                hits.append(f"{name}: {(res.filter or '').split(' <+> ')[0][:120]}")
        return hits

    # ------------------------------------------------------------------ main entry

    def classify(self, record: CrawlRecord) -> list[DetectedParty]:
        site = record.site
        hosts: dict[str, set[str]] = defaultdict(set)
        counts: dict[str, int] = defaultdict(int)
        hits: dict[str, list[str]] = defaultdict(list)
        cloaked: dict[str, str] = {}
        page_url = record.input_url
        for v in record.visits:
            for r in v.requests:
                if not r.url.startswith("http"):
                    continue
                d = etld1(r.url)
                h = hostname(r.url)
                hosts[d].add(h)
                counts[d] += 1
                if d == site:
                    target = self.cnames.get(h) or (h if h in self.cname_hosts else None)
                    if target:
                        cloaked[h] = target
                    continue
                if len(hits[d]) < 5:
                    for hit in self.match_filters(r, r.frame_url or page_url):
                        if hit not in hits[d]:
                            hits[d].append(hit)

        parties = []
        for d in sorted(hosts):
            first = d == site
            owner, cat, sources = self.owner_category(d)
            for h in hosts[d]:  # a more specific host may carry a better label
                if not owner or not cat:
                    o2, c2, s2 = self.owner_category(h)
                    owner, cat = owner or o2, cat or c2
                    sources = sorted(set(sources) | set(s2))
            evidence = list(hits.get(d, []))
            is_tracker = (cat in TRACKING) or bool(evidence)
            if first:
                is_tracker = False
            p = DetectedParty(domain=d, owner=owner, category=cat or "unknown", is_tracker=is_tracker,
                              first_party=first, request_count=counts[d], hosts=sorted(hosts[d])[:20],
                              sources=sources + sorted({e.split(":")[0] for e in evidence}), evidence=evidence)
            if first and cloaked:
                p.cloaked = True
                p.evidence += [f"cname: {h} -> {t}" for h, t in sorted(cloaked.items())]
            parties.append(p)
        return parties


@lru_cache(maxsize=1)
def default_classifier() -> Classifier:
    return Classifier.load()
