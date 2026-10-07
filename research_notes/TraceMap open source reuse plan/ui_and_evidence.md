# Open-source UI, visualization and evidence-report reuse for TraceMap

Research date: 2026-10-07. Repo metadata (license, last push, stars) was pulled from the GitHub API, repos.ecosyste.ms (a GitHub metadata mirror), the npm/PyPI registries and the code.europa.eu GitLab API during this session. "Last push" is the repo's `pushed_at` value, which shows recent activity but not release health. Items marked UNVERIFIED could not be confirmed from a primary source in this session.

## Key Question 1: For each candidate: URL, license, stack, 2025-2026 activity, which TraceMap screen it serves, reuse mode

### Takeaway
Almost all of the privacy-specific tools (Lightbeam, Blacklight, Exodus, PrivacyScore, Webbkoll, Request Map) are either copyleft (MPL/GPL/AGPL/EUPL), archived, or have no public front-end. Use them as design references only. The code TraceMap can actually embed is the permissively licensed general libraries: Cytoscape.js + fCoSE (MIT), PerfCascade (MIT), Recharts (MIT) / ECharts (Apache-2.0), FastAPI's built-in SSE, and bagit-python (CC0). The DuckDuckGo Privacy Dashboard (Apache-2.0) is the one permissive privacy UI, but it is coupled to DDG's data model, so treat it as a design reference too.

### Cited Findings

#### A. Privacy and tracking scanner UIs (design references)

