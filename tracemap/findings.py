"""Plain-English findings with stable reason codes. Every finding links to proof
(request ids) so the UI can show the exact request behind each sentence."""

from __future__ import annotations

from collections import defaultdict

from .contracts import (CrawlRecord, DetectedParty, Finding, LeakReport, RiskyScript, ScanSummary, SiteGraph)

FLAG_TEXT = {
    "canvas_fp": "drew hidden text on a canvas and read it back (canvas fingerprinting)",
    "font_fp": "probed installed fonts (font fingerprinting)",
    "webgl_fp": "read graphics-card details (WebGL fingerprinting)",
    "audio_fp": "ran a silent audio test (audio fingerprinting)",
    "webrtc_ip": "set up WebRTC in a way used to discover your local IP address",
    "device_enum": "collected many device/browser properties",
    "reads_form": "read what was typed into form fields",
    "listens_keys": "listens to typing/input events on the page",
}
SOURCE_NAME = {"ddg-tds": "DuckDuckGo", "ghostery": "Ghostery", "disconnect": "Disconnect",
               "third-party-web": "third-party-web", "supplement:india": "TraceMap India list",
               "supplement:testbed": "testbed labels", "easyprivacy": "EasyPrivacy", "easylist": "EasyList",
               "indianlist": "IndianList", "adguard_tracking": "AdGuard"}
HASHES = ("md5", "sha", "mmh3", "blake")
CHANNEL_TEXT = {"url": "address", "post_body": "body", "cookie": "cookies", "referer": "Referer header"}


def _who(owner: str | None, domain: str) -> str:
    return f"{owner} ({domain})" if owner and owner.lower() not in domain else domain


def _sources(names: list[str]) -> str:
    return ", ".join(dict.fromkeys(SOURCE_NAME.get(n, n) for n in names))


def _enc(e: str) -> str:
    base = e.split(" inside ")[0]
    if "(" not in base:
        how = "in plain text"
    elif any(h in base for h in HASHES):
        how = f"hashed ({base})"
    else:
        how = f"encoded ({base})"
    return how + (" inside an encoded payload" if " inside " in e else "")


