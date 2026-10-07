# Keep the Python crawler, borrow everything else

No open-source project already does most of TraceMap. Nearly every *component* does exist, though, and most of it can be reused legally. The closest single tools are The Markup's blacklight-collector (GPL-3.0) and DuckDuckGo's tracker-radar-collector (TRC, Apache-2.0). Each covers roughly the crawl-and-detect front half. Neither has A/B/revisit identifier-flow analysis, autoconsent plus canary typing in one run, a score, or an Indian corpus. The recommended build is therefore **wrap and port, not fork**. Keep the Python-Playwright crawler the team has already proven on this Windows machine, which already captures the two things TRC lacks (initiator stacks and POST bodies). Copy TRC's Apache-licensed API-breakpoint list and consent-handling logic into it with attribution. Vendor DuckDuckGo's autoconsent bundle unmodified. Pull detection data (DDG TDS, Tracker Radar, Disconnect, Ghostery TrackerDB, EasyPrivacy, IndianList, AdGuard CNAME lists, retire.js) at runtime. Call two small Node tools (MDN HTTP Observatory, csp_evaluator) as subprocesses. Build the analysis on permissively licensed Python libraries: adblock, networkx 3.6.1, graspologic-native, interpret, SALib and statsmodels. Licensing has three traps: tracker-entity data is non-commercial share-alike; the obvious Leiden library (leidenalg) is GPL; and the two best leak-detection codebases are GPL or unlicensed, so they must be reimplemented, not copied. Stay on Python 3.11. The fallback, if the Python consent/API tracer misses its week-2 gate, is to run TRC unmodified as a subprocess sidecar for those two collectors only. The genuinely new work is the integration, the Indian data, +91 phone canaries, the leak replay timeline, and the research questions. That is where the team's time should go.

## No single project does TraceMap, but 20 of its 22 parts already exist

The team's instinct that "there must be something on GitHub" is half right. Researchers cloned and inspected every plausible end-to-end candidate. **None combines mobile Chromium crawling with multi-profile revisits, cookie-banner modes, JS API instrumentation, an identifier-flow graph, canary form-leak testing, an interpretable score and an India focus.** The closest matches each cover two to four stages ([OpenWPM](https://github.com/openwpm/OpenWPM); [consentcrawl](https://github.com/dumkydewilde/consentcrawl); [Vettam scanner](https://github.com/Vettam/dpdp-cookie-scanner)).

