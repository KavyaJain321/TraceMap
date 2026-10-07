# TraceMap

TraceMap opens a website the way a phone user would, records every company the page quietly
talks to, types a **fake** email and phone number into its forms (never pressing Submit) to see
who receives them, and maps which companies exchange identifiers about you. Every finding links
to the exact request that proves it.

Research use: a sector-wise study of Indian websites (government, banking, health, e-commerce,
education) as a baseline before the DPDP Act's core duties apply. See `CONTEXT.md`, `PLAN.md`
and `PANEL_REVIEW.md`.

**Status:** first half (mid-semester scope) is built: crawler, tracker detection, leak tracer,
identifier-flow graph, findings, API, web UI, testbed with ground truth, pilot runner.
Second half: validated risk score, security checks (retire.js/OSV, SRI/CSP, dangling domains),
corpus-level Leiden communities, 1,500-site study, evidence bundles.

## Quick start (Windows, Python 3.11)

```bash
py -3.11 -m venv .venv
```

```bash
.venv\Scripts\python -m pip install -e ".[dev]"
```

```bash
.venv\Scripts\python -m playwright install chromium
```

```bash
.venv\Scripts\python -m tracemap lists fetch
```

```bash
cd frontend && npm install && npm run build
```

TraceMap uses your installed Google Chrome when present (most realistic), otherwise
Playwright's bundled browser.

## Run it

Web UI + API (open http://127.0.0.1:8000):

```bash
.venv\Scripts\python -m tracemap serve
```

Command line scan of one site (`--quick` = one visitor, ~1 min; default = thorough A/B/A2, ~3-4 min):

```bash
.venv\Scripts\python -m tracemap scan https://www.example.in --quick
```

Other commands:

| Command | What it does |
|---|---|
| `python -m tracemap.crawl <url>` | Stage 1 only: store a CrawlRecord |
| `python -m tracemap analyze [scan_id ...]` | Re-run detection, leak matching, graph and findings on stored crawls (no browser) |
| `python -m tracemap pilot data/corpus/pilot_50.csv` | Batch run with resume and per-sector summary |
| `python -m tracemap lists fetch` | Download tracker lists; versions pinned in `data/lists/manifest.json` |
| `python -m testbed` | Local test website with planted trackers and leaks (`http://shop.localhost:8765/`) |

### Settings (environment variables)

| Variable | Meaning |
|---|---|
| `TRACEMAP_CANARY_EMAIL_DOMAIN` | Domain for fake emails. Use a domain the team owns so mail arriving later proves a leak. Default `example.com`. |
| `TRACEMAP_CANARY_PHONES` | **Team-owned** 10-digit numbers. Empty = phone fields are skipped on real sites (a random number could be a real person's). |
| `TRACEMAP_DATA_DIR` | Where scans are stored (default `var/`). |
| `TRACEMAP_ALLOW_LOCAL=1` / `serve --allow-local` | Allow scanning `*.localhost` (testbed demo only). |

## Mid-semester demo script

1. Start the testbed and the UI (`.claude/launch.json` has both):
   `python -m testbed` and `python -m tracemap serve --allow-local`.
2. Scan `http://shop.localhost:8765/` in **Thorough** mode. Show the live log and stage rail.
3. Case file: the violet stamp, the ledger, then **Leak replay**. Press *Replay*; click a dot to
   open the proof drawer with the highlighted hash.
4. **ID-sharing map**: AdNet A → Broker B redirect sync; click the edge, show proof.
5. Show `testbed/ground_truth.json` and `pytest -m browser`: every planted leak, tracker and
   sync found, zero false recipients, zero hits for a negative-control canary.
6. Scan one real public site in Quick mode with the form test off, and open the pilot summary.
7. Fallback if Wi-Fi fails: open a stored scan from **Case files** (works offline).

## Tests

```bash
.venv\Scripts\python -m pytest -q
```

- `tests/test_units.py`: domains, subpage choice, bot walls, consent-rule filter, canary encodings
  (positive and negative), ID heuristics, storage.
- `tests/test_api.py`: SSRF guard, listing, proof lookup, event replay.
- `tests/test_testbed_e2e.py` (`-m browser`, ~2.5 min): full pipeline vs `testbed/ground_truth.json`.

## Layout

```
tracemap/
  contracts.py   data contracts between stages (Pydantic)
  crawl/         Stage 1: Playwright + CDP crawler, JS API hooks, consent, bot walls
  detect/        Stage 2: tracker lists, owners, categories, behaviour flags
  collusion/     Stage 3: user-ID detection (A/B/A2) and identifier-flow graph
  leak/          Stage 4: canaries, encoding/hash pool, form filling, matching
  findings.py    plain-English findings with reason codes
  pipeline.py    run_scan / analyze / reanalyze
  measure/       Stage 6: pilot batch runner
  api/           FastAPI + live progress (SSE)
  storage/       JSON documents, blob store, SQLite index
frontend/        React UI (case file, leak replay, ID-sharing map, proof drawer)
testbed/         fake sites on *.localhost + ground truth
data/lists/supplement/  team-authored India vendor list (+ testbed labels)
data/corpus/     site lists
docs/            threat model, ethics protocol, corpus plan
```

## Who owns what

| Member | Modules |
|---|---|
| Kavya | `crawl/`, `testbed/`, pilot operations |
| Nityavardhan | `detect/`, India supplement, `docs/threat_model.md` |
| Kartik | `leak/`, `api/`, `frontend/`, disclosure process |
| Krati | `collusion/`, `findings.py` scoring (second half), `measure/` statistics |

## Limits (stated, not hidden)

Browser-side only, so server-to-server sharing is invisible and every number is a **lower bound**.
Public pages only (no logins). Identifier edges are evidence with a confidence, not proof of
intent. Sites that show bot checks are recorded as blocked and skipped. Docker files are
provided but were not tested on the development machine (no Docker installed).

## Licences

Code: Apache-2.0. See `NOTICE.md` for adapted code (DuckDuckGo tracker-radar-collector, Apache-2.0),
the vendored autoconsent bundle (MPL-2.0) and runtime-fetched data (DuckDuckGo, Disconnect and
Ghostery data are CC BY-NC-SA 4.0, so derived datasets must be released non-commercially).
