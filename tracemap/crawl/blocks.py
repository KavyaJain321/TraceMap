"""Bot-wall / challenge-page detection.

We never try to bypass these. A blocked page is recorded with a reason so that
block rates can be reported per sector (unequal attrition biases comparisons).
"""

from __future__ import annotations

import re

TITLE_PATTERNS = [
    r"just a moment", r"attention required", r"access denied", r"request rejected", r"are you a robot",
    r"security check", r"verify you are human", r"pardon our interruption", r"ddos protection",
    r"bot (?:check|verification)", r"captcha",
]
BODY_PATTERNS = [
    r"verify you are human", r"checking if the site connection is secure", r"enable javascript and cookies to continue",
    r"request unsuccessful\. incapsula", r"reference #\d+\.[0-9a-f]+", r"cf-chl", r"challenge-platform",
    r"press (?:&|and) hold", r"the requested url was rejected", r"access to this page has been denied",
    r"why have i been blocked", r"perimeterx", r"datadome",
]
CHALLENGE_HOSTS = ("challenges.cloudflare.com", "hcaptcha.com", "geo.captcha-delivery.com", "perimeterx.net",
                   "www.google.com/recaptcha", "recaptcha.net")

_title_re = re.compile("|".join(TITLE_PATTERNS), re.I)
_body_re = re.compile("|".join(BODY_PATTERNS), re.I)


def detect_block(http_status: int | None, title: str | None, body_text: str | None, frame_urls: list[str]) -> str | None:
    """Return a short reason string if the page looks like a bot wall, else None."""
    title = title or ""
    body = (body_text or "")[:5000]
    if _title_re.search(title):
        return f"challenge title: {title[:80]!r}"
    if http_status in (403, 429, 503) and (_body_re.search(body) or len(body.strip()) < 600):
        return f"http {http_status} with challenge/empty body"
    m = _body_re.search(body)
    if m and len(body) < 3000:
        return f"challenge text: {m.group(0)[:60]!r}"
    for u in frame_urls:
        if any(h in u for h in CHALLENGE_HOSTS) and len(body) < 3000:
            return f"challenge frame: {u[:80]}"
    return None
