# TraceMap — Project Context

> A Web Privacy & Security Intelligence Platform for Detecting Third-Party Tracker Collusion Networks.
> This file is the single source of truth for what TraceMap is, why it exists, and how it works. Read it fully before writing any code.

---

## 1. One-paragraph summary

When a user opens a website, the browser silently contacts dozens of hidden third parties (ad networks, analytics, data brokers) that track the user, and it runs third-party scripts that can read everything on the page (including form fields). Existing tools only *list* individual trackers. **TraceMap** goes further: it loads any website in an instrumented headless browser, records all hidden activity, **reconstructs the "collusion network"** of trackers that secretly share a user's identity, **verifies where personal data actually leaks** using injected canary values, and fuses everything into an **interpretable 0–100 privacy-and-security risk score** with reasons. It is validated by a **measurement study of Indian websites** (banking, health, government, e-commerce).

## 2. The problem (why this matters)

- Users and even site owners cannot see who collects their data, where it goes, or how collectors cooperate.
- Two linked dangers on every page: (a) **surveillance** — trackers profile the user across sites; (b) **client-side supply-chain risk** — any included script can skim form data (the Magecart / formjacking class).
- Existing tools don't answer three questions *together*: who colludes, where data leaks, and how risky the site is overall.
- Regional gap: almost all measurement targets Western sites; the Indian web is barely studied despite the **DPDP Act, 2023**.

## 3. What makes TraceMap different (the novelty — protect this)

> **Revised 2026-10-07 after the panel review (`PANEL_REVIEW.md`).** Each technique below has
> prior art (Blacklight, Leaky Forms, cookie-sync and tracker-graph papers, PrivacyScore). The
> defensible contribution is the **sector-stratified Indian measurement** they enable, taken as a
> pre-enforcement DPDP baseline, plus the data products it produces. "Collusion" is replaced by
> **identifier-flow network** (evidence of ID sharing, not proof of intent).

Research questions (the paper is organised around these):

