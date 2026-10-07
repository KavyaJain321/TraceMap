# Open-source privacy/tracking scanners, measurement frameworks and third-party performance tooling: what TraceMap can reuse

Scope: Python and other non-Node candidates (plus the Node and performance tooling named in the brief) that TraceMap could reuse. TraceMap is Python 3.11 + Playwright Chromium + FastAPI on Windows, licensed Apache-2.0. Its pipeline: mobile crawl (2 fresh profiles + revisit; landing + subpages; cookie-banner modes) → capture requests/cookies/storage/JS API calls → third-party classification → identifier-sharing (cookie-sync) graph → canary form-leak test → interpretable risk score → measurement study of about 1,500 Indian sites.

How this was verified (as of 2026-10-07): repo metadata (language, SPDX license, stars, `pushed_at`, archived flag) came from the GitHub REST API (`api.github.com/repos/<owner>/<repo>`). Most READMEs, LICENSE files and source files were fetched raw from raw.githubusercontent.com / codeberg.org. Leak-detector files were listed from GitHub's HTML tree page, and the CookieBlock extension's MIT license comes from the API metadata only. Package versions came from the npm and PyPI registries. The GitHub API rate limit (60/hour, unauthenticated) ran out partway through, so per-repo commit messages could not be listed. "Last activity" therefore means the `pushed_at` timestamp, not a reviewed commit.

---

## Q1. Per-candidate facts: URL, stack, license, stars, last activity, pipeline coverage

### Takeaway
Most of the field is either (a) GPL-3.0 and Firefox/Selenium-based (OpenWPM and its forks: BannerClick, the CookieBlock consent crawler, Leaky Forms crawler, priv-accept), (b) archived (PrivacyScore, Webbkoll), or (c) small Playwright scripts of uneven quality. Two maintained projects match TraceMap's stack well. One is **consentcrawl** (Python + Playwright, MIT, a consent-before/after check). The other is **Vettam/dpdp-cookie-scanner** (TypeScript + Playwright, Apache-2.0, maps findings to India's DPDP Act). Among datasets, **third-party-web** (MIT) is safe to bundle, but **DuckDuckGo Tracker Radar** (CC BY-NC-SA 4.0) is not.

### Cited Findings

**Summary table (metadata from GitHub API on 2026-10-07 unless noted)**

