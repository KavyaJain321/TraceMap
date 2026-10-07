"""Runtime settings. Everything configurable comes from here (or env vars)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _env_list(name: str) -> list[str]:
    raw = os.environ.get(name, "")
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("TRACEMAP_DATA_DIR", REPO_ROOT / "var")))
    lists_dir: Path = field(default_factory=lambda: Path(os.environ.get("TRACEMAP_LISTS_DIR", REPO_ROOT / "data" / "lists")))
    # Canary email domain. Set this to a domain the team owns so that mail arriving
    # there later is independent proof of a leak. example.com is a safe placeholder.
    canary_email_domain: str = field(default_factory=lambda: os.environ.get("TRACEMAP_CANARY_EMAIL_DOMAIN", "example.com"))
    # Team-owned phone numbers only (10 digits). Empty = phone fields are not filled
    # on real sites, because a random number could belong to a real person.
    canary_phones: list[str] = field(default_factory=lambda: _env_list("TRACEMAP_CANARY_PHONES"))
    # The API refuses private/loopback targets unless this is set (SSRF protection).
    allow_local_targets: bool = field(default_factory=lambda: os.environ.get("TRACEMAP_ALLOW_LOCAL", "") == "1")


@dataclass
class CrawlConfig:
    """How one site is crawled. Snapshot is stored with every CrawlRecord."""

    profiles: list[str] = field(default_factory=lambda: ["A", "B", "A2"])
    device: str = "mobile"  # "mobile" (India is ~65% mobile traffic) or "desktop"
    subpages: int = 4
    consent_mode: str = "none"  # "none" | "optIn" | "optOut"
    headless: bool = True
    # "auto" = installed Google Chrome if present (most realistic), else Playwright's bundled build.
    channel: str = "auto"
    page_timeout_ms: int = 30_000
    settle_ms: int = 4_000  # max wait for network to go quiet after load
    dwell_ms: int = 3_000  # time on page after scrolling
    scroll: bool = True
    screenshot: bool = True
    # All frames share one process so a single CDP session sees every request.
    disable_site_isolation: bool = True
    locale: str = "en-IN"
    timezone_id: str = "Asia/Kolkata"

    @classmethod
    def quick(cls, **kw) -> "CrawlConfig":
        """Single profile, fewer pages: for interactive UI scans."""
        base = dict(profiles=["A"], subpages=2, dwell_ms=2_000)
        base.update(kw)
        return cls(**base)


settings = Settings()
