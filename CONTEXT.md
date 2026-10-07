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

TraceMap is **not** "another tracker list." Its defensible contributions, together in one tool:

1. **Interpretable collusion network per site** — reconstructed from identifier-sharing evidence, using graph community detection (Louvain) + centrality. (Existing tools give flat lists; the cookie-sync literature proves collusion happens but doesn't build a per-site usable graph.)
2. **Verified data-leak provenance** — canary injection proves a specific value reached a specific third party (not domain-list guessing).
3. **Fused privacy + security risk score** — combines tracking, collusion, and client-side supply-chain signals into one explainable number with reason codes.
4. **Regional measurement** — first focused study of Indian banking/health/gov/e-commerce sites.
5. **Interpretability** — plain-language reasons, not raw logs or a black box.

**Do NOT** manufacture novelty by only swapping ML models, adding a dashboard, or renaming things. The novelty lives in 1–4 above.

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

- **Language:** Python 3.11+
- **Crawler:** Playwright (preferred, modern) — OpenWPM optional for measurement parity
- **Tracker data:** Disconnect list, DuckDuckGo Tracker Radar, EasyPrivacy (public)
- **Graph:** NetworkX + `python-louvain` (community detection) + centrality
- **ML (classic, interpretable — NOT deep learning):** scikit-learn (script classification, risk-score calibration), SHAP for reason codes
- **Backend:** FastAPI
- **DB:** PostgreSQL (crawl results, findings); SQLite acceptable for MVP
- **Queue (optional):** Redis + a worker for scaling crawls
- **Frontend:** React + Cytoscape.js (collusion graph) / D3.js; plain, non-templated styling
- **Packaging:** Docker

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