def build_findings(record: CrawlRecord, parties: list[DetectedParty], scripts: list[RiskyScript],
                   leaks: LeakReport, graph: SiteGraph) -> tuple[list[Finding], ScanSummary]:
    site = record.site
    out: list[Finding] = []
    third = [p for p in parties if not p.first_party]
    trackers = [p for p in third if p.is_tracker]
    owners = {p.owner or p.domain for p in third}
    info = {p.domain: p for p in parties}

    pages = [pg for v in record.visits for pg in v.pages]
    blocked = bool(pages) and pages[0].status == "blocked"
    if blocked:
        out.append(Finding(severity="info", code="SCAN_BLOCKED",
                           title="The site showed a bot-check page, so results are incomplete.",
                           detail=pages[0].block_reason))

    # --- verified leaks (strongest evidence)
    third_leaks = [e for e in leaks.leaks if not e.first_party]
    by_recipient: dict[str, list] = defaultdict(list)
    for e in third_leaks:
        by_recipient[e.recipient_domain].append(e)
    for dom, evs in sorted(by_recipient.items(), key=lambda kv: min(e.ms_after_typing for e in kv[1])):
        kinds = sorted({e.kind for e in evs})
        first = min(evs, key=lambda e: e.ms_after_typing)
        what = " and ".join("email" if k == "email" else "phone number" for k in kinds)
        verb = "were" if len(kinds) > 1 else "was"
        out.append(Finding(
            severity="high", code="LEAK_BEFORE_SUBMIT",
            title=f"Your {what} {verb} sent to {_who(first.recipient_owner, dom)} before you pressed Submit.",
            detail=f"Sent {_enc(first.encoding)} in the request {CHANNEL_TEXT.get(first.channel, first.channel)}, "
                   f"{first.ms_after_typing / 1000:.1f}s after typing."
                   + (f" {len(evs)} separate leak events in total." if len(evs) > 1 else ""),
            request_ids=[e.request_id for e in evs][:10]))

    # --- session replay / fingerprinting / form readers (capability)
    replay = [p for p in third if p.category == "session_replay"]
    for p in replay:
        out.append(Finding(severity="high", code="SESSION_REPLAY",
                           title=f"A session-recording service, {_who(p.owner, p.domain)}, is loaded. These can record clicks, scrolling and typing.",
                           detail="Labelled session recording by: " + _sources(p.sources)))
    fp_flags = {"canvas_fp", "font_fp", "webgl_fp", "audio_fp", "webrtc_ip"}
    for s in scripts:
        party = info.get(s.domain)
        if s.domain == site:
            continue
        fp = [f for f in s.flags if f in fp_flags]
        if fp:
            out.append(Finding(severity="medium", code="FINGERPRINTING",
                               title=f"{_who(party.owner if party else None, s.domain)} tried to fingerprint your device.",
                               detail="It " + "; ".join(FLAG_TEXT[f] for f in fp) + f". Script: {s.src}"))
        if "reads_form" in s.flags and s.domain not in by_recipient and not (party and party.same_owner_as_site):
            out.append(Finding(severity="medium", code="READS_FORM",
                               title=f"A script from {_who(party.owner if party else None, s.domain)} read what you typed into a form.",
                               detail=f"No leak of the test values was seen from it, but it had access. Script: {s.src}"))

    # --- identifier sharing
    shared = [e for e in graph.edges if e.kind == "shared_id" and site not in (e.a, e.b)]
    for e in sorted(shared, key=lambda e: -e.confidence):
        a, b = info.get(e.a), info.get(e.b)
        note = " (same company)" if e.same_entity else ""
        out.append(Finding(severity="low" if e.same_entity else "medium", code="ID_SHARING",
                           title=f"{_who(a.owner if a else None, e.a)} and {_who(b.owner if b else None, e.b)} exchanged an identifier for you{note}.",
                           detail=f"Evidence: same user ID seen at both via {e.evidence_type}; confidence {e.confidence:.0%}. "
                                  "This is how 'cookie syncing' links your profiles across companies.",
                           request_ids=e.request_ids))
    fp_shared = [e for e in graph.edges if e.kind == "shared_id" and site in (e.a, e.b)]
    if fp_shared:
        names = sorted({_who(info[x].owner if x in info else None, x) for e in fp_shared for x in (e.a, e.b) if x != site})
        out.append(Finding(severity="low", code="FIRST_PARTY_ID_SHARED",
                           title=f"Your visitor ID on this site is shared with {len(names)} other compan{'y' if len(names) == 1 else 'ies'}.",
                           detail=", ".join(names[:8])))

    # --- trackers and consent
    a = record.visit("A") or (record.visits[0] if record.visits else None)
    banner = bool(a and a.consent.popup_found)
    if trackers:
        names = sorted({p.owner or p.domain for p in trackers})
        out.append(Finding(severity="medium" if len(trackers) >= 5 else "low", code="TRACKERS_PRESENT",
                           title=f"{len(trackers)} tracking domain{'s' if len(trackers) != 1 else ''} from {len(names)} "
                                 f"compan{'ies' if len(names) != 1 else 'y'} loaded"
                                 + (" before you made any cookie choice." if record.config.get("consent_mode", "none") == "none" else "."),
                           detail=", ".join(names[:12]) + (" ..." if len(names) > 12 else "")))
    cloaked = [p for p in parties if p.cloaked]
    for p in cloaked:
        out.append(Finding(severity="medium", code="CNAME_CLOAKING",
                           title="A tracker is disguised as part of this website (CNAME cloaking).",
                           detail="; ".join(x for x in p.evidence if x.startswith("cname:"))))
    if trackers and not banner:
        out.append(Finding(severity="info", code="NO_CONSENT_BANNER",
                           title="No cookie-consent banner was detected.",
                           detail="Detection uses DuckDuckGo autoconsent rules; banners it does not know may be missed."))
    if leaks.tested and not leaks.fields:
        out.append(Finding(severity="info", code="NO_FORM_TESTED", title="No email/phone field was found to test for leaks.",
                           detail="; ".join(leaks.notes)))
    elif leaks.tested and not third_leaks:
        out.append(Finding(severity="info", code="NO_LEAK_SEEN",
                           title="The test email/phone typed into this site's forms was not seen going to other companies.",
                           detail="Server-side sharing after submission cannot be observed from the browser."))

    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    out.sort(key=lambda f: order[f.severity])

    tracking_cookies = 0
    tracker_domains = {p.domain for p in trackers}
    for c in (a.cookies if a else []):
        from .util.domains import etld1
        if etld1(c.domain.lstrip(".")) in tracker_domains or (c.set_by == "js" and c.setter_url and etld1(c.setter_url) in tracker_domains):
            tracking_cookies += 1
    summary = ScanSummary(
        pages_visited=len(a.pages) if a else 0, requests=sum(len(v.requests) for v in record.visits),
        third_parties=len(third), trackers=len(trackers), companies=len(owners), tracking_cookies=tracking_cookies,
        leaks=len(third_leaks), leak_recipients=len(by_recipient), shared_id_edges=len(shared),
        risky_scripts=len([s for s in scripts if s.domain != site]), blocked=blocked, consent_banner=banner)
    return out, summary
