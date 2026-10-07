# TraceMap: Build Plan (revised 2026-10-07)

> Read `CONTEXT.md` first. This revision applies the panel review (`PANEL_REVIEW.md`) and the
> open-source reuse research (`reports/TraceMap open source reuse plan.md`). The project is
> split into two halves to match the college reviews: **first half (~45%) = a working tool on
> any website + a 50-site pilot**, **second half = the validated research study**.

## Guiding principles

- **The study is the contribution; the tool is the method.** Lead with the Indian measurement,
  not with "new detectors".
- **Reuse, don't rebuild:** public lists and data at runtime, DuckDuckGo autoconsent vendored,
  TRC's API list adapted (Apache-2.0), Leaky Forms / Englehardt methods reimplemented from papers.
- **Evidence, not certainty:** every edge and leak has a confidence and links to the captured request.
- **Interpretable, classic ML only, and only where real labels exist.**
- **Decoupled stages** via `tracemap/contracts.py`; stages 2-5 run on stored crawls
  (`python -m tracemap analyze`) so three people can work without a browser.

## Repository layout (as built)

See `README.md#layout`. Data contracts live in `tracemap/contracts.py`
(CrawlRecord → DetectedParty / RiskyScript → SiteGraph / CollusionEdge → LeakReport / LeakEvent → ScanResult).
Changes vs the original contracts: per-profile `Visit`s (A, B, A2, L), `post_data`, initiator
stacks, `APICall` log, cookie setter attribution, `PageVisit.status` (blocked/timeout), leak
`matched`/`where`/`field_typed_at` for the proof view, `RiskResult.score = None` until validated.

---

## FIRST HALF: mid-semester review (target ~week 7)

| # | Phase | Status | Owner |
|---|---|---|---|
| 0 | Setup: repo, contracts, storage, threat model, ethics draft | **Done** (`docs/threat_model.md`, `docs/ethics_protocol.md`). **Action: submit ethics form now.** | All |
| 1 | Crawler: Playwright + raw CDP, mobile emulation, A/B/A2 profiles, landing + 4 subpages, initiators, POST bodies, cookies with setter, storage, JS API hooks, consent modes (autoconsent), bot-wall detection | **Done** | Kavya |
| 1b | Testbed on `*.localhost` with ground truth | **Done** | Kavya |
| 2 | Detection: TDS, TrackerDB, Disconnect, third-party-web owners/categories (majority vote), EasyPrivacy/EasyList/IndianList/AdGuard rule matching, TDS CNAME map, India supplement v0, behaviour flags (canvas/audio/webgl/font/webrtc fingerprinting, form reads, key listeners) | **Done** (India supplement needs 2-coder verification) | Nityavardhan |
| 3 | Leak tracer v1: field finder (incl. iframes), canary typing with no-submit guard, 3-layer encoding/hash pool (~48k variants), source-field attribution | **Done** | Kartik |
| 4 | UI: scan + live progress, case file (stamp, ledger, findings + proof drawer), leak replay, ID-sharing map, companies table; FastAPI with SSE + SSRF guard | **Done** | Kartik + Kavya |
| 4b | Basic per-site graph: inclusion, redirects, shared-ID edges with A/B/A2 confirmation | **Done** | Krati |
| 5 | Pilot: `data/corpus/pilot_50.csv`, `python -m tracemap pilot` | **Runner done; run after ethics approval** (passive `--no-leak` run is fine before) | Krati + all |

**Mid-review demo:** see `README.md#mid-semester-demo-script`.

### Remaining first-half to-dos
- [ ] Submit ethics protocol; get faculty legal-cell note on IT Act s.43/66.
- [ ] Register a team canary email domain; set `TRACEMAP_CANARY_EMAIL_DOMAIN`; set `TRACEMAP_CANARY_PHONES` to a team-owned number.
- [ ] Two coders verify every entry of `data/lists/supplement/india.json` (set `verified`, add source URL).
- [ ] Run the TRC "measuring stick" once on the testbed (needs `npm i` in a separate folder) and compare API coverage with `instrument.js`.
- [ ] Run the 50-site pilot; record per-site time, block rate per sector, banner rate, fields found.
- [ ] Install Docker and test `docker compose up`.

---

## SECOND HALF: end-semester review

| # | Phase | Owner |
|---|---|---|
| 6 | **ID-flow graph, research grade:** 300 hand-labelled candidate edges (2 coders, κ) → calibrated logistic-regression edge confidence; corpus-level graph; Leiden (graspologic-native, MIT) with 100 seeds + consensus; configuration-model nulls (z-score); NMI vs ownership partition (tests Bashir & Wilson 2018) | Krati |
| 7 | **Security checks:** retire.js repository + OSV.dev API (vulnerable JS libs); SRI on login/payment pages; CSP via MDN HTTP Observatory (npx); dangling script domains (whoisit/RDAP, passive only); `tracemap diff` script-inventory change detection (PCI DSS 6.4.3/11.6.1) | Nityavardhan |
| 8 | **Full study:** ~1,500 sites from CrUX India stratified by sector (see `docs/corpus.md`); 200-site × 3 repeat stability subset; Blacklight-collector cross-check on 100 sites | Kavya + all |
| 9 | **Score + statistics:** transparent points scorecard (4 subscores) with Monte-Carlo/SALib sensitivity interval; expert ranking of 30 sites (3 raters, Krippendorff α); EBM leak-risk model trained on canary-verified labels; Kruskal-Wallis + Dunn (Holm), ε², Cliff's δ, negative-binomial GLM with popularity bucket | Krati + Kartik |
| 10 | **Full UI:** security panel, sector dashboard, evidence bundle (HAR + screenshots + JSON + SHA-256 manifest via bagit) | Kartik + Kavya |
| 11 | **Finish:** paper, dataset release (CC BY-NC-SA where list-derived), India supplement PRs upstream, responsible disclosure (sites + CERT-In, 45-day embargo) | All |

## Evaluation (see PANEL_REVIEW.md B6)

| Component | Ground truth | Metric |
|---|---|---|
| Instrumentation & leak tracer | testbed + negative-control canaries + mail received at canary domain + Blacklight agreement | precision / recall, false-positive rate |
| Third-party classification | 2-coder labels on unknown domains | coverage gain vs list-only, κ |
| ID edges | 300 labelled edges | precision/recall, Brier, reliability diagram |
| Communities | rewired nulls, ownership partition | Q z-score, NMI, seed ARI |
| Score | expert ranking, repeat crawls | Krippendorff α, Kendall τ, ICC, rank shift under weight perturbation |
| Sector comparison | — | effect sizes with BCa CIs, NB-GLM coefficients |

## Definition of done (whole project)
- `python -m tracemap serve` (and `docker compose up`) gives scan → case file with leaks, ID map, findings, proof.
- The study pipeline outputs a dataset + statistics + baseline comparison for ~1,500 Indian sites.
- Tests pass on the testbed ground truth; limitations stated in the UI and the paper.