1. **RQ1 Coverage:** how much of the Indian third-party ecosystem do global tracker lists miss? → India tracker supplement, contributed upstream.
2. **RQ2 Leakage:** how often do Indian sites send form PII (email, +91 phone) to third parties before Submit, to whom, in which encodings, by sector?
3. **RQ3 Structure:** which organisations are identifier-flow hubs, and do communities show cross-company sharing beyond corporate ownership (tested against Bashir & Wilson 2018's negative result)?
4. **RQ4 Supply chain:** exposure of login/payment pages to client-side attacks (vulnerable libraries, missing SRI/CSP, dangling script domains); ties to PCI DSS 6.4.3/11.6.1.
5. **RQ5 Readiness:** pre-consent tracking and undisclosed processors, phrased as DPDP readiness gaps (core duties apply from ~May 2027), never as violations.

The tool's distinctive pieces: A/B/A2 identifier confirmation feeding an entity-tagged graph,
canary typing timed against the same capture (leak replay with proof), +91 phone canaries, an
India vendor supplement, and a score shown with its uncertainty and validated against expert rankings.

**Do NOT** manufacture novelty by only swapping ML models, adding a dashboard, or renaming things.

## 4. Existing work & where we sit (so we don't rebuild)

| Existing | What it does | Gap we fill |
|---|---|---|
| **OpenWPM** (Englehardt & Narayanan, CCS 2016) | Standard large-scale tracking-measurement crawler | Framework only; we build detection + collusion + leak + scoring + viz on top |
| **webXray** (Libert 2015) | Maps trackers to owning companies | No per-site collusion graph, no verified leaks, no fused score |
| **Cookie Synchronization** (Papadopoulos et al., WWW 2019) | Proves trackers swap IDs to merge profiles | Measures the phenomenon; we reconstruct/visualize it per site |
| **Leaky Forms** (Senol et al., USENIX 2022) | Finds email/password leaked before submit | Validates our canary method; we make it a live integrated module |
| **Fingerprinting the Fingerprinters** (Iqbal et al., S&P 2021) | ML detection of fingerprinting scripts | One signal; we fuse into the risk score |
| **Blacklight** (The Markup) | Fixed single-page privacy tests | No collusion, no verified leaks, no regional study |
| **Ghostery / WhoTracks.Me** | Blocking + global stats | Not a per-site investigative audit |

## 5. How it works — the six-stage pipeline

```
INPUT (website URL)
  → 1. CRAWL        instrumented headless browser records every request, script, cookie, redirect
  → 2. DETECT       classify third parties (ad/analytics/broker) via public lists;
                    flag risky scripts (fingerprinting, outdated libs, form-field access)
  → 3. COLLUSION    build graph (nodes=third parties, edges=identifier-sharing evidence);
                    Louvain community detection + centrality → colluding clusters + hubs
  → 4. LEAK TRACE   inject unique canary values; watch outbound requests; prove who received them
                    (esp. before form submission)
  → 5. RISK SCORE   fuse signals → interpretable 0–100 score + reason codes
  → 6. MEASURE      run at scale on Indian site corpus; benchmark vs OpenWPM/blocklists
OUTPUT: Collusion Network Graph · Data-Leak Map · Risk Report (0–100)
```

### Edge = "identifier-sharing evidence" (the heart of Stage 3)
Add an edge between two third parties when there is observable evidence they share the same user identifier, e.g.:
- The same ID-looking value appears in requests/cookies to both parties (cookie syncing).
- ID passed via redirect chains, URL parameters, or `Referer` leakage between them.
- Shared value in query strings / response bodies.
Treat each edge as **confidence-weighted** (a clue, not proof). This honesty is part of the research contribution.

## 6. Tech stack (only what's needed)

*(Revised 2026-10-07 to match the build; reasons in `reports/TraceMap open source reuse plan.md`.)*

- **Language:** Python 3.11 (pins: `networkx<3.7`; Leiden via MIT `graspologic-native`, not GPL `leidenalg`)
- **Crawler:** Playwright driving installed Chrome over a raw CDP session (initiator stacks, POST bodies); mobile emulation; DuckDuckGo autoconsent (vendored, MPL-2.0) for banner modes; JS API hooks adapted from DuckDuckGo tracker-radar-collector (Apache-2.0). OpenWPM not used (Firefox-only, no Windows support).
- **Tracker data (fetched at runtime, versions pinned):** DuckDuckGo TDS, Ghostery TrackerDB, Disconnect, third-party-web, EasyPrivacy/EasyList/IndianList, AdGuard Tracking + CNAME lists, plus the team's India supplement
- **Graph:** NetworkX + centrality; Leiden + null models at corpus level (second half)
- **ML (classic, interpretable, only where real labels exist):** calibrated logistic regression for edge confidence; InterpretML EBM for leak risk; transparent scorecard + SALib sensitivity analysis (no score shown until validated)
- **Backend:** FastAPI with Server-Sent Events; SSRF guard
- **Storage:** JSON documents + content-addressed blobs + SQLite index (Postgres optional later)
- **Frontend:** React + TypeScript (Vite) + Cytoscape.js (fCoSE); hand-written CSS, fonts bundled for offline demos
- **Packaging:** Docker (files provided; to be tested once Docker is installed)

## 7. Team & ownership (4 members)

| Member | Spec | Owns |
|---|---|---|
| Kavya Jain | CSF | Instrumented crawler + capture pipeline; live demo harness |
| Nityavardhan Singh Hartala | CSF | Detection & threat analysis (tracker classification, fingerprinting + supply-chain/Magecart risk); threat model |
| Kartik Arora | CSF | Canary leak-tracer + backend + security testing; integration |
| Krati Dhenkawat | DS | Collusion graph (Louvain/centrality), risk-scoring model, measurement study, all figures |

Shared: dataset, evaluation design, paper.

## 8. Data sources & ethics

- **Only free/public data:** public tracker lists; publicly accessible websites; data TraceMap generates by crawling.
- **Canaries are synthetic** markers the team creates. **No real user data** is collected.
- Scan only public sites; respect robots/ToS where required; sandbox any risky analysis.
- The **labeled Indian-web dataset** the team produces is a deliverable (release for reproducibility).

## 9. Evaluation (NOT plain accuracy)

- **Collusion graph:** modularity, centrality distribution, cluster stability.
- **Leak tracer:** precision/recall vs the team's own planted canaries (ground truth is known).
- **Measurement study:** clustering quality (silhouette); sector-wise risk ranking with statistical tests.
- **Baselines:** OpenWPM, public blocklists, Blacklight-style checks.

## 10. Scope boundaries

- **In scope (college MVP):** scan a URL → collusion graph + leak map + risk score; a measurement run over a curated Indian site list; benchmark + written evaluation.
- **Out of scope / future:** hosted public service, browser extension, real-time/continuous monitoring, multi-country study, compliance-audit workflows.

## 11. Honest limitations (state these, don't hide)

- Collusion edges are evidence, not certainty → confidence-weighted.
- No public ground-truth for "collusion" → validate via structure + known cases.
- Anti-bot defenses can block crawling → record and skip gracefully.
- Don't claim to out-accuracy heavy academic defenses; win on interpretability + the combined pipeline + regional data.

## 12. Prior asset to reuse

The team earlier built a small **client-side data-collection demonstrator** (a page that, with consent, shows how much a single script can silently harvest: fingerprint, IP via WebRTC, etc.). Reuse it **only** as the consented "attacker's-eye-view" demo and as labeled examples of fingerprinting behavior. Never deploy it to collect from real users.

## 13. Success criteria for the build

- A user can submit a URL and get, within a reasonable time: an interpretable collusion graph, a verified leak list, and a 0–100 risk score with reasons.
- Canary leak detection is measurable (precision/recall on planted canaries).
- The measurement pipeline runs over a list of URLs and outputs a results dataset + summary stats.
- Everything reproducible via Docker; code is modular per the six stages.
