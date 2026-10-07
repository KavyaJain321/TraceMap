# TraceMap — Build Plan

> The phased plan we designed. Read `CONTEXT.md` first. Build in this order; each phase produces something testable. Roughly 12 weeks / 7 phases, but treat phases as dependency order, not fixed dates.

---

## Guiding principles

- **Protect the benchmark, not the attacks.** The marks and the paper come from rigorous evaluation (collusion metrics + canary precision/recall + measurement stats). Build a working engine + evaluation first; polish visuals on top.
- **Modular by stage.** One module per pipeline stage (crawl / detect / collusion / leak / score / measure) with clean interfaces, so four people work in parallel.
- **Interpretable, classic ML.** No deep learning. Every score must be explainable (reason codes / SHAP).
- **Confidence, not certainty.** Collusion edges and leaks carry confidence values.

---

## Target repository layout

```
tracemap/
├─ README.md
├─ CONTEXT.md                # the project context (copy of handoff)
├─ PLAN.md                   # this file
├─ docker-compose.yml
├─ pyproject.toml / requirements.txt
├─ data/
│  ├─ lists/                 # Disconnect, DDG Tracker Radar, EasyPrivacy (fetched)
│  └─ corpus/                # curated Indian site lists by sector
├─ tracemap/
│  ├─ crawl/                 # Stage 1: Playwright instrumented crawler
│  ├─ detect/                # Stage 2: tracker classification + risky-script flags
│  ├─ collusion/             # Stage 3: graph build + Louvain + centrality
│  ├─ leak/                  # Stage 4: canary injection + outbound matching
│  ├─ score/                 # Stage 5: interpretable risk model + reason codes
│  ├─ measure/               # Stage 6: batch runner + stats + benchmark
│  ├─ storage/               # DB models, persistence
│  └─ api/                   # FastAPI app
├─ frontend/                 # React + Cytoscape.js/D3
├─ notebooks/                # EDA + figures (DS)
└─ tests/
```

## Data contracts (keep stable so modules stay decoupled)

- **CrawlRecord**: `{ url, timestamp, requests[], scripts[], cookies[], redirects[], storage[] }`
  - `request`: `{ url, method, resource_type, initiator_script, headers, query_params, set_cookie }`
- **DetectedParty**: `{ domain, owner, category (ad|analytics|broker|functional|unknown), is_tracker, evidence[] }`
- **RiskyScript**: `{ src, flags (fingerprinting|outdated_lib|reads_form|obfuscated), evidence }`
- **CollusionEdge**: `{ a, b, evidence_type (cookie_sync|redirect|referer|url_param), shared_value_hash, confidence }`
- **LeakEvent**: `{ canary_id, field, recipient_domain, channel, before_submit (bool), confidence }`
- **RiskResult**: `{ url, score (0-100), subscores{privacy, collusion, supply_chain, leaks}, reasons[] }`

---

## Phase 1 — Foundations & Crawler (Weeks 1–2)  · owner: Kavya (crawler), all (setup)
**Goal:** repo, environment, and a crawler that records everything hidden for one URL.
- Repo scaffold, Docker, DB schema, data contracts above.
- Fetch + parse public lists (Disconnect, DDG Tracker Radar, EasyPrivacy) into `data/lists/`.
- Playwright crawler capturing: all requests (with initiator), scripts, cookies, localStorage, redirect chains.
- Persist a `CrawlRecord` to DB/JSON.
**Done when:** `python -m tracemap.crawl <url>` yields a complete CrawlRecord and it's stored.

## Phase 2 — Detection & Classification (Weeks 3–4)  · owner: Nityavardhan
**Goal:** turn raw crawl into labeled parties + risky scripts + threat model.
- Classify each third party via lists → category + owner.
- Flag risky scripts: fingerprinting (canvas/audio/WebGL API patterns; reuse prior demo as labeled examples), outdated/known-vuln libraries, scripts that can read form fields, heavy obfuscation.
- Write the **threat model** doc (attacker types, kill-chain, OWASP mapping where relevant).
**Done when:** a CrawlRecord produces `DetectedParty[]` + `RiskyScript[]` with evidence.

## Phase 3 — Collusion Graph Engine (Weeks 5–6)  · owner: Krati (DS)
**Goal:** the core novelty — reconstruct + cluster the collusion network.
- Build graph: nodes = third parties; edges = identifier-sharing evidence (cookie sync, redirect, referer, shared URL params). Extract candidate IDs (long, high-entropy, stable values) and match across parties.
- Run **Louvain** community detection + centrality (degree/betweenness). Confidence-weight edges.
- Output `CollusionEdge[]` + communities + hub ranking.
**Done when:** a site yields a graph with detected communities and a modularity value; results reproducible.

## Phase 4 — Canary Leak Tracer (Weeks 7–8)  · owner: Kartik
**Goal:** prove where data leaks.
- Auto-detect form fields; inject unique canary values (fake email/name/phone) per field.
- Monitor outbound requests (and bodies, encodings: plain, base64, hashed) for canaries; flag recipients and whether it left **before submit**.
- Output `LeakEvent[]` with confidence + channel.
**Done when:** on a known leaky test page, planted canaries are detected with correct recipients; precision/recall measurable.

## Phase 5 — Risk Scoring + API (Weeks 9–10)  · owner: Kartik + Krati
**Goal:** one interpretable score, served via API.
- Feature set from stages 2–4 (tracker count, category mix, collusion cluster size/centrality, verified leaks, supply-chain flags).
- Interpretable model: weighted/calibrated scikit-learn model → 0–100 + subscores + **reason codes** (SHAP or coefficient-based).
- FastAPI endpoints: `POST /scan {url}` → RiskResult + graph + leaks; `GET /scan/{id}`.
**Done when:** `POST /scan` returns a full, explainable result for any URL.

## Phase 6 — Frontend / Visualization (Weeks 9–11, parallel)  · owner: Kartik + Kavya
**Goal:** the showcase — clear, non-templated visuals.
- URL input → results view: **collusion graph** (Cytoscape.js, communities colored), **data-leak map** (canary → recipients), **risk report** (score + reasons).
- A visible "attacker's-eye-view" demo tab using the reused consented demonstrator.
**Done when:** a non-technical user can scan a URL and understand the output.

## Phase 7 — Measurement Study + Evaluation + Paper (Weeks 11–12)  · owner: Krati + all
**Goal:** the research contribution.
- Curate Indian site corpus by sector (banking/health/gov/e-commerce) in `data/corpus/`.
- Batch runner over the corpus → results dataset.
- Compute metrics: modularity/centrality; canary precision/recall; clustering silhouette; sector risk ranking with stats. Benchmark vs OpenWPM + blocklists.
- Figures + write-up; prepare dataset release.
**Done when:** a reproducible results dataset + evaluation report + figures exist.

---

## Definition of Done (whole project)
- `docker compose up` runs API + DB; `POST /scan` returns collusion graph + verified leaks + explainable 0–100 score.
- Measurement pipeline runs over a URL list and outputs a dataset + summary stats + baseline comparison.
- Code modular per stage, tested, documented; honest limitations stated.

## First-week checklist (do these first)
1. Scaffold repo + Docker + DB + data contracts.
2. Fetch and parse the three public tracker lists.
3. Playwright crawler capturing requests/scripts/cookies/redirects for one URL, persisted.
4. A single end-to-end smoke test: crawl one site → store a CrawlRecord.
