"""Per-site identifier-flow graph.

Nodes: the site and every third party (eTLD+1). Edges:
  loads      X's script (or document) made the request to Y         (inclusion)
  redirect   a request to X was redirected to Y                       (bounce)
  shared_id  the same user identifier was seen at both X and Y        (ID sharing)
shared_id edges are evidence of identifier flow, not proof of intent; each has a
confidence and a same_entity flag (sharing inside one company is expected).

Per-site graphs are small (10-40 nodes), so only descriptive centrality is
computed here; Leiden communities and null models run on the corpus-level graph
in Phase 6 (see PANEL_REVIEW.md A2.3).
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from itertools import combinations

import networkx as nx

from ..contracts import CollusionEdge, CrawlRecord, DetectedParty, GraphNode, SiteGraph
from ..util.domains import etld1
from .ids import find_ids

CONF = {"confirmed": 0.8, "unconfirmed": 0.45, "single_profile": 0.3}
CHANNEL_RANK = {"redirect": 0, "url_param": 1, "path": 2, "post_body": 3, "cookie": 4, "storage": 5, "cookie_jar": 6}


def build_graph(record: CrawlRecord, parties: list[DetectedParty]) -> SiteGraph:
    site = record.site
    info = {p.domain: p for p in parties}
    edges: dict[tuple, CollusionEdge] = {}

    def owner(d: str) -> str | None:
        return info[d].owner if d in info else None

    def add(a: str, b: str, kind: str, rid: str | None = None, **kw) -> None:
        if not a or not b or a == b:
            return
        if kind == "shared_id":
            a, b = sorted((a, b))
        key = (a, b, kind, kw.get("shared_value_hash"))
        e = edges.get(key)
        if e is None:
            same = bool(owner(a) and owner(a) == owner(b))
            e = edges[key] = CollusionEdge(a=a, b=b, kind=kind, same_entity=same, count=0, **kw)
        e.count += 1
        if rid and len(e.request_ids) < 10:
            e.request_ids.append(rid)

    # inclusion + redirects (profile A only, to keep counts interpretable)
    visit = record.visit("A") or (record.visits[0] if record.visits else None)
    by_id = {r.request_id: r for r in visit.requests} if visit else {}
    for r in visit.requests if visit else []:
        if not r.url.startswith("http"):
            continue
        dst = etld1(r.url)
        if r.redirect_from and r.redirect_from in by_id:
            add(etld1(by_id[r.redirect_from].url), dst, "redirect", r.request_id, evidence_type="redirect")
            continue
        src_url = r.initiator.stack_urls[0] if r.initiator.stack_urls else r.initiator.url
        if src_url and src_url.startswith("http"):
            add(etld1(src_url), dst, "loads", r.request_id, evidence_type="initiator")

    # identifier sharing
    for idv in find_ids(record):
        holders = list(idv.holders)
        if len(holders) < 2:
            continue
        vhash = hashlib.sha256(idv.value.encode()).hexdigest()[:16]
        conf = CONF[idv.status]
        if len({s.page_index for ss in idv.holders.values() for s in ss}) > 1:
            conf = min(0.95, conf + 0.1)  # seen on several pages: less likely a coincidence
        for a, b in combinations(sorted(holders), 2):
            ch = min((s.channel for s in idv.holders[a] + idv.holders[b]), key=lambda c: CHANNEL_RANK.get(c, 9))
            rids = [s.request_id for s in idv.holders[a] + idv.holders[b] if s.request_id][:10]
            key = tuple(sorted((a, b))) + ("shared_id", vhash)
            add(a, b, "shared_id", None, evidence_type=ch, shared_value_hash=vhash, confidence=conf)
            edges[key].request_ids = rids

    # collapse shared_id edges per pair: keep the strongest value, count distinct values
    pair_best: dict[tuple, CollusionEdge] = {}
    pair_n: dict[tuple, int] = defaultdict(int)
    others = []
    for e in edges.values():
        if e.kind != "shared_id":
            others.append(e)
            continue
        k = (e.a, e.b)
        pair_n[k] += 1
        if k not in pair_best or e.confidence > pair_best[k].confidence:
            pair_best[k] = e
    shared = []
    for k, e in pair_best.items():
        e.count = pair_n[k]
        shared.append(e)

    final = others + shared
    nodes = {site} | {d for e in final for d in (e.a, e.b)} | {p.domain for p in parties if not p.first_party}
    g = nx.Graph()
    g.add_nodes_from(nodes)
    for e in final:
        g.add_edge(e.a, e.b)
    btw = nx.betweenness_centrality(g) if g.number_of_nodes() > 2 else {n: 0.0 for n in g}
    out_nodes = []
    for n in sorted(nodes):
        p = info.get(n)
        out_nodes.append(GraphNode(id=n, owner=p.owner if p else None, category=p.category if p else "unknown",
                                   is_tracker=bool(p and p.is_tracker), first_party=n == site,
                                   degree=g.degree(n), betweenness=round(btw.get(n, 0.0), 4)))
    notes = []
    if record.visit("B") is None or record.visit("A2") is None:
        notes.append("Single-profile scan: identifier edges are unconfirmed (run a full scan for the A/B/A2 test).")
    return SiteGraph(nodes=out_nodes, edges=sorted(final, key=lambda e: (e.kind, e.a, e.b)), notes=notes)
