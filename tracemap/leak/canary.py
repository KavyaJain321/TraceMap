"""Synthetic canary values. Never real personal data.

Email: unique per site and run, on a domain the team controls (settings.canary_email_domain),
so later mail to that address is independent proof of a leak.
Phone: only team-owned numbers (settings.canary_phones). A random 10-digit Indian number
could belong to a real person, so on real sites phone fields are skipped unless configured.
Government ID formats (Aadhaar, PAN) are never used.
"""

from __future__ import annotations

import re
import secrets
import time

from ..contracts import Canary

_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"  # no 0/o/1/l confusion


def _token(n: int = 10) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(n))


def make_email(site: str, domain: str) -> Canary:
    tok = _token()
    return Canary(canary_id=f"em-{tok}", kind="email", value=f"tm.{tok}@{domain}", site=site, created_at=time.time())


def make_phone(site: str, number: str) -> Canary:
    digits = re.sub(r"\D", "", number)[-10:]
    if len(digits) != 10 or digits[0] not in "6789":
        raise ValueError("canary phone must be a 10-digit Indian mobile number starting 6-9")
    return Canary(canary_id=f"ph-{digits[-4:]}-{_token(4)}", kind="phone", value=digits, site=site, created_at=time.time())
