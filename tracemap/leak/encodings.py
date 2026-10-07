"""Precomputed pool of canary encodings and hashes, searched with Aho-Corasick.

Method follows Englehardt et al. (PETS 2018) and Senol et al. "Leaky Forms"
(USENIX Security 2022): apply every combination of encodings/hashes up to
`depth` layers to every normalised variant of each canary, then look for any of
those strings in outgoing traffic. This is a clean-room reimplementation (the
Leaky Forms code has no license); the transform set below is TraceMap's own.

Haystacks are also decoded (URL-decoding twice, base64 tokens once) so that a
canary inside a larger encoded blob is still found.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import re
from dataclasses import dataclass
from urllib.parse import quote, unquote_plus

import ahocorasick
import base58
import mmh3

from ..contracts import Canary

MIN_NEEDLE = 8
MAX_NEEDLE = 512


def _b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode().rstrip("=")


def _b64url(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")


def _h(name: str):
    return lambda s: hashlib.new(name, s.encode()).hexdigest()


TRANSFORMS: dict[str, callable] = {
    "url": lambda s: quote(s, safe=""),
    "base64": _b64,
    "base64url": _b64url,
    "base32": lambda s: base64.b32encode(s.encode()).decode().rstrip("="),
    "base58": lambda s: base58.b58encode(s.encode()).decode(),
    "hex": lambda s: s.encode().hex(),
    "md5": _h("md5"),
    "sha1": _h("sha1"),
    "sha224": _h("sha224"),
    "sha256": _h("sha256"),
    "sha384": _h("sha384"),
    "sha512": _h("sha512"),
    "sha3_256": _h("sha3_256"),
    "sha3_512": _h("sha3_512"),
    "blake2b": _h("blake2b"),
    "mmh3_128": lambda s: mmh3.hash128(s, signed=False).to_bytes(16, "big").hex(),
}
HEX_OUTPUT = {"hex", "md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "mmh3_128"}


def variants(c: Canary) -> dict[str, str]:
    """Normalised forms a script might take before encoding."""
    v = c.value
    if c.kind == "email":
        out = {"email": v, "lowercased email": v.strip().lower()}
    else:
        d = re.sub(r"\D", "", v)[-10:]
        out = {"phone": d, "+91 phone": "+91" + d, "91 phone": "91" + d, "0-prefixed phone": "0" + d,
               "+91 spaced phone": f"+91 {d[:5]} {d[5:]}", "spaced phone": f"{d[:5]} {d[5:]}",
               "+91- phone": "+91-" + d, "+91 phone (space)": "+91 " + d}
    seen, res = set(), {}
    for k, s in out.items():
        if s not in seen:
            seen.add(s)
            res[k] = s
    return res


@dataclass
class Match:
    canary: Canary
    encoding: str


class CanaryPool:
    def __init__(self, canaries: list[Canary], depth: int = 3):
        self.canaries = canaries
        self.depth = depth
        self.needles: dict[str, Match] = {}
        for c in canaries:
            for vname, base in variants(c).items():
                self._expand(c, base, vname, [], depth)
        self._auto = ahocorasick.Automaton()
        for needle, m in self.needles.items():
            self._auto.add_word(needle, (needle, m))
        self._auto.make_automaton()

    def _add(self, needle: str, m: Match) -> None:
        if MIN_NEEDLE <= len(needle) <= MAX_NEEDLE:
            prev = self.needles.get(needle)
            if prev is None or len(m.encoding) < len(prev.encoding):
                self.needles[needle] = m

    def _expand(self, c: Canary, s: str, vname: str, chain: list[str], depth: int) -> None:
        desc = vname if not chain else "(".join(reversed(chain)) + "(" + vname + ")" * len(chain)
        self._add(s, Match(c, desc))
        if chain and chain[-1] in HEX_OUTPUT:
            self._add(s.upper(), Match(c, desc + " [upper]"))
        if depth == 0:
            return
        for name, fn in TRANSFORMS.items():
            if chain and name == "url" and chain[-1] in HEX_OUTPUT | {"url"}:
                continue  # url-encoding hex is a no-op; double url handled by haystack decoding
            try:
                out = fn(s)
            except Exception:
                continue
            if out != s:
                self._expand(c, out, vname, chain + [name], depth - 1)

    def search(self, text: str) -> list[tuple[str, Match, str]]:
        """All (needle, match, where) found in text or its decoded forms.
        `where` is "raw" or how the payload had to be decoded first."""
        found: dict[str, tuple[Match, str]] = {}
        for hay, where in haystacks(text):
            for _end, (needle, m) in self._auto.iter(hay):
                found.setdefault(needle, (m, where))
        return [(n, m, w) for n, (m, w) in found.items()]

    def __len__(self) -> int:
        return len(self.needles)


_B64_TOKEN = re.compile(r"[A-Za-z0-9+/_-]{16,}={0,2}")


def haystacks(text: str, max_len: int = 400_000) -> list[tuple[str, str]]:
    """(text, how) pairs: the raw text, URL-decoded (x2) and base64-decoded variants."""
    text = text[:max_len]
    out = [(text, "raw")]
    cur = text
    for i in range(2):
        try:
            nxt = unquote_plus(cur)
        except Exception:
            break
        if nxt == cur:
            break
        out.append((nxt, "url-decoded" if i == 0 else "url-decoded x2"))
        cur = nxt
    decoded = []
    for hay, _how in out:
        for tok in _B64_TOKEN.findall(hay)[:200]:
            t = tok.replace("-", "+").replace("_", "/")
            t += "=" * (-len(t) % 4)
            try:
                raw = base64.b64decode(t, validate=True)
            except (binascii.Error, ValueError):
                continue
            s = raw.decode("utf-8", "ignore")
            if s and sum(ch.isprintable() for ch in s) / len(s) > 0.9:
                decoded.append((s, "base64-decoded"))
                u = unquote_plus(s)
                if u != s:
                    decoded.append((u, "base64+url-decoded"))
    return out + decoded
