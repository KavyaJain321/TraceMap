# Third-party notices

TraceMap's own code is licensed under Apache-2.0. It includes or adapts:

| Component | License | How it is used |
|---|---|---|
| DuckDuckGo tracker-radar-collector (commit 3aec03f) | Apache-2.0 | API list in `tracemap/crawl/instrument.js` and the autoconsent message protocol in `tracemap/crawl/consent.py` are adapted from `collectors/APICalls/breakpoints.js` and `collectors/CookiePopupsCollector.js`. Changes: rewritten as init-script wrappers / Python; extra hooks added. |
| DuckDuckGo autoconsent 16.47.0 | MPL-2.0 | Vendored unmodified in `tracemap/crawl/vendor/autoconsent/` (see NOTICE.md there). `filter_compact_rules` is a Python port of its `filterCompactRules`. |
| Englehardt & Narayanan 2016; Senol et al. 2022 (Leaky Forms); Englehardt et al. 2018 | papers | Methods reimplemented from the publications (no code copied). |

Data fetched at runtime (not redistributed; see `data/lists/manifest.json`):

| Data | License |
|---|---|
| DuckDuckGo TDS / Tracker Radar | CC BY-NC-SA 4.0 |
| Disconnect services.json | CC BY-NC-SA 4.0 |
| Ghostery TrackerDB | CC BY-NC-SA 4.0 |
| third-party-web | MIT |
| EasyList / EasyPrivacy / IndianList | GPL-3.0+ or CC BY-SA 3.0+ |
| AdGuard Tracking Protection filter | GPL-3.0 |
| AdGuard cname-trackers | MIT |

Because the NC-SA sources are non-commercial, TraceMap's labelled outputs that contain
substantial portions of them must be released under CC BY-NC-SA 4.0.
