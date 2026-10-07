"""python -m tracemap.crawl <url>  ->  crawl one site and store a CrawlRecord."""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections import Counter

from ..config import CrawlConfig, settings
from ..storage import Store
from ..util.domains import etld1
from .crawler import crawl


def build_config(args) -> CrawlConfig:
    cfg = CrawlConfig.quick() if args.quick else CrawlConfig()
    if args.profiles:
        cfg.profiles = [p.strip() for p in args.profiles.split(",")]
    if args.subpages is not None:
        cfg.subpages = args.subpages
    cfg.device = args.device
    cfg.consent_mode = args.consent
    cfg.headless = not args.headed
    cfg.channel = args.channel
    return cfg


def add_crawl_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("url")
    ap.add_argument("--quick", action="store_true", help="one profile, 2 subpages")
    ap.add_argument("--profiles", help="comma list, default A,B,A2")
    ap.add_argument("--subpages", type=int)
    ap.add_argument("--device", choices=["mobile", "desktop"], default="mobile")
    ap.add_argument("--consent", choices=["none", "optIn", "optOut"], default="none")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    ap.add_argument("--channel", default="auto", help="auto | chrome | bundled | msedge")


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m tracemap.crawl", description="Crawl one site, store a CrawlRecord")
    add_crawl_args(ap)
    args = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    store = Store(settings.data_dir)
    scan_id = store.new_scan_id()

    def progress(ev: dict) -> None:
        print(f"  {ev['message']}")

    record = asyncio.run(crawl(args.url, build_config(args), store, progress, crawl_id=scan_id))
    path = store.save_doc(scan_id, "crawl", record)
    print(f"\nstatus={record.status} site={record.site}  saved {path}")
    for v in record.visits:
        third = Counter(etld1(r.url) for r in v.requests if etld1(r.url) != record.site)
        print(f"  [{v.profile}] pages={len(v.pages)} requests={len(v.requests)} third-party domains={len(third)} "
              f"cookies={len(v.cookies)} api-calls={len(v.api_calls)} scripts={len(v.scripts)} "
              f"banner={'yes' if v.consent.popup_found else 'no'}")


if __name__ == "__main__":
    main()
