# TraceMap: Panel Review and Team Response

> **Part A** is a hostile review of the current proposal (CONTEXT.md + PLAN.md) as an experienced examiner would give it.
> **Part B** is the team's research-backed response: what we concede, how we reposition, and the upgrades we make.
> Research date: 30 Sep 2026. Sources marked **(verify)** are recent or came from a single secondary source. Confirm them before putting them in the paper.

---

# PART A: Panel Review

*Written from the chair's seat: someone who has examined web-measurement and security projects for a long time and has seen many "tracker scanners".*

## Verdict

**As proposed, TraceMap is an integration project presented as research.** Each of its four "novel" contributions already exists, often as maintained open-source code. Its core output, a 0–100 score, has no ground truth. Its central concept, "collusion", is not measured by what it collects. The Indian-web angle is the only defensible part, and the proposal overstates even that ("first focused study"). Without major changes I would grade it as a competent engineering exercise with an unsupported research claim.

Issues follow, by severity: **[F] = fatal** as written, **[M] = major**, **[m] = minor**.

## A1. Novelty and framing

**A1.1 [F] Claim 2 (canary leak detection) already exists, as maintained open source.**
- **The Markup's Blacklight (2020)** types fake email, password and card values into forms *without submitting*, then searches traffic for plain, base64, MD5, SHA-256 and SHA-512 forms. The collector is GPL-3.0 and had a new release in June 2026.
- **Leaky Forms (Senol et al., USENIX Security 2022)** did exactly this "before submit" on 100K sites. It covered roughly 30 hashes and encodings nested three deep, used an ML email-field classifier, and ran three consent modes. It found leaks on 1,844 EU sites and 2,950 US sites.
- **Starov et al. (PETS 2016)** and **Englehardt et al. (PETS 2018)** came earlier.
- What exactly is new here?

**A1.2 [F] Claim 1 (collusion network with Louvain and centrality) is not new.**
- Acar 2014, Englehardt & Narayanan 2016 and Papadopoulos 2019 detect cookie syncing.
- **Kalavri et al. (PAM 2016)** ran community detection on tracker graphs.
- **Bashir & Wilson (PETS 2018)** ran Louvain, label propagation, betweenness and PageRank on tracker graphs, and reported that the **Louvain communities were not meaningful**.
- **Solomos et al. (TMA 2020)** computed centralities on tracker-to-tracker graphs.
- **WebGraph (USENIX Security 2022)** builds per-page graphs with "shared information" edges whenever a cookie value appears in a request.
- Mozilla's 2012 visualiser was literally called **"Collusion"** (later Lightbeam).
- You are proposing a method that the literature has already tried and found wanting.

**A1.3 [M] Claim 3 (fused score) has precedent, and the precedent has been criticised.**
- **PrivacyScore** (2017) and **WebTrackingScore** (2025) already produce such scores.
- **Vansteenhuyse et al. (2025)** showed that website security scores disagree with each other, favour popular sites, and are easy to game.

**A1.4 [M] Claim 4 ("first focused study of the Indian web") is false as worded.** Prior work:
- **Agarwal/Vekaria et al. (ICWSM 2021)** measured tracking on 103 Indian news sites, *including cookie syncing*.
- **Götze et al. (WebSci 2022)** measured cookies on 5,124 .gov.in and .nic.in sites.
- **Arrka (2022)** and **ComplyZero (2026, 6,000+ Indian sites, "96% track without consent")** **(verify)** published industry reports.
- An examiner will look these up in the viva.

