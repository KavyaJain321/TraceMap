"""Risky-script behaviour flags from the instrumented JS API log.

Capability flags, not proof: e.g. `reads_form` means a script read input values,
which is necessary (not sufficient) for skimming. Verified exfiltration comes only
from the canary leak tracer.

Fingerprinting rules follow Englehardt & Narayanan 2016 (CCS), simplified to the
signals our hooks record:
  canvas_fp  : text drawn (fillText/strokeText) AND image extracted (toDataURL/getImageData/toBlob)
               from a canvas at least 16x16
  font_fp    : measureText called >= 50 times (font probing)
  webgl_fp   : getParameter for UNMASKED_VENDOR/RENDERER (37445/37446) or >= 20 parameter reads
  audio_fp   : OfflineAudioContext created AND oscillator/compressor created
  webrtc_ip  : RTCPeerConnection created with data channel/offer (local IP discovery pattern)
  device_enum: >= 10 distinct navigator/screen properties read
  reads_form : value of visible text/email/tel inputs read
  listens_keys: keyboard/input listeners registered on inputs or the whole document
"""

from __future__ import annotations

import re
from collections import defaultdict

from ..contracts import APICall, CrawlRecord, RiskyScript
from ..util.domains import etld1

_SIZE = re.compile(r"^(\d+)x(\d+)$")


def _calls_by_script(record: CrawlRecord, profiles: set[str] | None = None) -> dict[str, dict[str, APICall]]:
    out: dict[str, dict[str, APICall]] = defaultdict(dict)
    for v in record.visits:
        if profiles is not None and v.profile not in profiles:
            continue
        for c in v.api_calls:
            if not c.script_url:
                continue
            prev = out[c.script_url].get(c.api)
            if prev is None:
                out[c.script_url][c.api] = c.model_copy()
            else:
                prev.count += c.count
                prev.sample_args = (prev.sample_args + c.sample_args)[:12]
    return out


def script_flags(apis: dict[str, APICall]) -> dict[str, list[str]]:
    flags: dict[str, list[str]] = {}
    has = lambda a: a in apis  # noqa: E731
    count = lambda a: apis[a].count if a in apis else 0  # noqa: E731
    args = lambda a: apis[a].sample_args if a in apis else []  # noqa: E731

    extract = [a for a in ("HTMLCanvasElement.toDataURL", "HTMLCanvasElement.toBlob", "CanvasRenderingContext2D.getImageData") if has(a)]
    text = [a for a in ("CanvasRenderingContext2D.fillText", "CanvasRenderingContext2D.strokeText") if has(a)]
    if extract and text:
        sizes = [m.groups() for s in args("HTMLCanvasElement.toDataURL") + args("HTMLCanvasElement.toBlob")
                 if (m := _SIZE.match(s))]
        if not sizes or any(int(w) >= 16 and int(h) >= 16 for w, h in sizes):
            flags["canvas_fp"] = extract + text
    if count("CanvasRenderingContext2D.measureText") >= 50:
        flags["font_fp"] = ["CanvasRenderingContext2D.measureText"]
    gl = [a for a in apis if a.endswith(".getParameter") and "WebGL" in a]
    if any(x in ("37445", "37446") for a in gl for x in args(a)) or sum(count(a) for a in gl) >= 20:
        flags["webgl_fp"] = gl
    if has("OfflineAudioContext.constructor") and (has("BaseAudioContext.createOscillator") or has("BaseAudioContext.createDynamicsCompressor")):
        flags["audio_fp"] = [a for a in ("OfflineAudioContext.constructor", "BaseAudioContext.createOscillator",
                                         "BaseAudioContext.createDynamicsCompressor") if has(a)]
    if has("RTCPeerConnection.constructor") and (has("RTCPeerConnection.createDataChannel") or has("RTCPeerConnection.createOffer")):
        flags["webrtc_ip"] = [a for a in apis if a.startswith("RTCPeerConnection")]
    dev = [a for a in apis if a.startswith("Navigator.") or a.startswith("Screen.")]
    if len(dev) >= 10:
        flags["device_enum"] = sorted(dev)
    reads = [s for s in args("HTMLInputElement.value.get") if s.split(":")[0] in ("text", "email", "tel", "search", "number")]
    if reads:
        flags["reads_form"] = [f"HTMLInputElement.value ({s})" for s in reads[:4]]
    keys = [s for s in args("EventTarget.addEventListener")
            if s.split("@")[0] in ("keydown", "keyup", "keypress", "input", "change", "blur", "focusout", "paste")
            and s.split("@")[1] in ("INPUT", "TEXTAREA", "document", "window", "FORM")]
    if keys:
        flags["listens_keys"] = [f"addEventListener({s})" for s in keys[:4]]
    return flags


def risky_scripts(record: CrawlRecord) -> list[RiskyScript]:
    """reads_form only counts during the leak test (profile L), when we actually typed:
    in passive visits, frameworks read their own empty inputs all the time."""
    leak_calls = _calls_by_script(record, {"L"})
    out = []
    for src, apis in _calls_by_script(record).items():
        flags = script_flags(apis)
        flags.pop("reads_form", None)
        if src in leak_calls:
            reads = script_flags(leak_calls[src]).get("reads_form")
            if reads:
                flags["reads_form"] = reads
        if flags:
            out.append(RiskyScript(src=src, domain=etld1(src), flags=sorted(flags), evidence=flags))
    out.sort(key=lambda r: (-len(r.flags), r.src))
    return out
