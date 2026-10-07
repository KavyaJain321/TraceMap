"""Fetch public tracker lists and pin their versions.

    python -m tracemap.detect.lists fetch

Every download is recorded in data/lists/manifest.json (URL, time, sha256, license)
so a measurement can be reproduced against the exact same list versions.
Non-commercial share-alike data (DuckDuckGo, Disconnect, Ghostery) is stored in
data/lists/nc-sa/ and is never redistributed with TraceMap's code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from ..config import settings


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    filename: str
    license: str
    nc_sa: bool = False


SOURCES = [
    Source("tds", "https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json",
           "ddg-tds.json", "CC BY-NC-SA 4.0 (DuckDuckGo)", nc_sa=True),
    Source("disconnect", "https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json",
           "disconnect-services.json", "CC BY-NC-SA 4.0 (Disconnect)", nc_sa=True),
    Source("trackerdb", "https://github.com/ghostery/trackerdb/releases/latest/download/trackerdb.json",
           "ghostery-trackerdb.json", "CC BY-NC-SA 4.0 (Ghostery)", nc_sa=True),
    Source("third_party_web", "https://unpkg.com/third-party-web@latest/dist/entities.json",
           "third-party-web.json", "MIT (patrickhulce/third-party-web)"),
    Source("easyprivacy", "https://easylist.to/easylist/easyprivacy.txt", "easyprivacy.txt",
           "GPL-3.0+ or CC BY-SA 3.0+ (EasyList)"),
    Source("easylist", "https://easylist.to/easylist/easylist.txt", "easylist.txt",
           "GPL-3.0+ or CC BY-SA 3.0+ (EasyList)"),
    Source("indianlist", "https://easylist-downloads.adblockplus.org/indianlist.txt", "indianlist.txt",
           "GPL-3.0+ or CC BY-SA 3.0+ (IndianList)"),
    Source("adguard_tracking", "https://filters.adtidy.org/extension/ublock/filters/3.txt", "adguard-tracking.txt",
           "GPL-3.0 (AdGuard)"),
    Source("adguard_cname", "https://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_trackers_justdomains.txt",
           "adguard-cname.txt", "MIT (AdGuard cname-trackers)"),
]


def path_for(src: Source, lists_dir: Path | None = None) -> Path:
    d = Path(lists_dir or settings.lists_dir)
    return (d / "nc-sa" / src.filename) if src.nc_sa else (d / src.filename)


def fetch_all(lists_dir: Path | None = None, only: list[str] | None = None) -> dict:
    lists_dir = Path(lists_dir or settings.lists_dir)
    (lists_dir / "nc-sa").mkdir(parents=True, exist_ok=True)
    manifest_path = lists_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    with httpx.Client(follow_redirects=True, timeout=120, headers={"User-Agent": "TraceMap research crawler"}) as c:
        for src in SOURCES:
            if only and src.name not in only:
                continue
            r = c.get(src.url)
            r.raise_for_status()
            p = path_for(src, lists_dir)
            p.write_bytes(r.content)
            manifest[src.name] = {
                "url": src.url, "file": str(p.relative_to(lists_dir)).replace("\\", "/"),
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "sha256": hashlib.sha256(r.content).hexdigest(), "bytes": len(r.content), "license": src.license,
            }
            print(f"  {src.name:18} {len(r.content):>10,} bytes")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m tracemap.detect.lists")
    ap.add_argument("command", choices=["fetch", "show"])
    ap.add_argument("--only", help="comma list of source names")
    args = ap.parse_args()
    if args.command == "fetch":
        fetch_all(only=args.only.split(",") if args.only else None)
    else:
        p = Path(settings.lists_dir) / "manifest.json"
        print(p.read_text(encoding="utf-8") if p.exists() else "no lists fetched yet")


if __name__ == "__main__":
    main()