**A1.5 [M] "Collusion" is the wrong word, and a risky one.**
- Collusion implies intent and is a competition-law term.
- Most identifier sharing is contractual real-time-bidding syncing, disclosed in privacy policies, or accidental.
- The method (by Englehardt's own admission) mixes intentional syncing with accidental ID sharing.
- Naming Indian banks or government portals as parties to "collusion" in a public dataset is a defamation and reputational risk for the university.

**A1.6 [M] The "combination is the novelty" argument is weak.** Stapling Blacklight, Leaky Forms and OpenWPM cookie-sync analysis into one Python tool is integration work. It is not a research contribution unless the combination reveals something that no single part can.

## A2. Technical validity

**A2.1 [F] The pipeline is increasingly blind to where the data actually goes.**
- Server-to-server syncing, Meta's Conversions API, server-side Google Tag Manager and first-party proxying all bypass the browser.
- A June 2026 study finds **over 54% of sites use first-party or server-side tracking techniques** **(verify)**.
- Your graph therefore measures a shrinking, unknown fraction of reality, but the product presents it as "the collusion network".

**A2.2 [F] The "identifier" in "identifier-sharing evidence" is never defined.**
- A single visit cannot tell a user ID from a session nonce, a timestamp, a campaign code or a constant.
- The established methods need **two synchronised crawls with different profiles**, plus persistence, length and similarity thresholds. PLAN.md has none of this.
- Without it, the edges are noise with a confidence number attached.

**A2.3 [M] Per-site Louvain is statistically meaningless.**
- A single site has about 10–40 third parties.
- Modularity has a resolution limit (Fortunato & Barthélemy 2007), and **random graphs show high modularity** (Guimerà 2004).
- Louvain can produce disconnected communities (Traag 2019).
- "Cluster stability" is listed as a metric but never defined.

**A2.4 [M] Collapsing to domain level merges one company with collusion.** doubleclick.net ↔ google-analytics.com is Google talking to Google. Without an entity (ownership) layer, your top "colluding cluster" will be Alphabet, and you will have rediscovered corporate ownership.

**A2.5 [M] A homepage-only, desktop, headless crawl is not representative.**
- Subpages set about 36% more cookies (Urban 2020), and internal pages differ materially (Aqeel 2020).
- Headless Chromium gets soft-blocked about twice as often (15% vs 7%, Gundelach 2026 **(verify)**).
- Browser configuration alone shifts about 19% of tracking domains (Jueckstock 2021).
- **64.5% of Indian web traffic is mobile** (StatCounter, Aug 2026), yet you plan a desktop crawl.

**A2.6 [M] The "banking" sector measures marketing pages, not banking.**
- The sensitive flows (net-banking login, OTP, account pages) are behind authentication, which you rightly won't cross.
- A risk score for "SBI" derived from its homepage says little about the risk of banking with SBI. The sector label oversells what is measured.

**A2.7 [M] The bot-wall attrition will differ by sector.** Banks and government sites use WAFs and bot managers more than blogs do. If 25% of bank sites are blocked and 5% of e-commerce sites are, the sector comparison is biased before any statistics are run.

**A2.8 [M] The canary tracer has unexamined failure modes.**
- Fake values fail client-side validation, so the scripts never fire.
- Indian phone formats (+91, 0-prefixed, spaced, 10-digit) are not in the plan.
- There are OTP-gated flows, and virtual keyboards on bank pages.
- "Before submit" is undefined.
- Canaries in "valid" Aadhaar or PAN formats could collide with real people's identifiers.

**A2.9 [M] The "supply-chain" signal is capability, not behaviour.**
- Almost every analytics script touches the DOM, so the `reads_form` flag will fire everywhere.
- "Outdated library" is just a retire.js lookup.
- Magecart detection needs evidence of exfiltration, not capability. As designed, the security half is thin.

**A2.10 [m] Western tracker lists under-cover the Indian ecosystem.**
- DuckDuckGo Tracker Radar has **no India region** (its regions are AU, CA, CH, DE, FR, GB, NL, NO and US).
- Indian martech and ad-tech vendors (CleverTap, MoEngage, WebEngage, Netcore, InMobi, Affle, iZooto, Times Internet's Colombia, and others) may be missing or miscategorised. Coverage is unmeasured.
- Your tracker counts for Indian sites will be systematically low, and you would never know.

## A3. The score and the "ML"

**A3.1 [F] The risk score has no target variable.**
- "Calibrated scikit-learn model" asks: calibrated to what?
- No ground truth exists for "risky website".
- Training on labels the team invented, then explaining with SHAP, is circular. SHAP would faithfully explain your own labelling rules back to you.

**A3.2 [M] 0–100 is false precision, and it mixes incommensurable things.** Privacy exposure and security exposure have different units. A site scoring 62 vs 58 means nothing unless you show the uncertainty from the weighting choices (OECD/JRC Handbook: sensitivity analysis is mandatory for composite indicators).

**A3.3 [M] The ML is decorative.** Where exactly is a model trained, on which labelled data, and what does it beat? "scikit-learn for script classification" has no labels, no baseline and no metric in the plan. It reads as ML added to tick a box.

**A3.4 [m] The scores are gameable.** Once the weights are known, a site can lower its score, for example by proxying trackers server-side, without reducing any real data flow. The score would reward hiding.

## A4. Evaluation

**A4.1 [M] "Precision/recall vs our own planted canaries" is close to circular.** On a testbed you built, recall will be about 100% by construction. On the real web, recall is unknown. You need negative controls, independent confirmation (e.g., mail actually received at the canary address), and cross-validation against another tool.

**A4.2 [M] "Benchmark vs OpenWPM" compares unlike things.**
- OpenWPM is a crawler, not a detector.
- It runs on Firefox, so any difference confounds browser and tool.
- There is no baseline at all for the collusion graph.

**A4.3 [M] Modularity is not validation.** A high modularity value (Q) proves nothing without a null model. And what external check is there that the communities are real?

**A4.4 [M] The statistics are under-specified.**
- Sample size per sector is not stated.
- There is no control for site popularity.
- There is no multiple-comparison correction and no effect sizes.
- "Silhouette" of which clustering, of which feature space?

**A4.5 [m] The results are not reproducible.** The web changes daily, and tracker lists change weekly. There is no plan to version lists, pin the Public Suffix List, archive raw traffic, or repeat crawls.

## A5. Real-world usefulness: "Who would use this?"

**A5.1 [F] No user is named.**
- End users already have uBlock Origin and Brave.
- Site owners buy OneTrust, Cookiebot, ObservePoint, c/side, Jscrambler, Feroot or Reflectiz.
- Regulators need evidence, not a heuristic score.
- Journalists already have Blacklight.

**A5.2 [M] The DPDP framing is premature.** Data fiduciaries' substantive obligations (Sections 3–17) take effect only from **~13 May 2027** (DPDP Rules notified 13 Nov 2025). Nothing TraceMap finds today is a "DPDP violation". Claiming or implying otherwise is wrong.

**A5.3 [m] There is no output format anyone can act on.** A score and a pretty graph cannot be attached to an audit, a PCI assessment or a complaint.

## A6. Ethics, law, licensing

**A6.1 [M] Automated form interaction on bank and government sites needs formal ethics clearance.** It can trigger fraud-detection systems. The plan has no ethics approval, no disclosure policy, no rate limits and no plan for what happens when you find a real leak on a government site.

**A6.2 [M] The "attacker's-eye-view" demonstrator is dual-use.** It harvests fingerprints and the local IP via WebRTC. Shipping it in a public repo or demo tab invites the question of why the team is distributing a data-harvesting kit.

**A6.3 [m] Licensing constrains the dataset release.**
- OpenWPM and Blacklight are GPL-3.0.
- Tracker Radar, TDS, Disconnect and Ghostery TrackerDB are CC BY-NC-SA 4.0.
- The proposed "labelled dataset release" must respect all of these. Nobody has checked.

## A7. Feasibility and team

**A7.1 [M] The project is over-scoped for four students in 12 weeks.** It includes a crawler, a detection stack, a graph engine, a leak tracer, an ML score, a FastAPI backend, a React frontend, an attacker demo, a measurement study, an OpenWPM benchmark and a paper. Something will be faked at the end, usually the evaluation.

**A7.2 [M] One person is a single point of failure.** Krati owns the graph, the score model, the measurement study *and* all figures, which is the entire research contribution.

**A7.3 [m] The threat model is a Phase 2 afterthought.** It should drive design, not be written after detection is built.

## Chair's closing remark

> "Strip away the dashboard and what remains is a re-implementation of Blacklight's keylogging test, Englehardt's cookie-sync heuristic and an arbitrary weighted sum, pointed at Indian homepages. Tell me one finding this tool can produce that the existing tools cannot, and one person who will use it after you graduate."

---

# PART B: Team Response

*From the team, after deep research into prior art, methodology literature, reusable repos and the Indian regulatory context.*

## B1. What we concede (honestly)

1. **Claim 2 (canary leak detection) is not novel as a technique.** Blacklight and Leaky Forms did it. We now **build on their published method** instead of claiming it.
2. **Claim 1 (ID-sharing graph with community detection) is not novel as a technique.** Bashir & Wilson's negative Louvain result is real, and we make it a **hypothesis we test**, not something we assume away.
3. **"Collusion" is dropped as a technical term.** We say **"identifier-flow network"**, with edges meaning *observable client-side ID-sharing evidence*.
4. **"First study of the Indian web" is dropped.** Our claim is narrower and true (B2).
5. **A 0–100 score is a communication device, not a contribution.** We validate it rigorously and put the ML where real labels exist.
6. **Client-side measurement is a lower bound.** We say so in every output, and we add detection of server-side and cloaking signals.

## B2. Repositioned project

**TraceMap: an evidence-grade, open-source, outside-in auditor of client-side personal-data flows. It is applied in the first sector-stratified study of Indian government, health, banking, e-commerce and ed-tech websites to combine verified form-PII exfiltration, identifier-flow networks and client-side supply-chain exposure, as a pre-enforcement DPDP baseline.**

### Why this is defensible

- **Timing is unique and time-bound.**
  - The DPDP Rules were notified on 13 Nov 2025. The consent-manager provisions land around Nov 2026, and the core obligations around 13 May 2027.
  - A rigorous measurement taken **now** is a baseline that nobody can take retroactively.
  - Our open tool lets anyone (including us) re-run it after enforcement for a before/after comparison.
- **No peer-reviewed study** (as far as our search found) measures *verified form-PII leakage*, *ID-flow structure* and *supply-chain exposure* together across Indian sectors.
  - Prior Indian work covers news-site tracking (2021) and government cookies (2022).
  - The industry reports cover consent banners only.

### Research questions (the paper is organised around these, not around the tool)

| RQ | Question | Why it is new |
|---|---|---|
| **RQ1 Coverage** | How much of the Indian third-party ecosystem do global tracker lists miss? | Tracker Radar has no India region. Unknown third parties are classified by hand, giving an **India tracker supplement** that we contribute upstream. |
| **RQ2 Leakage** | How often do Indian sites send form PII (email, and phone in +91 formats) to third parties **before submission**, to whom, and in which encodings, by sector? | Leaky Forms covered EU/US top sites, with no Indian sector stratification and no Indian phone formats. |
| **RQ3 Structure** | Which organisations are ID-flow hubs on the Indian web? Do communities reveal *cross-organisation* sharing beyond corporate ownership? | Directly tests Bashir & Wilson's negative result, with an entity layer and null models. |
| **RQ4 Supply chain** | How exposed are Indian login and payment pages to client-side supply-chain attack? This covers vulnerable libraries, missing SRI/CSP, dangling script domains (polyfill.io-style) and skimming-capable scripts. | Ties directly to PCI DSS 6.4.3/11.6.1 and the polyfill.io incident. |
| **RQ5 Readiness** | Before enforcement, what share of sites show readiness gaps? Examples: pre-consent tracking, undisclosed processors, tracking on child-directed ed-tech pages (S.9(3)). | Framed as *readiness gaps*, never as violations. |

## B3. Point-by-point response to the panel

| Panel issue | Our upgrade | Built on |
|---|---|---|
| A1.1 Leak detection exists | Re-implement Leaky Forms' method: precomputed 3-layer encoding and hash pool, Aho-Corasick search. **Contributions:** Indian phone formats, sector stratification, a **cross-tool agreement** check against Blacklight-collector on the same sites. | leaky-forms/leaky-forms (method), the-markup/blacklight-collector (baseline) |
| A1.2 Graph with Louvain exists | Keep the graph as *infrastructure for RQ3*. Add an entity layer, directed edges and edge confidence learned from labels. Run communities on the **aggregated corpus graph** with null models, and test explicitly against the ownership partition. | Bashir & Wilson 2018 (hypothesis), WebGraph (edge semantics) |
| A1.3 Scores criticised | A transparent scorecard with **uncertainty bands** from a JRC-style sensitivity analysis. Every point traces to evidence. | OECD/JRC Handbook, optbinning |
| A1.4 Not the first Indian study | Cite Agarwal 2021, Götze 2022, Arrka and ComplyZero, and position against them (B2). | — |
| A1.5 "Collusion" | Renamed to *identifier-flow network*. Organisation names are published with neutral language and a right of reply. | — |
| A2.1 Server-side blind spot | Report a **lower bound** explicitly. Detect proxy signals: CNAME-cloaked first-party subdomains, sGTM/first-party `/collect`-style endpoints, and first-party cookies later seen in third-party requests. Quantify "invisible share" as a limitation metric. | AdguardTeam/cname-trackers, Dimova et al. PETS 2021 |
| A2.2 No ID definition | **Englehardt & Narayanan's criteria:** two synchronised fresh profiles plus a revisit; value constant within a profile and different across profiles; Ratcliff-Obershelp similarity < 0.66; length 8–100; expiry > 90 days. Sensitivity variants: Acar's 30-day cut-off and Fouad's no-expiry rule. We also search **POST bodies**, which Fouad 2020 did not. | Englehardt 2016 §4, Acar 2014, Fouad 2020 |
| A2.3 Per-site Louvain | **Leiden**, not Louvain, with 100 seeds and a consensus matrix. Report mean ARI/NMI across seeds, and modularity Q as a z-score against 1,000 degree-preserving rewired null graphs. Per-site graphs under ~15 nodes get only descriptive stats. | leidenalg, cdlib, Traag 2019, Guimerà 2004 |
| A2.4 Same company ≠ collusion | Merge DDG entities, Disconnect entities and Ghostery TrackerDB. Label every edge `intra_entity` or `cross_entity`; headlines use cross-entity only. | duckduckgo/tracker-radar, ghostery/trackerdb |
| A2.5 Representativeness | **Primary configuration is mobile** (Android Chrome emulation), matching India's 64.5% mobile share. A desktop ablation runs on a subset. Headful Chromium under Xvfb. Landing page plus 4 same-site subpages, with scrolling. Indian vantage points. A 200-site subset is crawled 3 times for stability (Jaccard, ICC). | Demir 2022 criteria C1–C18, Urban 2020, Jueckstock 2021 |
| A2.6 Banking = homepages | Label honestly as "public-facing pages". Add **page-type stratification** (landing / login / payment / form pages found by link classification) so the claims are about page types, not the institutions' full risk. | Leaky Forms' sign-in/register link heuristic |
| A2.7 Sector attrition | Detect bot walls (Cloudflare/Akamai challenges, CAPTCHA pages, 403s). Report **block rate by sector**. Sensitivity analysis on non-blocked sites only. No CAPTCHA solving, and stealth only as a disclosed ablation. | Gundelach 2026 **(verify)**, Jonker 2019 |
| A2.8 Canary failure modes | Canaries use a **domain we own**: `tm-<siteid>-<rand>@ourdomain`. Mail received there is independent ground truth. Phones come from team-owned numbers, with attribution by crawl-time separation. **Never** Aadhaar/PAN-format values. Validation-aware typing (realistic formats, key delays, Tab to fire blur). Pre-submit = any request after input/blur with no submit event ever fired. | Leaky Forms field filling, Fathom email classifier |
| A2.9 Capability ≠ behaviour | Two tiers: *capability* flags (reads form fields, no SRI) vs *behavioural proof* (canary exfiltrated). Only the behavioural tier feeds "verified" findings. Add **dangling-script-domain** detection (NXDOMAIN / expired registration of script hosts, with no registration by us). | retire.js, OSV.dev API, csp-evaluator checks |
| A2.10 Western list bias | Match against EasyList **IndianList** too. Measure **list coverage**: the share of third-party eTLD+1s absent from all lists, hand-classified by two coders (κ reported). The resulting **India tracker supplement** is released and submitted upstream as PRs. | easylist IndianList, DDG TDS |
| A3.1 No target variable | ML only where **real labels** exist: (1) **edge-confidence model**, a calibrated logistic regression on ~300 hand-labelled candidate ID-sharing edges; (2) **leak-risk model**, an Explainable Boosting Machine predicting *canary-verified* leakage from passive features, so sites without testable forms still get an evidence-based leak-risk estimate; (3) **form-field classifier** (email/phone/name) vs a `type=` baseline. | InterpretML EBM, sklearn calibration |
| A3.2 False precision | Show the score with an interval (e.g., **62 [55–68]**) from Monte Carlo over weights, normalisations and aggregations. Subscores are shown separately, and privacy and security are **never** merged without showing both. | OECD/JRC sensitivity analysis, Paruolo 2013 |
| A3.3 Decorative ML | Each model has a labelled dataset, a baseline, a metric and a calibration plot (B6). | — |
| A3.4 Gameable | Server-side and cloaking signals *raise* risk rather than hide it. Document the gaming limits. | Vansteenhuyse 2025 |
| A4.1 Circular precision/recall | Positive controls (testbed covering every encoding). **Negative controls** (a crawl with a different canary: expect 0 hits). **Independent confirmation** (mail received at the canary domain). **Cross-tool** agreement with Blacklight-collector on 100 sites. | Leaky Forms FN analysis |
| A4.2 OpenWPM benchmark | Dropped as a detector benchmark. The baselines become: (a) list-only detection vs TraceMap (the coverage gain from IndianList, CNAME and supplement); (b) Blacklight-collector for leak and key-logging agreement; (c) DDG's published test pages for instrumentation recall. | duckduckgo/privacy-test-pages, OpenWPM test_pages |
| A4.3 Modularity ≠ validation | Null-model z-score; NMI against the **ownership partition**. If NMI ≈ 1 we **report the null result**, and that is a finding. Manual review of 30 cross-entity edges against published sync endpoints. | — |
| A4.4 Statistics | ~300 sites per sector. Kruskal-Wallis, then Dunn with Holm correction. ε² and Cliff's δ effect sizes. BCa bootstrap CIs. **Negative binomial GLM** of tracker count ~ sector + log(popularity bucket). Logistic regression / Fisher's exact test for leak prevalence. | Tomczak 2014, Romano 2006 |
| A4.5 Reproducibility | Pin list versions (hash + date), pin the PSL snapshot. Store HAR plus CDP raw logs and content-addressed script bodies. Publish the corpus snapshot with its date, config and versions per Demir's C1–C18. | Playwright HAR |
| A5.1 No user | Concrete users and outputs (B7). | — |
| A5.2 DPDP premature | "Readiness gap" language only, with an explicit not-legal-advice note. The baseline framing *uses* the timing instead of misusing it. | DPDP Rules 2025 phased timeline |
| A6.1 Ethics | Institutional ethics sign-off before the full crawl. Protocol in B8. | Menlo Report, Leaky Forms ethics section |
| A6.2 Dual-use demo | Removed from the public repo and product. Kept only as a local, consented classroom demo. | — |
| A6.3 Licensing | TraceMap code under Apache-2.0: we *re-implement* methods and do not copy GPL code. Data derived from CC BY-NC-SA lists is released under the same licence with attribution. | — |
| A7.1 Over-scoped | Cut the React SPA (a static HTML report plus Cytoscape.js is enough), the OpenWPM benchmark and the attacker demo tab. Add a pilot crawl. | — |
| A7.2 Single point of failure | Ownership rebalanced (B9); hand-labelling is shared work. | — |
| A7.3 Threat model late | Threat model written in week 1; it defines which detectors exist. | — |

## B4. Stand on shoulders: the reuse stack (all verified to exist on 30 Sep 2026)

| Need | Adopt | License | How |
|---|---|---|---|
| Crawler | Playwright Python with **raw CDP sessions** (`Network.requestWillBeSent` initiators and postData, `Debugger.scriptParsed`), plus HAR | Apache-2.0 | Our core; no Node dependency |
| API instrumentation | Python port of the breakpoint list from **duckduckgo/tracker-radar-collector**, plus the OpenWPM / FP-Inspector fingerprinting API lists | Apache-2.0 / MIT (re-implemented, not copied, from GPL) | Fingerprinting and storage access with call stacks |
| Consent modes | **duckduckgo/autoconsent** (`autoconsent.playwright.js`) | MPL-2.0 | No-action / opt-in / opt-out crawls |
| Tracker classification | **DDG TDS + Tracker Radar entities**, Disconnect, **Ghostery TrackerDB** | CC BY-NC-SA 4.0 | Category and owner; entity layer for the graph |
| URL rule matching | EasyPrivacy + EasyList + **IndianList** via `braveblock`/`adblock` (adblock-rust) | GPL/CC BY-SA lists; MIT bindings | Fast, resource-type-aware matching |
| eTLD+1 | `tldextract` with a pinned PSL | BSD-3 | First- vs third-party |
| CNAME cloaking | **AdguardTeam/cname-trackers** plus DNS resolution | MIT | Server-side / cloaking signal |
| Vulnerable JS | **RetireJS** `jsrepository.json` plus the **OSV.dev** REST API | Apache-2.0 | Library/version → CVE and severity |
| Tech fingerprints | enthec/webappanalyzer | GPL-3.0 (data only) | Identify tag managers and frameworks |
| Obfuscation | tree-sitter-javascript, jsbeautifier, entropy features | MIT | Interpretable obfuscation features |
| Leak search | Leaky Forms method (3-layer encodings/hashes), `pyahocorasick` | our implementation | O(traffic) canary search |
| Communities | NetworkX (build), **leidenalg**, **cdlib** (NMI/ARI/stability) | BSD / GPL / BSD | Research-grade community analysis |
| Interpretable models | **InterpretML EBM**, sklearn calibrated LR, **optbinning** scorecard | MIT / BSD / Apache | Glass-box models plus a points-based score |
| Corpus | **zakird/crux-top-lists** `data/country/in` (monthly, bucketed ranks), Tranco, IGOD (gov), RBI bank lists | — | Stratified by popularity bucket and sector |
| Ground-truth testbeds | **duckduckgo/privacy-test-pages**, OpenWPM `test/test_pages`, our own FastAPI testbed | Apache / GPL (used, not shipped) | Positive controls for every detector |
| Baseline | **the-markup/blacklight-collector** | GPL-3.0 (run as an external tool) | Cross-tool agreement |

Environment note: on Python 3.11, networkx 3.7 and shap 0.52 won't install. **Use Python 3.12** (or pin `networkx<3.7`, `shap<0.52`).

## B5. Revised methodology (summary)

1. **Crawl protocol, per site:**
   - Profiles A and B start fresh at the same time from two Indian vantage points (team connections). Profile A revisits after ~30 minutes.
   - Each visit covers the landing page plus 4 same-site subpages, scrolls, and dwells for a fixed time.
   - Primary configuration is mobile emulation.
   - Consent mode: no action by default. When a banner is detected, add opt-in and opt-out crawls.
   - Captured: HAR, CDP logs, API-call traces with stacks, cookies with setter attribution, storage and a screenshot.
   - Bot walls are recorded, never bypassed.
2. **ID-flow edges:**
   - Candidate values from cookies, storage, URLs, the Referer, Location headers and POST bodies. We decode URL encoding, base64 and JSON, and split on delimiters.
   - Englehardt's ID criteria. Directed sender → receiver edges tagged with channel.
   - `intra_entity` / `cross_entity` tag. Confidence comes from the calibrated edge model.
3. **Leaks:**
   - An ML/heuristic field finder, including inside iframes, and a link finder for sign-in/register pages (≤10 links).
   - Canary typing without ever submitting.
   - Search against a precomputed 3-layer encoding/hash pool.
   - Every leak carries `before_submit`, channel, recipient entity and evidence (request ID).
4. **Supply chain:**
   - Script inventory per page type.
   - SRI presence, CSP evaluation, retire.js/OSV vulnerabilities, dangling script domains.
   - Two tiers: capability and verified behaviour.
   - Script-inventory diff between crawls (an 11.6.1-style change signal).
5. **Graph analysis:**
   - Per-site graphs for explanation.
   - The aggregated corpus graph for RQ3: Leiden, consensus clustering, null models, bootstrapped centrality, NMI against ownership.
6. **Score:**
   - Four subscores (tracking, ID-flow, verified leakage, supply chain), each a monotone points table.
   - Total shown with a sensitivity interval, plus reason codes that link to raw evidence.

## B6. Evaluation protocol

| Component | Ground truth | Metric | Pass bar |
|---|---|---|---|
| Instrumentation | DDG privacy-test-pages, OpenWPM test pages, our testbed | Recall per API/channel | ≥ 0.95 on the testbed |
| Third-party classification | 2-coder hand labels on 300 unknown domains | Coverage gain vs list-only; Cohen's κ | κ ≥ 0.7 |
| ID-edge detection | ~300 hand-labelled candidate edges (2 coders) | Precision/recall, Brier score, reliability diagram | κ ≥ 0.7; report as measured |
| Communities | Ownership partition, rewired nulls | Q z-score, NMI vs ownership, seed ARI | Any outcome reported, including a null |
| Leak tracer | Testbed (+), negative-canary crawls (−), mail received, Blacklight-collector | Precision/recall, FP rate on negatives, cross-tool agreement | 0 negative-control hits |
| Fingerprinting flags | 200 hand-labelled scripts, FP-Inspector domains | Precision/recall | Report |
| Leak-risk EBM | Canary-verified leak labels | Site-grouped CV AUC with CI, calibration | Beats the tracker-count baseline |
| Score | Expert ranking of 30 sites (3 raters), test-retest crawls, convergent measures | Krippendorff's α, Kendall's τ, ICC, rank shift under weight perturbation | α ≥ 0.667 among raters |
| Sector stats | — | NB-GLM coefficients, ε², Cliff's δ, BCa CIs, Holm-adjusted p-values | Effect sizes reported, not just p |

## B7. Real-world use: who uses it, and what they get

| User | Output | Hook |
|---|---|---|
| **E-commerce / payment-page owners and PCI QSAs** | Payment-page **script inventory** with SRI/CSP status, and a **diff mode** (`tracemap diff`, runnable in CI or cron) that flags new or changed scripts | PCI DSS 6.4.3 / 11.6.1 (mandatory since 31 Mar 2025). The SAQ A iframe-merchant "not susceptible to script attacks" criterion. The polyfill.io incident (>100K sites). |
| **DPOs / privacy teams (pre-May 2027)** | A **DPDP readiness report**: pre-consent trackers, third-party recipients (processor inventory), form-PII sent before submit, trackers on child-directed pages | DPDP S.5/6/8(2)/9(3). Readiness-gap language only. |
| **CERT-In empanelled auditors, RBI/SEBI IT audit** | Client-side supply-chain section: vulnerable libraries with CVEs, dangling domains, third-party script dependencies | RBI IT Governance Master Direction (third-party risk), CERT-In audit guidelines (July 2025). This is our inference; neither names third-party JS explicitly. |
| **Journalists / civil society** | An **evidence bundle** per finding: HAR, screenshot, the exact request, timestamp, and a SHA-256 manifest of all artefacts | The Markup's Pixel Hunt model, which led to FTC GoodRx and BetterHelp actions |
| **Researchers / list maintainers** | Open dataset, **India tracker supplement** (upstream PRs to IndianList / DDG), reproducible crawler | Measurable impact: merged PRs |

**Responsible disclosure:**
- Verified leaks and critical supply-chain findings go to the site owner, and for government or critical sites to **CERT-In**, before publication.
- 45-day embargo.
- Organisations get a right of reply.

## B8. Ethics and legal protocol

- Institutional ethics committee approval before the full crawl. Faculty or legal-cell sign-off on IT Act §43/§66 exposure; our position is that we crawl public pages passively and **never submit** forms.
- One concurrent visit per site; polite delays; a project info page linked from the crawler's contact line.
- **Never:** submit forms, type into password fields, solve CAPTCHAs, create accounts, cross login walls, or register dangling domains.
- Canaries are synthetic and use a team-owned domain and numbers. **No government-ID-format values.**
- The DPDP Act S.17(2) research exemption is noted, but no real personal data is processed anyway.
- The consented demonstrator stays out of the public repo.

## B9. Revised scope, phases, ownership

**Cut:** React SPA (replaced by a static report with Cytoscape.js), OpenWPM benchmark, attacker-demo tab, deep "ML for the score".
**Added:** pilot crawl, testbed, entity layer, India supplement, CNAME/dangling-domain checks, diff mode, disclosure.

| Wk | Phase | Deliverable |
|---|---|---|
| 1–2 | P1 Foundations | Threat model; contracts (v1, incl. `post_data`, `js_calls`, `profile_id`, `page_type`); CDP crawler with A/B/revisit profiles, mobile emulation and autoconsent; HAR plus raw store; testbed plus CI tests |
| 3–4 | P2 Detect + corpus | Lists, entity merge, CNAME, IndianList matcher; fingerprinting/supply-chain detectors; **corpus curation** (CrUX-IN + IGOD + RBI lists; 2-coder sector labels) |
| 3–6 | P3 Leak tracer (parallel) | Field finder, canary typing, 3-layer pool search, negative controls, mail-sink verification |
| 5–7 | P4 ID-flow graph | Edge extraction, hand-labelling round, calibrated edge model, per-site graph |
| 7 | **Pilot** | 100-site pilot → fix block/timeout/coverage issues; ethics approval in hand |
| 8–9 | P5 Wave-1 crawl | ~1,500 sites (5 sectors × ~300); stability subset of 200 × 3 repeats; Blacklight cross-run on 100 sites |
| 9–10 | P6 Analysis | Corpus graph + Leiden + nulls; score + sensitivity; EBM; sector stats; expert ranking |
| 10–12 | P7 Deliver | Static report UI + API; evidence bundles; dataset + supplement release; disclosures sent; paper |

**Crawl budget:**
- Per site: 3 visits × 5 pages × ~15 s ≈ 4 min.
- For 1,500 sites that is ≈ 100 worker-hours, or **~25 h with 4 parallel workers** (different sites, one visit per site at a time).
- Leak tests add ~1–2 min on sites with forms.

| Member | Owns |
|---|---|
| Kavya | Crawler, consent modes, subpage selection, vantage points, testbed, pilot/wave operations |
| Nityavardhan | Threat model, classification + entity layer + India supplement, CNAME, fingerprinting, supply-chain detectors |
| Kartik | Leak tracer, mail-sink verification, evidence bundles, API/CLI/report, disclosure process |
| Krati | ID-flow graph + edge model, corpus-graph community analysis, score + sensitivity, sector statistics |
| All | Corpus sector labelling, edge/script/domain hand labelling (2 coders each), expert ranking, paper |

## B10. Limitations we will state up front

- Client-side only: a **lower bound** on data flows. Server-to-server sharing and native apps are invisible.
- Public-facing pages only; nothing behind authentication.
- One country, one time window. Wave 2 (post-May 2027) may fall after the degree timeline.
- Edges are evidence with calibrated confidence, not proof of intent.
- The score is a summary for communication; the evidence and subscores are the product.

## B11. Viva cheat-sheet

- **"Blacklight already does this."** Blacklight is a single-page journalist tool with fixed tests. We re-implement the Leaky Forms method, add Indian phone formats and page-type stratification, run a sector-stratified Indian study, and report *agreement with Blacklight* as validation.
- **"Louvain was shown not to work (Bashir & Wilson 2018)."** Correct. We test that hypothesis on the Indian web with Leiden, null models and an ownership partition, and report whatever we find.
- **"Where's the ML?"** Three models with real labels: edge confidence (hand-labelled), leak risk (canary-verified), and form fields (hand-labelled). Each has a baseline and a calibration plot. The score itself is deliberately a transparent scorecard.
- **"Who uses it?"** PCI 6.4.3/11.6.1 script inventory and diff for merchants; DPDP readiness reports for DPOs; evidence bundles for journalists; the dataset and supplement for researchers.
- **"Isn't DPDP not in force yet?"** Exactly. That's why a baseline taken now is valuable and cannot be reconstructed later.
- **"Server-side tracking makes this obsolete."** It makes it a lower bound, which we state. We also detect the visible fingerprints of server-side setups (CNAME cloaking, first-party collectors).

---

## Key sources

**Prior art**
- Blacklight: github.com/the-markup/blacklight-collector
- Leaky Forms (USENIX Security 2022): usenix.org/system/files/sec22-senol.pdf · github.com/leaky-forms/leaky-forms
- Englehardt & Narayanan (CCS 2016): cs.princeton.edu/~arvindn/publications/OpenWPM_1_million_site_tracking_measurement.pdf
- Acar et al. (CCS 2014): "The Web Never Forgets"
- Papadopoulos et al. (WWW 2019): arxiv.org/abs/1805.10505
- Fouad et al. (PoPETs 2020): "Missed by Filter Lists"
- Bashir & Wilson (PETS 2018): "Diffusion of User Tracking Data"
- Kalavri et al. (PAM 2016)
- Solomos et al. (TMA 2020)
- WebGraph (USENIX Security 2022): github.com/spring-epfl/WebGraph
- PrivacyScore: arxiv.org/abs/1705.05139
- Vansteenhuyse et al. 2025: "One Does Not Simply Score a Website"

**Indian studies**
- Agarwal/Vekaria et al. (ICWSM 2021): arxiv.org/abs/2102.03656
- Götze et al. (WebSci 2022): dl.acm.org/doi/10.1145/3501247.3531545
- ComplyZero 2026 **(verify)**
- Arrka 2022

**Methodology**
- Demir et al. (WWW 2022)
- Jueckstock et al. (WWW 2021)
- Urban et al. (WWW 2020)
- Aqeel et al. (IMC 2020)
- Zeber et al. (WWW 2020)
- Traag et al. 2019 (Leiden)
- Fortunato & Barthélemy 2007
- Guimerà et al. 2004
- OECD/JRC Handbook on Composite Indicators (2008)
- Dimova et al. (PETS 2021, CNAME cloaking)
- Böttger et al. arXiv 2606.16720 **(verify)**
- Gundelach et al. arXiv 2606.14525 **(verify)**

**Regulation and context**
- DPDP Rules 2025 (PIB, 13 Nov 2025)
- PCI SSC on 6.4.3/11.6.1 (effective 31 Mar 2025) and the SAQ A update (Jan 2025)
- Sansec on polyfill.io (2024)
- The Markup Pixel Hunt (2022)
- FTC GoodRx and BetterHelp (2023)
- StatCounter India (2026)
- Google Privacy Sandbox update (17 Oct 2025)

**Data**
- zakird/crux-top-lists (`data/country/in`)
- duckduckgo/tracker-radar (no IN region)
- AdguardTeam/cname-trackers
- RetireJS/retire.js
- duckduckgo/autoconsent
- duckduckgo/privacy-test-pages