- **Simon Hearne's Request Map** (https://requestmap.webperf.tools/): builds a node map of every request a page makes, to show third parties. It runs on WebPageTest agents with 30+ test locations, and the page credits "Simon" (@simonhearne) with a blog link to simonhearne.com/2015/find-third-party-assets/. The page shows no GitHub link and no license. — [requestmap.webperf.tools](https://requestmap.webperf.tools/)
  - The page's HTML references the `vis` library, so the map is very likely vis.js / vis-network. This was found by grepping the page source and has not been confirmed in code. — [requestmap.webperf.tools](https://requestmap.webperf.tools/)
  - The source repo was NOT FOUND. github.com/simonhearne/request-map, /requestmap and /request-map-generator all return 404. His related public repos are `simonhearne/webperf.tools` (MIT, last push 2017-02), `third-party-web` (MIT, 2023-11) and `third-party-impact` (no license, 2022-12). Whether any of these contains the current Request Map generator is UNVERIFIED. — [repos.ecosyste.ms owner listing](https://repos.ecosyste.ms/api/v1/hosts/GitHub/owners/simonhearne/repositories)
  - Reuse mode: design reference only. Borrow the concept of a force-directed request map with node size by request count and color by domain type.
- **Mozilla Lightbeam (original)** (https://github.com/mozilla/lightbeam): MPL-2.0, JavaScript, **archived**, last push 2017-03-22. — [GitHub API](https://api.github.com/repos/mozilla/lightbeam)
- **Mozilla lightbeam-we** (https://github.com/mozilla/lightbeam-we): MPL-2.0, last push 2023-04-10, 201 stars, v2.1.0. It is a WebExtension that draws a **D3 v4** force graph. It uses Dexie (IndexedDB) for storage and the Disconnect entity list to group domains by company, which is the same "color by owner" idea TraceMap needs. — [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/mozilla%2Flightbeam-we); [package.json](https://raw.githubusercontent.com/mozilla/lightbeam-we/master/package.json)
  - Reuse mode: design reference. MPL-2.0 is file-level copyleft: copied files must stay MPL, but the rest of TraceMap does not have to. D3 v4 code is dated.
  - No maintained modern fork was found. This is a gap: no search was done beyond the Mozilla repos.
- **The Markup Blacklight** (https://themarkup.org/blacklight): `the-markup/blacklight-collector` is GPL-3.0, TypeScript, last push 2026-09-03, 240 stars, published on npm as `@themarkup/blacklight-collector`. Its README says it contains "some, but not all, of the code backing Blacklight." The tests are key_logging, session_recorders, canvas fingerprinting, fb_pixel_events, third_party_trackers and so on, and it can capture a HAR. — [blacklight-collector README](https://raw.githubusercontent.com/the-markup/blacklight-collector/main/README.md); [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/the-markup%2Fblacklight-collector)
  - `the-markup/blacklight-query` is also GPL-3.0. — [GitHub](https://github.com/the-markup/blacklight-query)
  - The Blacklight **website/results UI does not appear to be open source**. No repo was found at the-markup/blacklight or the-markup/blacklight-website (both 404), and the collector README says the repo holds only part of the code. — [GitHub 404 checks](https://github.com/the-markup/blacklight)
  - Reuse mode: design reference for the results-page UX (a plain-English finding per test, each with an explanation). The methodology article is at themarkup.org/blacklight/2020/09/22/how-we-built-a-real-time-privacy-inspector; it is linked from the README but was not fetched here.
- **Webbkoll**: the original GitHub repo `andersju/webbkoll` is MIT, Elixir, **archived**, last push 2022-11. It moved to Codeberg (`codeberg.org/dataskydd.net/webbkoll`), which is also **archived**, with its last update on 2025-04-25. The live site webbkoll.5july.net still returns HTTP 200. — [ecosyste.ms andersju/webbkoll](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/andersju%2Fwebbkoll); [Codeberg API](https://codeberg.org/api/v1/repos/dataskydd.net/webbkoll); [webbkoll.5july.net](https://webbkoll.5july.net/en)
  - Reuse mode: design reference. Its single long results page has sections for HTTPS, CSP, cookies and third-party requests, each with a green/yellow/red verdict and expandable raw data, which maps well to "reason + show proof". MIT means templates could be copied, but the code is Elixir/Phoenix, so it would not drop into React.
- **PrivacyScore** (https://github.com/PrivacyScore/PrivacyScore): GPL-3.0, Python (Django), last push 2021-06-22. privacyscore.org did not respond (curl returned 000). Effectively dead. — [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/PrivacyScore%2FPrivacyScore)
  - Reuse mode: design reference only, for its idea of comparing site lists and ranking sites within a list (relevant to the sector dashboard).
- **Exodus Privacy** (https://github.com/Exodus-Privacy/exodus): AGPL-3.0, Python, last push 2026-09-13, 805 stars. Its reports are at https://reports.exodus-privacy.eu.org/. The database and API results are under ODbL / DbCL. — [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/Exodus-Privacy%2Fexodus); [README](https://raw.githubusercontent.com/Exodus-Privacy/exodus/v1/README.md)
  - Reuse mode: **design reference only**. AGPL makes code reuse in a hosted web app impractical. Its report card is a strong pattern to follow: a big count of trackers and permissions, then a list of tracker names, each linking to a tracker detail page.
- **WhoTracks.me / Ghostery** (https://github.com/whotracksme/whotracks.me, which ghostery/whotracks.me redirects to): MIT, last push 2026-10-01, 484 stars. The repo now mainly publishes monthly **data**. The site itself is served at https://www.ghostery.com/whotracksme/ (trackers, websites, explorer). Company metadata lives in the separate TrackerDB repo (https://github.com/ghostery/trackerdb). — [README](https://raw.githubusercontent.com/whotracksme/whotracks.me/master/README.md); [GitHub API](https://api.github.com/repos/whotracksme/whotracks.me)
  - Reuse mode: data plus design reference (tracker profile pages, "presence on websites" charts). TrackerDB's license is UNVERIFIED (not fetched). Check it before bundling the domain-to-company mapping.
- **DuckDuckGo Privacy Dashboard** (https://github.com/duckduckgo/privacy-dashboard): **Apache-2.0**, TypeScript + Preact, last push 2026-07-20. It shows trackers found and blocked per site, grouped by company, plus connection details. It is built to be embedded in DDG apps and extensions, not to run on its own, and DDG is "not currently accepting new feature pull requests." — [GitHub repo page](https://github.com/duckduckgo/privacy-dashboard); [GitHub API](https://api.github.com/repos/duckduckgo/privacy-dashboard)
  - Reuse mode: design reference (company-grouped tracker list, the "x trackers from y companies" summary, the per-company expand). Small components or CSS can be copied under Apache-2.0 if the NOTICE/attribution is kept, but its data contract is DDG-specific.
- **PrivacyTests.org** (https://github.com/arthuredelstein/privacytests.org): MIT per its GitHub page. Activity was not verified (ecosyste.ms had no record). — [GitHub](https://github.com/arthuredelstein/privacytests.org)
  - Reuse mode: design reference for a dense comparison table (rows = tests, columns = browsers, pass/fail icons). That layout transfers to the sector dashboard (rows = sites, columns = checks).
- **Lookyloo** (https://github.com/Lookyloo/lookyloo, an open-source urlscan.io-style tool from CIRCL): BSD-3-Clause, Python, last push 2026-10-02, 781 stars. It "captures a webpage and then displays a tree of the domains, that call each other." — [LICENSE](https://raw.githubusercontent.com/Lookyloo/lookyloo/main/LICENSE); [README](https://raw.githubusercontent.com/Lookyloo/lookyloo/main/README.md); [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/Lookyloo%2Flookyloo)
  - Reuse mode: design reference and possibly code. It is the closest permissively licensed open-source analog to urlscan.io: capture page, domain redirect/call tree, per-node details with the request, screenshot. Its stack is Flask + D3 tree (inferred from repo structure, UNVERIFIED in detail).

#### B. Evidence-report generators

- **EDPS Website Evidence Collector (WEC)**: it moved from GitHub (EU-EDPS/website-evidence-collector now 404s on ecosyste.ms) to **https://code.europa.eu/edps/website-evidence-collector**. License **EUPL-1.2** (filter lists under EasyList licenses). Very active: v4.5.0 released 2026-09-30, v4.4.0 2026-09-24, v4.3.1 2026-09-04, last activity 2026-10-06. Node.js ≥22.17 + Puppeteer. — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/raw/main/README.md); [GitLab API releases](https://code.europa.eu/api/v4/projects/edps%2Fwebsite-evidence-collector/releases)
  - Features: a `collect` command writes output to a folder, and a `serve` command starts a local web UI on :8080 "to display the collected evidence". It can output `--yaml`, run testssl.sh, take a custom cookie DB, and crawl with `--max/--depth`. — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/raw/main/README.md)
  - Report templating: the files `src/assets/template.pug`, `src/assets/template-office.pug` and `src/assets/template-blocks/`, plus the dependencies `pug`, `marked`, `github-markdown-css` and `@turbodocx/html-to-docx`. That means HTML reports come from Pug templates and DOCX ("office") from HTML. HAR comes via `@themarkup/puppeteer-har`, tracker blocking via `@ghostery/adblocker-puppeteer`. — [package.json](https://code.europa.eu/api/v4/projects/edps%2Fwebsite-evidence-collector/repository/files/package.json/raw?ref=main); [repo tree](https://code.europa.eu/api/v4/projects/edps%2Fwebsite-evidence-collector/repository/tree?path=src/assets&ref=main)
  - Its README admits open HAR accuracy bugs: "fix bugs in HAR creation and verify accuracy". — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/raw/main/README.md)
  - Reuse mode: **design reference for the evidence report structure** (sections, how cookies, beacons and third-party hosts are listed). EUPL-1.2 is copyleft, though it is compatible with GPL and similar licenses. Do not copy the templates into TraceMap unless the project accepts EUPL obligations. TraceMap can still run WEC as an external tool to cross-validate results.
- **Lighthouse report renderer** (https://github.com/GoogleChrome/lighthouse, `report/`): Apache-2.0, last push 2026-09-30, 30.8k stars. It is "an independent report renderer that takes the LHR ... and creates a DOM tree of the report. It's all done client-side". `report-generator.js` builds a single self-contained HTML file from Node, and the renderer deliberately avoids `innerHTML`, using `<template>` + `textContent`. — [report/README.md](https://raw.githubusercontent.com/GoogleChrome/lighthouse/main/report/README.md); [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/GoogleChrome%2Flighthouse)
  - Reuse mode: design reference (gauge score ring, category sub-scores, expandable audits with a "details" table, which is exactly the score card + 4 subscores + reasons with "show proof" pattern) plus an architecture pattern: one self-contained offline HTML report with the JSON embedded inside it. The renderer is coupled to the LHR schema, so do not try to feed TraceMap data into it.
- **PerfCascade** (https://github.com/micmro/PerfCascade, npm `perf-cascade`): MIT, TypeScript, an SVG HAR waterfall viewer. Latest npm release 3.0.3 (2022-11-13), last repo push 2023-03-03. — [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/micmro%2FPerfCascade); [npm registry](https://registry.npmjs.org/perf-cascade)
  - Reuse mode: library. It takes a HAR and renders a waterfall with a per-request detail overlay (headers, timings). Stable but unmaintained since 2023, so wrap it in a React component.
- **HAR Viewer by Jan Odvarko** (https://github.com/janodvarko/harviewer): BSD license (from its GitHub page), last push 2022-11-25, 1,074 stars. — [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/janodvarko%2Fharviewer); [GitHub](https://github.com/janodvarko/harviewer)
  - Reuse mode: legacy (pre-React, RequireJS era). Better to send users to it, or to Google's HAR Analyzer, for viewing the downloaded HAR than to embed it.
- **BagIt / bagit-python** (https://github.com/LibraryOfCongress/bagit-python): **CC0** (public domain dedication per README), PyPI `bagit` 1.9.0, last push 2026-06-18. — [README](https://raw.githubusercontent.com/LibraryOfCongress/bagit-python/master/README.rst); [PyPI](https://pypi.org/pypi/bagit/json); [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/LibraryOfCongress%2Fbagit-python)
  - Reuse mode: library. `bagit.make_bag(dir, checksums=["sha256"])` produces `manifest-sha256.txt` + `bagit.txt` + `bag-info.txt` + `tagmanifest-sha256.txt`. This is the standard Library of Congress packaging format, specified in IETF RFC 8493. The RFC number comes from background knowledge and the RFC was not fetched (UNVERIFIED).
- **FastAPI built-in SSE**: `from fastapi.sse import EventSourceResponse`, available **since FastAPI 0.135.0**. Each yielded Pydantic model is JSON-encoded into `data:`, and keep-alive pings every 15 s, cache prevention and proxy-buffering prevention happen automatically. The current FastAPI version is 0.142.2. — [FastAPI SSE tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/); [PyPI fastapi](https://pypi.org/pypi/fastapi/json)
  - Alternative: `sse-starlette` (https://github.com/sysid/sse-starlette), BSD-3-Clause, v3.5.0, last push 2026-09-28. — [repo metadata](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/sysid%2Fsse-starlette); [PyPI](https://pypi.org/pypi/sse-starlette/json)
- **Playwright `page.pdf()`**: renders the page with `print` CSS media; call `emulate_media(media="screen")` first to keep the screen styles. Options include `format`, header/footer templates and so on. — [Playwright Python docs](https://playwright.dev/python/docs/api/class-page#page-pdf)
  - That `page.pdf()` works only in Chromium is from background knowledge; the fetched Python doc excerpt did not state it (UNVERIFIED in this session).

#### C. Graph libraries (for the network-graph screen)

| Library | URL | License | Latest version / activity | Notes |
|---|---|---|---|---|
| Cytoscape.js | https://github.com/cytoscape/cytoscape.js | MIT | npm 3.34.3 (2026-09-07); push 2026-10-06; 11.2k stars | Compound (parent) nodes, CSS-like stylesheet (e.g. `line-style: dashed`), graph algorithms |
| cytoscape-fcose | https://github.com/iVis-at-Bilkent/cytoscape.js-fcose | MIT | npm 2.2.0 (2023-01); push 2026-04-17 | Compound-graph layout; "up to 2 times as fast as CoSE"; fixed / alignment / relative-placement constraints |
| cytoscape-cola | https://github.com/cytoscape/cytoscape.js-cola | MIT | push 2026-04-10 | Physics layout that keeps animating (looks "live") |
| react-cytoscapejs | https://github.com/plotly/react-cytoscapejs | MIT | npm 2.0.0 (2022-09); push 2025-01 | Thin wrapper, stale |
| sigma.js + graphology | https://github.com/jacomyal/sigma.js, https://github.com/graphology/graphology | MIT / MIT | sigma push 2026-10-05 (12.2k stars); @react-sigma/core 5.0.6 (2025-12) | WebGL, aimed at thousands of nodes |
| vis-network | https://github.com/visjs/vis-network | Apache-2.0 OR MIT | npm 10.1.2 (2026-08-19); push 2026-10-05 | Easy physics, dashed edges, clustering API; used by Request Map |
| react-force-graph | https://github.com/vasturiano/react-force-graph | MIT | react-force-graph-2d 1.29.2 (2026-09-29) | Canvas d3-force; 2D/3D/VR |

Sources: [GitHub API batch](https://api.github.com/repos/cytoscape/cytoscape.js); [npm registry](https://registry.npmjs.org/cytoscape); [fCoSE README](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose); [ecosyste.ms cola](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/cytoscape%2Fcytoscape.js-cola); [npm react-cytoscapejs](https://registry.npmjs.org/react-cytoscapejs); [npm vis-network](https://registry.npmjs.org/vis-network); [npm react-force-graph-2d](https://registry.npmjs.org/react-force-graph-2d); [npm @react-sigma/core](https://registry.npmjs.org/@react-sigma/core); [ecosyste.ms graphology](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/graphology%2Fgraphology)

- fCoSE "combines the speed of spectral layout with the aesthetics of force-directed layout", and its README asks users to cite Balci & Dogrusoz, IEEE 2022. — [fCoSE README](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose)

#### D. Dashboard and chart libraries (for the sector dashboard)

| Library | License | Latest / activity | Source |
|---|---|---|---|
| Recharts | MIT | 3.10.1 (2026-07-25); push 2026-10-07; 27.6k stars | [npm](https://registry.npmjs.org/recharts), [GitHub API](https://api.github.com/repos/recharts/recharts) |
| Apache ECharts (+ echarts-for-react) | Apache-2.0 (wrapper MIT) | echarts push 2026-10-04, 67.5k stars; echarts-for-react 3.0.6 (2026-01-21) | [GitHub API](https://api.github.com/repos/apache/echarts), [npm](https://registry.npmjs.org/echarts-for-react) |
| Observable Plot | ISC | npm 0.6.17 (2025-02-14); push 2026-09-01 | [npm](https://registry.npmjs.org/@observablehq/plot), [GitHub API](https://api.github.com/repos/observablehq/plot) |
| Vega-Lite (+ react-vega) | BSD-3-Clause | push 2026-10-05; react-vega 8.0.0 (2025-08-27) | [GitHub API](https://api.github.com/repos/vega/vega-lite), [npm](https://registry.npmjs.org/react-vega) |

### Inferences
- No privacy-scanner front-end is both permissively licensed and maintained in a form TraceMap could drop in. The realistic plan is to build the UI with React plus general MIT/Apache libraries, and to cite Blacklight, Exodus, Webbkoll, the DDG dashboard, Lighthouse and Lookyloo as design inspirations in the project report. Panels usually reward this kind of attributed design lineage.
- Licensing has a pattern: measurement and scanner engines are usually copyleft (GPL/AGPL/EUPL/MPL), while visualization and UI plumbing libraries are usually MIT/Apache. So TraceMap should take its visual building blocks from the second group and only borrow ideas from the first.
- Request Map's lack of a public source repo is not a problem. Its look (force-directed graph, node size by request count, color by category) can be reproduced in Cytoscape.js or vis-network in a few hundred lines.

### Gaps
- Request Map source code location and license: NOT FOUND (all probed GitHub URLs 404; the page has no repo link).
- Modern maintained Lightbeam forks: none were found, but the search was shallow.
- Blacklight results-page source: appears closed. Not definitively confirmed (no statement from The Markup found).
- TrackerDB license and the exact Exodus report UI stack: not fetched.
- The exact formats WEC writes by default (HTML vs DOCX vs YAML/JSON flags) were inferred from the dependencies and templates, not from a run or the full option list.
- PrivacyTests.org activity date: unknown.
- Google HAR Analyzer (toolbox.googleapps.com) license: not checked; it is believed to be a closed hosted tool (UNVERIFIED).

## Key Question 2: Concrete recommended UI stack and libraries for the 6 screens + evidence bundle, with trade-offs

### Takeaway
Use React + TypeScript (Vite) with Tailwind + shadcn/ui-style components. Use FastAPI's native `EventSourceResponse` for live progress, Cytoscape.js + fCoSE (called directly, not through the stale react-cytoscapejs wrapper) for the graph, PerfCascade or a custom table for request proof, and Recharts for the dashboard (ECharts if heatmaps or treemaps are needed). Build the evidence bundle with bagit-python (SHA-256) plus a self-contained Lighthouse-style HTML report that Playwright prints to PDF. Every embedded dependency is MIT, Apache-2.0, BSD, ISC or CC0.

### Cited Findings
- FastAPI ≥0.135 ships `fastapi.sse.EventSourceResponse`, which streams Pydantic objects as SSE with automatic keep-alive pings and anti-buffering headers. — [FastAPI docs](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- Cytoscape.js is MIT and was released 2026-09-07. fCoSE handles compound (cluster) graphs with constraints and is MIT. react-cytoscapejs was last released in 2022. — [npm cytoscape](https://registry.npmjs.org/cytoscape); [fCoSE](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose); [npm react-cytoscapejs](https://registry.npmjs.org/react-cytoscapejs)
- sigma.js targets "thousands of nodes and edges" (WebGL). — [GitHub API description](https://api.github.com/repos/jacomyal/sigma.js)
- PerfCascade renders a HAR waterfall in SVG (MIT). — [repo](https://github.com/micmro/PerfCascade)
- bagit-python is CC0 and actively maintained (push 2026-06). — [README](https://raw.githubusercontent.com/LibraryOfCongress/bagit-python/master/README.rst)
- Lighthouse's report model is a self-contained HTML file with the result JSON embedded and rendered client-side. — [Lighthouse report README](https://raw.githubusercontent.com/GoogleChrome/lighthouse/main/report/README.md)
- Playwright `page.pdf()` uses print media, and `emulate_media(media="screen")` keeps the screen styles. — [Playwright docs](https://playwright.dev/python/docs/api/class-page#page-pdf)

### Inferences (recommendations)

**Base stack:** React 18/19 + TypeScript + Vite; Tailwind CSS; shadcn/ui (Radix-based, MIT) for cards, badges, tabs, accordions, dialogs and tooltips; TanStack Query for fetching. Licenses for Tailwind, shadcn/ui, Radix and TanStack were not verified in this session; they are widely known to be MIT (UNVERIFIED here).

1. **Scan page + live progress**
   - Backend: `@app.get("/scans/{id}/events", response_class=EventSourceResponse)` yields typed events (`stage_started`, `request_captured`, `canary_hit`, `stage_done`, `done`). Prefer this over WebSockets: progress only flows one way, the browser `EventSource` reconnects on its own, and it needs no extra dependency. If FastAPI is pinned below 0.135, fall back to sse-starlette (BSD-3).
   - Frontend: a stepper of stages (Load page → Consent → Fill canary form → Crawl → Analyze) plus a scrolling monospace log, and a live counter of "third-party domains contacted" that increments as events arrive. Design references: Lookyloo's capture flow, WEC `serve`.
2. **Results summary (score card with uncertainty, 4 subscores, reasons + "show proof")**
   - Draw the main score as a custom SVG radial gauge (Lighthouse-style ring) with a shaded arc band for the uncertainty range, e.g. "62 (55–70)". This takes about 50 lines and needs no library.
   - Show the 4 subscores as small gauges or bullet bars.
   - Show each reason as an accordion row: severity icon, a plain-English sentence, and a "Show proof" button that opens a drawer with the exact request (method, URL, highlighted params), screenshot crop and HAR entry ID.
   - Design references: Lighthouse audits, Blacklight per-test explanations, Exodus big-number card, Webbkoll traffic-light sections.
3. **Leak replay timeline**
   - Build a custom vertical timeline in React + Tailwind. Each step shows "typed `email` field at t=3.2s → request to `analytics.example` at t=3.4s".
   - Show the request in a code block, with the canary substring highlighted using `<mark>` after decoding (URL-decode, base64, hash match labelled "SHA-256 of canary").
   - Optionally add PerfCascade's HAR waterfall (MIT) underneath, with the leaking entries highlighted, for timing context. Trade-off: PerfCascade has not been updated since 2023 and is not React-native, so mount it in a `useEffect` ref.
   - Optional animation: Framer Motion (MIT, UNVERIFIED here) for "replay" step-through.
4. **Network graph (owner colors, solid vs dashed by confidence)**
   - **Cytoscape.js + cytoscape-fcose**, using a thin custom `useEffect` wrapper (or react-cytoscapejs, accepting that it is stale).
   - Use compound nodes for the company (parent) → domains (children). That gives "clusters by owner" natively, and fCoSE lays out compound graphs well.
   - Style edges with `line-style: solid` for high confidence and `dashed` for inferred, and set edge width by the number of shared identifiers.
   - Add a hover tooltip with the identifier name and value hash, and click-through to proof.
   - Use cytoscape-cola only if a "live physics" feel is wanted for the demo.
   - Trade-offs: at 20–200 nodes, sigma.js's WebGL is unnecessary and its compound-node support is weaker. vis-network (Apache/MIT) is the easiest alternative with built-in clustering and physics, but its styling is less expressive. react-force-graph looks impressive (it even has 3D) but has no compound grouping.
   - Color by owner using an entity list (Disconnect entity list as used in Lightbeam, DuckDuckGo Tracker Radar entities, or TrackerDB). Check each list's license before bundling.
5. **Security panel (scripts with badges)**
   - Use a sortable table (TanStack Table, MIT, UNVERIFIED here) with shadcn `Badge`s: "Third-party", "No SRI", "Inline", "Session recorder", "Fingerprinting API", "Keylogging", "Mixed content".
   - Each row expands to show the script URL, owner, hash and the Blacklight-style finding that triggered it. Design references: Blacklight tests list, Webbkoll CSP/headers sections.
6. **Sector dashboard (Indian sectors)**
   - **Recharts** (MIT) for bar, box-like and scatter charts of score by sector, median third parties, and % of sites leaking the canary.
   - Choose **ECharts** (Apache-2.0) instead if a site × check heatmap, a treemap of tracker companies per sector or a Sankey (sector → company) is wanted. ECharts does these natively and they impress panels, at the cost of a bigger bundle and an imperative API.
   - Use a PrivacyTests-style matrix table (sites × checks with pass/fail icons) as the drill-down.
7. **Evidence bundle**
   - Layout: `evidence/<scan_id>/` containing `har/scan.har`, `screenshots/*.png`, `results.json`, `report.html` (self-contained, JSON embedded, Lighthouse-style), `report.pdf` (Playwright `page.pdf()` after `emulate_media("screen")`) and `README.txt`.
   - Run `bagit.make_bag(path, {"Source-Organization": "TraceMap", "External-Description": url, "Bagging-Date": ...}, checksums=["sha256"])`. This yields `manifest-sha256.txt` and `tagmanifest-sha256.txt`, and `bag.validate()` lets the panel re-verify integrity. Zip it and offer it for download.
   - Optionally record a top-level SHA-256 of the zip, plus the scan start/end timestamps, in the DB/UI for tamper evidence.
   - Model the report sections on the EDPS WEC report (cookies, beacons/third-party hosts, HTTPS info). Use it as a reference only, since it is EUPL-1.2.
   - Users can open the HAR in any standard HAR viewer (janodvarko/harviewer is BSD; Google HAR Analyzer). Link out rather than embedding.

**Trade-off summary:** the custom work (gauge, timeline, proof drawer) is small and is where TraceMap's UI will stand out. The libraries cover the hard parts (graph layout, charts, SSE, BagIt hashing). Avoid AGPL/GPL/EUPL code (Exodus, Blacklight, PrivacyScore, WEC) in the shipped codebase.

### Gaps
- Bundle-size and performance numbers for Cytoscape vs vis-network vs ECharts-graph at 200 nodes were not measured or sourced.
- Licenses and activity of Tailwind, shadcn/ui, Radix, TanStack Table/Query and Framer Motion were not verified in this session (believed MIT).
- The claim that Playwright PDF works only in Chromium was not re-confirmed from the fetched docs.
- RFC 8493 (BagIt) was not fetched.
- No open-source "privacy inspector" was found that already has a canary leak-replay timeline UI. This looks like a novel screen for TraceMap; no prior art was found in this search.