| Candidate | URL | Stack | License (SPDX) | Stars | Last push | Status |
|---|---|---|---|---|---|---|
| OpenWPM | https://github.com/openwpm/OpenWPM | Python + Firefox/Selenium + TS WebExtension | GPL-3.0 (API says NOASSERTION; LICENSE file says "Licensed GPL v3") | 1,422 | 2026-10-04 | Active; v0.38.0 released 2026-10-04 |
| openwpm-utils | https://github.com/openwpm/openwpm-utils | Python | MPL-2.0 | 0 | 2021-04-09 | Dormant (PyPI 0.2.0) |
| consentcrawl | https://github.com/dumkydewilde/consentcrawl | Python + Playwright | MIT | 51 | 2025-10-12 | Alpha; PyPI 0.1.4 (2024-03-15) |
| Privacy Pioneer Web Crawler | https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler | Selenium (JS) + Firefox Nightly + extension + Node REST API + MySQL; analysis in Python/Jupyter | MIT | 4 | 2026-09-08 | Active (research lab) |
| Privacy Pioneer (extension) | https://github.com/privacy-tech-lab/privacy-pioneer | JS Firefox extension | CC BY-NC-SA 4.0 (LICENSE file; API says NOASSERTION) | 37 | 2026-09-30 | Active |
| webXray (original) | https://github.com/timlibert/webXray → 404; README of a mirror points to `github.com/timlib/webXray` (README also 404) | Python + Chrome (DevTools) | PolyForm Strict 1.0.0 (mirror thezedwards/webXray) | n/a | n/a | Original repo not reachable; mirrors only |
| webXray mirrors | https://github.com/agilemobiledev/webXray ; https://github.com/thezedwards/webXray | Python | GPL-3.0 (2015 mirror) / PolyForm Strict (2021 mirror) | 34 / 4 | 2015-08-19 / 2021-03-04 | Stale |
| PrivacyScore | https://github.com/privacyscore/privacyscore | Python/Django + Celery + Redis | GPL-3.0 | 127 | 2021-06-22 | **Archived** |
| privacyscanner (PrivacyScore's scanner) | https://github.com/PrivacyScore/privacyscanner | Python + Chrome | MIT (PyPI metadata) | — | PyPI 0.8.1 uploaded 2021-12-20 | Stale |
| Webbkoll | https://github.com/andersju/webbkoll → moved to https://codeberg.org/dataskydd.net/webbkoll | Elixir/Phoenix front end + Node/Puppeteer backend (https://codeberg.org/dataskydd.net/webbkoll-backend) | MIT | 262 (GitHub) / 18 (Codeberg) | GitHub 2022-11-18; Codeberg updated 2025-04-25 | **Archived on both**; service now run by 5th of July Foundation |
| CookieBlock (extension) | https://github.com/dibollinger/CookieBlock | JS extension | MIT | 226 | 2023-12-08 | Stale |
| CookieBlock Consent Crawler | https://github.com/dibollinger/CookieBlock-Consent-Crawler | OpenWPM v0.12.0 fork (Python) + requests-based CMP presence crawler | no license file detected by API (embeds GPL-3.0 OpenWPM code) | 13 | 2023-06-03 | Stale |
| CookieBlock Consent Classifier | https://github.com/dibollinger/CookieBlock-Consent-Classifier | Python (feature extraction + XGBoost) | MIT | — | not checked (rate limit) | — |
| BannerClick | https://github.com/bannerclick/bannerclick (search also surfaced https://github.com/mohammadmahdijavid/bannerclick, metadata UNVERIFIED) | OpenWPM fork (Python + Firefox) | GPL-3.0 (LICENSE is OpenWPM's) | 9 | 2025-07-01 | Low activity |
| priv-accept | https://github.com/marty90/priv-accept | Python + Selenium + Chrome | GPL-3.0 | 8 | 2024-02-27 | Stale |
| third-party-web | https://github.com/patrickhulce/third-party-web | JS + SQL on HTTP Archive; JSON dataset | MIT | 1,111 | 2026-09-14 | Active; npm 0.30.0 (2026-09-14) |
| HTTP Archive Almanac | https://github.com/HTTPArchive/almanac.httparchive.org | HTML + BigQuery SQL | Apache-2.0 | 691 | 2026-10-03 | Active |
| HTTP Archive custom metrics | https://github.com/HTTPArchive/custom-metrics | JS (WebPageTest custom metrics) | Apache-2.0 | 29 | 2026-10-07 | Active |
| Lighthouse | https://github.com/GoogleChrome/lighthouse | Node (>=22.19) | Apache-2.0 | 30,867 | 2026-10-07 | Active; v13.5.0 in package.json |
| DDG Tracker Radar Collector | https://github.com/duckduckgo/tracker-radar-collector | Node + Puppeteer | Apache-2.0 (LICENSE text; API says NOASSERTION) | 169 | 2026-10-07 | Active |
| DDG Tracker Radar (data) | https://github.com/duckduckgo/tracker-radar | JSON dataset | CC BY-NC-SA 4.0 | 1,734 | 2026-10-02 | Active |
| DDG autoconsent | npm `@duckduckgo/autoconsent` | JS rule library; runs in an extension or Playwright | MPL-2.0 | — | npm 16.47.0 published 2026-10-07 | Very active |
| Blacklight collector (The Markup) | https://github.com/the-markup/blacklight-collector | TypeScript + Puppeteer | GPL-3.0 | 242 | 2026-09-03 | Active |
| Leaky Forms (USENIX Sec '22) | https://github.com/asumansenol/leaky-forms ; crawler https://github.com/asumansenol/leaky-forms-crawler | Python leak detector + analysis; crawler = Tracker Radar Collector fork (Node) | crawler GPL-3.0 (LICENSE file); main repo: no root LICENSE found (UNVERIFIED) | — | not checked (rate limit) | Research artifact |
| Vettam dpdp-cookie-scanner | https://github.com/Vettam/dpdp-cookie-scanner | TypeScript + Playwright (npm CLI) | Apache-2.0 (code); trackers/ data CC BY-SA 4.0; rule text CC BY-ND 4.0 | 4 | 2026-09-30 | Active, India DPDP-specific |
| truconsent/truscanner | https://github.com/truconsent/truscanner | Python | MIT | 18 | 2026-07-06 | README not fetchable on `main` (404): contents UNVERIFIED |
| devbret/cookie-tracker-scanner | https://github.com/devbret/cookie-tracker-scanner | Python + Playwright | MIT | 1 | 2026-08-05 | Toy/demo |
| Slashgear/gdpr-cookie-scanner | https://github.com/Slashgear/gdpr-cookie-scanner | Node CLI | MIT | 24 | 2026-10-01 | GDPR-focused |

**OpenWPM**
- Description: "a web privacy measurement framework" for "thousands to millions of websites", "built on top of Firefox, with automation provided by Selenium". — [OpenWPM README](https://github.com/openwpm/OpenWPM)
- Windows: "OpenWPM does not support windows: https://github.com/openwpm/OpenWPM/issues/503". It is tested on Ubuntu 24.04 in CI, and the Docker image is based on Ubuntu 22.04. Install is via conda + `install.sh`. — [OpenWPM README](https://github.com/openwpm/OpenWPM)
- Very active in 2026: v0.38.0 (2026-10-04) bumps to Firefox 157, v0.37.0 (2026-09-06) to Firefox 155, and v0.36.0 (2026-08-23) to Firefox 154. The project now pins Python 3.14. — [OpenWPM CHANGELOG](https://github.com/openwpm/OpenWPM/blob/master/CHANGELOG.md)
- Storage tables (from `openwpm/storage/schema.sql`): `task`, `crawl`, `site_visits`, `crawl_history`, `http_requests`, `http_responses`, `http_redirects`, `javascript`, `javascript_cookies`, `navigations`, `callstacks`, `incomplete_visits`, `dns_responses`. — [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)
- License file: "OpenWPM: Copyright © 2021 Steven Englehardt, Licensed GPL v3". — [OpenWPM LICENSE](https://github.com/openwpm/OpenWPM/blob/master/LICENSE)
- The original OpenWPM paper made 15 measurement types, including cookie syncing, fingerprinting and cookie respawning. — [Help Net Security on OpenWPM](https://www.helpnetsecurity.com/2016/01/19/openwpm-an-automated-open-source-framework-for-measuring-web-privacy/); [Princeton publication page](https://collaborate.princeton.edu/en/publications/online-tracking-a-1-million-site-measurement-and-analysis/)
- **openwpm-utils**: "A collection of utilities for working with OpenWPM datasets". PyPI 0.2.0, MPL-2.0, last push 2021. The domain utilities were split out into `domain_utils`. — [openwpm-utils README](https://github.com/openwpm/openwpm-utils); [PyPI openwpm-utils](https://pypi.org/project/openwpm-utils/)

**consentcrawl**
- What it does: "running a Playwright headless browser to crawl and check for marketing and analytics scripts firing before and after consent". It claims to detect "25+" CMPs (the README lists about 35 plus a generic CSS-selector fallback). It also detects "unconsented third-party domains and cookies", classifies tracking domains against "7 commonly used ad blocking lists", takes screenshots before and after consent, and captures JSON-LD and meta tags. — [consentcrawl README](https://github.com/dumkydewilde/consentcrawl)
- Output: by default results go to a SQLite DB `crawl_results.db`. It can be called from Python as `asyncio.run(crawl.crawl_single(...))`. Examples include a FastAPI server on Cloud Run. — [consentcrawl README](https://github.com/dumkydewilde/consentcrawl)
- CMP detection is by CSS selectors in `consentcrawl/assets/consent_managers.yml`. The to-do list still includes "Detect consent managers with cookies instead of just CSS selectors". — [consentcrawl README](https://github.com/dumkydewilde/consentcrawl)
- Dependencies: Python ^3.10, playwright >=1.34,<2.0, requests, pyyaml. License MIT. Development status "3 - Alpha". — [consentcrawl pyproject.toml](https://github.com/dumkydewilde/consentcrawl/blob/main/pyproject.toml); [PyPI](https://pypi.org/project/consentcrawl/)

**Privacy Pioneer extension + web crawler**
- The extension detects personal data in web traffic. Categories: monetization (Disconnect lists); location (GPS fine/coarse, ZIP, street address, city, region); tracking (tracking pixel, IP address, fingerprinting); personal (**phone number, email address, custom keywords**). It uses "a machine learning model as well as rule-based heuristics". It runs on Firefox only. — [Privacy Pioneer README](https://github.com/privacy-tech-lab/privacy-pioneer)
- Extension license file: "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license". — [Privacy Pioneer LICENSE](https://github.com/privacy-tech-lab/privacy-pioneer/blob/main/LICENSE)
- The crawler uses a Selenium script (`selenium-crawler/local-crawler.js`), Firefox Nightly pinned to a 2024-01-01 build, a Node `rest-api`, and MySQL. The setup guide is written for **Windows** ("we recommend the Windows route"). It also ships per-country crawl data and Python/Jupyter analysis scripts (pandas, seaborn, tldextract), including cookie-banner accept vs no-action experiments for DE/ES/US. — [Privacy Pioneer Web Crawler README](https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler)
- Recent publication: "Global Web, Local Privacy? An International Review of Web Tracking", Pragmatic Cybersecurity, March 2026. — [Privacy Pioneer README](https://github.com/privacy-tech-lab/privacy-pioneer)

**webXray**
- Mirror README: a Python + consumer Chrome tool for "analyzing webpage traffic and content, extracting legal policies, and identifying the companies which collect user data". It has "haystack" and "forensic" scans, SQLite/Postgres storage, and a custom domain-ownership library. The README also says: "Commercial use of webXray is prohibited, as is redistributing the code". The license is PolyForm Strict 1.0.0. — [thezedwards/webXray mirror](https://github.com/thezedwards/webXray)
- `github.com/timlibert/webXray` returns 404 from the GitHub API. The clone URL in the mirror README (`timlib/webXray`) also returns 404 for raw README. A separate GPL-3.0 domain-owner list exists at https://github.com/RDBinns/webXray_Domain_Owner_List (2 stars, last push 2018). — GitHub API/search results (this session)
- Tim Libert later launched a webXray search engine for tracking/privacy violations. — [itc.ua](https://itc.ua/en/news/google-ex-engineer-launches-webxray-search-engine-it-will-show-you-which-sites-are-tracking-you/amp)

**PrivacyScore / privacyscanner**
- PrivacyScore goals: compare and rank whole lists of sites, check for embedded known trackers, rescan periodically and track changes. "Beta quality". Dependencies include privacyscanner, testssl.sh, Celery, adblockparser, geoip2, and Redis. License GPLv3-or-later. — [PrivacyScore README](https://github.com/privacyscore/privacyscore)
- privacyscanner is a pip CLI (`privacyscanner scan http://example.com/`) that needs Chrome/Chromium, EasyList and a MaxMind GeoIP licence key. It outputs a JSON result plus a screenshot per site. "there is no development documentation currently". — [privacyscanner README](https://github.com/PrivacyScore/privacyscanner)

**Webbkoll**
- "This repository is no longer maintained. Since mid-September 2024, Webbkoll is hosted and maintained by the 5th of July Foundation at https://webbkoll.5july.net/". Architecture: an Elixir/Phoenix front end asks a Node.js Puppeteer backend to load the page in Chromium. The backend returns requests, cookies and response headers as JSON. The front end "analyzes the data and presents the results on a webpage along with explanations and advice". It is multilingual (EN/SV/DE/NO), keeps results in memory only, and saves nothing to disk. — [Webbkoll README on Codeberg](https://codeberg.org/dataskydd.net/webbkoll)
- Both Codeberg repos are marked archived: webbkoll (updated 2025-04-25) and webbkoll-backend (updated 2024-12-03). — Codeberg API (`codeberg.org/api/v1/repos/dataskydd.net/webbkoll`, `.../webbkoll-backend`)

**CookieBlock**
- Extension: "classifies cookies on-the-fly into four distinct categories" (necessary plus functionality, analytics/statistics, advertising/tracking) and deletes non-consented ones. It does not handle banners; it recommends Consent-O-Matic. — [CookieBlock README](https://github.com/dibollinger/CookieBlock)
- Consent crawler: (1) a fast `requests`-based "CMP Presence Crawler" for Cookiebot, OneTrust and Termly; (2) an OpenWPM v0.12.0-based "Consent Crawler" that extracts cookies **and their declared purposes** from CMP cookie notices. It uses a Consent-O-Matic fork. — [CookieBlock-Consent-Crawler README](https://github.com/dibollinger/CookieBlock-Consent-Crawler)
- Classifier repo: "feature extraction tools as well as the classifiers used for CookieBlock", MIT licensed. — [CookieBlock-Consent-Classifier](https://github.com/dibollinger/CookieBlock-Consent-Classifier)

**BannerClick and priv-accept**
- BannerClick is built on OpenWPM. It finds the most specific banner-containing DOM element and also searches iframes. It reports about 99% accuracy in detecting, accepting and rejecting banners. With it, Rasaii, Gosain and Gasser (IMC '23, "Thou Shalt Not Reject") measured 5.5x more third-party cookies after "accept" on the Tranco top-10k. — [arXiv 2310.01108](https://arxiv.org/abs/2310.01108); [Rasaii thesis](https://publikationen.sulb.uni-saarland.de/bitstream/20.500.11880/41533/1/Seyedali-Rasaii-Thesis.pdf)
- The bannerclick/bannerclick README's master branch is essentially OpenWPM's README, and its LICENSE is OpenWPM's GPL v3. — [bannerclick repo](https://github.com/bannerclick/bannerclick)
- priv-accept is a keyword heuristic that clicks "Accept". Flow: fresh profile visit → click → **revisit**. Options include `--visit_internals` (random internal pages), `--pre_visit`, `--lang`, `--network_conditions` and RUM Speed Index. Output is a JSON log with all URLs, cookies and OnLoad metrics, plus screenshots. Stack is Python + Selenium + Chrome. License GPL-3.0. — [priv-accept README](https://github.com/marty90/priv-accept)

**Python/Playwright scanners and form-leak tooling**
- Leaky Forms: crawler extended DDG's Tracker Radar Collector. It used the Firefox Relay Fathom email-field classifier ("76% more email fields than by simply searching for input fields with type email") and Consent-O-Matic. It measured the top 100k sites EU vs US, desktop vs mobile, and found email exfiltration before submission on 1,844 (EU) / 2,950 (US) sites. — [Leaky Forms repo](https://github.com/asumansenol/leaky-forms); [USENIX page](https://www.usenix.org/conference/usenixsecurity22/presentation/senol)
- Leaky Forms leak detector (Python): "searches for the filled email address and the password, and their various encodings and hashes in the HTTP traffic", based on Englehardt et al. (PETS 2018). Files: `LeakDetector.py`, `RunLeakDetector.py`, `BlockListParser.py`, `DisconnectParser.py`, `LoginLeakDetector.py`. `LeakDetector.py` (823 lines) says it is "Based on code from 'I never signed up for this!'". Hash list: md2, md4, md5, sha1, sha224/256/384/512, sha3_*, mmh3_64/128, ripemd160, whirlpool, salted sha256. Encodings: base16/32/58/64 and more, with "likely" subsets (md5, sha1, sha256, sha512, base64). — [leak-detector README](https://github.com/asumansenol/leaky-forms/tree/main/leak-detector); [LeakDetector.py](https://github.com/asumansenol/leaky-forms/blob/main/leak-detector/LeakDetector.py)
- Leaky Forms crawler LICENSE: "Copyright © 2022 Gunes Acar, Asuman Senol, Licensed GPL v3". — [leaky-forms-crawler](https://github.com/asumansenol/leaky-forms-crawler)
- The original Englehardt email-tracking code: https://github.com/citp/email_tracking. No LICENSE file at root (raw LICENSE returned 404). — [citp/email_tracking](https://github.com/citp/email_tracking)
- devbret/cookie-tracker-scanner: Playwright on a single site. It logs requests, resource types, headers and redirects; classifies first vs third party; diffs cookies across consent interactions; exports JSON/MD/HTML. MIT. Labelled as a skills demo. — [README](https://github.com/devbret/cookie-tracker-scanner)
- Blacklight collector tests: behaviour_event_listeners, canvas_fingerprinters, canvas_font_fingerprinters, cookies, fb_pixel_events, google_analytics_events, **key_logging**, session_recorders, third_party_trackers. Options include `numPages` (default 3), `emulateDevice`, and HAR capture. GPL-3.0. — [blacklight-collector README](https://github.com/the-markup/blacklight-collector)
- DDG Tracker Radar Collector: modular collectors (`requests`, `cookies`, API calls, screenshots, `cookiepopups` with `--autoconsent-action optIn|optOut`), a `--only-3p` mode, and a `BaseCollector` plugin pattern. — [tracker-radar-collector README](https://github.com/duckduckgo/tracker-radar-collector)
- DDG autoconsent: "a library of rules for navigating through common consent popups... can be run in a Chrome extension, or in a Playwright-orchestrated headless browser... opt-in and opt-out options can be selected automatically". MPL-2.0, v16.47.0 published 2026-10-07. — [npm @duckduckgo/autoconsent](https://www.npmjs.com/package/@duckduckgo/autoconsent)
- Consent-O-Matic is MIT licensed. — [Consent-O-Matic LICENSE](https://github.com/cavi-au/Consent-O-Matic)
- No meaningful mitmproxy-based tracker analyzer turned up. A GitHub search for "mitmproxy tracker" returned only irrelevant repos. — GitHub search API (this session)

**third-party-web**
- Entity classification published as an npm module (`getEntity(url)` → `{name, homepage, category, domains}`). Methodology: HTTP Archive's monthly Lighthouse mobile crawl of ~4M sites, attributing script execution time per entity. — [third-party-web README](https://github.com/patrickhulce/third-party-web)
- `dist/entities.json` (npm 0.30.0, 2026-09-14) has **2,143 entities**. Fields: `name`, `company`, `homepage`, `category`, `domains`. Category counts: ad 751, analytics 393, utility 281, content 192, hosting 92, other 91, marketing 82, customer-success 76, consent-provider 69, social 64, cdn 30, tag-manager 15, video 7. — [unpkg third-party-web/dist/entities.json](https://unpkg.com/third-party-web@latest/dist/entities.json)
- India coverage spot-check (substring search of entities.json): present are CleverTap, WebEngage, iZooto, Taboola, Freshdesk/Freshchat, Branch Metrics, Hotjar, Clarity. **Absent** are MoEngage, Netcore, Razorpay, Paytm, Jio, Juspay, Cashfree, Colombia (Times Internet), vdo.ai and AppsFlyer. — same source (this session's check)
- License MIT. — [third-party-web LICENSE](https://github.com/patrickhulce/third-party-web/blob/master/LICENSE)

**Lighthouse**
- v13.0.0 (2025-10-10) changelog: "remove third-party-facades audit (#16710)". In current `main`, `core/audits/third-party-summary.js` and `third-party-facades.js` return 404. The replacement is `core/audits/insights/third-parties-insight.js` with `replacesAudits: ['third-party-summary']`. It reports per-entity `mainThreadTime` and `transferSize` using DevTools' trace_engine. `core/audits/third-party-cookies.js` still exists. — [Lighthouse changelog](https://github.com/GoogleChrome/lighthouse/blob/main/changelog.md); [third-parties-insight.js](https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/insights/third-parties-insight.js)
- package.json: version 13.5.0, Apache-2.0, `engines.node >=22.19`, depends on `third-party-web ^0.30.0`. — [Lighthouse package.json](https://github.com/GoogleChrome/lighthouse/blob/main/package.json)

**HTTP Archive / Web Almanac**
- 2025 Privacy chapter (authors Rumaisa Habib, Vinod Tiwari, Nurullah Demir). It uses the WhoTracks.Me catalog. Measures: tracker prevalence, 1P/3P cookies, fingerprinting, bounce tracking, UA-CH, Referrer-Policy, CMPs/IAB TCF/USP/GPP, DNT and GPC. Headlines: 75% of desktop and 74% of mobile pages have at least one tracker; Google on 61% of sites; only 1.7% fully TCFv2 compliant; Referrer-Policy at 37.66% (up from 32% in 2024). **No India-specific analysis.** — [Web Almanac 2025 Privacy](https://almanac.httparchive.org/en/2025/privacy)
- Open SQL: `sql/2025/privacy/` has 20 queries, e.g. `cookies_third_party_top.sql`, `fingerprinting_top.sql`, `tracker_distribution.sql`, `whotracksme_trackers_top.sql`, `iab_tcf_v2_countries_top.sql`. `sql/2024/privacy/` has 33, e.g. `most_common_cname_domains.sql`, `number_of_websites_with_gpc.sql`, `easylist-tracker-detection.sql`. Repo license Apache-2.0. — [almanac sql/2025/privacy](https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql/2025/privacy); [sql/2024/privacy](https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql/2024/privacy)
- `custom-metrics/dist/privacy.js` keys include `iab_gpp`, `iab_usp`, `navigator_doNotTrack`, `navigator_globalPrivacyControl`, `document_permissionsPolicy`, `referrerPolicy`, `request_hostnames_with_cname` and `ccpa_link`. `third-parties.js`, `cookies.js` and `almanac.js` also exist. — [HTTPArchive/custom-metrics](https://github.com/HTTPArchive/custom-metrics/tree/main/dist)

**Indian DPDP / cookie-compliance scanners (GitHub search: "DPDP scanner", "DPDP cookie", "DPDP compliance", "cookie compliance india", "DPDPA")**
- **Vettam/dpdp-cookie-scanner** (the only substantive hit): loads a page in a headless browser, records what it collects, and "maps each observation to the provisions of India's Digital Personal Data Protection Act 2023 and DPDP Rules 2025". Each finding gets a certainty tier (`settled` / `arguable` / `open`) and an enforceability date ("Most substantive obligations commence 13 May 2027"). There is "no severity field". Features: `--interact` three-pass banner interaction (load, accept-all, reject-all), `--gpc`, JSON/MD output, diffing of two scans, and a separate `dpdp-notice-lint` that checks notices for itemisation, withdrawal, grievance officer, and English + Hindi text. Architecture: "Surfaces → Mapper → Engine (Playwright)", with `rules/*.yaml` and `trackers/*.yaml`; observation is kept separate from interpretation. Licensing: code Apache-2.0, `trackers/` CC BY-SA 4.0, rule rationale text CC BY-ND 4.0 (owned by Rylematic Technologies), IP-to-country DB-IP Lite CC BY 4.0. Forks may not use the "Vettam"/"Sentinel" names. Rule freshness date 30 September 2026. — [dpdp-cookie-scanner README](https://github.com/Vettam/dpdp-cookie-scanner)
- Other hits are tiny (0–18 stars, mostly 2026): truconsent/truscanner (Python, MIT, 18★, content UNVERIFIED); abdash1994/shipsafe-india (TS); Divith23/DPDP-Act-Compliance-Scanner (Python, no license, README 404); Sarvesh8521/dpdp-scanner (Python, no license, README 404); manvithin/dpdp-scanner (TS); arun4131/DPDP_Scanner (Go); NIKITATAPALI/ConsentFair (Chrome extension auditing banners against GDPR + DPDP, MIT); FREAKYBILLU/CookieConsent (Java, "DPDPA Cookie scanning project"). — GitHub search API results (this session)

### Inferences
- **Stack fit ranking for TraceMap (Python 3.11 + Playwright Chromium + Windows):** consentcrawl (direct fit) > Vettam scanner (Playwright, but TypeScript/Node) > Privacy Pioneer crawler (runs on Windows, but Selenium/Firefox/MySQL) > DDG Tracker Radar Collector / Leaky Forms crawler (Node/Puppeteer) > OpenWPM and its forks (Firefox, no Windows support, conda, GPL).
- OpenWPM is the gold-standard *reference design*. It is the wrong *runtime* for TraceMap: Firefox only, no Windows support, GPL-3.0, and TraceMap's mobile-Chromium requirement does not map onto it.
- The Leaky Forms leak detector is the single most directly reusable algorithm for TraceMap's canary form-leak test. Treat it as an algorithm to re-implement: the license is unclear, and parts depend on legacy packages (`sha3`, `Crypto.Hash.MD2`, `mmh3`).

### Gaps
- Per-repo recent commit messages and open-issue counts could not be pulled (GitHub API rate limit). "Last activity" reflects `pushed_at` only.
- truconsent/truscanner contents and the two Python DPDP scanners' READMEs could not be read (404 on `main`), so they are UNVERIFIED.
- BannerClick: which of `bannerclick/bannerclick` and `mohammadmahdijavid/bannerclick` is canonical was not confirmed.
- Stars and last push for the CookieBlock-Consent-Classifier and leaky-forms repos were not retrieved.

---

## Q2. Is there any single project that already covers most of TraceMap end to end?

### Takeaway
No. No single open-source project combines mobile Chromium crawling with multi-profile revisits, cookie-banner modes, JS API instrumentation, cookie-sync graphing, canary form-leak testing, an interpretable risk score and an India focus. The closest partial matches each cover 2–4 stages: OpenWPM (capture + instrumentation), Leaky Forms (form leak), consentcrawl / Vettam (banner modes + third-party inventory), and Webbkoll / PrivacyScore (UI + scoring, both archived).

### Cited Findings
- OpenWPM covers capture (HTTP, JS calls, cookies, navigations, DNS, call stacks) but is Firefox-only and does not support Windows. — [OpenWPM README](https://github.com/openwpm/OpenWPM); [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)
- consentcrawl covers before/after-consent third-party domains and cookies, CMP detection, blocklist classification and SQLite output. It has no JS API instrumentation, no form-leak test, no ID-sharing graph and no score. — [consentcrawl README](https://github.com/dumkydewilde/consentcrawl)
- Vettam covers load/accept/reject banner passes, a tracker inventory, GPC, and DPDP interpretation with certainty tiers (explicitly no severity score). It does no crawl of subpages at scale per the documented flags, no form-leak test and no ID-sharing graph. — [dpdp-cookie-scanner README](https://github.com/Vettam/dpdp-cookie-scanner)
- Leaky Forms covers form filling plus a leak detector (encodings/hashes), including a mobile configuration and consent interaction. It is Node/Puppeteer and GPL-3.0 for the crawler. — [leaky-forms](https://github.com/asumansenol/leaky-forms)
- Blacklight covers key logging, session recorders, canvas fingerprinting, FB pixel/GA events and third-party trackers over 3 pages with device emulation. It has no ID-sharing graph and is GPL-3.0. — [blacklight-collector](https://github.com/the-markup/blacklight-collector)
- Privacy Pioneer covers detection of email, phone, location and IP in traffic, plus a measurement crawler with per-country data. It is Firefox/Selenium, and the extension is under a non-commercial license. — [privacy-pioneer](https://github.com/privacy-tech-lab/privacy-pioneer); [crawler](https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler)
- priv-accept covers the fresh profile → accept → revisit pattern plus internal pages. — [priv-accept](https://github.com/marty90/priv-accept)
- PrivacyScore covered list ranking and periodic rescans; it is archived. — [PrivacyScore](https://github.com/privacyscore/privacyscore)

### Inferences
- TraceMap's novelty claim holds up. The combination is new: Playwright mobile Chromium + an ID-sharing graph + a form-leak canary + an interpretable score + an Indian corpus. The "no prior India-specific privacy measurement" angle holds against the Almanac too, which has no India section. The one India-specific tool, Vettam, is a single-URL compliance-risk CLI, not a measurement framework.
- The team should cite these projects as related work and say clearly which component each one inspired.

### Gaps
- Academic India-specific web-tracking measurements (papers, not tools) were outside this scope and were not searched.

---

## Q3. Which data schemas and approaches should TraceMap copy?

### Takeaway
Copy OpenWPM's *table decomposition and key columns*, re-implemented in your own SQLite/Postgres DDL rather than copied from their files. Copy the Englehardt / Leaky Forms *leak-detection candidate-pool* approach. Copy priv-accept's / Vettam's *multi-pass consent protocol*. Copy DDG's *collector plugin pattern*. Copy Vettam's separation of *observation vs interpretation*.

### Cited Findings
- OpenWPM per-visit keys: `browser_id`, `visit_id`, `site_visits(site_url, site_rank)` and `crawl_history(command, retry_number, command_status, error, traceback, duration)`. TraceMap can mirror these for crawl-failure accounting across 1,500 sites. — [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)
- `http_requests` columns worth mirroring: `url`, `top_level_url`, `frame_id`/`parent_frame_id`, `method`, `referrer`, `headers`, `is_third_party_channel`, `is_third_party_to_top_window`, `triggering_origin`, `loading_origin`, `req_call_stack`, `resource_type`, `post_body`, `post_body_raw`, `time_stamp`, `event_ordinal`. `post_body` is essential for form-leak detection; OpenWPM even documents `__proto__` form-field edge cases in v0.38.0. — [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql); [CHANGELOG](https://github.com/openwpm/OpenWPM/blob/master/CHANGELOG.md)
- `http_responses` (status, headers, `is_cached`, `location`, `content_hash`) and `http_redirects` (`old_request_url` → `new_request_url`). Redirect chains are where cookie-sync IDs commonly travel. — [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)
- `javascript` table: `script_url`, `script_line`, `script_col`, `func_name`, `document_url`, `top_level_url`, `call_stack`, `symbol`, `operation` (get/set/call), `value`, `arguments`. This is a ready-made schema for TraceMap's JS API-call capture (e.g., `symbol='CanvasRenderingContext2D.toDataURL'`). — [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)
- `javascript_cookies`: `record_type`, `change_cause`, `expiry`, `is_http_only`, `is_host_only`, `is_session`, `host`, `is_secure`, `name`, `path`, `value`, `same_site`, `first_party_domain`. — [schema.sql](https://github.com/openwpm/OpenWPM/blob/master/openwpm/storage/schema.sql)
- Leak detection: build a candidate pool from the canary value under many encodings (base16/32/58/64, URL-encoding, etc.) and hashes (md5, sha1, sha256, sha512, salted sha256, sha3, mmh3, ripemd160, whirlpool), including nested combinations. Search URLs, `post_body`, cookies and headers for any of them. — [Leaky Forms leak-detector](https://github.com/asumansenol/leaky-forms/tree/main/leak-detector); [LeakDetector.py](https://github.com/asumansenol/leaky-forms/blob/main/leak-detector/LeakDetector.py)
- Email-field detection with Firefox Relay's Fathom classifier found 76% more email fields than `type=email` alone. — [leaky-forms README](https://github.com/asumansenol/leaky-forms)
- Consent protocol: priv-accept does fresh profile → accept → revisit (`--pre_visit`, `--visit_internals`). Vettam's `--interact` does a "three-pass banner interaction (load, accept-all, reject-all)". consentcrawl keeps before/after screenshots and `tracking_domains_no_consent`. — [priv-accept](https://github.com/marty90/priv-accept); [Vettam](https://github.com/Vettam/dpdp-cookie-scanner); [consentcrawl](https://github.com/dumkydewilde/consentcrawl)
- Banner automation: DDG autoconsent's rules run "in a Playwright-orchestrated headless browser" with optIn/optOut. TRC exposes these as `--autoconsent-action optIn|optOut`. — [npm autoconsent](https://www.npmjs.com/package/@duckduckgo/autoconsent); [TRC README](https://github.com/duckduckgo/tracker-radar-collector)
- Collector pattern: each collector extends `BaseCollector` and implements `id()` and lifecycle hooks; `CookieCollector` is the minimal template. — [TRC README](https://github.com/duckduckgo/tracker-radar-collector)
- Observation vs interpretation: "Observation (facts) and interpretation (rules) are kept in separate modules so the facts can be trusted independently of the reading". Rules live in YAML. — [Vettam README](https://github.com/Vettam/dpdp-cookie-scanner)
- Entity mapping schema: `{name, company, homepage, category, domains[]}`. — [third-party-web entities.json](https://unpkg.com/third-party-web@latest/dist/entities.json)
- Results-page design: Webbkoll's model is to collect JSON in a backend, then show results "along with explanations and advice", per section, multilingual. — [Webbkoll README](https://codeberg.org/dataskydd.net/webbkoll)
- Almanac SQL gives off-the-shelf definitions for cross-checking TraceMap's metrics: third-party cookie domains, fingerprinting scripts, CNAME cloaking domains, GPC, referrer policy, tracker distribution. — [almanac sql/2024/privacy](https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql/2024/privacy); [sql/2025/privacy](https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql/2025/privacy)

### Inferences
- Suggested TraceMap tables:
  - `crawl` / `site_visit` (add `profile_id`, `visit_phase` ∈ {fresh_A, fresh_B, revisit}, `banner_mode` ∈ {none, accept, reject}, `page_type` ∈ {landing, subpage}, `device_profile`)
  - `http_request` / `http_response` / `http_redirect` (OpenWPM columns, plus `entity`, `category`, `etld1`, `is_third_party`)
  - `js_call` (OpenWPM `javascript` columns)
  - `cookie` (OpenWPM `javascript_cookies` columns plus `source` ∈ {http, js, cdp_snapshot})
  - `storage_item` (localStorage/sessionStorage/IndexedDB; OpenWPM has no equivalent table)
  - `id_candidate` / `id_flow` (edges for the cookie-sync graph)
  - `canary_leak` (`request_id`, `field_type`, `encoding_chain`, `location` ∈ {url, body, header, cookie})
  - `score_component`
- Cookie-sync detection approach (from the OpenWPM / Englehardt line of work, re-implemented). Treat cookie values that meet all of these as candidate IDs:
  - long enough (≥8 chars, a common heuristic)
  - stable across revisits of the same profile
  - different across fresh profiles A and B

  Then find those values in request URLs, query params, redirect URLs or POST bodies sent to a different eTLD+1. TraceMap's two-fresh-profiles + revisit design is exactly what this method needs. (Inference: the exact thresholds were not verified in this session; see Gaps.)
- Prefer CDP-level capture in Playwright (e.g., `Network.requestWillBeSentExtraInfo` for the real Cookie headers, plus init scripts that wrap JS APIs) to reproduce OpenWPM's instrumentation in Chromium.

### Gaps
- OpenWPM's own cookie-sync analysis code was not found in openwpm-utils' README. The 2016 paper's thresholds (ID length, entropy, lifetime) were not re-verified from primary text in this session; check the "Online Tracking: A 1-million-site Measurement and Analysis" paper directly.
- OpenWPM's JS instrumentation symbol list (`js_instrument_settings` / fingerprinting preset) was not fetched.

---

## Q4. Licensing implications for an Apache-2.0 project

### Takeaway
Apache-2.0 TraceMap can freely copy or bundle code and data from MIT and Apache-2.0 sources: consentcrawl, third-party-web, Vettam (code only), Lighthouse, DDG Tracker Radar Collector, Consent-O-Matic, CookieBlock and its classifier, Webbkoll, and the HTTP Archive SQL. MPL-2.0 (autoconsent, openwpm-utils) is fine if kept as separate, unmodified files or dependencies. Do **not** copy code from GPL-3.0 projects (OpenWPM, BannerClick, PrivacyScore, priv-accept, Blacklight, Leaky Forms crawler) into the repo. Do **not** bundle CC BY-NC-SA data (DDG Tracker Radar, Privacy Pioneer) or PolyForm Strict code (webXray).

### Cited Findings
- GPL-3.0: OpenWPM ("Licensed GPL v3"), BannerClick (same LICENSE), PrivacyScore (GPLv3+), priv-accept, blacklight-collector, and leaky-forms-crawler ("Licensed GPL v3"). — [OpenWPM LICENSE](https://github.com/openwpm/OpenWPM/blob/master/LICENSE); [PrivacyScore](https://github.com/privacyscore/privacyscore); [priv-accept](https://github.com/marty90/priv-accept); [blacklight-collector](https://github.com/the-markup/blacklight-collector); [leaky-forms-crawler](https://github.com/asumansenol/leaky-forms-crawler)
- MIT: consentcrawl, third-party-web, CookieBlock, CookieBlock-Consent-Classifier, Webbkoll, Consent-O-Matic, privacyscanner (PyPI), devbret scanner, Privacy Pioneer **web crawler**. — respective LICENSE files / API metadata cited in Q1
- Apache-2.0: Lighthouse, HTTP Archive almanac and custom-metrics, DDG tracker-radar-collector, and Vettam code. — cited in Q1
- MPL-2.0: `@duckduckgo/autoconsent`, openwpm-utils. — [npm autoconsent](https://www.npmjs.com/package/@duckduckgo/autoconsent); [PyPI openwpm-utils](https://pypi.org/project/openwpm-utils/)
- CC BY-NC-SA 4.0: DDG Tracker Radar data ("Licensed under the CC BY-NC-SA 4.0 license") and the Privacy Pioneer extension. — [tracker-radar LICENSE](https://github.com/duckduckgo/tracker-radar); [privacy-pioneer LICENSE](https://github.com/privacy-tech-lab/privacy-pioneer)
- PolyForm Strict 1.0.0: webXray ("Commercial use of webXray is prohibited, as is redistributing the code"). — [webXray mirror](https://github.com/thezedwards/webXray)
- Vettam: code Apache-2.0, but `trackers/` is CC BY-SA 4.0, rule rationale text is CC BY-ND 4.0, and the names "Vettam"/"Sentinel" may not be used by forks. — [Vettam README](https://github.com/Vettam/dpdp-cookie-scanner)
- Leaky Forms main repo (leak detector): no root LICENSE was found (raw `LICENSE` 404). The Englehardt `citp/email_tracking` repo also has no root LICENSE (404). — [leaky-forms](https://github.com/asumansenol/leaky-forms); [citp/email_tracking](https://github.com/citp/email_tracking)

### Inferences
- **GPL-3.0.** Apache-2.0 code can flow into a GPLv3 work, but not the reverse. Copying OpenWPM/BannerClick/Blacklight code into TraceMap would force the combined distribution to GPLv3. Reading these projects and re-implementing their *ideas* (schemas, heuristics, algorithms) is fine, because copyright does not cover ideas or column names. Running them as separate, unmodified external programs and reading their output files is also generally fine.
- **CC BY-NC-SA (DDG Tracker Radar).** It can be used *for the non-commercial academic study* if downloaded at runtime, kept in a separate folder with attribution, and not relicensed. It must not be merged into an Apache-licensed bundled entity list, and derived lists would inherit NC-SA. Safer default: third-party-web (MIT), plus a self-curated India supplement under Apache-2.0 or CC BY 4.0.
- **CC BY-SA (Vettam `trackers/`).** It can be used with attribution, but any derived tracker list must stay CC BY-SA. Keep it as a separate data file with its own license notice. Do not copy Vettam's rule rationale text (CC BY-ND); write your own DPDP explanations.
- **No-license code (leak-detector).** By default all rights are reserved. Re-implement from the paper's described method (encodings/hashes pool), or email the authors for permission.
- **MPL-2.0 (autoconsent).** Using it as an npm dependency or an injected script file is fine. Modifications to MPL files must stay MPL, and only at file level.
- Add a `THIRD_PARTY_NOTICES` / `NOTICE` file listing every bundled MIT/Apache/MPL component and data source.

### Gaps
- Whether the bannerclick/bannerclick fork adds its own license text beyond OpenWPM's was not checked.
- Licensing of the Fathom email-classifier model from Firefox Relay (MPL-2.0 is expected for Mozilla, but this was not verified here; UNVERIFIED).

---

## Q5. Recommendation per candidate (fork / wrap / port ideas / ignore)

### Takeaway
Do not fork any framework. Build on Playwright directly. Then:
- **Wrap** third-party-web (entity list) and DDG autoconsent (banner modes).
- **Optionally wrap** Lighthouse as a Node sidecar for performance attribution.
- **Port ideas** from OpenWPM (schema, instrumentation), Leaky Forms (leak detector), priv-accept / Vettam / consentcrawl (consent passes, CMP selectors), Blacklight (key-logging and session-recorder tests), Webbkoll (results-page UX), PrivacyScore (list ranking and rescans) and Vettam (DPDP rule mapping).
- **Ignore** webXray and the stale DPDP student repos.

### Cited Findings
(Facts underpinning each recommendation are cited in Q1–Q4. This section is primarily the decision layer.)

| Candidate | Recommendation | Rationale (with key fact) |
|---|---|---|
| **OpenWPM** | **Port ideas** (schema + instrument list); do not fork or run | Firefox/Selenium, "does not support windows", GPL v3, conda; but it is the canonical schema and the most-cited framework — [README](https://github.com/openwpm/OpenWPM) |
| openwpm-utils | Ignore | Last push 2021; parsing helpers only — [repo](https://github.com/openwpm/openwpm-utils) |
| **consentcrawl** | **Port ideas / selectively vendor** (MIT): `consent_managers.yml` CMP selectors, blocklist bootstrap, before/after-consent diff | Same stack (Python + Playwright); alpha; PyPI last 2024-03 — [README](https://github.com/dumkydewilde/consentcrawl) |
| Privacy Pioneer crawler | Port ideas (analysis notebooks, per-country design, accept vs no-action experiment) | Selenium/Firefox/MySQL; crawler MIT but detection logic lives in the CC BY-NC-SA extension — [crawler](https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler) |
| Privacy Pioneer extension | Port ideas only (email/phone/location/IP watch-list detection) | CC BY-NC-SA 4.0 — [LICENSE](https://github.com/privacy-tech-lab/privacy-pioneer) |
| webXray | **Ignore** | Original repo unreachable; PolyForm Strict forbids redistribution — [mirror](https://github.com/thezedwards/webXray) |
| PrivacyScore / privacyscanner | Port ideas (list comparison/ranking, periodic rescans, scan-module layout) | Archived/stale; GPL (PrivacyScore) — [README](https://github.com/privacyscore/privacyscore) |
| Webbkoll | Port ideas (results-page layout: per-check explanation + advice, multilingual) | Archived; MIT — [Codeberg](https://codeberg.org/dataskydd.net/webbkoll) |
| CookieBlock + classifier | **Optional wrap** (MIT classifier) for cookie-purpose labels (necessary / functional / analytics / advertising) as a risk-score feature; otherwise port ideas | Stale since 2023; trained on GDPR-era CMP data — [CookieBlock](https://github.com/dibollinger/CookieBlock); [Classifier](https://github.com/dibollinger/CookieBlock-Consent-Classifier) |
| CookieBlock Consent Crawler | Ignore (OpenWPM v0.12 fork) | — [repo](https://github.com/dibollinger/CookieBlock-Consent-Crawler) |
| BannerClick | Port ideas (DOM-containment banner localisation, iframe traversal, accept/reject) | OpenWPM fork, GPL, low activity — [arXiv](https://arxiv.org/abs/2310.01108) |
| priv-accept | Port ideas (multilingual accept-keyword list concept, fresh → accept → revisit, internal pages) | GPL-3.0, Selenium, stale — [repo](https://github.com/marty90/priv-accept) |
| **DDG autoconsent** | **Wrap** (inject into Playwright for accept / reject / none modes) | MPL-2.0, published 2026-10-07, designed for Playwright — [npm](https://www.npmjs.com/package/@duckduckgo/autoconsent) |
| DDG Tracker Radar Collector | Port ideas (collector plugin architecture, `--only-3p`) | Node/Puppeteer, Apache-2.0 — [README](https://github.com/duckduckgo/tracker-radar-collector) |
| DDG Tracker Radar data | Use only as a runtime-downloaded, attributed, non-commercial research input, or ignore | CC BY-NC-SA 4.0 — [LICENSE](https://github.com/duckduckgo/tracker-radar) |
| **Leaky Forms leak detector** | **Port ideas** (re-implement the encoding/hash candidate pool in Apache-2.0 Python) | Exactly matches the canary test; no license file; crawler GPL — [leak-detector](https://github.com/asumansenol/leaky-forms/tree/main/leak-detector) |
| Blacklight collector | Port ideas (key_logging, session_recorders, canvas fingerprinting, FB pixel/GA event tests) | GPL-3.0, Puppeteer — [README](https://github.com/the-markup/blacklight-collector) |
| **third-party-web** | **Wrap / bundle** (MIT) as the primary entity → company → category map; add an India supplement | 2,143 entities; missing MoEngage, Razorpay, Paytm, Netcore, Juspay, Cashfree, Colombia etc. — [entities.json](https://unpkg.com/third-party-web@latest/dist/entities.json) |
| HTTP Archive Almanac SQL / custom metrics | Port ideas (metric definitions, privacy.js keys); cite as baseline comparison | Apache-2.0; no India section — [Almanac 2025](https://almanac.httparchive.org/en/2025/privacy) |
| **Lighthouse** | **Optional wrap** as a Node CLI sidecar (`third-parties-insight`, `third-party-cookies`) on a sample of sites | v13 removed `third-party-facades` and replaced `third-party-summary`; Node >=22.19 — [changelog](https://github.com/GoogleChrome/lighthouse/blob/main/changelog.md) |
| **Vettam dpdp-cookie-scanner** | **Port ideas** (DPDP rule mapping with certainty tiers, three-pass interaction, observation/interpretation split); optionally run as an external CLI for cross-validation on a subset; cite as closest Indian prior art | Apache-2.0 code but CC BY-SA trackers and CC BY-ND rule text; trademark restriction — [README](https://github.com/Vettam/dpdp-cookie-scanner) |
| Small Python/Playwright scanners (devbret, truscanner, Divith23, Sarvesh8521) | Ignore (glance at devbret for a cookie-diff idea) | Toy-scale, unlicensed or unverified — GitHub search |
| mitmproxy-based analyzers | Ignore (none found); Playwright/CDP capture is sufficient | GitHub search found nothing relevant |

### Inferences
- **Minimal reuse stack:** Playwright (Python) + a custom CDP/init-script instrumentation modelled on OpenWPM's tables + `@duckduckgo/autoconsent` injected for banner modes + `third-party-web` entities.json (+ India supplement) + a re-implemented Englehardt / Leaky Forms leak detector + consentcrawl's CMP selector YAML as a fallback. Everything in this stack is MIT, Apache-2.0 or MPL-2.0, which keeps TraceMap cleanly Apache-2.0.
- **Lighthouse caveat for Windows/Python:** it needs Node ≥22.19, and its third-party output is now an "insight" built on trace_engine. Run it via `subprocess` (`npx lighthouse --output=json --form-factor=mobile`) on a sample (e.g., 100–200 sites), not all 1,500 × visit-phase combinations.
- **Score design:** take inspiration from Vettam's "certainty tier, no severity" framing for the legal layer. Keep TraceMap's own interpretable risk score separate and transparent (component weights listed), echoing PrivacyScore's per-check approach and Webbkoll's explanation-plus-advice presentation.

### Gaps
- Not checked in this session: whether the autoconsent rules cover the CMPs most common on Indian sites (e.g., CookieYes and others). It is worth a pilot on 50 Indian sites.
- Not checked in this session: Lighthouse's exact CLI flags and JSON paths for `third-parties-insight`.
