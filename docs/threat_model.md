# TraceMap threat model

Written in week 1 so it drives which detectors exist (panel review A7.3). Each threat
maps to what TraceMap observes, the detector that covers it, and what stays invisible.

## Assets (what the user stands to lose)

- **Identity**: email, phone, name typed into a site.
- **Linkability**: a stable identifier that lets companies join a user's visits across sites.
- **Device identity**: fingerprint surface (canvas, audio, WebGL, fonts, navigator, WebRTC IP).
- **Behaviour**: what the user reads, clicks and types (session recording).
- **Payment/credential data** on checkout and login pages (supply-chain attack target).

## Adversaries

| Adversary | Goal | Capability on the page |
|---|---|---|
| A1. Ad/analytics third party (legitimate business) | Build a profile; attribute conversions | Runs JS in the first-party context; sets cookies/storage; sends beacons |
| A2. Data broker / sync partner | Merge its profile with A1's | Receives IDs via redirects, URL parameters, POST bodies (cookie syncing) |
| A3. Session-replay vendor | Record the session for the site owner | Reads DOM and input values; streams them to its servers |
| A4. Compromised or malicious script (Magecart, polyfill.io-style) | Skim form/payment data | Same JS capabilities as A1, but exfiltrates to an attacker domain |
| A5. The first party itself | Analytics, marketing | Can proxy data server-side (invisible to us) |

## Kill chain (client side) and what TraceMap sees

| Step | Example | Observed by | Detector |
|---|---|---|---|
| 1. Inclusion | `<script src=adnet/tag.js>` or a tag manager loads it | CDP request initiator stacks | `loads` edges, party classification |
| 2. Identification | random ID stored in cookie/localStorage; fingerprint APIs | cookie jar, storage dump, JS API hooks | `collusion.ids` (A/B/A2 test), `detect.behaviour` (canvas/audio/webgl/font/webrtc) |
| 3. Collection | reading input values, key/input listeners | JS hooks on `HTMLInputElement.value`, `addEventListener` | `reads_form`, `listens_keys` flags |
| 4. Exfiltration | GET pixel / POST beacon with the value, often hashed or encoded | full request URL, headers, POST body | canary leak tracer (3-layer encoding/hash pool) |
| 5. Sharing onward | redirect to a partner with the ID in the URL | redirect chains | `redirect` + `shared_id` edges |

## OWASP mapping (security side)

- OWASP Top 10 2021 **A06 Vulnerable and Outdated Components** — outdated JS libraries (retire.js/OSV, second half).
- OWASP Top 10 2021 **A08 Software and Data Integrity Failures** — third-party scripts without Subresource Integrity on login/payment pages (second half).
- OWASP Top 10 2021 **A05 Security Misconfiguration** — missing/weak CSP (MDN HTTP Observatory, second half).
- PCI DSS v4.0.1 **6.4.3 / 11.6.1** — payment-page script inventory and change detection (`tracemap diff`, second half).

## Out of scope / invisible (stated as limitations)

- Server-to-server sharing (Conversions APIs, server-side tag managers, back-end ID matching).
  Every count is therefore a **lower bound**. Visible proxies we do record: CNAME-cloaked first-party subdomains.
- Native mobile apps.
- Anything behind login or OTP walls (we never authenticate).
- Pages that block automated browsers (recorded as `blocked`, never bypassed).

## Threats to TraceMap itself

| Threat | Mitigation in code |
|---|---|
| API used to probe internal networks (SSRF) | `api/scans.validate_target` refuses private, loopback, link-local and reserved addresses unless `--allow-local` |
| Path traversal via scan ids / blobs | `Store.scan_dir` rejects separators and `..`; blob names must be 64 hex chars |
| Accidental form submission on real sites | leak-test context cancels `submit` events and disables `form.submit()`; no Enter key is ever sent |
| Real personal data entering the system | canaries are synthetic; phone canaries only from team-owned numbers; government ID formats never used |
| Hostile page content (XSS in our UI) | React escapes all captured strings; raw bodies shown as text only |