**Blacklight-collector** is the strongest overlap. It samples 3 same-site pages with autoscroll, emulates an iPhone 13 Mini by default, fills forms with known values without submitting, and searches POST bodies for those values in plain, base64 and hashed forms. It has no consent handling, its subpage sample is random, and it is GPL-3.0 ([README](https://github.com/the-markup/blacklight-collector/blob/main/README.md); [key-logging.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/inspectors/key-logging.ts)). **TRC** is the cleanest base: Apache-2.0, maintained by DuckDuckGo with commits through 6 October 2026, mobile emulation, autoconsent in optIn/optOut modes, and about 150 breakpointed JS APIs attributed to the calling script. It still lacks POST bodies, cookie values, subpages, multi-profile runs and form filling ([TRC repo](https://github.com/duckduckgo/tracker-radar-collector); [RequestCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/RequestCollector.js)).

**Leaky Forms** is the methodological ancestor of the leak tracer. Its USENIX 2022 study found email exfiltration before submission on 1,844 EU and 2,950 US sites ([USENIX](https://www.usenix.org/conference/usenixsecurity22/presentation/senol)). But its crawler is a 2022-era TRC fork on Puppeteer 10 with a GPL LICENSE file ([package.json](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/package.json)), and its Python leak detector has no license at all ([leaky-forms](https://github.com/leaky-forms/leaky-forms)). The only Indian tool, **Vettam's dpdp-cookie-scanner**, is a single-URL compliance CLI. It maps observations to DPDP provisions with certainty tiers and explicitly has "no severity field". It has no form-leak test and no ID-sharing graph ([README](https://github.com/Vettam/dpdp-cookie-scanner)).

Of the 22 capabilities in the table below, only two have no prior art the researchers could find: bot-wall detection and the leak replay timeline. The other 20 exist as code, data or a published method. What TraceMap adds to them is mostly parameters, glue and Indian data.

| Capability | Best existing source | What TraceMap reuses | What is genuinely new |
|---|---|---|---|
| Mobile Chromium crawl with initiator stacks and POST bodies | TRC (no POST), Blacklight (HAR, GPL), WEC (no mobile) | Nothing to fork; the team's probe already does this | Nothing; this is plumbing |
| Cookie-banner modes none/optIn/optOut | DDG autoconsent, wired in TRC's CookiePopupsCollector | Vendored bundle + TRC logic (Apache) | Nothing |
| JS API calls with calling script | TRC `breakpoints.js` (Apache), OpenWPM, Blacklight (GPL) | TRC's API list, copied with NOTICE | Nothing |
| Landing + 4 subpages + scroll | Blacklight (3 random pages), WEC `--max/--depth` | Ideas only | Deterministic page choice so A and B see the same pages |
| Two fresh profiles + revisit | priv-accept (fresh → accept → revisit) | Idea only | The A/B/A2 design tied to ID detection |
| Third-party classification | DDG TDS, Tracker Radar, Disconnect, TrackerDB, third-party-web, EasyPrivacy, IndianList | Runtime data + `adblock` | India entity supplement |
| CNAME cloaking | AdGuard cname-trackers, TDS `cnames` | Data + dnspython | Nothing |
| Fingerprinting flags | Englehardt & Narayanan 2016 rules, DDG API weights | Reimplemented rules | Nothing |
| Session-replay vendors | TDS "Session Replay", Blacklight list, Princeton list | Union of lists | Small behavioural layer |
| Vulnerable JS libraries | retire.js repository + OSV.dev | Data + API | Nothing |
| CSP / SRI | MDN HTTP Observatory, csp_evaluator | Subprocess | SRI checked on login/payment pages from crawl data |
| Bot-wall detection | None of the crawlers (TRC only *evades*) | Nothing | Small, new |
| ID-cookie (cookie-sync) detection | E&N 2016 spec; vibhor98 MIT scripts | Clean rewrite to the paper's parameters | POST-body channel, entity tagging |
| Communities and centrality | networkx, graspologic-native, cdlib | Libraries | Testing Bashir & Wilson's result on Indian data (research, not code) |
| Canary leak detection | Leaky Forms method (unlicensed), Blacklight (GPL) | Clean-room reimplementation | +91 phone formats; channels beyond POST |
| Scorecard + sensitivity + EBM | SALib, interpret, optbinning | Libraries | The score design itself |
| DPDP readiness framing | Vettam (code Apache, text CC BY-ND) | Ideas | Readiness-gap language for Indian sectors |
| Corpus | CrUX India via zakird/crux-top-lists | Data | Sector labels |
| Live progress | FastAPI built-in SSE | Library | Nothing |
| Graph view | Cytoscape.js + fCoSE | Library | Owner-compound nodes, dashed low-confidence edges |
| Leak replay timeline | None found | Nothing | New screen |
| Evidence bundle | bagit-python; WEC/Lighthouse report patterns | Library + design | Packaging |

The table supports the panel-era repositioning. The defensible novelty is not any detector. It is the combination, applied to a sector-stratified Indian corpus, and the data products that come out of it. On that point, **DuckDuckGo's Tracker Radar crawls only AU, CA, CH, DE, FR, GB, NL, NO and US, with no India region** ([tracker-radar/domains](https://github.com/duckduckgo/tracker-radar/tree/main/domains)). **third-party-web's 2,143 entities omit MoEngage, Netcore, Razorpay, Paytm, Juspay and Times Internet's Colombia** ([entities.json](https://unpkg.com/third-party-web@latest/dist/entities.json)). Ghostery TrackerDB lists only seven organisations with country IN ([trackerdb.json](https://github.com/ghostery/trackerdb/releases/download/202610011537/trackerdb.json)). The 2025 Web Almanac privacy chapter has no India analysis ([Web Almanac 2025](https://almanac.httparchive.org/en/2025/privacy)).

## Port tracker-radar-collector's ideas into Python instead of forking it

The researchers disagreed on this question. The Node-crawler researcher recommended forking TRC as a subprocess sidecar. They estimated 800–1,200 net-new JS lines on top of its roughly 4,600-line core. The Python-scanner researcher recommended building on Playwright directly and porting TRC's ideas. Both positions are reasonable in general. For *this* team, the Python route wins clearly. The reason is not language preference. It is that **TRC is missing, or actively discards, the exact data TraceMap's novel stages depend on.**

### Three gaps in TRC's data would have to be rebuilt

TRC's CookieCollector calls `Network.getAllCookies` and then outputs only name, domain, path, expires, session and sameSite. **It drops the cookie value, httpOnly, secure and size** ([CookieCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/CookieCollector.js)). Englehardt-style ID detection is impossible without values. Its RequestCollector typedef has **no postData and no request headers**, and it flattens the CDP initiator into a de-duplicated set of script URLs, dropping function names and line numbers ([RequestCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/RequestCollector.js); [initiators.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/helpers/initiators.js)). Both the leak tracer and the ID-flow edges need those fields. Each crawl also uses a fresh temp profile that is deleted on close ([LocalChrome.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/browser/LocalChrome.js)), and there is no subpage loop: one navigation, a 2.5 s wait, then `getData()` ([crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js)).

A TRC fork would therefore need a rewritten request collector, a rewritten cookie and storage collector, a new subpage driver, a profile-owning wrapper, a leak collector and a bot-wall collector. That is most of the crawler. What would survive is the autoconsent wiring, mobile emulation and the API tracer. Whether TRC's collectors behave correctly across multiple navigations in one `crawler()` call is untested; the Node researcher flagged it as needing a spike ([crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js)).

### The Python probe already has what TRC lacks

On this machine, Python Playwright 1.63 driving installed Chrome over a raw CDP session already captures initiator stacks and POST bodies, and `*.localhost` subdomains resolve for a multi-domain testbed. The existing Pydantic contracts already model `post_data`, an `Initiator` with stack URLs, `page_index`, and per-profile `Visit`s ("A", "B", "A2", "L"). `pyproject.toml` already reserves `crawl/vendor/autoconsent/*` as package data. TRC's genuinely hard-won assets are its ~650-line API breakpoint list and its ~671-line consent collector. Both are Apache-2.0, so they **can be copied or translated into an Apache-2.0 Python codebase as long as the LICENSE/NOTICE text is kept and changes are marked** ([LICENSE](https://github.com/duckduckgo/tracker-radar-collector/blob/main/LICENSE)). "Port the ideas" here can legally mean "port the code".

| Criterion (for this team) | Fork TRC, run as Node subprocess | Python Playwright + ported TRC pieces |
|---|---|---|
| Language fit | Three of four owners work in Python; a 4,600-line JS core to learn | One language from capture to UI backend |
| Proven on this Windows machine | Not run; `npm i` downloads Chrome for Testing (needs approval; may hit the same "side-by-side" failure Playwright's Chromium hit) | Already proven with installed Chrome |
| POST bodies, full initiator stacks | Must be added | Already captured |
| Cookie values for ID detection | Must rewrite the collector | `Network.getAllCookies` in Python, nothing dropped |
| A/B/revisit | Wrapper must launch and own browsers via `browserConnection` | Persistent context per profile directory, natively |
| Subpages | Unproven multi-navigation lifecycle | Plain loop in Python |
| Canary typing with `before_submit` timing | Separate collector; timing reconstructed after the fact | Same event loop as capture; exact timestamps |
| Live progress to FastAPI SSE | Needs a stdout event protocol plus a parser | Events pushed straight into an asyncio queue |
| Consent modes | Already integrated (strongest TRC asset) | Must translate TRC's CookiePopupsCollector logic; 1–2 day risk |
| JS API tracing | Already integrated; CDP Debugger breakpoints, invisible to page JS but heavier ([TrackerTracker.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/TrackerTracker.js)) | Init-script wrappers using TRC's API list; simpler, but detectable by page scripts |
| Upstream maintenance | No releases, version fixed at 1.0.0; pin a commit and merge by hand | Only the autoconsent bundle tracks upstream |
| Data contract | JSDoc typedefs only; Pydantic mirrors to maintain ([README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md)) | Existing Pydantic contracts are the source of truth |

The Python route loses on exactly two rows: consent handling and API tracing. Those are bounded, testable ports of Apache code. The TRC route loses on the rows that carry TraceMap's research contribution: values, POST bodies, profiles, subpages, canary timing and live progress.

**Decision:** keep the Python-Playwright crawler as the only production crawler. For API tracing, start with an init-script that wraps the APIs in TRC's breakpoint list and records `new Error().stack` per call (the OpenWPM/Blacklight approach, reimplemented). Add the three breakpoints TRC lacks, `HTMLInputElement.value` reads, keyboard/input `addEventListener` and `Storage.setItem` ([breakpoints.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/breakpoints.js)), because the leak and keylogger detectors need them. Disclose in the methods that wrappers are page-detectable, and treat CDP Debugger breakpoints as a second-half upgrade.

### Fallback gate at the end of week 2

The trade-off is real. If the team gets the autoconsent translation or the API hooks wrong, it loses the two features TRC gives for free. Make the fallback cheap and pre-tested. In week 1, Kavya spends half a day running TRC unmodified at a pinned commit against the `*.localhost` testbed, with mobile emulation and an opt-out consent action. That is the researchers' recommended 30-minute spike, which needs explicit approval for the npm Chrome download. Its JSON then becomes an **instrumentation oracle**: Python's API log must find at least what TRC finds on the testbed.

At the end of week 2 there are two checks. First, opt-in and opt-out must succeed on the testbed's CMP pages. Second, the hooks' API recall must match TRC's. If either check fails, run TRC as a **sidecar for the `apis` and `cookiepopups` collectors only**, as a separate mobile visit per consent mode. Merge its per-script API counts by script URL, and keep everything else in Python. If TRC cannot launch on this machine either, consentcrawl's MIT `consent_managers.yml` selectors are a crude but working accept/reject clicker ([consentcrawl](https://github.com/dumkydewilde/consentcrawl)).

## A reuse-maximising architecture with one Python core and two thin Node helpers

The architecture follows from the licensing pattern the UI researcher noticed. **Measurement engines tend to be copyleft (GPL/AGPL/EUPL/MPL), while data-plumbing and visualisation libraries tend to be MIT/Apache.** So TraceMap owns its engine, takes libraries from the permissive group, takes data at runtime, and talks to anything copyleft only across a process boundary.

```
                         React + Vite UI (Cytoscape.js+fCoSE, Recharts later)
                                   │  REST + EventSource (SSE)
                         FastAPI ≥0.135 (fastapi.sse) ── SQLite (OpenWPM-style tables)
                                   │ asyncio queue of progress events
 ┌──────────────── tracemap.crawl (Python, Playwright → installed Chrome, raw CDP) ───────────┐
 │ profiles A, B (persistent dirs), A2 = reopen A, L = leak profile; mobile device emulation   │
 │ injected: vendor/autoconsent (MPL, unmodified) + instrument.js (API list ported from TRC)   │
 │ CDP: requestWillBeSent(initiator, postData), responseReceivedExtraInfo(Set-Cookie),         │
 │      getAllCookies(values), storage dump, script bodies (sha256)  → CrawlRecord JSON + HAR  │
 └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │ CrawlRecord (Pydantic)                              runtime-fetched data, hash+date pinned
 ┌───────┴─────── analysis packages (pure Python, Apache-2.0) ───────┐   data/lists/  (EasyPrivacy, EasyList,
 │ detect/  adblock engines per list, entity resolver, CNAME,        │   IndianList, AdGuard 3, AdGuard CNAME)
 │          E&N fingerprint rules, replay lists, retire.js + OSV     │   data/third_party/ (TDS, Tracker Radar,
 │ leak/    canary pool (3 layers), Aho-Corasick search              │   Disconnect, TrackerDB: CC BY-NC-SA)
 │ graph/   E&N ID extraction, networkx, graspologic-native Leiden   │   data/india/ (own supplement)
 │ score/   scorecard, SALib, interpret EBM                          │
 └───────────────────────────────────────────────────────────────────┘
   subprocess (files/JSON only): npx @mdn/mdn-http-observatory · node csp_eval.js
   optional, separate folders:   TRC (oracle/fallback, Apache) · blacklight-collector (GPL baseline)
```

Three design choices do most of the work. First, the **crawler emits facts and the analysis packages interpret them**. This copies Vettam's "observation vs interpretation" split ([Vettam README](https://github.com/Vettam/dpdp-cookie-scanner)) and lets Nityavardhan, Kartik and Krati develop against saved CrawlRecords without a browser. Second, the **storage tables mirror OpenWPM's decomposition** (`http_requests` with `post_body` and `req_call_stack`, `javascript` with symbol/operation/arguments, `javascript_cookies`, `crawl_history` for failure accounting). TraceMap adds `profile_id`, `page_type`, `banner_mode`, a `storage_item` table and leak/edge tables. The DDL is written fresh, since OpenWPM is GPL ([schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)). Third, **Node appears only as short-lived subprocesses with JSON in and out**. That fits Node 24.18 on this machine, which satisfies MDN Observatory's `node >=24` requirement ([package.json](https://github.com/mdn/mdn-http-observatory/blob/main/package.json)). Docker is not needed for the first half. OpenWPM, which "does not support windows", is not used at all ([OpenWPM README](https://github.com/openwpm/OpenWPM)).

Several verified details change the plan. The third-party-web JSON must come from npm/unpkg, because `dist/` is not committed to GitHub ([unpkg](https://unpkg.com/third-party-web@0.30.0/dist/entities.json)). The NextDNS CNAME list now returns 404, so AdGuard's MIT list is the CNAME ground truth: about 224,825 disguised hostnames mapped to 93 original trackers ([cname-trackers](https://github.com/AdguardTeam/cname-trackers/tree/master/data)). `adblock` returns the matched rule text when built in debug mode, while braveblock returns only a boolean. A local Windows/Python 3.11 test built an EasyPrivacy+EasyList+AdGuard+IndianList engine in 1.37 s and ran 20,000 checks in 0.065 s ([PyPI adblock](https://pypi.org/pypi/adblock/json)). Building **one engine per list** gives per-list explanation features. FastAPI's native `EventSourceResponse` exists only **from 0.135.0** ([FastAPI SSE](https://fastapi.tiangolo.com/tutorial/server-sent-events/)), so `pyproject.toml`'s `fastapi>=0.110` floor must be raised.

### Component-by-component adopt table

| Component | URL | License | Status (Oct 2026) | Reuse mode | Owner |
|---|---|---|---|---|---|
| Playwright (Python) + raw CDP | [docs](https://playwright.dev/python/docs/api/class-page#page-pdf) | Apache-2.0 | v1.63 proven locally with installed Chrome | Core dependency | Kavya |
| DDG autoconsent | [npm](https://www.npmjs.com/package/@duckduckgo/autoconsent) | MPL-2.0 | 16.47.0 published 2026-10-07 | Vendor bundle unmodified, inject | Kavya |
| DDG tracker-radar-collector | [repo](https://github.com/duckduckgo/tracker-radar-collector) | Apache-2.0 | Active, no releases | Copy API list + consent logic with NOTICE; oracle; fallback sidecar | Kavya |
| blacklight-collector | [repo](https://github.com/the-markup/blacklight-collector) | GPL-3.0 | v3.11.0, 2026-06-04 | Ideas (subpages, form values, keylogging); external baseline only | Kavya / Kartik |
| EDPS website-evidence-collector | [repo](https://code.europa.eu/EDPS/website-evidence-collector) | EUPL-1.2 | v4.5.0, 2026-09-30 | Ideas (first-party link queue, report sections) | Kavya / Kartik |
| consentcrawl CMP selectors | [repo](https://github.com/dumkydewilde/consentcrawl) | MIT | Alpha, pushed 2025-10 | Fallback clicker data | Kavya |
| adblock (python-adblock) | [PyPI](https://pypi.org/pypi/adblock/json) | MIT OR Apache-2.0 | 0.6.0; repo idle since 2023, works on 3.11 | Pinned dependency | Nityavardhan |
| EasyPrivacy / EasyList | [easyprivacy.txt](https://easylist.to/easylist/easyprivacy.txt) | GPL-3.0+ or CC BY-SA 3.0+ | Updated 2026-10-07 | Runtime fetch | Nityavardhan |
| IndianList | [repo](https://github.com/mediumkreation/IndianList) | EasyList licence | Active (ad-focused) | Runtime fetch | Nityavardhan |
| AdGuard Tracking Protection (filter 3) | [filter](https://filters.adtidy.org/extension/ublock/filters/3.txt) | GPL-3.0 (repo) | Active | Runtime fetch | Nityavardhan |
| DDG TDS v6 | [TDS](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json) | CC BY-NC-SA 4.0 | 1,001 trackers, 788 cnames | Runtime fetch, NC-SA folder | Nityavardhan |
| DDG Tracker Radar | [repo](https://github.com/duckduckgo/tracker-radar) | CC BY-NC-SA 4.0 | Active, no IN region | Runtime fetch (entities, API weights) | Nityavardhan |
| Ghostery TrackerDB | [releases](https://github.com/ghostery/trackerdb/releases/latest) | CC BY-NC-SA 4.0 | Release 202610011537 | Runtime fetch (org country) | Nityavardhan |
| Disconnect | [services.json](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json) | CC BY-NC-SA 4.0 | Active | Runtime fetch | Nityavardhan |
| third-party-web | [repo](https://github.com/patrickhulce/third-party-web) | MIT | 0.30.0, 2026-09-14 | Bundle | Nityavardhan |
| AdGuard cname-trackers | [repo](https://github.com/AdguardTeam/cname-trackers) | MIT | Active | Bundle | Nityavardhan |
| dnspython | [PyPI](https://pypi.org/pypi/dnspython/json) | ISC | 2.8.0 | Dependency | Nityavardhan |
| retire.js repository | [jsrepository-v4.json](https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository-v4.json) | Apache-2.0 | Active | Own Python matcher | Nityavardhan |
| OSV.dev API | [osv.dev](https://github.com/google/osv.dev) | Apache-2.0 | Active | Raw HTTP (PyPI client needs 3.13) | Nityavardhan |
| MDN HTTP Observatory | [repo](https://github.com/mdn/mdn-http-observatory) | MPL-2.0 | 1.7.1 | `npx` subprocess | Nityavardhan |
| csp_evaluator | [repo](https://github.com/google/csp-evaluator) | Apache-2.0 | 1.1.8 | 10-line Node script | Nityavardhan |
| FP-Inspector data | [repo](https://github.com/uiowa-irl/FP-Inspector) | MIT | Unmaintained since 2021 | Weak labels | Nityavardhan |
| whoisit (dangling domains) | [repo](https://github.com/meeb/whoisit) | BSD-3-Clause | 4.0.5 | Dependency (second half) | Nityavardhan |
| tree-sitter + JS grammar | [PyPI](https://pypi.org/pypi/tree-sitter/json) | MIT | 0.26.0 | Dependency (second half) | Nityavardhan |
| Leaky Forms leak detector | [leak-detector](https://github.com/leaky-forms/leaky-forms) | None (all rights reserved) | Research artifact | Clean-room reimplementation of the method | Kartik |
| pycryptodome, mmh3, base58, lzstring | [pysha3 is dead](https://pypi.org/pypi/pysha3/json) | BSD/PD, MIT, MIT, MIT | Current | Hash/encoding dependencies (`hashlib.sha3_*`, not pysha3) | Kartik |
| FastAPI SSE | [docs](https://fastapi.tiangolo.com/tutorial/server-sent-events/) | — | ≥0.135 required; 0.142.2 current | Built-in | Kartik |
| Cytoscape.js + cytoscape-fcose | [repo](https://github.com/cytoscape/cytoscape.js) | MIT | 3.34.3 | Library, own `useEffect` wrapper (skip stale react-cytoscapejs) | Kartik / Krati |
| PerfCascade | [repo](https://github.com/micmro/PerfCascade) | MIT | Idle since 2023 | Optional waterfall under leak timeline | Kartik |
| bagit-python | [repo](https://github.com/LibraryOfCongress/bagit-python) | CC0 | 1.9.0 | Evidence bundle (second half) | Kartik |
| Recharts / ECharts | [recharts](https://registry.npmjs.org/recharts) | MIT / Apache-2.0 | Active | Sector dashboard (second half) | Krati |
| networkx 3.6.1 | [PyPI](https://pypi.org/pypi/networkx/json) | BSD-3 | 3.7 needs Python ≥3.12 | Dependency | Krati |
| graspologic-native | [PyPI](https://pypi.org/pypi/graspologic-native/json) | MIT | 1.3.1, Windows wheels | Leiden on 3.11 | Krati |
| cdlib | [docs](https://cdlib.readthedocs.io/en/latest/reference/evaluation.html) | BSD-2 | 0.4.1 | NMI/ARI stability (check transitive deps) | Krati |
| vibhor98 cookie-sync scripts | [repo](https://github.com/vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites/tree/main/Cookie%20Synchronization) | MIT | 2021 | Reference only; rewrite to paper's parameters | Krati |
| interpret (EBM) | [PyPI](https://pypi.org/pypi/interpret/json) | MIT | 0.7.8 | Second half | Krati |
| optbinning / SALib | [optbinning](https://pypi.org/pypi/optbinning/json), [SALib](https://pypi.org/pypi/SALib/json) | Apache-2.0 / MIT | 1.0.0 / 1.6.0 | Second half | Krati |
| scikit-posthocs, statsmodels | [posthocs](https://pypi.org/pypi/scikit-posthocs/json), [statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html) | MIT / BSD-3 | Current | Second half | Krati |
| CrUX India list | [crux-top-lists](https://github.com/zakird/crux-top-lists/tree/main/data/country/in) | CC BY 4.0 (Google) | Monthly; 202608 | Corpus seed | Krati |

Two smaller notes on this table. The Fathom email-field detector that Leaky Forms injected (76% more email fields than `type=email` alone) comes from Firefox Relay, and its license was not verified, so treat it as off-limits until checked ([leaky-forms](https://github.com/asumansenol/leaky-forms)). Two consentcrawl repositories appeared in the research (Liscor's, last commit 2023-12, and dumkydewilde's, on PyPI). Use dumkydewilde's.

## Licensing comes down to one data rule and three code traps

This is not legal advice, but the boundaries are clear enough to engineer around. **The data rule:** DDG TDS, Tracker Radar, Disconnect and Ghostery TrackerDB are all CC BY-NC-SA 4.0 ([tracker-radar LICENSE](https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/LICENSE); [Disconnect LICENSE](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/LICENSE); [TrackerDB LICENSE](https://github.com/ghostery/trackerdb/blob/main/LICENSE)). A college project is non-commercial. But a released table containing a substantial portion of such a database counts as Adapted Material, so ShareAlike applies ([CC BY-NC-SA 4.0 legal code](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en)). Aggregate findings and statistics remain free to publish. third-party-web (MIT) is the only rich entity map safe for any future commercial pivot.

**The three code traps** are each a case where the most obvious library or codebase is copyleft or unlicensed. First, **leidenalg is GPL-3.0-or-later and igraph's license files carry GPLv2 text**, so the panel review's "leidenalg" row should become graspologic-native (MIT) ([leidenalg](https://pypi.org/pypi/leidenalg/json); [graspologic-native](https://pypi.org/pypi/graspologic-native/json)). Second, the two best leak-detection implementations are Blacklight's GPL TypeScript and Leaky Forms' unlicensed Python. Without a license, "nobody else can copy, distribute, or modify your work" ([choosealicense](https://choosealicense.com/no-permission/)). Both must be **reimplemented from the published method**. Third, **pingouin is GPL-3.0** ([pingouin LICENSE](https://raw.githubusercontent.com/raphaelvallat/pingouin/main/LICENSE)), and `hashid` is GPLv3+. Use scikit-posthocs, statsmodels and hand-written effect sizes.

The FSF treats pipes, sockets and command-line arguments as communication between separate programs. It treats "the output of a program" as generally not covered by the program's copyright ([GPL FAQ: mere aggregation](https://www.gnu.org/licenses/gpl-faq.html#MereAggregation); [GPL FAQ: output](https://www.gnu.org/licenses/gpl-faq.html#GPLOutput)). That is what makes a Blacklight cross-tool baseline legitimate.

| Situation | Do | Don't |
|---|---|---|
| TRC (Apache-2.0) | Copy/translate the API list and consent logic; keep LICENSE + NOTICE; mark changes; skip DDG logos (CC BY-NC-ND) | Strip attribution |
| autoconsent, MDN Observatory (MPL-2.0) | Ship the vendored file unmodified with its header and a NOTICE naming the upstream tag; call Observatory via `npx` | Paste MPL code into Apache files or relabel it Apache |
| Blacklight, OpenWPM, Leaky Forms crawler (GPL-3.0); WEC (EUPL-1.2) | Read for ideas; run unmodified in a separate folder via CLI; reimplement thresholds from papers | Copy source, import modules, or adapt their templates |
| Leaky Forms leak detector, citp/email_tracking (no license) | Reimplement from the paper and README description; cite | Copy any code verbatim |
| leidenalg, igraph, pingouin, hashid (GPL) | Use graspologic-native, networkx, scikit-posthocs; isolate any GPL tool as an optional CLI | `import` them in the Apache core |
| TDS / Tracker Radar / Disconnect / TrackerDB (NC-SA) | Fetch at runtime into `data/third_party/` with attribution; release derived tables as CC BY-NC-SA | Merge them into the bundled Apache entity file or release them as CC BY/CC0 |
| EasyList, EasyPrivacy, IndianList, AdGuard filters | Fetch at runtime; attribute; pin hash and date | Redistribute modified lists under Apache |
| India supplement (team-authored) | Release under CC BY 4.0 or Apache-2.0, built only from the team's own observations | Seed it by copying NC-SA rows |
| CrUX India list | Redistribute with attribution and month (Google states CC BY 4.0) | Mix in Cloudflare Radar ranks (CC BY-NC) |
| Vettam scanner | Borrow the observation/interpretation split; cite as prior art | Reuse its CC BY-ND rule text or its names |

### Python 3.11 stays; 3.12 buys nothing the first half needs

The panel review advised moving to Python 3.12. The verified package data now argues against it. Everything the first half needs installs and runs on 3.11 and was tested locally on Windows: adblock 0.6.0, dnspython, whoisit, tree-sitter ([PyPI adblock](https://pypi.org/pypi/adblock/json); [tree-sitter](https://pypi.org/pypi/tree-sitter/json)). The probe already runs on 3.11. The only concrete gain from 3.12 is networkx 3.7's built-in `leiden_communities`, since 3.6.1 has no default implementation ([networkx 3.7 notes](https://networkx.org/documentation/stable/release/release_3.7.html)). graspologic-native supplies MIT Leiden on 3.11 with Windows wheels, and Leiden is a second-half need anyway. The machine also has no 3.12 installed. Its other interpreter, 3.14, is untested for adblock's 2022 abi3 wheel, and braveblock's wheels stop at cp311. On 3.11, scipy caps at 1.17.1, which is fine.

**Decision:** standardise on 3.11 and pin `networkx>=3.6,<3.7`. Add `graspologic-native>=1.3` (not full graspologic, which pins numpy<2). Raise `fastapi>=0.135`. Use `hashlib.sha3_*` and raw OSV HTTP calls. Revisit only if a must-have package drops 3.11 support.

## A seven-week build order that reaches the mid-semester demo

The first-half deliverables are the crawler, tracker detection, leak tracer v1, three UI screens (scan/progress, summary, leak replay), a basic per-site graph and a 50-site pilot. The order below front-loads the two risks: the consent/API port (gated at week 2) and the leak tracer's correctness on a known testbed. "Reused" means existing code, data or libraries; "written" means TraceMap code. The pilot uses CrUX India's 202608 file, whose ranks are buckets (1k, 5k, 10k and so on) shuffled within each bucket ([crux-top-lists README](https://raw.githubusercontent.com/zakird/crux-top-lists/main/README.md)). The top bucket includes adult sites, so the 50 sites need manual screening.

| Week | Kavya (crawler) | Nityavardhan (detection) | Kartik (leak/API/UI) | Krati (graph/score/stats) |
|---|---|---|---|---|
| 1 | **Written:** CDP capture into contracts (requests with initiator + postData, Set-Cookie, `getAllCookies` with values, storage dump, script hashes); mobile emulation; persistent A/B/A2 profile dirs; `*.localhost` testbed v0 (tracker, cookie-sync, leaky-form pages). **Reused:** Playwright, installed Chrome. Half-day TRC oracle spike (with download approval) | **Written:** threat model; list fetcher with hash+date pin. **Reused:** TDS, EasyPrivacy/EasyList, IndianList, AdGuard 3, Disconnect, TrackerDB, third-party-web, AdGuard CNAME; `adblock` engine per list | **Written:** canary generator (team-domain email, +91 phone variants: +91…, 91…, 0…, 10-digit, spaced/dashed); 3-layer encoding/hash pool with unit tests; FastAPI skeleton + SSE stub. **Reused:** hashlib, pycryptodome, mmh3, base58, lzstring | **Written:** SQLite schema (OpenWPM-style tables, own DDL); E&N ID-extraction spec (expiry >90 d, length 8–100, similarity <0.66, constant within profile). **Reused:** CrUX India 202608 |
| 2 | **Reused:** autoconsent bundle; TRC consent logic + API list (Apache, with NOTICE). **Written:** none/optIn/optOut modes; instrument.js plus the 3 extra hooks; deterministic subpage choice (first 4 same-site links, sorted) + scroll. **Gate:** testbed CMP success + API recall ≥ TRC oracle, else TRC sidecar | **Written:** entity resolver (TDS → Tracker Radar → TrackerDB → Disconnect → third-party-web → India seed); unified category taxonomy; `india_entities.json` v0 (CleverTap, MoEngage, WebEngage, Netcore, iZooto, Times/Colombia, InMobi, Affle, Wingify, Zoho, Freshworks) | **Written:** form-field finder (type/autocomplete/name heuristics, iframes); typing with per-key delays + Tab blur in profile L; never submit, never password fields | **Written:** ID-candidate extraction across A/B/A2 from cookies, storage, URLs, Referer, Location and POST bodies (decode URL/base64/JSON, split on delimiters) |
| 3 | **Written:** bot-wall detection (403/429/503, challenge DOM/titles, challenge hosts); crawl_history-style error accounting; 10 real Indian sites | **Written:** CNAME cloaking via dnspython (fixed resolver, cached) against AdGuard + TDS `cnames`; E&N canvas/font/WebRTC/audio rules over the API log; session-replay list union (TDS, Blacklight list as data, Princeton) | **Written:** leak search over URLs, POST bodies, headers, cookies and beacons with pyahocorasick; `before_submit` from the event timeline; positive + negative controls on the testbed; precision/recall harness | **Written:** per-site directed graph in networkx; `intra_entity`/`cross_entity` tags from Nityavardhan's resolver; degree/PageRank. **Reused:** networkx 3.6.1 |
| 4 | **Written:** progress events into the asyncio queue; HAR + raw CDP log saving; record Chrome version; 2–4 parallel site workers with one visit per site at a time | **Reused:** retire.js repository, OSV API. **Written:** retire matcher (`§§version§§` regexes + version ranges); SRI check from crawl data; optional `npx` MDN Observatory call | **Reused:** React + Vite, EventSource. **Written:** Screen 1, scan + live progress (stage stepper, live log, third-party counter) | **Written:** graph JSON for Cytoscape (owner compound nodes, dashed low-confidence edges); per-site summary metrics; screen the 50 pilot sites and label sectors |
| 5 | **Written:** batch runner with resume, per-site timeouts and politeness delays; dry run on 15 sites | **Written:** "unknown third party" report (eTLD+1s absent from every list) feeding the India supplement; per-list match flags for later ML | **Written:** Screen 2, results summary (findings with "show proof" drawer, subscores as plain counts for now); Screen 3, leak replay timeline (typed field → request, canary substring highlighted with decoding chain). **Reused:** Cytoscape.js + fCoSE for the embedded graph panel | **Written:** basic graph panel integration with Kartik; descriptive stats only for graphs under ~15 nodes (per the panel protocol) |
| 6 | **50-site pilot run** (mobile, none mode, plus opt-in/opt-out where a banner is detected); triage of timeouts, blocks and consent failures | Fix list/entity gaps the pilot surfaces; hand-classify top unknown domains (2 coders) | Leak-tracer fixes from pilot; optional Blacklight cross-run on ~10 sites from a separate GPL folder (needs npm download approval) | Pilot statistics: block rate by sector, list-coverage gap, leak counts by channel, ID-edge counts intra vs cross entity |
| 7 | Freeze crawler; reproducibility notes (Chrome version, list hashes, PSL snapshot) | Write up detection evaluation on the testbed | Demo script on a known testbed site plus one live site; API endpoints frozen | Mid-semester slides and figures; buffer for slippage |

The order keeps every owner unblocked. Crawler output is a saved CrawlRecord, so detection, leak and graph work in weeks 1–3 runs on testbed fixtures rather than waiting for a full crawler. The only cross-team dependencies are the entity resolver (week 2) feeding graph tagging (week 3), and the progress-event contract (week 4) feeding Screen 1. Both are small interfaces that can be agreed in week 1.

Three things are deliberately absent from the first half: Leiden and null models, the scorecard with sensitivity analysis and EBM, and the evidence bundle. All three are library-backed (graspologic-native, SALib/interpret, bagit-python) and can only be validated once the 1,500-site corpus exists. The pilot's crawl costs also need checking against the panel's budget of about 4 minutes per site for 3 visits × 5 pages. The researchers flagged their own runtime estimates as unmeasured. The week-6 pilot is the first real measurement, and the second-half crawl plan should be re-sized from it, not from the estimate.

## Conclusion

The search changed what TraceMap is. It is not a crawler project with research attached. It is an integration-and-data project whose crawler should stay as small and boring as possible. Every expensive capability TraceMap needs to *detect* things already exists under a usable license or as a published method. The things nobody has built are the joins between them: A/B/revisit values flowing into an entity-tagged ID graph, canary typing timed against the same capture stream, +91 phone formats, Indian vendor ownership, and a replay view that shows a leak happening. That is also where viva questions will land. The team's best defence is the attribution table: it shows exactly which parts are borrowed, which are reimplemented, and which are original.

The TRC question had a less obvious answer than either researcher gave. TRC's real value to TraceMap is not as a runtime. It is as an Apache-licensed source of two hard-won assets, the API list and the consent logic, and as a **measuring stick**. Running it unmodified on the testbed turns "our instrumentation works" from a claim into a recall number. That is the same move the panel asked for with Blacklight on leaks, and it costs half a day. The licensing review points the same way: the libraries that look most standard for this work (leidenalg, pingouin, Blacklight's leak code) are exactly the ones the Apache core cannot import. That should be settled before the second half starts.
