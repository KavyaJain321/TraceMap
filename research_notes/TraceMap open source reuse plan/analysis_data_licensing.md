# TraceMap — open-source analysis code, corpus datasets, and licensing/interop (as of 7 Oct 2026)

(Saved by coordinator from researcher hand-back. Licenses checked via raw LICENSE files + PyPI JSON API; GitHub API was rate-limited so no stars/commit dates. Not legal advice.)

## Q1. Cookie-sync / user-ID detection code — which has the most reusable Python ID-extraction logic?

### Takeaway
Only vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites (MIT; 103 Indian news sites) has usable Python ID-extraction code: a "Cookie Synchronization" folder of Englehardt-style scripts. Its defaults deviate from Englehardt & Narayanan 2016 and their provenance is uncertain. citp/OpenWPM-analysis does not exist (404); no public code found for Papadopoulos (CONRAD), Fouad et al., or CrumbCruncher; PURL is GPL-3.0; CookieGraph has no LICENSE.

### Cited findings
- Englehardt & Narayanan 2016 criteria: (cookie-name, parameter-name, value) tuple is an ID cookie if (1) expiry > 90 days, (2) 8 ≤ len ≤ 100, (3) constant throughout the measurement, (4) differs between two synchronized machines by Ratcliff-Obershelp similarity < 66%; values split on characters outside `a-zA-Z0-9 -=` — https://www.cs.princeton.edu/~arvindn/publications/OpenWPM_1_million_site_tracking_measurement.pdf
- vibhor98 license MIT; `Cookie Synchronization/` folder contains census_util.py, extract_cookie_ids.py, extract_id_knowledge.py, ccs_sync_measurements.py, classify_domains.py, final_cs_analysis.py, find_site_leaning.py — https://raw.githubusercontent.com/vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites/main/LICENSE ; https://github.com/vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites/tree/main/Cookie%20Synchronization
- extract_cookie_ids.py defaults num_days=30, short_cutoff=11, long_cutoff=100, sim=.33 (vs paper's 90 days, 8 chars, <0.66); splits only on ':' and '&'; requires ≥2 crawls and equal length; reads OpenWPM `javascript_cookies`; builds SQL by string concatenation — https://raw.githubusercontent.com/vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites/main/Cookie%20Synchronization/extract_cookie_ids.py
- census_util.py uses difflib.SequenceMatcher and tldextract; extract_domain relies on a dataset-specific WHOIS map — https://raw.githubusercontent.com/vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites/main/Cookie%20Synchronization/census_util.py
- extract_id_knowledge.py builds ID→domains-that-know-it map from cookies, request URLs + referrers, and response `location` redirects, plus inverse map — effectively TraceMap's identifier-flow edge list — https://raw.githubusercontent.com/vibhor98/Web-Tracking-in-Indian-Partisan-News-Websites/main/Cookie%20Synchronization/extract_id_knowledge.py
- vibhor98 dataset is request-form only: "non-profit research or non-profit education", no re-identification, sharing limited to immediate group, citation required — https://netsys.surrey.ac.uk/datasets/india-tracking
- openwpm-utils: MPL-2.0; last PyPI release 0.2.0 (June 2019); analysis.py has only generic helpers (get_cookie, get_set_cookie, get_requests_from_visits, callstack helpers), no ID detection — https://raw.githubusercontent.com/openwpm/openwpm-utils/master/LICENSE ; https://raw.githubusercontent.com/openwpm/openwpm-utils/master/openwpm_utils/analysis.py
- OpenWPM: "Licensed GPL v3" — https://raw.githubusercontent.com/openwpm/OpenWPM/master/LICENSE
- Princeton Web Census data available by email request; no data license stated; no analysis-code repo linked — https://webtransparency.cs.princeton.edu/webcensus/data-release/
- 404s: citp/OpenWPM-analysis, citp/openwpm-analysis, uiowa-irl/crumbcruncher, uiowa-irl/purl, uiowa-irl/CookieGraph, imanefouad/missed-by-filter-lists (guess).
- PURL at shaoormunir/purl is GPL-3.0; needs customized OpenWPM, Ubuntu 18.04+, 64GB+ RAM — https://raw.githubusercontent.com/shaoormunir/purl/main/LICENSE
- CookieGraph at shaoormunir/cookiegraph uses custom OpenWPM; no LICENSE/LICENSE.md on main or master — https://raw.githubusercontent.com/shaoormunir/cookiegraph/main/README.md
- CrumbCruncher: authors say they release "complete dataset and measurement pipeline" but no URL on Brave page or arXiv PDF; token rule: discard only if identical across users; length > 8; no length-similarity limit — https://brave.com/research/measuring-uid-smuggling-in-the-wild/ ; https://arxiv.org/pdf/2203.10188
- CONRAD (Papadopoulos): no code link — https://arxiv.org/pdf/1805.10505
- "Cookie Synchronization HTTP Requests" dataset at Edinburgh DataShare (found in search, not fetched) — https://datashare.ed.ac.uk/handle/10283/4411
- Smith 2022 review notes "a lack of consistency among implementations" of detection — https://arxiv.org/pdf/2301.02619
- Fouad et al.: no code found — https://www.petsymposium.org/popets/2020/popets-2020-0038.php

### Inferences
- Write a clean module using the paper as spec with vibhor98 as reference: 90 days / 8–100 / <0.66 sim; paper's delimiter rule; parameterised SQL; replace WHOIS map with PSL eTLD+1 + entity map; add revisit stability check.
- vibhor98 census scripts may derive from earlier Princeton code — if that was GPL, the MIT label may be shaky (UNVERIFIED).
- Report CrumbCruncher's looser rule as a sensitivity variant.
- PURL/CookieGraph: ideas only.

## Q2. PII / canary leak detection code

### Takeaway
Leaky Forms' LeakDetector.py is the most complete implementation (3 encoding layers, 11 encodings, ~18 hashes, URL/referrer/cookie/POST search) but neither it nor its upstream citp/email_tracking has a LICENSE → all rights reserved. Reimplement from the published method.

### Cited findings
- leaky-forms repo contains analysis/, leak-detector/, README.md; no LICENSE file and no license in README — https://github.com/leaky-forms/leaky-forms
- LeakDetector.py header: based on Englehardt, Han & Narayanan's PETS 2018 email-tracking code; ENCODING_LAYERS = 3; encodings base16, base32, base58, base64, urlencode, entity, deflate, zlib, gzip, lzstring, custom_map_1; hashes md2, md4, md5, sha1, sha2 family, sha3 family, mmh3 (64_1, 64_2, 128), ripemd160, whirlpool, sha_salted_1; imports Crypto.Hash.MD2, sha3, mmh3, base58, lzstring — https://raw.githubusercontent.com/leaky-forms/leaky-forms/main/leak-detector/LeakDetector.py
- Method (leak-detector README): precompute pool of canary hash/encoding combinations; split request contents on separators; apply decodings; repeat up to three layers; tracker labelling via Disconnect + WhoTracks.me; Node script for DDG TDS and uBlock checks — https://raw.githubusercontent.com/leaky-forms/leaky-forms/main/leak-detector/README.md
- citp/email_tracking: no LICENSE file; README targets Ubuntu 16.04 — https://github.com/citp/email_tracking
- choosealicense: without a license "nobody else can copy, distribute, or modify your work without being at risk of take-downs, shake-downs, or litigation" — https://choosealicense.com/no-permission/
- Blacklight GPL-3.0; key-logging hashes input values one level only: base64, md5, sha256, sha512 — https://raw.githubusercontent.com/the-markup/blacklight-collector/main/src/inspectors/key-logging.ts ; https://raw.githubusercontent.com/the-markup/blacklight-collector/main/src/helpers/utils.ts
- pysha3 abandoned (1.0.2, 2017, Python ≤3.5; backport of the stdlib SHA-3 module added in 3.6) — https://pypi.org/pypi/pysha3/json
- Permissive deps: pycryptodome 3.24.0 BSD/Public Domain; mmh3 5.3.1 MIT (Python ≥3.10); base58 2.1.1 MIT; lzstring 1.0.4 MIT. `hashid` is GPLv3+ (avoid).
- No "PIIxel Leaks" code found; no Python hash-chain package found.

### Inferences
- Clean-room Apache-2.0 module: canary token pool (email, +91 phone variants), 3-layer search.
- Python 3.11: use hashlib.sha3_* (not `import sha3`); pycryptodome for MD2/MD4/RIPEMD-160 (hashlib.new('md4') may be unavailable under OpenSSL 3 — test); Whirlpool optional.
- Phone forms to precompute: +91XXXXXXXXXX, 91…, 0…, 10-digit, spaced/dashed variants (design suggestion).

## Q3. Graph analysis

### Takeaway
On Python 3.11 the only permissively licensed Leiden is graspologic-native (MIT, Windows wheels). NetworkX has a built-in Leiden only from 3.7 (Python ≥3.12); in 3.6.1 it needs a backend. leidenalg is GPL-3.0-or-later; igraph license file is GPLv2 text. Use networkx (BSD) for Louvain, centrality, rewired null models; cdlib (BSD-2) for partition comparison.

### Cited findings
- leidenalg 0.12.0 (May 2026), GPL-3.0-or-later; find_partition(..., n_iterations=2, seed=None), Optimiser, CPMVertexPartition, RBConfigurationVertexPartition — https://pypi.org/pypi/leidenalg/json ; https://leidenalg.readthedocs.io/en/stable/reference.html
- igraph 1.0.0 (Oct 2025), Python 3.11 OK; Python package + C core license files contain GPL v2 text ("or later" UNVERIFIED) — https://pypi.org/pypi/igraph/json ; https://raw.githubusercontent.com/igraph/igraph/master/COPYING
- graspologic 3.4.4, MIT, Python 3.9–3.12, pins numpy<2, statsmodels<0.15, gensim, umap-learn, POT; leiden(... resolution, randomness, random_seed, trials) undirected only; hierarchical_leiden — https://pypi.org/pypi/graspologic/3.4.4/json ; https://graspologic-org.github.io/graspologic/reference/reference/partition.html
- graspologic-native 1.3.1, MIT, wheels Python 3.9+ incl. win_amd64; Rust Leiden behind graspologic — https://pypi.org/pypi/graspologic-native/json ; https://raw.githubusercontent.com/microsoft/graspologic-native/main/README.md
- NetworkX 3.7 (Sep 2026) requires Python ≥3.12; 3.6.1 requires ≥3.11; BSD-3 — https://pypi.org/pypi/networkx/json
- NetworkX 3.7 release notes: "Leiden based community detection algorithms are now supported via leiden_communities"; 3.6.1 docs: function "does not have a default NetworkX implementation" — https://networkx.org/documentation/stable/release/release_3.7.html ; https://networkx.org/documentation/networkx-3.6.1/reference/algorithms/generated/networkx.algorithms.community.leiden.leiden_communities.html
- networkx degree-preserving null models: double_edge_swap, directed_edge_swap, connected_double_edge_swap — https://networkx.org/documentation/stable/reference/algorithms/swap.html
- cdlib 0.4.1 (Jul 2026), BSD-2; evaluation includes AMI, NMI, variation of information, adjusted Rand, Rand, omega, F1 — https://cdlib.readthedocs.io/en/latest/reference/evaluation.html
- Python 3.11 ceilings: scipy 1.17.1; numpy 2.4.6; pandas 3.0.x OK.

### Inferences
- networkx 3.6.1 + graspologic-native directly (avoid full graspologic's numpy<2 pin) + cdlib for multi-seed stability.
- Symmetrise for community detection; keep directed graph for PageRank/in-out strength.
- Implement co-association consensus with numpy.
- If leidenalg needed (CPM/resolution sweep), isolate as separate GPL CLI.
- Moving to Python 3.12 would give networkx 3.7's built-in Leiden.
- Gaps: graspologic-native exact Python signature unverified; cdlib transitive deps (igraph/leidenalg?) unchecked.

## Q4. Interpretable ML & composite index
- interpret 0.7.8 (Mar 2026), Python 3.10–3.14, MIT; ExplainableBoostingClassifier/Regressor, MorrisSensitivity, measure_interactions — https://pypi.org/pypi/interpret/json ; https://raw.githubusercontent.com/interpretml/interpret/main/LICENSE ; https://interpret.ml/docs/ebm.html
- optbinning 1.0.0 (Sep 2026), Apache-2.0, Python ≥3.11; Scorecard(binning_process, estimator, scaling_method, ...) binary/continuous target — https://pypi.org/pypi/optbinning/json ; https://gnpalencia.org/optbinning/scorecard.html
- SALib 1.6.0 (Sep 2026), MIT; saltelli.sample → sobol.analyze — https://pypi.org/pypi/SALib/json ; https://salib.readthedocs.io/en/latest/api/SALib.analyze.html
- COINr (R) covers full composite-indicator workflow incl. Monte Carlo variance-based SA — https://cran.r-project.org/web/packages/COINr/vignettes/sensitivity.html
- Python "CIF" mentioned only in a search summary — UNVERIFIED.
- Inferences: treat weights, normalisation, aggregation, ID thresholds as SALib factors; report Sobol S1/ST on rank shifts. EBM to explain drivers; scorecard stays transparent additive. optbinning Scorecard needs a labelled target — otherwise use binning only.

## Q5. Statistics
- scikit-posthocs 0.17.0 (Sep 2026), MIT, posthoc_dunn — https://pypi.org/pypi/scikit-posthocs/json ; https://scikit-posthocs.readthedocs.io/en/latest/generated/scikit_posthocs.posthoc_dunn.html
- statsmodels 0.15.0, BSD-3, Python ≥3.10; NegativeBinomial(endog, exog, loglike_method='nb2', offset, exposure), no intercept by default — https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html
- pingouin 0.7.0 GPL-3.0 (avoid) — https://pypi.org/pypi/pingouin/json ; https://raw.githubusercontent.com/raphaelvallat/pingouin/main/LICENSE
- Inferences: NB2 with sector dummies + exposure, report IRRs; Holm/BH on Dunn; compute ε² and Cliff's delta manually.

## Q6. Corpus datasets
- zakird/crux-top-lists: origins by rank bucket, shuffled within bucket; monthly; country query uses BigQuery `chrome-ux-report.experimental.country`; repo has no LICENSE, calls itself "a cache"; no current.csv.gz for countries — https://raw.githubusercontent.com/zakird/crux-top-lists/main/README.md ; https://github.com/zakird/crux-top-lists/tree/main/data/country/in
- Analysis of 202608 India file: columns origin,rank; buckets 1k:1,000; 5k:4,000; 10k:5,000; 50k:40,000; 100k:50,000; 500k:400,000; 1M:500,000; 15,891 .gov.in, 1,703 .nic.in, 15,509 .ac.in, 6,925 .edu.in; 4,000 contain "bank"; top bucket includes adult sites — https://raw.githubusercontent.com/zakird/crux-top-lists/main/data/country/in/202608.csv.gz
- Google: "CrUX datasets by Google are licensed under a Creative Commons Attribution 4.0 International License" (Tranco lists CrUX as CC BY-SA 4.0 — conflict; Google authoritative) — https://developer.chrome.com/docs/crux/methodology ; https://tranco-list.eu/
- Tranco: permanent citable IDs; no country lists; `tranco` package MIT; Cloudflare Radar data CC BY-NC 4.0 per Tranco — https://tranco-list.eu/
- Cloudflare Radar: top-100 per country daily; API data CC BY-NC 4.0 (search snippet) — https://developers.cloudflare.com/radar/investigate/domain-ranking-datasets/
- IGOD run by NIC; /sectors HTML only, no CSV/API found — https://igod.gov.in/about_us ; https://igod.gov.in/sectors
- RBI "Banks in India", UGC university page and UGC consolidated PDF return 200; NMC and AICTE URLs tried 404.
- ComplyZero 2026: industry, not peer-reviewed; 6,000+ sites, 24 sectors, headless Chromium; "only 2 out of 1,154" gov sites had consent notices; no data download stated — https://www.complyzero.com/research/state-of-cookie-compliance-india-2026 ; https://news.webindia123.com/news/Articles/Business/20260331/4433674.html
- Götze et al. WebSci 2022: 5,500 G20 sites incl. India; no dataset link — https://research.tudelft.nl/en/publications/measuring-web-cookies-in-governmental-websites ; https://networks.imdea.org/up-to-90-of-governmental-websites-include-cookies-of-third-party-trackers/
- Inferences: rank ≤100k, sector-label, ~250/sector × 6 ≈ 1,500; pin + cite CrUX month; rank as ordered categorical; release list CC BY 4.0 with CrUX attribution; keep Cloudflare Radar out of anything released non-NC.
- Gaps: no machine-readable IGOD/NMC/AICTE lists; HTTP Archive India subsets not examined; ComplyZero reuse terms unknown.

## Q7. Licensing/interop — practical do/don't (not legal advice)

### Cited findings
- FSF GPL FAQ: mere aggregation — "Pipes, sockets and command-line arguments … normally are separate programs" https://www.gnu.org/licenses/gpl-faq.html#MereAggregation ; linking to a GPL library — "the program actually links to the library … GPL apply to the entire combination" #IfLibraryIsGPL ; plug-ins sharing function calls/data structures = "a single combined program" #GPLPlugins ; interpreted programs using GPL facilities "must be released in a GPL-compatible way" #IfInterpreterIsGPL ; private modifications OK "use them privately, without ever releasing them" #GPLRequireSourcePostedPublic ; "The output of a program is not, in general, covered by the copyright on the code" #GPLOutput
- FSF license list: Apache-2.0 "compatible with version 3 of the GNU GPL … not compatible with GPL version 2" (#apache2); MPL-2.0 indirectly GPL-compatible via §3.3, MPL files stay dual-licensed (#MPL-2.0); CC BY-SA 4.0 one-way compatible with GPLv3 (#ccbysa); CC NonCommercial licenses are non-free (#CC-BY-NC) — https://www.gnu.org/licenses/license-list.html
- MPL 2.0 FAQ: copyleft "applies to any files containing MPLed code"; combining allowed; for minified JS must "inform the recipients … how they can obtain a copy of the source code"; notices via Exhibit A or SPDX — https://www.mozilla.org/en-US/MPL/2.0/FAQ/
- autoconsent MPL-2.0 — https://raw.githubusercontent.com/duckduckgo/autoconsent/main/LICENSE
- Tracker Radar & tracker-blocklists (TDS) CC BY-NC-SA 4.0 — https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/LICENSE ; https://raw.githubusercontent.com/duckduckgo/tracker-blocklists/main/LICENSE ; Disconnect CC BY-NC-SA 4.0 — https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/LICENSE ; Ghostery TrackerDB CC BY-NC-SA 4.0 — https://raw.githubusercontent.com/ghostery/trackerdb/main/LICENSE
- CC BY-NC-SA 4.0: NonCommercial = "not primarily intended for or directed towards commercial advantage"; §4 sui generis database rights allow extracting substantial portions for NonCommercial; a database containing a substantial portion "is Adapted Material" (ShareAlike applies) — https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en
- CC FAQ: "CC licenses do not contractually impose restrictions on uses of a work where there is no underlying copyright" — https://creativecommons.org/faq/
- EasyList/EasyPrivacy "dual licensed under Creative Commons Attribution-ShareAlike and the GNU General Public License"; GitHub repo has no LICENSE file — https://easylist.to/pages/about.html

| Situation | Do | Don't |
|---|---|---|
| OpenWPM, blacklight-collector (GPL-3.0) | Run as separate processes/containers exchanging files/SQLite/CLI args; ship their source + license if you distribute a container | Copy their source into the Apache-2.0 tree; import OpenWPM internals in core |
| Crawl output | Treat as data (#GPLOutput) | Assume output inherits GPL |
| leidenalg / igraph / pingouin (GPL) | Prefer graspologic-native, networkx, scikit-posthocs; else separate GPL-3.0 plugin/CLI via files/JSON | `import leidenalg` in core distributed as Apache-only; combine with GPLv2-only code |
| Private runs | No source-release duty | Forget publishing a package/container = distribution |
| autoconsent bundle (MPL-2.0) | Keep MPL header/SPDX, NOTICE with upstream source repo + tag, changes stay in MPL files | Strip headers or relabel Apache-2.0 |
| openwpm-utils (MPL-2.0) | Use as dependency or copy into separate MPL files | Paste MPL code into Apache files |
| Tracker Radar/TDS, Disconnect, Ghostery (NC-SA) | Label with attribution; derived tables with substantial portions released CC BY-NC-SA 4.0 in separate data/third_party/ with own LICENSE; aggregate stats/findings free | Release combined data as CC BY/CC0; commercial spin-off without license |
| EasyList/EasyPrivacy | Fetch at runtime + attribute; modified list redistributed under CC BY-SA or GPL | Relicense as Apache-2.0 |
| Leaky Forms, email_tracking, CookieGraph (no license) | Read for method, clean reimplementation, cite; or ask authors for license | Copy code verbatim |
| PURL (GPL-3.0) | Cite, reimplement ideas | Vendor code |
| vibhor98 scripts (MIT) | Adapt with MIT notice in NOTICE, re-parameterise to paper | Assume clean provenance — rewrite is safer |
| CrUX lists (CC BY 4.0) | Redistribute with attribution + month | Mix in Cloudflare Radar (CC BY-NC) |

### Inferences
- Process-boundary design: crawler containers emit SQLite/Parquet; separate Apache-2.0 Python analysis package reads them.
- Python import = derivative work is contested; follow FSF conservative reading.
- NC: college project is non-commercial, but NC propagates to downstream users of released data — keep NC-derived columns in a separately licensed file.

## Q8. Recommended analysis stack

| Step | Component | License | Version | Reuse mode | Gotchas |
|---|---|---|---|---|---|
| ID cookies / cookie sync | Englehardt & Narayanan 2016 spec + vibhor98 as reference | MIT (vibhor98) | 2021 | Clean rewrite | Re-parameterise; provenance |
| ID helpers | openwpm-utils | MPL-2.0 | 0.2.0 (2019) | Optional dep | Generic only |
| PII leaks | Clean-room Leaky Forms method | Apache-2.0 (yours) | – | Write | Original unlicensed; pysha3 dead |
| Hashing | pycryptodome, mmh3, base58, lzstring | BSD/PD, MIT, MIT, MIT | 3.24.0 / 5.3.1 / 2.1.1 / 1.0.4 | Deps | — |
| Graph/centrality/nulls | networkx 3.6.1 | BSD-3 | 3.7 needs py3.12 | Dep | Pin 3.6.1 for 3.11 |
| Leiden | graspologic-native | MIT | 1.3.1 | Dep | Undirected only |
| Leiden (alt) | leidenalg/igraph | GPL | 0.12.0 / 1.0.0 | Separate GPL plugin | Apache vs GPLv2 incompatible |
| Partition stability | cdlib | BSD-2 | 0.4.1 | Dep | Check transitive GPL deps |
| Explainable model | interpret | MIT | 0.7.8 | Dep | — |
| Binning | optbinning | Apache-2.0 | 1.0.0 | Dep | Scorecard needs target |
| Sensitivity | SALib | MIT | 1.6.0 | Dep | Build COINr-style steps |
| Stats | scipy, scikit-posthocs, statsmodels | BSD, MIT, BSD-3 | 1.17.1 (3.11 cap), 0.17.0, 0.15.0 | Deps | No pingouin |
| Corpus | CrUX India | CC BY 4.0 | 202608 | Data | Buckets only; adult sites |
| Tracker labels | Tracker Radar/TDS, Disconnect, Ghostery | CC BY-NC-SA 4.0 | Active | NC-SA data | NC + SA |
| Tracker labels | EasyList/EasyPrivacy | GPL or CC BY-SA | 7 Oct 2026 | Data | Attribution; SA if modified |

Pins (Python 3.11): numpy<2.5, scipy<1.18, networkx==3.6.1, graspologic-native>=1.3, cdlib, interpret>=0.7, optbinning>=1.0, SALib>=1.5, scikit-posthocs, statsmodels, tldextract, pycryptodome, mmh3, base58, lzstring; GPL packages in separate optional [gpl] package.

Biggest single risk: neither core method (2016 ID detection, Leaky Forms leak detection) has a clean, permissively licensed, maintained Python implementation — budget a tested reimplementation with unit tests on synthetic cookies and known canaries (e.g., email→sha256→base64, 3 layers).

Gaps: repo activity (GitHub rate-limited; re-check with gh api); CrumbCruncher/CONRAD/Fouad code; HTTP Archive India subsets; NMC/AICTE machine-readable lists; cdlib dependencies.
