# Open-source detection & classification building blocks for TraceMap (verified 2026-10-07)

Method note: every repo was checked on 2026-10-07 through its GitHub commits Atom feed (last-commit date) and LICENSE file. Every data URL was fetched live (HTTP 200 unless stated). Every pip package was checked on the PyPI JSON API. Several components were also **run locally** in a fresh Python 3.11 venv on Windows: adblock, braveblock, dnspython, whoisit, tree-sitter, the OSV API, and the retire.js repo. Results marked "local test" come from those runs. Anything I could not fetch is marked **UNVERIFIED**.

---

## Q1. Tracker lists and entity/ownership data: which to use, formats, licenses

### Takeaway
Use DuckDuckGo's **TDS + Tracker Radar** and **Ghostery TrackerDB** for owner and category. Use **Disconnect** for extra owners and categories, and **third-party-web** (MIT) as the only permissively licensed entity map. Use **EasyPrivacy + AdGuard Tracking Protection** as the rule layer.

All the rich entity datasets (DDG, Disconnect, Ghostery) are **CC BY-NC-SA 4.0**. That is fine for a non-commercial college project, but derived data must stay NC-SA and be attributed.

### Cited Findings
**DuckDuckGo TDS (blocklist)**
- The v6 URL works: `https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json`. It returned 200, 1,484,300 bytes, Last-Modified 21 Sep 2026. A v5 URL also still works. — [TDS v6](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json)
- Top-level keys are `_builtWith, readme, trackers, entities, domains, cnames`.
  - Counts in the current file: 1,001 trackers, 761 entities, 5,215 domains, 788 cnames.
  - A tracker object looks like `{domain, owner:{name,displayName}, prevalence, fingerprinting(0-3), cookies, categories[], default:"block"|"ignore", rules:[{rule(regex), fingerprinting, cookies, exceptions?}]}`.
  - `entities[name] = {domains[], prevalence, displayName}`.
  - `domains[domain] = entityName`.
  - `cnames[cloakedHost] = trackerHost`, for example `aa.philippineairlines.com → t72rzxitjl.data.adobedc.net`.
  - Source: local parse of [TDS v6](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json).
