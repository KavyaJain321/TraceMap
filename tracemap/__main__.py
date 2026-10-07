"""TraceMap command line.

    python -m tracemap scan <url> [--quick] [--no-leak] [--consent optOut]
    python -m tracemap serve [--port 8000]
    python -m tracemap lists fetch
    python -m tracemap pilot data/corpus/pilot_50.csv
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from .config import settings


def _scan(args) -> None:
    from .pipeline import run_scan
    from .storage import Store

    store = Store(settings.data_dir)
    phones = [p.strip() for p in args.phone.split(",")] if args.phone else None

    def progress(ev: dict) -> None:
        print(f"  [{ev.get('stage')}] {ev.get('message')}")

    res = asyncio.run(run_scan(args.url, store, mode="quick" if args.quick else "full", leak_test=not args.no_leak,
                               consent_mode=args.consent, device=args.device, phones=phones, progress=progress))
    print(f"\n{res.status.upper()}  {res.url}  scan_id={res.scan_id}")
    s = res.summary
    print(f"  third parties={s.third_parties} trackers={s.trackers} companies={s.companies} "
          f"leaks={s.leaks} to {s.leak_recipients} recipients, shared-ID links={s.shared_id_edges}, "
          f"risky scripts={s.risky_scripts}, banner={'yes' if s.consent_banner else 'no'}")
    for f in res.findings:
        print(f"  - [{f.severity}] {f.title}")
    print(f"\nSaved under {settings.data_dir / 'scans' / res.scan_id}")


def _analyze(args) -> None:
    from .pipeline import reanalyze
    from .storage import Store

    store = Store(settings.data_dir)
    ids = args.scan_ids or [r["scan_id"] for r in store.list_scans(10_000) if r["status"] == "done"]
    for sid in ids:
        try:
            res = reanalyze(store, sid)
        except FileNotFoundError as e:
            print(f"  skip {sid}: {e}")
            continue
        s = res.summary
        print(f"  {sid} {res.site}: trackers={s.trackers} leaks={s.leaks} id-links={s.shared_id_edges} findings={len(res.findings)}")


def _serve(args) -> None:
    import uvicorn

    from .api.app import create_app

    if args.allow_local:
        settings.allow_local_targets = True
        print("Local targets allowed (testbed mode). Do not expose this server to a network.")
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="info")


def main() -> None:
    sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(prog="python -m tracemap")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="full scan of one URL")
    s.add_argument("url")
    s.add_argument("--quick", action="store_true", help="one profile, 2 subpages (fast, ID edges unconfirmed)")
    s.add_argument("--no-leak", action="store_true", help="skip the form leak test")
    s.add_argument("--consent", choices=["none", "optIn", "optOut"], default="none")
    s.add_argument("--device", choices=["mobile", "desktop"], default="mobile")
    s.add_argument("--phone", help="team-owned 10-digit number(s) for phone canaries (default: env TRACEMAP_CANARY_PHONES)")
    s.set_defaults(fn=_scan)

    a = sub.add_parser("analyze", help="re-run detection/graph/findings on saved scans (no browser)")
    a.add_argument("scan_ids", nargs="*", help="default: all stored scans")
    a.set_defaults(fn=_analyze)

    v = sub.add_parser("serve", help="run the API + web UI")
    v.add_argument("--host", default="127.0.0.1")
    v.add_argument("--port", type=int, default=8000)
    v.add_argument("--allow-local", action="store_true", help="allow scanning *.localhost (for the testbed demo)")
    v.set_defaults(fn=_serve)

    lst = sub.add_parser("lists", help="fetch/show tracker lists")
    lst.add_argument("command", choices=["fetch", "show"])
    lst.set_defaults(fn=lambda a: (sys.argv.__setitem__(slice(1, None), [a.command]),
                                   __import__("tracemap.detect.lists", fromlist=["main"]).main()))

    p = sub.add_parser("pilot", help="run a batch of scans from a CSV (url,sector)")
    p.add_argument("csv")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--no-leak", action="store_true")
    p.add_argument("--limit", type=int)
    p.add_argument("--delay", type=float, default=5.0, help="seconds between sites (politeness)")
    p.set_defaults(fn=lambda a: __import__("tracemap.measure.pilot", fromlist=["main"]).main(a))

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
