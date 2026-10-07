# Ethics protocol (draft for the institutional ethics committee)

> Submit this in week 1: approval is needed **before** the 50-site pilot runs the form test on
> real sites and before the full crawl. Until approval, run the form test only on the local testbed;
> passive scans of public landing pages (`--no-leak`) follow normal web-measurement practice.

## What the study does

An automated browser visits public pages of about 1,500 Indian websites (government, banking,
health, e-commerce, education), records the network requests the page makes, and on pages with
a newsletter/contact/sign-up form types a **made-up** email address and phone number into the
fields **without submitting the form**, to see whether scripts send these values to third parties.

## Principles (Menlo Report) and how we meet them

| Principle | Commitment |
|---|---|
| Respect for persons | No human participants and no real personal data. Canary emails use a domain the team controls; phone canaries use team-owned numbers only. Never Aadhaar/PAN/card-like values. |
| Beneficence | One visit per site at a time, a delay between sites, short sessions (~1–4 min). No load testing. Forms are never submitted, so no records are created on the site. |
| Justice | Sites are sampled by sector and popularity (CrUX India), not singled out. |
| Respect for law and public interest | Public pages only; no login, no CAPTCHA solving, no bot-wall evasion, no access controls bypassed. Findings phrased as *readiness gaps* under the DPDP Act, never as legal violations. |

## Technical safeguards (enforced in code, see docs/threat_model.md)

- Form submission is blocked in the leak-test browser profile (submit events cancelled).
- Password, OTP, PIN, card, Aadhaar/PAN-like fields are never touched.
- Bot-check pages are recorded as `blocked` and the site is skipped.
- No registration of expired script domains (dangling-domain checks are passive lookups).

## Data handling

- Stored: request URLs/headers/bodies observed during the visit, cookies set on our synthetic
  profiles, page screenshots, script files. No data about real people is collected.
- Kept on team machines; released dataset contains aggregate statistics and per-site
  observations, with tracker-list-derived labels under CC BY-NC-SA 4.0.

## Responsible disclosure

- Verified leaks of form data and critical supply-chain findings are reported privately to the
  site (security/privacy contact) before publication, and to **CERT-In** for government sites.
- 45-day embargo; organisations get a right of reply. Company names appear with neutral wording
  ("identifier-sharing evidence"), never "collusion".

## Legal note (to confirm with the faculty legal cell)

Passive loading of public pages and typing synthetic values without submission is not access
"without permission" in our reading of IT Act 2000 s.43/s.66, but this is not legal advice and
must be confirmed before the pilot. The DPDP Act s.17(2) research exemption is noted; no real
personal data is processed in any case.