- TDS categories seen (counts): Ad Motivated Tracking 225, Advertising 219, Analytics 158, Third-Party Analytics Marketing 112, Audience Measurement 95, Embedded Content 82, Content Delivery 71, Action Pixels 58, Ad Fraud 31, **Session Replay 24**, Social-Share 14, Support Chat Widget 12, and others. — local parse of [TDS v6](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json)
- 532 TDS trackers have `fingerprinting >= 2`. — same source
- License: "Licensed under the CC BY-NC-SA 4.0 license". Repo last commit 2026-09-21. — [tracker-blocklists LICENSE](https://github.com/duckduckgo/tracker-blocklists/blob/main/LICENSE)

**DuckDuckGo Tracker Radar (full dataset)**
- Layout: `domains/<REGION>/<domain>.json` and `entities/<Entity>.json`. Regions present are only **AU, CA, CH, DE, FR, GB, NL, NO, US**. There is **no IN (India) crawl region**. — [tracker-radar/domains](https://github.com/duckduckgo/tracker-radar/tree/main/domains)
- Domain-file fields: `domain, owner{name,displayName,privacyPolicy,url}, source, prevalence, sites, subdomains, cnames, fingerprinting, resources[{rule, cookies, fingerprinting, apis{API:count}, sites, prevalence, cnames, responseHashes(sha256), type, firstPartyCookies, exampleSites}], categories, performance, cookies, topInitiators, types, nameservers`. — [clevertap.com.json](https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/domains/US/clevertap.com.json), [fullstory.com.json](https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/domains/US/fullstory.com.json)
- Fingerprinting score scale:
  - 0 = "No use of browser API's"
  - 1 = "some use … not obviously for tracking"
  - 2 = "many browser API's, possibly for tracking"
  - 3 = "Excessive use … almost certainly for tracking"
  - Source: [DATA_MODEL.md](https://github.com/duckduckgo/tracker-radar/blob/main/docs/DATA_MODEL.md)
- `build-data/generated/api_fingerprint_weights.json` maps API names to fingerprinting weights. Examples: `Navigator.prototype.cookieEnabled: 11.57`, `window.innerHeight: 8.1`, `Screen.prototype.height: 6.71`. — [api_fingerprint_weights.json](https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/build-data/generated/api_fingerprint_weights.json)
- An entity file lists all properties. For example, CleverTap has `clevertap-prod.com, clevertap.com, leanplum.com, wzrkt.com`. — [entities/CleverTap.json](https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/entities/CleverTap.json)
- "Session Replay" category definition: "scripts that record visitors' journeys… mouse movement, clicks, taps, scrolls or even network activity". — [CATEGORIES.md](https://github.com/duckduckgo/tracker-radar/blob/main/docs/CATEGORIES.md)
- License is CC BY-NC-SA 4.0. Last commit 2026-09-23. Its collector (`tracker-radar-collector`) was last committed 2026-10-06. — [tracker-radar LICENSE](https://github.com/duckduckgo/tracker-radar/blob/main/LICENSE), [tracker-radar-collector](https://github.com/duckduckgo/tracker-radar-collector)

**Disconnect**
- `services.json` (378 KB) and `entities.json` (413 KB) are both live. Their embedded license header reads "Copyright 2010-2026 Disconnect, Inc. / Licensed under … CC BY-NC-SA 4.0". — [services.json](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json), [entities.json](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/entities.json)
- `services.json` categories: Email, EmailAggressive, Advertising, Content, Analytics, **FingerprintingInvasive (282 entries)**, **FingerprintingGeneral (96)**, Anti-fraud, Social, ConsentManagers, Cryptomining.
  - Structure: `categories[cat] = [{EntityName: {homepage: [domains…]}}]`.
  - `entities.json`: `{entities: {Name: {properties[], resources[]}}}`.
  - Source: local parse of [services.json](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json)
- Repo last commit 2026-09-28. — [disconnect-tracking-protection](https://github.com/disconnectme/disconnect-tracking-protection)

**Ghostery TrackerDB**
- Latest release is `202610011537`. Release assets are `trackerdb.json`, `trackerdb.db`, `trackerdb.engine` and `trackerdb.txt`. — [releases/latest](https://github.com/ghostery/trackerdb/releases/latest)
- `trackerdb.json` keys and counts: `categories` (11), `organizations` (2,608), `patterns` (3,535), `domains` (5,106 domain → pattern key), `filters` (4,606 ABP filter → pattern).
  - An organization has `{name, description, website_url, country, privacy_policy_url, ghostery_id}`.
  - A pattern has `{name, category, organization, domains[], filters[]}`.
  - The 11 categories: advertising, audio_video_player, consent, customer_interaction, extensions, hosting, misc, pornvertising, site_analytics, social_media, utilities. There is **no session-replay category**.
  - Source: local parse of [trackerdb.json](https://github.com/ghostery/trackerdb/releases/download/202610011537/trackerdb.json)
- Orgs with `country == "IN"`: adadyn, adgebra, admaya, cirklestudio, inmobi, vizury, zoho_corp. — same source
- npm `@ghostery/trackerdb` is at 1.0.952 (2026-10-01), license CC-BY-NC-SA-4.0. It has a JS SDK (`matchDomain`, `matchUrl`) and a CLI (`npx @ghostery/trackerdb <url>`). **No PyPI package exists** (`trackerdb` returns 404 on PyPI). — [npm registry](https://registry.npmjs.org/@ghostery/trackerdb), [trackerdb README](https://github.com/ghostery/trackerdb), [PyPI 404](https://pypi.org/pypi/trackerdb/json)
- LICENSE: "Licensed under the CC-BY-NC-SA-4.0 license". — [trackerdb LICENSE](https://github.com/ghostery/trackerdb/blob/main/LICENSE)

**WhoTracks.me**
- The repo is MIT and was last committed 2026-10-01. The site has moved to ghostery.com/whotracksme (`whotracks.me/trackers/*.html` now redirects there).
  - It publishes monthly raw data with a Python loader: `from whotracksme.data.loader import DataSource`, installed via `uv sync` from the repo.
  - Its metadata comes from TrackerDB.
  - The PyPI `whotracksme` package is stale (2018.5.17).
  - Sources: [whotracks.me repo](https://github.com/whotracksme/whotracks.me), [PyPI whotracksme](https://pypi.org/pypi/whotracksme/json)

**patrickhulce/third-party-web**
- MIT; npm `third-party-web` 0.30.0 published 2026-09-14. — [npm](https://registry.npmjs.org/third-party-web), [repo](https://github.com/patrickhulce/third-party-web)
- Data is at `data/entities.js` in the repo (200). The built JSON comes from the npm package at `https://unpkg.com/third-party-web@0.30.0/dist/entities.json`. **`raw.githubusercontent.com/.../dist/entities.json` returns 404** because `dist` is not committed. — [data/entities.js](https://raw.githubusercontent.com/patrickhulce/third-party-web/master/data/entities.js), [unpkg dist](https://unpkg.com/third-party-web@0.30.0/dist/entities.json)
- 2,143 entities, each `{name, company, homepage, category, domains[] (wildcards like *.x.com)}`. Categories (counts): ad 751, analytics 393, utility 281, content 192, hosting 92, other 91, marketing 82, customer-success 76, consent-provider 69, social 64, cdn 30, tag-manager 15, video 7. — local parse of [unpkg dist](https://unpkg.com/third-party-web@0.30.0/dist/entities.json)

**Filter lists**
- EasyList and EasyPrivacy are live, with version 202610071457 dated 07 Oct 2026 (57,043 lines in EasyPrivacy). — [easyprivacy.txt](https://easylist.to/easylist/easyprivacy.txt), [easylist.txt](https://easylist.to/easylist/easylist.txt)
- The EasyList repo is dual-licensed **GPL-3.0+ or CC BY-SA 3.0+**, with attribution to "The EasyList authors". — [EasyList licence](https://easylist.to/pages/licence.html)
- IndianList:
  - It is described as a supplement to EasyList "designed to block advertising on Indian websites", covering 14 languages. It is ad-focused, not tracker-focused.
  - The list header points to the EasyList licence.
  - Download URL: `https://easylist-downloads.adblockplus.org/indianlist.txt`. A combined `indianlist+easylist.txt` also exists.
  - Repo `mediumkreation/IndianList` was last committed 2026-10-06.
  - Sources: [IndianList repo](https://github.com/mediumkreation/IndianList), [indianlist.txt](https://easylist-downloads.adblockplus.org/indianlist.txt)
- AdGuard filters:
  - Tracking Protection is filter 3 (`https://filters.adtidy.org/extension/ublock/filters/3.txt`, 10.9 MB). Base is filter 2. URL Tracking is filter 17.
  - AdGuard's own catalogue lists **no AdGuard-authored Indian filter**. The only India entry (id 253) is the third-party IndianList.
  - The AdguardFilters repo is GPL-3.0.
  - Sources: [filter 3](https://filters.adtidy.org/extension/ublock/filters/3.txt), [AdGuard filters.json](https://filters.adtidy.org/extension/chromium/filters.json), [AdguardFilters](https://github.com/AdguardTeam/AdguardFilters)
- uBlock Origin:
  - It ships IndianList as asset `IND-0` (langs as bn gu hi kn ml mr ne pa sat si ta te).
  - `uAssets/filters/privacy.txt` is live.
  - uAssets is GPL-3.0, last commit 2026-10-07.
  - Sources: [uBlock assets.json](https://github.com/gorhill/uBlock/blob/master/assets/assets.json), [uAssets privacy.txt](https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt)
- Peter Lowe list is live in ABP and hosts formats (Last-Modified 05 Oct 2026). — [pgl.yoyo.org](https://pgl.yoyo.org/adservers/serverlist.php?hostformat=adblockplus&showintro=0&mimetype=plaintext)

### Inferences
- **Primary owner/category resolver:** a merged lookup keyed by eTLD+1 (use `tldextract`, which [PyPI](https://pypi.org/pypi/tldextract/json) shows at v5.4.0, 2026-10). Use this priority:
  1. DDG TDS `domains` and `entities`
  2. Tracker Radar entity files
  3. Ghostery TrackerDB `domains` → `patterns` → `organizations` (adds country and description)
  4. Disconnect `entities`
  5. third-party-web
  6. TraceMap's own India seed list
- Map every source's category vocabulary onto one TraceMap taxonomy, for example: advertising, analytics, session-replay, CDP/martech, push-notification, social, consent, CDN/hosting, fraud/fingerprint, chat/support.
- Licensing: keep the CC BY-NC-SA data as runtime-downloaded data, not baked into the code. Credit the sources in the report and UI. Do not sell TraceMap output. third-party-web (MIT) is the only entity map safe for any future commercial pivot.
- TDS `extension-tds.json` is a *subset* (about 1k trackers). For broader coverage, also load Tracker Radar `domains/US/*.json`, which also carries per-resource fingerprinting scores and API counts.

### Gaps
- Peter Lowe list licence/terms text could not be extracted from pgl.yoyo.org (**UNVERIFIED**).
- I did not measure the exact size of the WhoTracks.me monthly raw-data download, and I did not verify its current download URL (**UNVERIFIED**; the README links `whotracksme/data/Readme.md`).

---

## Q2. Which source has the best India coverage? Are there India-specific tracker lists?

### Takeaway
No single list covers Indian martech well. **EasyPrivacy and AdGuard Tracking Protection have the best Indian rule coverage. Disconnect has the best Indian owner and category coverage.** IndianList is ad-focused and contributes almost nothing for trackers. DDG Tracker Radar has no India crawl.

TraceMap should ship a small hand-curated **India seed entity file** for CleverTap, MoEngage, WebEngage, Netcore, iZooto, Times/Colombia, InMobi, Affle, Wingify, Zoho, Freshworks and others, layered on top of the merged datasets.

### Cited Findings
- Local coverage matrix computed 2026-10-07 against the live files. T = TDS tracker, D = TDS domain map, Y = a rule matches the domain. Sources: [TDS](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json), [Disconnect](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json), [TrackerDB](https://github.com/ghostery/trackerdb/releases/download/202610011537/trackerdb.json), [3PW](https://unpkg.com/third-party-web@0.30.0/dist/entities.json), [EasyPrivacy](https://easylist.to/easylist/easyprivacy.txt), [AdGuard 3](https://filters.adtidy.org/extension/ublock/filters/3.txt), [IndianList](https://easylist-downloads.adblockplus.org/indianlist.txt), [Peter Lowe](https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext), [AdGuard CNAME](https://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_trackers_justdomains.txt)

| Vendor / domain | TDS | Disconnect | TrackerDB | 3PWeb | EasyPrivacy | AdG-Track | IndianList | P.Lowe |
|---|---|---|---|---|---|---|---|---|
| CleverTap clevertap.com | - | CleverTap/Analytics | - | - | . | . | . | . |
| CleverTap wzrkt.com | - | - | clever_tap/site_analytics | WizRocket/analytics | Y | Y | . | . |
| CleverTap clevertap-prod.com | - | CleverTap/Analytics | - | - | Y | Y | . | . |
| MoEngage moengage.com | - | MoEngage/EmailAggressive | - | - | Y | Y | . | . (in AdG CNAME list) |
| WebEngage webengage.com | T: Webklipper, fp2 | - | - | WebEngage/customer-success | Y | Y | . | . |
| Netcore netcoresmartech.com | - | - | - | - | Y | Y | . | . |
| Netcore netcorecloud.net / pepipost.com | - | - | - | - | . | . | . | . |
| Netcore Unbxd unbxdapi.com | T: Unbxd, fp3 | Netcore UNBXD/Advertising | - | - | Y | Y | . | . |
| iZooto izooto.com | - | iZooto/Advertising | - | iZooto/marketing | Y | Y | **Y** | . |
| Times/Colombia clmbtech.com | - | TimesInternet/Advertising | - | - | . (EasyList Y) | . | **Y** | Y |
| Times growthrx.in | - | - | - | - | Y | Y | . | Y |
| InMobi inmobi.com | T: InMobi, fp1 | - | - | InMobi/ad | Y | Y | . | Y |
| Affle vizury.com | - | Affle/Advertising | vizury/advertising | Vizury/ad | Y | Y | . | . |
| Affle affle.com / revx.io | - | - | - | - | . | . | . | . |
| Wingify visualwebsiteoptimizer.com | T: Wingify [Analytics, **Session Replay**], fp2 | Wingify/Analytics | site_analytics | VWO/analytics | Y | Y | . | Y |
| Zoho pagesense.io | D: ZOHO | Zoho/Analytics | - | PageSense/analytics | Y | Y | . | . |
| Freshworks freshmarketer.com | - | - | - | - | Y | Y | . | Y |
| Zeotap zeotap.com | T: Zeotap, fp1 | Zeotap/Advertising | - | ZEOTAP/ad | Y | Y | . | Y |
| Lemnisk lemnisk.co | - | - | - | - | Y | . | . | Y |
| NotifyVisitors notifyvisitors.com | - | - | - | - | Y | Y | . | . |
| Wigzo wigzo.com | - | - | - | Wigzo/marketing | . | . | . | . |
| Tyroo tyroo.com | - | Tyroo/Advertising | - | - | . (EasyList Y) | . | . | Y |
| GoKwik gokwik.co / Truecaller truecaller.com | - | - | - | - | Y | Y | . | . |
| Apxor, Haptik, Plumb5, Capillary, mFilterIt | - | - | - | - | . | . | . | . |

- TrackerDB has only 7 orgs with country=IN: adadyn, adgebra, admaya, cirklestudio, inmobi, vizury, zoho_corp. — local parse of [trackerdb.json](https://github.com/ghostery/trackerdb/releases/download/202610011537/trackerdb.json)
- Tracker Radar crawl regions exclude India. — [tracker-radar/domains](https://github.com/duckduckgo/tracker-radar/tree/main/domains)
- IndianList's stated purpose is advertising on Indian-language sites. — [IndianList README](https://github.com/mediumkreation/IndianList)

### Inferences
- Recommended India stack:
  1. EasyPrivacy + AdGuard Tracking Protection + IndianList + Peter Lowe, as matching rules via `adblock`. This gives the "is it a tracker / which rule" answer.
  2. TDS + Tracker Radar + TrackerDB + Disconnect + third-party-web, merged, for owner and category.
  3. A curated `india_entities.json` maintained by the TraceMap team. It should hold entity, parent company, country, category and domains, for example Netcore {netcoresmartech.com, netcorecloud.net, pepipost.com, unbxd.io}, Affle {affle.com, vizury.com, mediasmart.io, appnext.com, jampp.com, revx.io}, and Times Internet {clmbtech.com, colombiaonline.com, growthrx.in, timesinternet.in}.
- Parent-company mapping must be hand-curated. The datasets disagree on ownership. For example, Disconnect labels vdopia.com as Silverpush and adpushup.com as Geniee, while TDS attributes adpushup.com to "CacheNetworks". A hand-verified table is a legitimate project contribution (an "India martech ownership dataset").
- Several Indian vendors (Apxor, Haptik, Plumb5, Capillary, mFilterIt, pepipost, netcorecloud.net) appear in **no** list. TraceMap's crawl of Indian sites can surface these as "unknown third party with tracking behaviour", which the ML classifier then labels.

### Gaps
- I matched only registrable domains. Vendor CDN hostnames (for example `cdn.moengage.com` and SDK subdomains) were not enumerated exhaustively.
- I did not verify which domains MoEngage, WebEngage or Netcore actually load on Indian sites today. That needs TraceMap's own crawl.
- I found no maintained India-specific *tracker* (privacy) list.

---

## Q3. Filter-list matching in Python: adblock vs braveblock vs adblockparser

### Takeaway
Use **`adblock` (python-adblock)**. It has a Windows abi3 wheel that works on Python 3.11. It returns the **matched rule text** (`BlockerResult.filter`) when `FilterSet(debug=True)`, and it is very fast. braveblock returns only a bool. adblockparser is archived, pure Python and slow.

### Cited Findings
- PyPI `adblock` 0.6.0 (2022-07-17), license MIT OR Apache-2.0. Wheels include `adblock-0.6.0-cp37-abi3-win_amd64.whl`. It is a wrapper of Brave's Rust adblock engine. — [PyPI adblock](https://pypi.org/pypi/adblock/json), [python-adblock](https://github.com/ArniDagur/python-adblock)
- The repo's last commit is 2023-03-28, so it is effectively unmaintained. Upstream `brave/adblock-rust` (MPL-2.0) is active, with its last commit on 2026-09-29. — [python-adblock commits](https://github.com/ArniDagur/python-adblock/commits), [adblock-rust](https://github.com/brave/adblock-rust)
- API from the type stubs:
  - `FilterSet(debug: bool)` with `.add_filter_list(text, format="standard")`
  - `Engine(filter_set, optimize=True)` with `.check_network_urls(url, source_url, request_type) -> BlockerResult{matched, important, redirect, exception, filter, error}`
  - `check_network_urls_with_hostnames(...)`, `serialize_to_file` / `deserialize_from_file`, and `use_tags` / `enable_tags`
  - Source: [adblock.pyi](https://github.com/ArniDagur/python-adblock/blob/master/adblock/adblock.pyi)
- Local test on Python 3.11, Windows, with EasyPrivacy + EasyList + AdGuard Tracking + IndianList:
  - Engine build took 1.37 s.
  - `https://wzrkt.com/a` gave `matched=True, filter=||wzrkt.com^`.
  - `cdn.izooto.com` gave `filter=||izooto.com^$3p`.
  - `ade.clmbtech.com` gave `filter=||clmbtech.com^`.
  - `code.jquery.com` gave `matched=False`.
  - 20,000 checks took 0.065 s.
  - Source: local run of [adblock](https://pypi.org/pypi/adblock/json)
- `braveblock` 0.5.1 (2024-02-14, MIT) has Windows wheels for cp37–cp311. Its `Adblocker.check_network_urls(url, source_url, request_type) -> bool` returns no rule text (verified locally). The repo is `intsights/braveblock`; the `dhvcc/braveblock` URL returns 404. — [PyPI braveblock](https://pypi.org/pypi/braveblock/json)
- `adblockparser` 0.7 was last released 2016 and the repo is archived. It is MIT and pure Python. — [PyPI adblockparser](https://pypi.org/pypi/adblockparser/json), [scrapinghub/adblockparser](https://github.com/scrapinghub/adblockparser)

### Inferences
- The matched rule does not say which list it came from. Build **one Engine per list** (EasyPrivacy, AdGuard-Tracking, IndianList, Peter Lowe, uBO-privacy). This yields per-list binary ML features like `in_easyprivacy` and `in_adguard_tracking` plus the rule string for explanations, which keeps the model interpretable.
- Pin `adblock==0.6.0`. If it ever breaks on a newer Python, the fallback is the Ghostery engine via a Node subprocess, or rebuilding the wheel with maturin from the repo. Python 3.11 is safe today.

### Gaps
- The local throughput figure may be helped by internal caching on repeated URLs. A realistic benchmark on unique URLs was not run.

---

## Q4. CNAME cloaking detection

### Takeaway
Resolve each first-party-looking subdomain with **dnspython**, follow the CNAME chain, and match the final targets against:
- **AdGuard cname-trackers** "original trackers" (about 93 tracker domains, MIT),
- DDG TDS `cnames` (788 entries),
- Tracker Radar `cnames`.

The NextDNS list repo now returns 404.

### Cited Findings
- AdGuard `cname-trackers` is MIT, last commit 2026-09-14. Its `data/` folder provides lists for trackers, ads, clickthroughs, mail_trackers and microsites, in `.txt` (ABP), `_justdomains.txt`, `_rpz.txt` and `.json` (`{disguised_host: original_tracker}`) formats.
  - `combined_disguised_trackers_justdomains.txt` has about 224,825 disguised hostnames.
  - `combined_original_trackers_justdomains.txt` has 93 original tracker domains.
  - Sources: [cname-trackers data](https://github.com/AdguardTeam/cname-trackers/tree/master/data), [combined_disguised_trackers.json](https://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/combined_disguised_trackers.json)
- TDS `cnames` maps a cloaked host to the tracker host (788 entries). Tracker Radar domain files also carry a `cnames` field per resource. — [TDS v6](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json), [DATA_MODEL.md](https://github.com/duckduckgo/tracker-radar/blob/main/docs/DATA_MODEL.md)
- NextDNS repo `nextdns/cname-cloaking-blocklist` and its raw `domains` file both returned **HTTP 404** on 2026-10-07. A NextDNS forum post says their list "only lists CNAME targets", unlike AdGuard's list. — [NextDNS help forum](https://help.nextdns.io/t/35hfwjg/add-adguard-cname-trackers-blocklist)
- dnspython 2.8.0 (2025-09-07, ISC, requires Python >=3.10) is pure Python and works on Windows. — [PyPI dnspython](https://pypi.org/pypi/dnspython/json), [dnspython LICENSE](https://github.com/rthalley/dnspython/blob/main/LICENSE)
- In a local test, `aa.philippineairlines.com` resolved via CNAME to `t72rzxitjl.data.adobedc.net`, and `metrics.att.com` resolved to `…edgekey.net → akamaiedge.net`. Read the chain from `answer.response.answer` (rdtype 5). — local run of [dnspython](https://pypi.org/pypi/dnspython/json)

### Inferences
- Algorithm:
  1. For each request host whose eTLD+1 equals the site's eTLD+1 (or a sibling first-party domain), resolve A/AAAA and collect every CNAME in the chain.
  2. If any chain member's eTLD+1 differs from the site's and matches a tracker in AdGuard-original, a TDS tracker, or a Tracker Radar domain, flag it as **CNAME-cloaked**. Record the target entity and whether cookies were sent, since first-party cookies leak.
- Point dnspython at a fixed public resolver (for example 1.1.1.1) for reproducibility, and cache results.
- Prefer the **AdGuard JSON (disguised → original)** as ground truth for evaluation. Use the 93 "original" domains plus TDS/Tracker Radar as the live matcher, so new cloaked subdomains are still caught.

### Gaps
- I could not find out whether the NextDNS list moved or was deleted. Treat it as **UNVERIFIED/unavailable**.

---

## Q5. Fingerprinting detection (canvas, font, WebRTC, audio, navigator)

### Takeaway
Implement the **Englehardt & Narayanan 2016 rules** directly. Blacklight's MIT-incompatible GPL TypeScript (`canvas-fingerprinting.ts`) is a faithful reference, so reimplement it in Python rather than copying. Use **OpenWPM's `fingerprinting.json`** instrumentation set and **Blacklight's `FINGERPRINTABLE_WINDOW_APIS`** as the API inventory.

For ML features, use DDG's `api_fingerprint_weights.json`. For extra labels, use Disconnect Fingerprinting categories, FP-Inspector's 3,325 fingerprinting domain/script records, and EasyPrivacy's "fingerprint" rules.

### Cited Findings
- **Englehardt & Narayanan (CCS 2016), exact rules**, from [the paper PDF](https://www.cs.princeton.edu/~arvindn/publications/OpenWPM_1_million_site_tracking_measurement.pdf):
  - **Canvas:** a script counts as fingerprinting only if all of these hold:
    1. Canvas height and width are not set below 16 px.
    2. Text is written to the canvas with at least two colours or at least 10 distinct characters.
    3. The script does not call `save`, `restore` or `addEventListener` on the rendering context.
    4. It extracts an image with `toDataURL`, or with a single `getImageData` call covering at least 16×16 px.
    - The authors report 4 false positives out of 3,493 scripts.
  - **Canvas font:** "the script sets the `font` property to at least 50 distinct, valid values and also calls `measureText` at least 50 times on the same text string". They report zero false positives.
  - **WebRTC local-IP discovery:** "select the scripts which call the `createDataChannel` and `createOffer` APIs, and access the event handler `onicecandidate`".
  - **Audio:** described from manual analysis, not a numeric rule. The pattern is an OscillatorNode feeding a DynamicsCompressorNode, then an OfflineAudioContext buffer, then a hash of the summed buffer. A second variant uses OscillatorNode with AnalyserNode, ScriptProcessorNode and a zero-gain GainNode feeding the destination.
- **Blacklight (The Markup) `blacklight-collector`:**
  - **GPL-3.0**, last commit 2026-06-04. The working repo URL is `the-markup/blacklight-collector`; `themarkup/...` returns 404.
  - `src/canvas-fingerprinting.ts` implements the above with constants: `MIN_CANVAS_IMAGE_WIDTH/HEIGHT = 16`, `MIN_FONT_LIST_SIZE = 50`, `MIN_TEXT_MEASURE_COUNT = 50`, `MIN_TEXT_LENGTH = 10`.
  - API sets in that file:
    - Read: `HTMLCanvasElement.toDataURL`, `CanvasRenderingContext2D.getImageData`
    - Write: `fillText`, `strokeText`
    - Do-not-call: `save`, `restore`, `HTMLCanvasElement.addEventListener`
  - A script is flagged when it reads and writes on the same host and has no banned call.
  - Sources: [canvas-fingerprinting.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/canvas-fingerprinting.ts), [LICENSE](https://github.com/the-markup/blacklight-collector/blob/main/LICENSE)
- Blacklight's `FINGERPRINTABLE_WINDOW_APIS` groups:
  - AUDIO: AudioContext.createOscillator / createAnalyser / createDynamics…, AnalyserNode.getFloatFrequencyData, OscillatorNode.start, ScriptProcessorNode.onaudioprocess, and similar
  - BATTERY: getBattery
  - CANVAS
  - MEDIA_DEVICES: enumerateDevices
  - MIME, NAVIGATOR (16 properties), PLUGIN
  - SCREEN: pixelDepth, colorDepth
  - WEBRTC: RTCPeerConnection
  - Source: [statics.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/helpers/statics.ts)
- **OpenWPM** is GPL v3 and active (last commit 2026-10-04). `openwpm/js_instrumentation_collections/fingerprinting.json` has 14 entries:
  - ScriptProcessorNode, GainNode, AnalyserNode, OscillatorNode, OfflineAudioContext, AudioContext
  - RTCPeerConnection, HTMLCanvasElement, CanvasRenderingContext2D (with excludedProperties)
  - Storage, window.navigator
  - window {name, localStorage, sessionStorage}
  - window.document {cookie, referrer}
  - window.screen {pixelDepth, colorDepth}
  - Sources: [fingerprinting.json](https://github.com/openwpm/OpenWPM/blob/master/openwpm/js_instrumentation_collections/fingerprinting.json), [OpenWPM LICENSE](https://github.com/openwpm/OpenWPM/blob/master/LICENSE)
- **FP-Inspector (Iqbal et al., IEEE S&P 2021):**
  - MIT, last commit 2021-03-31 (unmaintained).
  - It releases `Data/fingerprinting_domains.json`, 3,325 hash-keyed entries of `{script_url, top_url}`, and `Data/potential_fingerprinting_APIs.md` (API keyword, FP/non-FP ratio).
  - Its method uses OpenWPM traces plus static script features with ML.
  - The EasyPrivacy "! Fingerprinting" section was created as a result of their reports.
  - Sources: [FP-Inspector README](https://github.com/uiowa-irl/FP-Inspector), [fingerprinting_domains.json](https://raw.githubusercontent.com/uiowa-irl/FP-Inspector/master/Data/fingerprinting_domains.json)
- DDG `api_fingerprint_weights.json` gives a per-API weight, and Tracker Radar per-resource `apis{}` counts and a `fingerprinting` 0–3 score. — [weights](https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/build-data/generated/api_fingerprint_weights.json), [DATA_MODEL.md](https://github.com/duckduckgo/tracker-radar/blob/main/docs/DATA_MODEL.md)
- Disconnect has FingerprintingInvasive (282 entities) and FingerprintingGeneral (96). — [services.json](https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json)
- FingerprintJS (open-source library) is MIT and active (last commit 2026-10-07). EasyPrivacy has path rules such as `/fingerprint-3.4.1.js` and `/fingerprint.min.js`. — [fingerprintjs](https://github.com/fingerprintjs/fingerprintjs), [easyprivacy.txt](https://easylist.to/easylist/easyprivacy.txt)

### Inferences
- TraceMap should implement four rule-based detectors in Python over its JS-call log, keyed by calling-script URL: canvas, canvas-font, WebRTC and audio. For audio, flag `OscillatorNode` + (`OfflineAudioContext.startRendering` or `AnalyserNode.getFloatFrequencyData`) + (`DynamicsCompressorNode` or zero-gain) + buffer read, by the same script.
- Add a fifth, **"navigator enumeration score"**: the sum of DDG weights over the distinct APIs a script touched. Use that score as a continuous feature for the interpretable classifier (logistic regression or decision tree). FP-Inspector and Disconnect Fingerprinting domains can serve as weak positive labels for training and validation.
- Licensing: the rules themselves (thresholds) are facts from a paper. Reimplementing them in Python avoids GPL obligations from Blacklight and OpenWPM code. Cite both.
- For FingerprintJS signature detection, add string signatures on script bodies plus EasyPrivacy path matches. Examples: `FingerprintJS`, `fpjs`, `@fingerprintjs`, `getVisitorId`, `ClientJS`, `getFingerprint`. These signatures are an inference and were not validated.

### Gaps
- The DDG fingerprinting heuristics code lives in "tracker-radar-detector". I did not inspect its exact scoring formula.
- No maintained "FingerprintJS-signature detection list" was found as a standalone open dataset.

---

## Q6. Session-replay and keylogger/form-field-reader detection

### Takeaway
Session replay:
- Union of DDG TDS "Session Replay" (24 domains), Blacklight `SESSION_RECORDERS_LIST` (21 URL patterns), and the Princeton "No Boundaries" vendor set.
- Add behavioural signals: many mouse, key and scroll listeners plus DOM-mutation serialization posted to a third party.

Keylogging:
- Reimplement Blacklight's method. Type canary values (plain, base64, md5, sha256, sha512) into inputs without submitting, then search outgoing POST bodies for them.

### Cited Findings
- DDG TDS trackers with category "Session Replay": abtasty.com, contentsquare.net, crazyegg.com, exponential.com, ezoic.net, flashtalking.com, foresee.com, fullstory.com, hotjar.com, ml314.com (Bombora), mouseflow.com, mxpnl.com (Mixpanel), permutive.com, qualaroo.com, qualtrics.com, tealiumiq.com, **visualwebsiteoptimizer.com (Wingify, an Indian company)**, webvisor.org, yandex.net, yandex.ru, and some Fastly hostnames. — local parse of [TDS v6](https://staticcdn.duckduckgo.com/trackerblocking/v6/current/extension-tds.json)
- Blacklight `SESSION_RECORDERS_LIST`: `mc.yandex.ru/metrika/watch.js`, `mc.yandex.ru/metrika/tag.js`, `mc.yandex.ru/webvisor/`, `fullstory.com/s/fs.js`, `…sessioncam.recorder.js`, `ws.sessioncam.com/Record/record.asmx`, `userreplay.net`, `static.hotjar.com`, `script.hotjar.com`, `insights.hotjar.com/api`, `clicktale.net`, `smartlook.com`, `decibelinsight.net`, `quantummetric.com`, `inspectlet.com`, `mouseflow.com`, `logrocket.com`, `salemove.com`, `d10lpsik1i8c69.cloudfront.net`, `luckyorange.com`, `vwo.com`.
  - The inspector does a substring match of `hostname+pathname` against this list.
  - Blacklight also instruments `addEventListener` and has `BEHAVIOUR_TRACKING_EVENTS`: KEYBOARD (keydown, keypress, keyup, input), MOUSE (click, mousedown, mouseup, mousemove, select, dblclick, scroll), SENSOR and TOUCH.
  - Sources: [statics.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/helpers/statics.ts), [session-recording.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/inspectors/session-recording.ts)
- The Princeton "No Boundaries" session-replay sites page is still online (200). Vendor domains by frequency on the page: yandex.ru, hotjar.com, clicktale.net, inspectlet.com, mouseflow.com, fullstory.com, sessioncam.com, decibelinsight.net, quantummetric.com, userreplay.net, luckyorange.com, smartlook.com. — [No Boundaries session_replay_sites](https://webtransparency.cs.princeton.edu/no_boundaries/session_replay_sites.html)
- Ghostery TrackerDB has no session-replay category. — local parse of [trackerdb.json](https://github.com/ghostery/trackerdb/releases/download/202610011537/trackerdb.json)
- Blacklight key-logging (`src/inspectors/key-logging.ts`):
  - On every **POST** request, it checks whether `postData` contains any canary value from `DEFAULT_INPUT_VALUES`, or the base64, md5, sha256 or sha512 of those values.
  - If so, it emits `KeyLogging {filter, match_type, post_data, post_request_url}`.
  - Example canaries are email `blacklight-headless@themarkup.org` and password `SUPERS3CR3T_PASSWORD`. These are typed by `pptr-utils/interaction-utils.ts` (fills inputs by type/autocomplete, without submitting).
  - The code is GPL-3.0.
  - Sources: [key-logging.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/inspectors/key-logging.ts), [interaction-utils.ts](https://github.com/the-markup/blacklight-collector/blob/main/src/pptr-utils/interaction-utils.ts)

### Inferences
- TraceMap's crawler should fill forms with TraceMap's own canary values (never real data) and log every outgoing body, including GET query strings, beacons and WebSocket frames. Blacklight checks only POST, so extending to these is an improvement. Then test for plain, base64, URL-encoded, md5, sha1, sha256 and sha512 variants. Attribute the leak to the initiator script and label it "form-field exfiltration before submit".
- The session-replay detector should be layered:
  1. Known vendor (domain/URL list union).
  2. Behavioural: a script registers 4 or more of mousemove, scroll, keydown, input, click, plus `MutationObserver`, plus large or compressed periodic POSTs to the same third party.
- Add **Microsoft Clarity** (`clarity.ms`) and **LogRocket**, **Smartlook** and **VWO** explicitly to the India seed list. They are popular on Indian sites. That popularity claim is an inference and was not measured here.

### Gaps
- I did not find a maintained, standalone open "session replay vendors" list beyond these three sources.

---

## Q7. JS library and version identification plus known vulnerabilities

### Takeaway
Use the **retire.js `jsrepository-v4.json`** (Apache-2.0, active) in a small Python matcher. It provides URI, filename and file-content regexes with `§§version§§` placeholders, plus vulnerable ranges with CVEs. Cross-check or extend with the **OSV.dev API** (free, no key, verified) using the npm ecosystem.

For broader technology fingerprints, use **enthec/webappanalyzer** JSON (GPL-3.0 data) with your own matcher. Avoid `python-Wappalyzer` (archived). Treat `wappalyzer-next` as an optional external tool only: it drives the Wappalyzer extension through Playwright.

### Cited Findings
- Retire.js:
  - Apache-2.0, last commit 2026-10-06; npm `retire` 6.1.0 published 2026-10-06.
  - Repository URLs (both 200): `https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository-v4.json` (595 KB) and `jsrepository.json` (573 KB).
  - Sources: [retire.js](https://github.com/RetireJS/retire.js), [jsrepository-v4.json](https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository-v4.json), [npm retire](https://registry.npmjs.org/retire)
- Format (local parse), 76 library entries. Each has `{bowername, npmname, licenses, vulnerabilities[{below, atOrAbove?, severity, cwe[], identifiers{summary, CVE[], githubID}, info[]}], extractors{func[], uri[], filename[], filecontent[], hashes?}}`.
  - Version regexes use the placeholder `§§version§§`.
  - Example jQuery extractors: `uri: "/(§§version§§)/jquery(\.min)?\.js"`, `filecontent: "/\*!? jQuery v(§§version§§)"`.
  - Source: local parse of [jsrepository-v4.json](https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository-v4.json)
- The PyPI `retirejs` Python port is v1.5 from 2019. It is stale; do not use it. — [PyPI retirejs](https://pypi.org/pypi/retirejs/json)
- OSV.dev:
  - Apache-2.0, active (last commit 2026-10-07).
  - A local `POST https://api.osv.dev/v1/query {"package":{"name":"jquery","ecosystem":"npm"},"version":"3.4.1"}` returned GHSA-gxr4-xjj5-5px2 (CVE-2020-11022) and GHSA-jpcq-cgw6-v4j6 (CVE-2020-11023).
  - The PyPI `osv` package (0.1.3) requires Python >=3.13. Use plain `requests` instead.
  - Sources: [osv.dev repo](https://github.com/google/osv.dev), [PyPI osv](https://pypi.org/pypi/osv/json)
- webappanalyzer:
  - GPL-3.0, last commit 2026-09-16. It is "a continuation of … Wappalyzer that went private in August 2023", with the same JSON structure.
  - Files are `src/technologies/{a..z,_}.json` and `src/categories.json`.
  - Fingerprint keys include `cats, cookies, dom, dns, js, headers, html, meta, scriptSrc, scripts, implies, excludes, cpe`. Version capture uses `\;version:\1`.
  - Sources: [webappanalyzer README](https://github.com/enthec/webappanalyzer), [a.json](https://raw.githubusercontent.com/enthec/webappanalyzer/main/src/technologies/a.json)
- `python-Wappalyzer` (chorsley): repo archived, PyPI 0.3.1 from 2020. — [repo](https://github.com/chorsley/python-Wappalyzer), [PyPI](https://pypi.org/pypi/python-Wappalyzer/json)
- `wappalyzer` (s0md3v/wappalyzer-next) 2.0.4 (2026-09-30, GPL-3.0). It needs `playwright install chromium`. Its "full" scan runs the Wappalyzer browser extension, while the fast/balanced modes are HTTP-only. It has a Python API (`from wappalyzer import Wappalyzer`). — [wappalyzer-next](https://github.com/s0md3v/wappalyzer-next), [PyPI wappalyzer](https://pypi.org/pypi/wappalyzer/json)
- `HTTPArchive/wappalyzer` (GPL-3.0) is another active fork, last commit 2026-10-03. — [HTTPArchive/wappalyzer](https://github.com/HTTPArchive/wappalyzer)

### Inferences
- TraceMap pipeline per script:
  1. Hash the body (sha256). Optionally compare with Tracker Radar `responseHashes`.
  2. Run retire extractors: `uri` against the URL, `filename`, then `filecontent` against the body. Replace `§§version§§` with `[0-9][0-9.a-z_\-]+`.
  3. Compare the version against `below` / `atOrAbove` with `packaging.version`. Fall back to a semver-lenient parse.
  4. Query OSV (npm) for the `npmname`/version to get fresh advisories. Cache them.
  5. Optionally run webappanalyzer `scriptSrc` and `js` patterns for libraries that retire does not cover.
- Retire's `func` extractors (for example `jQuery.fn.jquery`) need runtime evaluation in the page. TraceMap's crawler can evaluate these during the crawl and store the results.
- wappalyzer-next runs a second browser per site. That is too heavy and duplicates TraceMap's crawler. Also, its "full" mode uses the official extension's fingerprints, whose licence is not open since 2023 (inference from the webappanalyzer note).

### Gaps
- I did not verify the exact number of webappanalyzer technologies. I also did not check whether OSV has a batch endpoint limit (`/v1/querybatch` exists per OSV docs, but this is **UNVERIFIED** here).

---

## Q8. CSP and SRI evaluation, and whether Mozilla HTTP Observatory is reusable

### Takeaway
**Yes, reuse the MDN HTTP Observatory.** The old Python `mozilla/http-observatory` is archived and deprecated. Its Node rewrite, `mdn/mdn-http-observatory` (MPL-2.0, very active, npm `@mdn/mdn-http-observatory` 1.7.1), includes **CSP and Subresource Integrity tests** and the official scoring and grades. It runs locally via `npx`, with JSON output, so it can be called from Python with `subprocess`. Node 24 is required, and the dev machine has Node v24.18.0.

For deeper CSP analysis (bypass hosts, unsafe-inline/eval, nonce/strict-dynamic), call **google/csp-evaluator** (npm `csp_evaluator`, Apache-2.0) through a tiny Node script. No maintained Python port exists.

### Cited Findings
- `mozilla/http-observatory` (Python, MPL-2.0):
  - Archived, last commit 2024-10-22. Its README carries a "Deprecation Announcement… There is a Node/Javascript based replacement".
  - The old Python analyzer has `subresource_integrity(reqs)` with results such as `sri-implemented-and-external-scripts-loaded-securely` and `sri-not-implemented-and-external-scripts-not-loaded-securely`.
  - PyPI `httpobs` 0.9.3 dates from 2022.
  - The V1 public API was shut down on 31 Oct 2024.
  - Sources: [mozilla/http-observatory](https://github.com/mozilla/http-observatory), [content.py](https://github.com/mozilla/http-observatory/blob/main/httpobs/scanner/analyzer/content.py), [PyPI httpobs](https://pypi.org/pypi/httpobs/json), [MDN README](https://github.com/mdn/mdn-http-observatory)
- `mdn/mdn-http-observatory`:
  - MPL-2.0, last commit 2026-10-06; npm 1.7.1 (2026-09-03); `"engines": {"node": ">=24"}`.
  - CLI: `npx @mdn/mdn-http-observatory <host>` or `mdn-http-observatory-scan <host>`, with optional `--headers` JSON. Subpaths and ports are supported.
  - Output: `{scan:{algorithmVersion, grade, score, testsFailed, testsPassed, responseHeaders…}, tests:{<test>:{expectation, pass, result, scoreModifier, data}}}`.
  - Sources: [README](https://github.com/mdn/mdn-http-observatory), [package.json](https://github.com/mdn/mdn-http-observatory/blob/main/package.json), [npm](https://registry.npmjs.org/@mdn/mdn-http-observatory)
- Test modules in `src/analyzer/tests/`: cookies, cors, cross-origin-embedder-policy, cross-origin-opener-policy, cross-origin-resource-policy, **csp**, redirection, referrer-policy, strict-transport-security, **subresource-integrity**, x-content-type-options, x-frame-options. — [tests dir](https://github.com/mdn/mdn-http-observatory/tree/main/src/analyzer/tests)
- The SRI test (`subresourceIntegrityTest(requests, expectation)`) has 8 possible results, including `SriNotImplementedAndExternalScriptsNotLoadedSecurely`. — [subresource-integrity.js](https://github.com/mdn/mdn-http-observatory/blob/main/src/analyzer/tests/subresource-integrity.js)
- `src/index.js` exports `scan`. `src/scanner/index.js` also exports `analyzeScan(requests)`, which analyses an already-retrieved `requests` object. — [src/index.js](https://github.com/mdn/mdn-http-observatory/blob/main/src/index.js), [scanner/index.js](https://github.com/mdn/mdn-http-observatory/blob/main/src/scanner/index.js)
- The public API `POST https://observatory-api.mdn.mozilla.net/api/v2/scan?host=` is rate-limited to one scan per host per minute and returns a summary only. — [README](https://github.com/mdn/mdn-http-observatory)
- google/csp-evaluator:
  - Apache-2.0, last commit 2026-05-26; npm `csp_evaluator` 1.1.8 (2026-05-26).
  - Usage: `new CspEvaluator(new CspParser(policy).csp).evaluate()`.
  - It has "a built-in list of common CSP allowlist bypasses".
  - Sources: [csp-evaluator](https://github.com/google/csp-evaluator), [npm README](https://unpkg.com/csp_evaluator@1.1.8/README.md)
- No Python port of csp-evaluator was found on PyPI (`csp-evaluator`, `pycspeval` and `csp-parser` are all 404) or in search. — [PyPI csp-evaluator 404](https://pypi.org/pypi/csp-evaluator/json), [search result: npm package only](https://npmjs.com/package/csp_evaluator)

### Inferences
- **Security subscore design:**
  1. For the site's landing URL and for each detected login or payment page URL, run `npx @mdn/mdn-http-observatory <host/path>` via `subprocess.run([... ], capture_output=True)` and parse the JSON. Use `score` (0–135ish, A+ to F) plus per-test `pass` and `result` as features.
  2. Run `csp_evaluator` via a 10-line Node script reading the CSP from stdin and writing JSON findings (type, severity, directive). This feeds explanations such as "script-src allows 'unsafe-inline'" or "allowlists a JSONP bypass host".
  3. Compute SRI on login/payment pages **from TraceMap's own crawl data**: a cross-origin `<script>` or `<link rel=stylesheet>` without an `integrity` attribute counts as a finding. This reuses the Observatory's result vocabulary for consistency.
- Optional advanced route: a small Node wrapper that builds the `requests` object from TraceMap's captured responses and calls `analyzeScan`. This avoids re-fetching (helpful for pages behind interactions) but needs the internal `Requests` shape mirrored. **UNVERIFIED**: I did not test this.
- The old Python `httpobs` analyzer functions are MPL-2.0 Python and could be vendored. However, they are archived, use outdated scoring (algorithm v1–3), and the README warns there are no further fixes. Prefer MDN's Node version.

### Gaps
- I did not run `npx @mdn/mdn-http-observatory` locally, so first-run install time and the postinstall HSTS/TLD downloads are not measured.
- No securityheaders.com-like open-source alternative was evaluated further. Observatory covers the same headers.

---

## Q9. Dangling or expired script-host domains (polyfill.io-style)

### Takeaway
For every external script host's registrable domain:
1. Use dnspython to detect NXDOMAIN or SERVFAIL.
2. Use **whoisit** (RDAP, BSD-3-Clause, active, 4.0.5 from 2026-09) with `bootstrap(overrides=True)` to get expiry date, status and registrar, or a 404 "does not exist", which means unregistered and therefore hijackable.

Add a static **"known compromised/abandoned CDN" list**: polyfill.io, cdn.polyfill.io, bootcss/bootcdn, staticfile.org and similar, maintained by hand.

### Cited Findings
- whoisit 4.0.5 (2026-09-21, requires Python >=3.10) is pure Python. The repo is BSD-3-Clause, last commit 2026-09-21. — [PyPI whoisit](https://pypi.org/pypi/whoisit/json), [meeb/whoisit](https://github.com/meeb/whoisit)
- Local test results:
  - `whoisit.domain('clevertap.com')` returned expiry 2027-02-22 and statuses.
  - A non-existent `.com` raised `ResourceDoesNotExist` (Verisign RDAP 404), which signals an unregistered domain.
  - `polyfill.io` with default bootstrap raised `UnsupportedError: TLD "io" has no known RDAP endpoint`. With `whoisit.bootstrap(overrides=True)` it succeeded (expiry 2029-03-18). `clevertap.in` (.in) also worked with overrides.
  - Source: local run of [whoisit](https://pypi.org/pypi/whoisit/json)
- The IANA RDAP bootstrap file `https://data.iana.org/rdap/dns.json` is live (publication 2026-09-30). — [IANA dns.json](https://data.iana.org/rdap/dns.json)
- Fallback WHOIS libraries:
  - `python-whois` 0.9.6 (2025-10, MIT) — [PyPI](https://pypi.org/pypi/python-whois/json)
  - `asyncwhois` 1.1.15 (2026-10-02, MIT) — [PyPI](https://pypi.org/pypi/asyncwhois/json)
  - `whoisdomain` 2.20260806.3 (2026-08) — [PyPI](https://pypi.org/pypi/whoisdomain/json)
- Prior research: Nikiforakis et al., "You Are What You Include" (CCS 2012). It identified "stale domain-based inclusions" and found 56 unregistered domains still being included. Registering two of them recorded about 85,000 JavaScript requests in two weeks. It also described typosquatting XSS. — [CCS 2012 paper](https://www.securitee.org/files/jsinclusions_ccs2012.pdf), [author blog](https://blog.securitee.org/?p=255)

### Inferences
- Dangling-risk features per script host:
  - `nxdomain`
  - `rdap_not_found` (unregistered)
  - `days_to_expiry < 30`
  - status contains `pendingDelete`, `redemptionPeriod` or `clientHold`
  - registrar or nameserver changed recently (registration date under 90 days, which suggests a re-registration)
  - domain in the hand-kept "compromised CDN" list
  - the script loads without SRI
- Cache RDAP results and rate-limit them, because registries throttle.
- The polyfill.io case is not a dangling domain. The domain was *sold*, so it stays registered. That is why the hand-curated compromised list and the "registration date recently changed" heuristic matter.

### Gaps
- I found no open-source code release for the "You Are What You Include" stale-inclusion detection, or for later "abandoned resources" studies. No code located.
- I did not find an open, maintained "compromised JS CDN" list. Such a list would need hand-curation, and was not verified.

---

## Q10. Obfuscated-JS detection

### Takeaway
Build TraceMap's own interpretable features with **tree-sitter + tree-sitter-javascript** (MIT, Windows wheels, Python 3.11 OK, verified parsing locally). Combine them with entropy and lexical heuristics in a random forest or logistic regression.

JStap (AGPL-3.0) and JaSt (GPL-3.0) are research proofs of concept pinned to Python 3.6 and Node 8. Use them for ideas (token/AST n-gram features plus random forest) and cite them, but do not depend on them.

### Cited Findings
- JStap (ACSAC'19):
  - **AGPL-3.0**, last commit 2021-01-18.
  - The README calls it "a Poc and not a fully-fledged production-ready API".
  - It combines five code abstractions (tokens, AST, CFG, PDG-DFG, PDG) with n-gram or identifier features and a random forest per module.
  - It was tested with Python 3.6.7, Node 8.10 and esprima 4.0.1.
  - Sources: [JStap](https://github.com/Aurore54F/JStap)
- JaSt: **GPL-3.0**, last commit 2020-02-01. — [JaSt](https://github.com/Aurore54F/JaSt)
- `tree-sitter` 0.26.0 (2026-06-30) has win wheels and requires Python >=3.10. `tree-sitter-javascript` 0.25.0 (2025-09-01, MIT) ships cp310-abi3 wheels. Both repos are MIT.
  - Local test: `Parser(Language(tree_sitter_javascript.language()))` parsed an obfuscated sample into `program → variable_declaration, function_declaration`.
  - Sources: [PyPI tree-sitter](https://pypi.org/pypi/tree-sitter/json), [PyPI tree-sitter-javascript](https://pypi.org/pypi/tree-sitter-javascript/json), [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter)
- Alternative pure-Python parsers are stale: `esprima` (Python port) 4.0.1 from 2018 and `pyjsparser` 2.7.1 from 2019. `jsbeautifier` 2.0.3 (2026-06, MIT) can normalise minified code before feature extraction. — [PyPI esprima](https://pypi.org/pypi/esprima/json), [PyPI pyjsparser](https://pypi.org/pypi/pyjsparser/json), [PyPI jsbeautifier](https://pypi.org/pypi/jsbeautifier/json)

### Inferences
- Interpretable obfuscation features:
  - Shannon entropy of the whole file and of string literals
  - share of `\xNN` / `\uNNNN` escapes
  - longest string-literal length
  - ratio of hex-named identifiers (`_0x[0-9a-f]+`)
  - mean identifier length
  - count of `eval`, `Function(`, `atob`, `unescape`, `String.fromCharCode` and `setTimeout(string)`
  - large array-of-strings plus rotation function (the obfuscator.io signature)
  - characters per line and whitespace ratio, to separate *minified* from *obfuscated*
  - AST node-type distribution and depth from tree-sitter
- Train on a small labelled set, with minified-but-benign libraries from cdnjs as negatives and obfuscator.io-generated samples as positives. Keep minification separate from obfuscation, so popular minified libraries are not flagged.

### Gaps
- I found no maintained, permissively licensed, ready-made obfuscation classifier for Python. Entropy thresholds from the literature were not collected here.

---

## Q11. Recommended combination (summary across needs)

### Takeaway
A pure-Python core with two small Node subprocess helpers covers everything:
- Python: `adblock`, `dnspython`, `whoisit`, `tldextract`, `tree-sitter`, plus the retire JSON and OSV API.
- Node: MDN Observatory and csp_evaluator.
- Data: DDG TDS and Tracker Radar, Ghostery TrackerDB, Disconnect, third-party-web, EasyPrivacy, AdGuard Tracking, IndianList, Peter Lowe, AdGuard CNAME, Blacklight and Princeton replay lists, plus a TraceMap-curated India entity file.

### Cited Findings
- Python 3.11 compatible with Windows wheels or pure Python (verified by local install): adblock 0.6.0, braveblock 0.5.1, dnspython 2.8.0, whoisit 4.0.5, tree-sitter 0.26.0, tree-sitter-javascript 0.25.0. — [PyPI adblock](https://pypi.org/pypi/adblock/json), [PyPI dnspython](https://pypi.org/pypi/dnspython/json), [PyPI whoisit](https://pypi.org/pypi/whoisit/json), [PyPI tree-sitter](https://pypi.org/pypi/tree-sitter/json)
- Node is required for MDN Observatory (>=24). csp_evaluator and the Ghostery SDK are npm-only. — [MDN package.json](https://github.com/mdn/mdn-http-observatory/blob/main/package.json), [npm csp_evaluator](https://npmjs.com/package/csp_evaluator), [npm @ghostery/trackerdb](https://registry.npmjs.org/@ghostery/trackerdb)
- Licence summary:
  - CC BY-NC-SA 4.0 (data): DDG TDS, Tracker Radar, Disconnect, Ghostery TrackerDB
  - MIT: third-party-web, WhoTracks.me code, AdGuard cname-trackers, FP-Inspector, fingerprintjs, tree-sitter
  - GPL-3.0: AdGuard filters, uAssets, webappanalyzer, Blacklight, OpenWPM, wappalyzer-next, JaSt
  - AGPL-3.0: JStap
  - EasyList: GPL-3.0 or CC BY-SA 3.0
  - Apache-2.0: retire.js, OSV, csp-evaluator
  - MPL-2.0: MDN Observatory, adblock-rust
  - ISC: dnspython
  - BSD-3: whoisit
  - Sources: links in Q1–Q10 above.

### Inferences
- **Gotchas to put in the report:**
  1. NC-SA data means TraceMap outputs derived from it must be non-commercial and share-alike, with attribution.
  2. GPL code (Blacklight, OpenWPM, webappanalyzer) should be *reimplemented from documented rules* rather than copied if TraceMap's own code is MIT. Data files used at runtime are lower risk.
  3. python-adblock is unmaintained: pin the version.
  4. Tracker Radar has no India region.
  5. The NextDNS CNAME list is gone (404).
  6. whoisit needs `bootstrap(overrides=True)` for .io and other ccTLDs.
  7. The third-party-web JSON comes from npm/unpkg, not GitHub raw.
  8. The PyPI `osv` client needs Python 3.13, so use raw HTTP.
- Paths from detection to the classic-ML feature table:
  - per-list match flags and rule text (adblock)
  - entity, category and country (merged datasets plus India seed)
  - `tds_fingerprinting` score
  - DDG API-weight sum
  - E&N rule flags (canvas, font, WebRTC, audio)
  - session-replay list hit plus listener counts
  - canary-exfiltration flag
  - CNAME-cloaked flag
  - retire/OSV vulnerability count and maximum severity
  - Observatory score, CSP-evaluator high-severity count, SRI-missing count on login/payment pages
  - dangling-domain flags
  - obfuscation features
  - All of these are human-readable, which suits interpretable models (logistic regression, decision tree, random forest with SHAP/feature importances).

### Gaps
- End-to-end runtime cost per site (DNS + RDAP + Observatory + CSP-evaluator) was not benchmarked.
