# Open-source end-to-end Node.js web-privacy crawlers TraceMap could build on

Method note: As of 2026-10-07, each main candidate was shallow-cloned onto the team's Windows 11 machine. Its LICENSE, package.json, README, source files and recent `git log` were read directly. Repo metadata (stars, forks, pushed_at, SPDX) came from the GitHub REST API, and from the GitLab API for code.europa.eu. Effort estimates are labelled as inferences. Anything not checked against a primary source is marked UNVERIFIED.

TraceMap capability checklist used throughout (abbreviations):
- **MP** = multi-profile (fresh A, fresh B, revisit of A)
- **SP** = same-site subpages plus scrolling
- **MOB** = mobile emulation
- **AC** = autoconsent with none/optIn/optOut
- **INIT** = request initiator call stack
- **POST** = POST bodies
- **RH** = response headers and Set-Cookie
- **CSA** = cookie setter attribution
- **LS** = localStorage
- **API** = JS API calls with the calling script (fingerprinting, form-field reads, keyboard listeners)
- **SS** = screenshots
- **BOT** = bot-wall detection
- **LEAK** = canary form filling without submit

---

## Q1. Identity: URL, stack, license (SPDX), stars, recent activity, maintainers

### Takeaway
Only two candidates are actively maintained in 2026 and also general-purpose:
- DuckDuckGo **tracker-radar-collector (TRC)**: Apache-2.0, last commit 2026-10-06.
- The Markup **blacklight-collector**: GPL-3.0, v3.11.0 released 2026-06-04.

The EDPS **website-evidence-collector (WEC)** is also very active (v4.5.0, 2026-09-30) but is EUPL-1.2 and has no mobile emulation. Leaky Forms' crawler code was last changed in 2022 and still uses Puppeteer 10. Brave **pagegraph-crawl** is active but needs a PageGraph-enabled Brave binary.

### Cited Findings

**duckduckgo/tracker-radar-collector (TRC)**
- URL: https://github.com/duckduckgo/tracker-radar-collector. JavaScript, Node >=18, Puppeteer ^24.7.1, `@duckduckgo/autoconsent` ^16.8.1 — [package.json](https://github.com/duckduckgo/tracker-radar-collector/blob/main/package.json)
- License: Apache License 2.0. GitHub reports SPDX "NOASSERTION" only because the LICENSE file begins with a note that DuckDuckGo logos and marks are licensed separately (CC BY-NC-ND 4.0). package.json says "Apache 2.0". — [LICENSE](https://github.com/duckduckgo/tracker-radar-collector/blob/main/LICENSE)
- 169 stars, 68 forks, pushed 2026-10-07, not archived — [GitHub API](https://api.github.com/repos/duckduckgo/tracker-radar-collector)
- Recent commits by Sam Macbeth and Maxim Tsoy (DuckDuckGo) — [commits](https://github.com/duckduckgo/tracker-radar-collector/commits/main):
  - 2026-10-06: test fix
  - 2026-08-24: Asana automation
  - 2026-07-22: cookie-button regex patterns for CA/GB/DE/FR/NL
  - 2026-07-15: browser-locale support
  - 2026-07-08: autoconsent update
- No GitHub releases or tags are used. The package version is fixed at "1.0.0", so consumers pin by git commit — [package.json](https://github.com/duckduckgo/tracker-radar-collector/blob/main/package.json)

**leaky-forms/leaky-forms-crawler**
- URL: https://github.com/leaky-forms/leaky-forms-crawler. JavaScript, a fork/extension of TRC. Puppeteer ^10.2.0, Node >=12.22.4 — [package.json](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/package.json)
- License conflict:
  - LICENSE file: "Copyright © 2022 Gunes Acar, Asuman Senol / Licensed GPL v3", plus a contributor relicensing agreement — [LICENSE](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/LICENSE)
  - package.json still says "Apache 2.0", inherited from TRC — [package.json](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/package.json)
  - GitHub SPDX: NOASSERTION — [GitHub API](https://api.github.com/repos/leaky-forms/leaky-forms-crawler)
- 27 stars, 8 forks. Last commit 2026-01-07 was README-only ("remove homepage reference"). The previous commits are from May 2022 (Asuman Şenol, Gunes Acar) — [commits](https://github.com/leaky-forms/leaky-forms-crawler/commits/main)
- Paper: "Leaky Forms: A Study of Email and Password Exfiltration Before Form Submission", Senol, Acar, Humbert, Zuiderveen Borgesius, USENIX Security 2022 — [USENIX](https://www.usenix.org/conference/usenixsecurity22/presentation/senol)
  - Crawled the top 100K sites from EU and US vantage points, desktop and mobile, three consent modes. Found email exfiltration before submission on 1,844 (EU) and 2,950 (US) sites — [USENIX](https://www.usenix.org/conference/usenixsecurity22/presentation/senol)

**the-markup/blacklight-collector**
- URL: https://github.com/the-markup/blacklight-collector. TypeScript, published on npm as `@themarkup/blacklight-collector` v3.11.0. Puppeteer ^22.15.0 — [package.json](https://github.com/the-markup/blacklight-collector/blob/main/package.json)
- License: GPL-3.0 (LICENSE file and GitHub SPDX). package.json `license` points to a "#licensing" README anchor that does not exist in the current README — [LICENSE](https://github.com/the-markup/blacklight-collector/blob/main/LICENSE), [GitHub API](https://api.github.com/repos/the-markup/blacklight-collector)
- 242 stars, 44 forks, pushed 2026-09-03 — [GitHub API](https://api.github.com/repos/the-markup/blacklight-collector)
- Release cadence: 3.11.0 (2026-06-04), 3.10.0 (2026-01-29), 3.9.x (2025-08), 3.8 (2025-07), and roughly six releases in 2025 — [CHANGELOG](https://github.com/the-markup/blacklight-collector/blob/main/CHANGELOG.md)
- Maintainer of recent releases: Miles Hilton. The 3.11.0 commit is titled "updating library, changing default device" — [commits](https://github.com/the-markup/blacklight-collector/commits/main)
- README warns: "This repo contains some, but not all, of the code backing Blacklight. It may not be very useful on its own." — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md)

**EDPS website-evidence-collector (WEC)**
- URL: https://code.europa.eu/EDPS/website-evidence-collector. The old GitHub path EU-EDPS/website-evidence-collector now returns 404 from the GitHub API. TypeScript, Node >=22.17, Puppeteer ^25.0.0, package `@EDPS/website-evidence-collector` v4.5.0 — [package.json](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/package.json)
- License: EUPL-1.2 — [LICENSE.txt](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/LICENSE.txt)
- 11 stars, 0 forks on code.europa.eu, last activity 2026-10-06 — [GitLab API](https://code.europa.eu/api/v4/projects/EDPS%2Fwebsite-evidence-collector)
- Releases: v4.5.0 (2026-09-30), v4.4.0, v4.3.1 (2026-09-04), v4.3.0 (2026-08-05) — [CHANGELOG](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/CHANGELOG.md)
- Recent committers: Felix Woestmann, Ufuk Uysal — [repo](https://code.europa.eu/EDPS/website-evidence-collector)
- Installed from the EU GitLab npm registry (`@EDPS:registry=https://code.europa.eu/api/v4/projects/812/packages/npm/`). Container images are also published — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/README.md)

**brave/pagegraph-crawl**
- URL: https://github.com/brave/pagegraph-crawl. JavaScript (built output committed under `built/`), puppeteer-core ^24.40.0, v1.2.13 — [package.json](https://github.com/brave/pagegraph-crawl/blob/main/package.json)
- License: MPL-2.0. 34 stars, 11 forks, pushed 2026-10-07. Recent commits are mostly dependabot merges by pes10k (Peter Snyder) — [GitHub API](https://api.github.com/repos/brave/pagegraph-crawl), [commits](https://github.com/brave/pagegraph-crawl/commits/main)
- PageGraph itself: "included in all Brave builds starting with version 1.46" but needs command-line flags. "Recording builtin JS APIs requires nightly Brave builds." Output is GraphML. Companion tools are pagegraph-query (Python) and pagegraph-rust — [Brave wiki: PageGraph](https://github.com/brave/brave-browser/wiki/PageGraph)

**spring-epfl/WebGraph**
- URL: https://github.com/spring-epfl/WebGraph. Python, not Node. No LICENSE detected by the GitHub API. 15 stars. Last push 2024-07-30 — [GitHub API](https://api.github.com/repos/spring-epfl/WebGraph)
- Uses a custom OpenWPM fork (sandrasiby/OpenWPM, `webgraph` branch) for crawling. As of 2024-07-30 it has "issues related to OpenWPM compatibility with Firefox" — [README](https://github.com/spring-epfl/WebGraph/blob/main/README.md)
- `spring-epfl/WebGraph-crawler` does not exist (GitHub API 404).

**Other candidates found**
- **Liscor/consentcrawl**: Python plus Playwright, MIT. Last commit 2023-12-16 — [repo](https://github.com/Liscor/consentcrawl)
  - Detects 25+ CMPs, clicks "accept", compares third-party domains and cookies before and after consent, takes screenshots, stores results in SQLite — [README](https://github.com/Liscor/consentcrawl/blob/main/README.md)
- **privacy-tech-lab/gpc-web-crawler**: MIT, active (dependabot merge 2026-10-06). Based on Selenium plus the "OptMeowt Analysis" Firefox extension, run as a Docker Compose stack (Selenium, REST API, MariaDB). Measures GPC compliance — [README](https://github.com/privacy-tech-lab/gpc-web-crawler/blob/main/README.md)
- **andersju/webbkoll-backend** (Webbkoll's Puppeteer backend), MIT:
  - GitHub repo moved to Codeberg — [README](https://github.com/andersju/webbkoll-backend/blob/master/README.md)
  - The Codeberg repo was archived on 2025-04-25. Last commit 2024-06-05 (Puppeteer 22.10). Self-described as "highly experimental" — [Codeberg](https://codeberg.org/dataskydd.net/webbkoll-backend)
- **ghostery/areweprivateyet**: Apache-2.0, last commit 2015-06-03. Dead — [repo](https://github.com/ghostery/areweprivateyet)
- **whotracksme/whotracks.me**: MIT, monthly data updates (latest 2026-10-01). The repo holds data, a Python API and the site renderer, not an open crawler. Tracker metadata comes from ghostery/trackerdb — [README](https://github.com/whotracksme/whotracks.me/blob/master/README.md)
- **duckduckgo/autoconsent**: TypeScript, MPL-2.0, 130 stars, pushed 2026-10-07. This is the CMP library that TRC bundles — [GitHub API](https://api.github.com/repos/duckduckgo/autoconsent)
- **OpenWPM**: Python plus Firefox, 1,422 stars, pushed 2026-10-04. Listed for reference only, as it is not Node — [GitHub API](https://api.github.com/repos/openwpm/OpenWPM)

### Inferences
- TRC is the only candidate that is permissively licensed, actively maintained by an organisation, Chromium/Puppeteer-based, and architected around pluggable collectors. It is the strongest base.
- The license field for Leaky Forms is ambiguous. Because the LICENSE file explicitly says GPL v3, treat the fork as GPL-3.0. Upstream TRC code inside it remains Apache-2.0.

### Gaps
- Star counts and dates for consentcrawl, gpc-web-crawler, webbkoll and areweprivateyet could not be fetched: the GitHub API rate limit was hit. Activity dates come from `git log` on fresh clones.
- No open-source crawler for Ghostery WhoTracks.me data collection was found. Their data pipeline (browser-extension-based, per Ghostery's materials) is UNVERIFIED as open source.
- No maintained Node packages named "privacy-scanner", "cookie-crawler", "headless-privacy", "trackerless", "fx-privacy" or "Lumen web crawler" were found. GitHub search returned nothing relevant before rate-limiting. Treat these as not existing / UNVERIFIED.

---

## Q2. Which TraceMap capabilities each tool already covers

### Takeaway
- **TRC** covers MOB, AC (none/optIn/optOut), API (about 150 breakpointed APIs, attributed to the calling script), SS, and partial INIT, RH and CSA. It lacks POST, real MP or revisit, SP, BOT detection and LEAK.
- **Leaky Forms** adds POST bodies, request headers, WebSocket frames and email/password filling.
- **Blacklight** natively covers SP (3 sampled same-site pages plus autoscroll), MOB (iPhone 13 Mini by default), form filling with known values, keylogging detection, full JS stacks and cookie setter attribution. It is GPL-3.0.
- **WEC** covers SP (`--max/--depth`), cookie and localStorage setter stacks, beacons, a persistent profile and a HAR. It has no mobile emulation and no autoconsent.

### Cited Findings

**TRC — what exists**
- **Collectors present:** RequestCollector, CookieCollector, APICallCollector, CookiePopupsCollector, TargetCollector, ScreenshotCollector, TraceCollector, ContentScriptCollector. The `-d` flag selects them, e.g. `-d 'requests,cookies'` — [collectors/](https://github.com/duckduckgo/tracker-radar-collector/tree/main/collectors), [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md)
- **MOB:** `-m, --mobile`. It sets an Android 10 Chrome 135 mobile UA and a 412x691 viewport at DPR 2 via `Emulation.setDeviceMetricsOverride` — [constants.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/constants.js), [crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js)
- **AC:** `--autoconsent-action <optIn|optOut>` with the `cookiepopups` collector. Omitting it means "none" (an explicit `null` is passed so autoconsent does not default to optOut).
  - The collector also scrapes cookie-popup text and buttons in all frames and records `optInResult`, `optOutResult`, `autoconsentDone` and self-test results — [CookiePopupsCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/CookiePopupsCollector.js)
- **INIT (partial):** RequestCollector records the CDP `initiator`, but its output `initiators` is a de-duplicated set of script URLs flattened from `initiator.stack` and its parents. Function names, line and column are dropped.
  - Redirects inherit the original initiator. CORS "parser" initiators are corrected — [helpers/initiators.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/helpers/initiators.js), [RequestCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/RequestCollector.js)
- **POST: missing.** The RequestData typedef has url, method, type, initiators, redirectedFrom/To, status, remoteIPAddress, responseHeaders, responseBodyHash, failureReason, size and time. It has no postData and no request headers — [RequestCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/RequestCollector.js)
- **RH (partial):** response headers are filtered to a safelist. The default is etag, set-cookie, cache-control, expires, pragma, p3p, timing-allow-origin, access-control-allow-origin and accept-ch, overridable through the `saveHeaders` constructor option — [RequestCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/RequestCollector.js)
- **Cookies:** CookieCollector calls `Network.getAllCookies` and outputs only name, domain, path, expires, session and sameSite. It drops value, httpOnly, secure and size — [CookieCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/CookieCollector.js)
- **CSA (partial, derivable):**
  - JS-set cookies: APICallCollector breakpoints `Document.cookie setter` with `saveArguments: true`, which yields the script plus the cookie string — [breakpoints.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/breakpoints.js)
  - HTTP-set cookies: the per-request `set-cookie` response header gives HTTP attribution — [RequestCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/RequestCollector.js)
- **API:** breakpoints cover, among others:
  - Navigator.* (userAgent, plugins, hardwareConcurrency, webdriver, getBattery, …), NavigatorUAData.getHighEntropyValues, Screen.*
  - HTMLCanvasElement.toDataURL/getImageData, WebGL getParameter/getExtension/readPixels, OfflineAudioContext, AudioBuffer.getChannelData, RTCPeerConnection
  - KeyboardEvent.code/keyCode, Date.getTimezoneOffset, Intl resolvedOptions, window.localStorage/sessionStorage/indexedDB access, CookieStore, sensors and more
  - Each call is attributed to the "top non-anonymous source" script URL.
  - Output: `callStats` (per script, per API counts) and `savedCalls` (source, description, arguments) — [breakpoints.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/breakpoints.js), [TrackerTracker.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/TrackerTracker.js), [APICallCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICallCollector.js)
  - No breakpoints exist for HTMLInputElement.value reads or addEventListener('keydown'/'input') — [breakpoints.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/breakpoints.js)
- **LS:** only access to `window.localStorage` is breakpointed. Storage contents are not dumped — [breakpoints.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/breakpoints.js)
- **SS:** ScreenshotCollector. The CLI writes it as a separate `.jpg` and keeps the path in the JSON — [crawl-cli.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/cli/crawl-cli.js)
- **BOT:** only *evasion*. `notABot.js` spoofs navigator.webdriver, Notification.permission and window.chrome, and `-a` disables it. There is no bot-wall *detection* — [helpers/notABot.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/helpers/notABot.js)
- **MP:** each crawl launches a browser with a fresh `mkdtemp` profile in the OS temp dir and removes it on close — [browser/LocalChrome.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/browser/LocalChrome.js)
  - The `crawler()` API accepts an external `browserConnection` (README: "if you prefer to create the browser context yourself (to e.g. use other browser or non-incognito context)") — [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md), [crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js)
- **SP: missing.** The flow is: navigate one URL → `postLoad()` hooks → wait `extraExecutionTimeMs` (default 2.5 s) → `getData()`. There is no link discovery or subpage loop — [crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js)
- **Other:** locale support (2026-07), Selenium-hub remote browsers, SOCKS proxy, `--chromium-version` (downloads Chrome for Testing via `@puppeteer/browsers`) — [crawl-cli.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/cli/crawl-cli.js), [chromiumDownload.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/helpers/chromiumDownload.js)

**Leaky Forms crawler (adds to an older TRC)**
- RequestCollector captures `postData` for POST, `requestHeaders` (using extraInfo headers), and WebSocket creation plus **sent frames** (`webSocketFrameSent` payload stored as postData) — [RequestCollector.js](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/collectors/RequestCollector.js)
- EmailPasswordFieldsCollector (533 lines) — [EmailPasswordFieldsCollector.js](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/collectors/EmailPasswordFieldsCollector.js), [helpers/formInteraction.js](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/helpers/formInteraction.js):
  - injects Firefox Relay's Fathom email-field detector
  - finds email and password fields on the page and in iframes
  - if none are found, clicks login/register links (native click, then JS click) and follows new pages
  - types the canary with randomized per-key dwell delays (`elementHandle.type(key,{delay})`) and presses Tab to blur
  - takes screenshots after clicks
  - No submit call appears in that collector.
- CLI adds `-e` (email) and `-w` (password). The paper used Consent-O-Matic for consent modes. The `email-field-collector` branch holds the exact study version and `main` is a rebase — [README](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/README.md)
- Desktop and mobile batch scripts: `crawl_in_parts.sh` and `crawl_in_parts_mobile.sh` — [repo](https://github.com/leaky-forms/leaky-forms-crawler)

**Blacklight collector**
- **Tests:** behaviour_event_listeners, canvas_fingerprinters, canvas_font_fingerprinters, cookies, fb_pixel_events, google_analytics_events, key_logging, session_recorders, third_party_trackers — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md)
- **SP:** `numPages` (default 3). After the landing page it collects same-site links, randomly samples `numPages` of them, and on each page runs `fillForms()` then `autoScroll()` — [src/collector.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/collector.ts)
- **MOB:** `emulateDevice` takes any Puppeteer KnownDevice. The default is `KnownDevices['iPhone 13 Mini']`, changed in 3.11.0 — [src/collector.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/collector.ts)
- **LEAK-like:**
  - `fillForms()` types fixed values keyed by autocomplete/type: email `blacklight-headless@themarkup.org`, tel, name, address, and a test credit-card number. It skips `submit`/`hidden` inputs, uses Backspace, `keyboard.type` and Tab — [interaction-utils.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/pptr-utils/interaction-utils.ts)
  - The `key_logging` inspector searches each request's `postData()` for those values in plain, base64 and hashed forms — [key-logging.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/inspectors/key-logging.ts)
- **API with stack:**
  - The js-instrument plugin (OpenWPM-style) records full `StackTrace.getSync()` stacks for:
    - navigator and screen properties, plugins and mimeTypes
    - window.name, localStorage and sessionStorage, Storage.prototype
    - document.cookie, document.referrer
    - canvas, 2D context, RTCPeerConnection, Audio nodes
  - document and window `addEventListener` are proxied, which covers keyboard listeners
  - Sources: [fingerprinting-apis.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/plugins/fingerprinting-apis.ts), [js-instrument.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/plugins/js-instrument.ts), [add-event-listener.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/plugins/add-event-listener.ts)
- **CSA:** HTTP cookies are tagged "set in Set-Cookie HTTP response header for <url>". JS cookies are tagged with the script URL from the document.cookie event. `matchCookiesToEvents` joins them — [src/inspectors/cookies.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/inspectors/cookies.ts)
- **POST/INIT:** requests go to `requests.har` via `@themarkup/puppeteer-har` (`captureHar`, default true) — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md), [src/collector.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/collector.ts)
- **SS:** `n.jpeg` per page. Also HTML per page and `browser-cookies.json`. `saveBrowsingProfile` keeps the profile; `clearCache` defaults to true — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md)
- **AC: none built in.** README options list no consent handling. An `enableAdBlock` option exists — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md)

**EDPS WEC**
- **SP:** "By default WEC visits only the landing page. Use `--max` and/or `--depth` to follow links". `-l/--browse-link` adds explicit URIs. `-f/--first-party-uri` defines first-party scope. `--sleep` defaults to 3000 ms per page. A pre-flight HEAD check now refuses redirects that leave the first party (v4.4.0) — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/README.md), [collector-command.ts](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/src/commands/collector-command.ts), [CHANGELOG](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/CHANGELOG.md)
- **Recorders:** beacon, cookie, local-storage, network, host and websocket. Cookie and localStorage events carry a stacktrace-js stack (2 frames kept). Beacons are matched against bundled filter lists — [src/collector/recorder/](https://code.europa.eu/EDPS/website-evidence-collector/-/tree/main/src/collector/recorder)
- **Persistent profile:** `-p/--browser-profile` sets userDataDir. `-c/--set-cookie` presets cookies — [collector-command.ts](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/src/commands/collector-command.ts), [browser-session.ts](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/src/collector/browser/browser-session.ts)
- **Other flags:** `--screenshots` (default true), `--har` (default true), `--dnt`, `--headless`, `--browser-options`, a `serve` mode with an HTTP API — [collector-command.ts](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/src/commands/collector-command.ts), [README](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/README.md)
- **Mobile emulation:** a grep for `emulate`, `isMobile` and `setViewport` in src/collector and src/commands found no mobile emulation — [repo](https://code.europa.eu/EDPS/website-evidence-collector)
- **Autoconsent:** none. README links to a third-party "WEC-Accept" extension for accepting banners — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/README.md)

**pagegraph-crawl**
- **Options:** `-b` binary, `-u`, `-t` seconds, `-r` recursive depth, `-e/--existing-user-data-dir`, `-p/--persist-user-data-dir`, `--screenshot`, `--har`, `--har-body`, `-a/--user-agent`, `--proxy-server`, `-i` interactive, `--extensions-path` — [built/run.js](https://github.com/brave/pagegraph-crawl/blob/main/built/run.js)
- **Recording:** PageGraph records script execution with origins, requests with response headers, DOM mutations and Web API fingerprinting calls, all with attribution — [Brave wiki](https://github.com/brave/brave-browser/wiki/PageGraph)
- **Interaction limit:** README: "PageGraph currently does not track puppeteer / automation scripts, and so modifying or interacting with the document through devtools/puppeteer while recording a PageGraph file will likely fail." — [README](https://github.com/brave/pagegraph-crawl/blob/main/README.md)

### Inferences

Coverage matrix. Y = native, P = partial or derivable, N = absent.

| Capability | TRC | Leaky Forms | Blacklight | WEC | pagegraph-crawl |
|---|---|---|---|---|---|
| MP A/B/revisit | P (pass own browserConnection) | P (same) | P (saveBrowsingProfile) | P (`--browser-profile`) | P (`-e/-p` user-data-dir) |
| SP + scroll | N | P (clicks login links only) | Y (3 random same-site + autoScroll) | Y (`--max/--depth`) | P (`-r` depth) |
| MOB | Y | Y | Y (default iPhone 13 Mini) | N | P (UA only) |
| AC none/optIn/optOut | Y (DDG autoconsent) | P (Consent-O-Matic, old) | N | N | N |
| INIT stack | P (URL set only) | P | P (HAR; UNVERIFIED whether `_initiator` is kept) | P (stack on cookies/LS/beacons) | Y (graph edges) |
| POST bodies | N | Y | Y (HAR + postData scan) | Y (HAR) | P (`--har-body`) |
| RH / Set-Cookie | P (safelist incl. set-cookie) | P | Y (HAR) | Y | Y |
| CSA | P (cookie-setter breakpoint + set-cookie join) | P | Y | Y | Y |
| LS | P (access only) | P | Y (Storage proto w/ stack) | Y | Y |
| API w/ caller | Y (top script) | Y | Y (full stack) | P | Y |
| Form-read / key listeners | P (KeyboardEvent.code/keyCode only) | N | Y (addEventListener proxy) | N | P |
| SS | Y | Y | Y | Y | Y |
| BOT-wall detection | N (evasion only) | N | N | N | N |
| LEAK canary, no submit | N | Y (email/password) | Y (many fields + detection) | N | N (interaction breaks PageGraph) |

- No tool covers TraceMap's A/B/revisit cookie-sync design or bot-wall detection. These must be TraceMap-specific code whichever base is chosen.

### Gaps
- Whether Blacklight's HAR (`@themarkup/puppeteer-har`) keeps Chrome's `_initiator` stack and response bodies was not verified.
- Whether the EmailPasswordFieldsCollector ever triggers submission indirectly (e.g. via the Enter key) was not exhaustively audited. Only the absence of explicit submit calls was confirmed.

---

## Q3. Extensibility: plugin/collector API and effort to add A/B/revisit, subpages and the leak-test

### Takeaway
TRC has a documented collector API. Each collector is a class with `id()`, `init()`, `addTarget(cdpSession, targetInfo)`, `postLoad()` and `getData()`, and receives raw CDP sessions for every page, iframe and worker. TraceMap's missing pieces map cleanly onto it: a POST/initiator-full request collector, a storage dump, extra breakpoints, a subpage/scroll postLoad collector, a leak collector and a bot-wall collector. A/B/revisit is best done as a thin wrapper that owns the browser profiles. Blacklight and WEC are monolithic pipelines (one `collect()` function or CLI), so extending them means forking.

### Cited Findings
- **TRC collector API:**
  - Collectors extend `BaseCollector` and override `id()` and `getData(options)`.
  - Optional hooks: `init(options)`; `addTarget(session, targetInfo)`, called for the main page, iframes, workers etc. with a Puppeteer CDPSession; `postLoad()`, "the place for executing heavy page interactions".
  - Optional `collectorExtraTimeMs` extends the crawl budget.
  - New collectors must be registered in `crawlerConductor.js` and `main.js`, with types in `helpers/collectorsList.js`.
  - Sources: [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md), [BaseCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/BaseCollector.js)
- **TRC as a library:** the `crawler(url, {collectors, browserConnection, emulateMobile, runInEveryFrame, maxLoadTimeMs, extraExecutionTimeMs, collectorFlags…})` API lets a caller inject custom collectors without touching the CLI — [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md)
- **TRC `collectorFlags`** already carries `enableAsyncStacktraces` and `autoconsentAction` — [BaseCollector.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/BaseCollector.js)
- **TRC code size:** the whole collector, crawler and browser core is about 4,600 lines of JS.
  - RequestCollector 387, CookieCollector 78, APICallCollector 231, CookiePopupsCollector 671, breakpoints.js 650, crawler.js 499 (counted with `wc -l` on the clone) — [repo](https://github.com/duckduckgo/tracker-radar-collector)
- **Leaky Forms shows the leak-test pattern on TRC:**
  - fill logic sits in `getData()` of a collector that has its own Puppeteer `page`
  - Fathom detection is injected with `page.evaluateOnNewDocument`
  - Sources: [EmailPasswordFieldsCollector.js](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/collectors/EmailPasswordFieldsCollector.js), [formInteraction.js](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/helpers/formInteraction.js)
  - Its RequestCollector diff for postData, requestHeaders and WebSocket frames is small: about 85 lines more than TRC's (472 vs 387) — [RequestCollector.js](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/collectors/RequestCollector.js)
- **Blacklight** exposes a single `collect(inUrl, {blTests, numPages, emulateDevice, ...})`. Tests are fixed inspectors and plugins inside `src/` — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md), [src/](https://github.com/the-markup/blacklight-collector/tree/main/src)
- **WEC** is structured as recorders plus an inspector plus a reporter (`src/collector/recorder/*`, `src/inspector`, `src/reporter`). There is no documented third-party plugin API — [src/](https://code.europa.eu/EDPS/website-evidence-collector/-/tree/main/src)

### Inferences

Effort estimates for TraceMap on TRC. These are rough guesses for a 4-person student team.

1. **`TraceMapRequestCollector`** (~120 lines; subclass or copy RequestCollector):
   - store `request.postData`, using `Network.getRequestPostData` for large bodies
   - store full request and response headers
   - store the raw CDP `initiator` with callFrames (url, functionName, line, col) instead of the flattened URL set
   - port the WebSocket-frame capture from Leaky Forms
2. **`StorageCollector`** (~60 lines): at `getData()`, evaluate `localStorage` and `sessionStorage` dumps in every frame target and call `Network.getAllCookies` with values and flags. The full stock CookieCollector only drops fields.
3. **Breakpoints** (config-level edits plus a test page) for:
   - `HTMLInputElement.value` getter
   - `EventTarget.addEventListener` with type `keydown`/`keyup`/`keypress`/`input`, saving arguments
   - `Storage.prototype.setItem` with arguments, which gives localStorage setter attribution
4. **`SubpageCollector` in `postLoad()`** (~150–250 lines):
   - extract same-site `<a href>` links, pick about 4, then `Page.navigate` and scroll each one
   - Caveat: TRC's crawl lifecycle (`navigateMainTarget`, timeouts, `finalUrl`) assumes one main navigation, and the collectors keep accumulating across navigations. Two options:
     - (a) accept merged data and tag requests by timestamp or document URL, or
     - (b) call `crawler()` once per page while reusing the same `browserConnection`. Option (b) is simpler and keeps per-page JSON.
5. **A/B/revisit wrapper** (~100–150 lines):
   - launch Chromium with an explicit persistent `--user-data-dir` per profile (A, B) and pass `browserConnection` into `crawler()`
   - for the revisit, relaunch with A's dir
   - TRC's own LocalChrome always uses a temp profile it deletes, so the wrapper must own the browser — [LocalChrome.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/browser/LocalChrome.js)
6. **`LeakTestCollector`** (~200–300 lines; port ideas from Leaky Forms or Blacklight `fillForms`):
   - detect email and tel inputs (port Fathom or use autocomplete/type heuristics), type canaries, blur, never submit
   - Python then searches POST bodies, URLs, cookies and WebSocket frames for plain, URL-encoded, base64 and hashed variants (Blacklight's key-logging approach)
   - Licensing for copying code: see Q6.
7. **`BotWallCollector`** (~80 lines): check status codes (403/429/503), challenge-page DOM markers and titles, and known challenge script hosts. It can reuse the screenshot.

- Total net-new JS is estimated at about 800–1,200 lines on top of TRC. That is far less than writing CDP plumbing, autoconsent integration and the breakpoint-based API tracer from scratch.

### Gaps
- Whether TRC collectors behave correctly across multiple navigations in one `crawler()` call is untested. The hypothesis is that per-page `crawler()` calls with a shared connection are safer. This needs a spike.
- Whether `Network.getRequestPostData` is needed for large or multipart bodies in Puppeteer 24 is not verified.

---

## Q4. Output format and Python ingestion

### Takeaway
All candidates emit JSON (or JSON plus HAR, YAML or GraphML), so Python ingestion is easy.
- **TRC:** one JSON per site with a typed `CollectResult` plus `metadata.json`, the cleanest per-site schema.
- **Blacklight:** `inspection.json` + NDJSON event log + HAR.
- **WEC:** JSON/YAML/HTML/PDF reports + HAR.
- **pagegraph-crawl:** GraphML, which Brave's Python `pagegraph-query` can read.

### Cited Findings
- **TRC:**
  - Each crawled site produces a JSON file named after the website.
  - Shape: `{initialUrl, finalUrl, timeout, testStarted, testFinished, data:{<collectorId>: ...}}`. A failed collector yields `null` for its key.
  - Screenshots are moved to a separate `.jpg` and referenced by path.
  - A `metadata.json` holds the crawl config, system config and stats.
  - Sources: [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md), [crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js), [crawl-cli.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/cli/crawl-cli.js)
  - Reporters: cli, file, html and clickhouse — [reporters/](https://github.com/duckduckgo/tracker-radar-collector/tree/main/reporters)
- **Blacklight:**
  - `inspection.json` keys: browser, browsing_history, config, deviceEmulated, end_time, host, hosts, reports, script, start_time, uri_ins, uri_dest, uri_redirects, location
  - Other files: `inspection-log.ndjson` (raw events), `browser-cookies.json`, `requests.har`, `n.html`, `n.jpeg`
  - Source: [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md)
- **WEC:** `-j/--json` and `-y/--yaml` to STDOUT, HTML (pug template), PDF, `requests.har`, `error.json` on navigation failure (v4.3.0). The FAQ suggests jq recipes for JSON — [collector-command.ts](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/src/commands/collector-command.ts), [CHANGELOG](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/CHANGELOG.md), [FAQ](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/FAQ.md)
- **PageGraph:** GraphML output; `pagegraph-query` (Python) and `pagegraph-rust` for analysis — [Brave wiki](https://github.com/brave/brave-browser/wiki/PageGraph)

### Inferences
- **Recommended contract.** TraceMap's Node sidecar writes one directory per (site, profile, visit), for example `out/<site>/{A1,B1,A2}/<page_idx>.json` plus screenshots. The schema is TRC's `CollectResult` extended with TraceMap collectors.
- **Python side.** Read with `json` or `orjson` and validate with pydantic models that mirror the TRC JSDoc typedefs (`RequestData`, `APICallReport`, cookies). Parse HAR, if used, with `haralyzer` or plain json.
- **Calling convention.** Python calls `node trace-crawler.js --config job.json` through `subprocess.run`. This is a clean process boundary, which also matters for licensing (Q6).

### Gaps
- TRC publishes no JSON Schema. The schema exists only as JSDoc typedefs, so TraceMap would need to write its own pydantic models.

---

## Q5. Windows compatibility and runtime/performance notes

### Takeaway
None of the candidates documents Windows as a supported platform, but TRC, Blacklight and WEC are pure Node and Puppeteer, and Puppeteer supports Windows. TRC uses cross-platform `os.tmpdir()` and `@puppeteer/browsers` platform detection, so it should run on Windows. Only its `unit` npm script uses POSIX env syntax. Docker is the safer route for any batch crawl. Two concrete Windows problems were seen in our own test clones (both below).

### Cited Findings
- **TRC on Windows (should work, not tested):**
  - Chrome download uses `detectBrowserPlatform()` from `@puppeteer/browsers`, which picks the host platform — [chromiumDownload.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/helpers/chromiumDownload.js)
  - Profiles go in `mkdtemp(os.tmpdir()…)` — [LocalChrome.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/browser/LocalChrome.js)
  - The `unit` test script is `TRC_UNSAFE_DISABLE_SANDBOX=1 node ./tests/runTests.js`, which does not work in cmd.exe or PowerShell without `cross-env` — [package.json](https://github.com/duckduckgo/tracker-radar-collector/blob/main/package.json)
- **TRC concurrency:** defaults to `floor(cpus*0.8)` parallel crawlers ("hard limit of 38"). maxLoadTimeMs defaults to 30 s per the README, though the crawler code falls back to 60000 ms when unset. extraExecutionTimeMs defaults to 2.5 s.
  - The README hints at raising Node memory (`--max_old_space_size=4096`) for big post-processing.
  - Sources: [crawlerConductor.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawlerConductor.js), [crawler.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/crawler.js), [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md)
- **TRC debugger cost:** the API tracer pauses on CDP `Debugger` breakpoints for every instrumented call. That is heavier than JS-proxy instrumentation, but invisible to page JS — [TrackerTracker.js](https://github.com/duckduckgo/tracker-radar-collector/blob/main/collectors/APICalls/TrackerTracker.js)
- **Blacklight on Windows (observed):** after cloning, `git status` showed `D __tests__/test-pages/eicar`. The EICAR antivirus test file in the test fixtures was removed on the Windows machine, almost certainly by Microsoft Defender. Expect AV interference with its test suite — [repo test-pages](https://github.com/the-markup/blacklight-collector/tree/main/__tests__)
- **Leaky Forms:** Puppeteer ^10.2.0 and Node >=12 (2021-era). The repo includes `.sh` batch scripts, and the README notes that 100K-site crawls had to be split into 1K chunks "due to an issue on the TRC" — [package.json](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/package.json), [README](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/README.md)
- **WEC:** requires Node >=22.17. Ships a Containerfile and registry images. `testssl.sh` integration implies a POSIX shell is needed for that feature — [package.json](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/package.json), [README](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/README.md), [CHANGELOG](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/CHANGELOG.md)
- **pagegraph-crawl:** needs a Brave Nightly binary path passed with `-b`. The README example uses a macOS path — [README](https://github.com/brave/pagegraph-crawl/blob/main/README.md)
  - On our Windows clone, git reported a failed checkout and a large set of staged deletions. The cause was not diagnosed (UNVERIFIED).

### Inferences
- **Development:** run TRC natively on Windows with `node cli/crawl-cli.js …` rather than `npm run unit`.
- **Batch crawls:** use the Docker image later (Linux Chromium, consistent fonts and screenshots).
- **Antivirus:** add the repo folder to the Defender exclusions if test fixtures disappear. This is a user action, as it changes a security setting.
- **Rough runtime** per site for TraceMap's design is about 3 visits × 5 pages × (load ≤30 s + 2.5–5 s settle + scroll). With concurrency of 4–6 on a laptop, a few hundred sites per day is realistic (inference).

### Gaps
- No candidate was actually executed on Windows. `npm install` would download Chromium, and per the session rules downloads need the user's explicit approval. A 30-minute spike is recommended: `npm i` then `node cli/crawl-cli.js -u https://example.com -o out -m -d requests,cookies,apis,screenshots,cookiepopups --autoconsent-action optOut`.

---

## Q6. Licensing: subprocess use from Apache-2.0 TraceMap, and which code can be forked in

### Takeaway
- **TRC (Apache-2.0)** can be forked into an Apache-2.0 repo freely: keep the LICENSE and NOTICE text and mark changes. DuckDuckGo marks are excluded.
- **duckduckgo/autoconsent and brave/pagegraph-crawl (MPL-2.0)** can be used as dependencies. Modified MPL files stay MPL; this is file-level copyleft.
- **Blacklight and the Leaky Forms crawler (GPL-3.0)** and **WEC (EUPL-1.2)** should not be vendored into Apache-2.0 TraceMap code. Running them as separate executables over CLI, pipes or files is normally treated as "separate programs" per the FSF. Their ideas (algorithms, field lists, heuristics) can be reimplemented independently.

### Cited Findings
- **TRC:** LICENSE is the Apache License 2.0 with an added notice that DuckDuckGo logos and marks are under CC BY-NC-ND 4.0 — [LICENSE](https://github.com/duckduckgo/tracker-radar-collector/blob/main/LICENSE)
- **Blacklight:** GPL-3.0 — [LICENSE](https://github.com/the-markup/blacklight-collector/blob/main/LICENSE)
- **Leaky Forms:** "Licensed GPL v3", while package.json says "Apache 2.0" — [LICENSE](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/LICENSE), [package.json](https://github.com/leaky-forms/leaky-forms-crawler/blob/main/package.json)
- **WEC:** EUPL-1.2 — [LICENSE.txt](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/LICENSE.txt)
- **pagegraph-crawl** and **autoconsent:** MPL-2.0 — [pagegraph-crawl LICENSE](https://github.com/brave/pagegraph-crawl/blob/main/LICENSE), [GitHub API autoconsent](https://api.github.com/repos/duckduckgo/autoconsent)
- **FSF GPL FAQ:** "pipes, sockets and command-line arguments are communication mechanisms normally used between two separate programs. So when they are used for communication, the modules normally are separate programs. But if the semantics of the communication are intimate enough, exchanging complex internal data structures, that too could be a basis to consider the two parts as combined into a larger program." — [GNU GPL FAQ #MereAggregation](https://www.gnu.org/licenses/gpl-faq.html#MereAggregation)
- **Consentcrawl, gpc-web-crawler and webbkoll-backend** are MIT, so they can be copied with attribution — [consentcrawl LICENSE](https://github.com/Liscor/consentcrawl/blob/main/LICENSE), [gpc-web-crawler LICENSE](https://github.com/privacy-tech-lab/gpc-web-crawler/blob/main/LICENSE), [webbkoll-backend](https://github.com/andersju/webbkoll-backend/blob/master/LICENSE)

### Inferences
- **Safe architecture:** `tracemap-crawler/` is a TRC fork (Apache-2.0) inside the TraceMap repo, with NOTICE kept and changes marked. Python talks to it only through CLI arguments and JSON files on disk.
- **Optional GPL comparison:** Blacklight could run as an unmodified npm dependency in a *separate* folder or container, invoked via CLI, for cross-checking. That folder must keep its GPL license, and the team should never import Blacklight modules into TraceMap's JS.
- **Leaky Forms code:** do not copy it into TraceMap. Its RequestCollector postData changes are trivial to re-implement directly on TRC's Apache code (CDP `request.postData`). The Fathom email detector comes from Mozilla Firefox Relay, whose license (believed MPL-2.0) is UNVERIFIED here. Check before vendoring.
- **Not legal advice.** For a college project that is not distributed commercially, GPL obligations are triggered on distribution. Keeping clean boundaries still matters if the repo is published under Apache-2.0.

### Gaps
- The Firefox Relay (`fx-private-relay`) license for `email_detector.js`/Fathom was not verified in this session.
- EUPL-1.2 compatibility with Apache-2.0 for linking was not analysed. EUPL is copyleft, so treat it like GPL for vendoring.

---

## Q7. Recommendation per candidate (fork / extend / sidecar / port ideas / ignore)

### Takeaway
**Fork and extend DuckDuckGo tracker-radar-collector as TraceMap's Node crawler sidecar**, called from Python as a subprocess. Port ideas, not code, from Leaky Forms (POST, WebSocket capture and canary typing), Blacklight (subpage sampling, autoscroll, form-value list, key-logging detection, cookie setter attribution, addEventListener hooks) and WEC (first-party link queue, redirect-to-third-party skip, cookie/localStorage stack recording). Use Blacklight unmodified as an optional GPL sidecar only for validation. Ignore pagegraph-crawl, WebGraph and the dead or Python tools for the core build.

### Cited Findings (basis for each verdict)
- TRC: Apache-2.0, active 2026, collector API, mobile emulation, autoconsent optIn/optOut, API breakpoints with script attribution, screenshots, library mode with injectable `browserConnection` — [README](https://github.com/duckduckgo/tracker-radar-collector/blob/main/README.md), [LICENSE](https://github.com/duckduckgo/tracker-radar-collector/blob/main/LICENSE)
- Leaky Forms: GPL v3, Puppeteer 10, code untouched since 2022, but implements exactly the email-fill-without-submit plus postData capture — [repo](https://github.com/leaky-forms/leaky-forms-crawler)
- Blacklight: GPL-3.0, active, subpages, mobile, fills forms, key-logging detection, full stacks, no autoconsent — [README](https://github.com/the-markup/blacklight-collector/blob/main/README.md)
- WEC: EUPL-1.2, very active, `--max/--depth` subpages, persistent profile, cookie/LS stack, HAR, no mobile, no autoconsent — [README](https://code.europa.eu/EDPS/website-evidence-collector/-/blob/main/README.md)
- pagegraph-crawl: needs a Brave Nightly binary; Puppeteer interaction "will likely fail" while recording — [README](https://github.com/brave/pagegraph-crawl/blob/main/README.md)
- WebGraph: Python and OpenWPM (Firefox), with open compatibility issues as of 2024-07 — [README](https://github.com/spring-epfl/WebGraph/blob/main/README.md)

### Inferences

| Candidate | Verdict | Reasons |
|---|---|---|
| **duckduckgo/tracker-radar-collector** | **FORK + EXTEND (primary base), run as subprocess sidecar** | Apache-2.0. Active (commits through 2026-10-06; autoconsent updated 2026-07). Already does MOB, AC (all 3 modes), the API tracer with caller, SS and Set-Cookie. A clean collector API means TraceMap adds POST/initiator, storage, subpage, leak, bot-wall and profile-wrapper code (≈0.8–1.2k lines). Risks: no releases (pin a commit), JSDoc-only schema, single-navigation lifecycle. |
| **leaky-forms/leaky-forms-crawler** | **PORT IDEAS** (do not fork) | GPL-3.0 (LICENSE) vs Apache (package.json) ambiguity. Puppeteer 10 / Node 12 is badly outdated relative to current TRC. Its postData + requestHeaders + WebSocket-frame capture and its human-like typing + Tab blur + Fathom detection are the exact design for TraceMap's leak test. Re-implement on current TRC. Cite the USENIX'22 paper as methodological precedent. |
| **the-markup/blacklight-collector** | **PORT IDEAS + optional SIDECAR for validation** | Best feature overlap for SP, LEAK and keylogging, but GPL-3.0, no autoconsent, monolithic `collect()`, and a random subpage sample (reproducibility issue for A/B comparison). Useful as a ground-truth cross-check run as a separate npm program in its own folder or container. Port: autocomplete-keyed canary field list, postData search in plain/base64/hash forms, addEventListener proxy idea, cookie setter matching. |
| **EDPS website-evidence-collector** | **PORT IDEAS / optional reference sidecar** | Very active (v4.5.0, 2026-09-30) and evidence-grade reports (HTML/PDF/YAML/JSON). But EUPL-1.2 copyleft, Node >=22.17, no mobile emulation, no autoconsent. Ideas to borrow: first-party link queue with `--max/--depth`, refusing redirects to third parties during link pre-checks, stack-recorded cookie/localStorage events, beacon classification via filter lists. |
| **brave/pagegraph-crawl (+ PageGraph)** | **IGNORE for core**; maybe a stretch goal | MPL-2.0 and active, with the richest attribution (full graph). But it requires a Brave Nightly binary for JS API recording, outputs GraphML, and Puppeteer interaction breaks recording, which conflicts with autoconsent, scrolling and canary typing. Possible stretch: a separate passive PageGraph visit for attribution analysis. |
| **spring-epfl/WebGraph** | **IGNORE** (cite only) | Not a Node crawler. Python ML pipeline over OpenWPM (Firefox) data. Last push 2024-07 with unresolved OpenWPM issues. No LICENSE detected. Its graph features could inspire TraceMap analysis later. |
| **Liscor/consentcrawl** | **PORT IDEAS** (MIT) | Python/Playwright, inactive since 2023-12. Before/after-consent comparison and CMP list are useful references. TRC's autoconsent is better maintained. |
| **privacy-tech-lab/gpc-web-crawler** | **IGNORE** (cite if GPC is in scope) | MIT and active, but Selenium + Firefox extension + Docker Compose stack focused on GPC. |
| **webbkoll-backend** | **IGNORE** | Archived on Codeberg in 2025-04. Self-described "highly experimental". |
| **ghostery/areweprivateyet** | **IGNORE** | Dead since 2015. |
| **whotracks.me** | **Use as DATA, not crawler** | MIT data + Python API + TrackerDB for tracker→company labelling in TraceMap's Python analysis. No open crawler found. |
| **duckduckgo/autoconsent** | **USE as dependency** (via TRC) | MPL-2.0, very active. Already wired into TRC's CookiePopupsCollector. |

**Suggested build plan for TraceMap's Node part** (inference):
1. Fork TRC at a pinned commit into `crawler/`.
2. Add `TraceMapRequestCollector` (postData, all headers, raw initiator stack, WebSocket frames).
3. Add `StorageCollector` (cookie values and flags, localStorage/sessionStorage per frame).
4. Add breakpoints for `HTMLInputElement.value`, `addEventListener` (keyboard/input types) and `Storage.setItem`.
5. Add `BotWallCollector`.
6. Add `LeakTestCollector`: detect fields, type canaries, blur, no submit.
7. Write a `tracemap-run.js` wrapper that:
   - launches Chromium with persistent profiles A and B
   - for each profile and each page (landing plus about 4 deterministic same-site links, e.g. sorted or first-N, for A/B comparability), calls `crawler()` with mobile emulation and the chosen autoconsent action
   - relaunches profile A for the revisit
   - writes `out/<site>/<profile_visit>/<page>.json`
8. Python orchestrates through `subprocess.run` and parses the JSON with pydantic models.

### Gaps
- None of these effort or performance estimates are measured. A 1–2 day spike on TRC (install, mobile + optOut crawl, one custom collector) would validate the plan before committing.
