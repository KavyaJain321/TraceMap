# Pilot results (2026-10-07)

Run: `python -m tracemap pilot data/corpus/pilot_50.csv --quick --no-leak` (passive: no form typing,
which waits for ethics approval). Phone emulation, landing page + 2 inner pages, no cookie choice.
Convenience sample of 10 well-known sites per sector — for testing the pipeline, **not** for claims.
Live view: **Pilot study** page in the app (`#/pilot`); raw rows in `var/pilot/pilot_50/results.csv`.

| | Sites | Completed | Median tracking domains | Max | Cookie banner |
|---|---|---|---|---|---|
| Government | 10 | 10 | 2 | 13 (MyGov) | 2 |
| Banking | 10 | 10 | 10 | 19 (HDFC Bank) | 3 |
| Health | 10 | 10 | 13.5 | 17 | 1 |
| E-commerce | 10 | 9 (AJIO blocked us) | 15 | 42 (Croma) | 2 |
| Education | 10 | 10 | 16.5 | 18 | 0 |
| **All** | 50 | 49 | 13 | — | 8 of 49 |

Other signals:
- 48 of 49 completed sites loaded at least one tracker before any cookie choice.
- 8 of 49 load a known session-recording tool (FullStory, Hotjar, Crazy Egg, ContentSquare),
  including Axis Bank, Fortis Healthcare and Narayana Health (capability, not proof of recording).
- 19 of 49 use Indian martech per the draft India list: CleverTap 10, WebEngage 5, MoEngage 2,
  VWO 2, Colombia 2 (needs 2-coder verification).
- 69 of 790 third-party appearances (8.7%) are on no list (e.g. bhashini.co.in, senseforth.com).
  Some are site-owned domains (e.g. axisbank.com loaded by Axis Bank's new domain) — hand review needed.
- Possible cross-company ID sharing on 36 sites, **unconfirmed** (quick scans use one visitor).

Operational lessons:
- Median 22.8 s per site in quick mode; one site (epfindia.gov.in) froze the page → added hard
  timeouts on every in-page call and a per-scan budget.
- SBI moved to `sbi.bank.in` (RBI `.bank.in` migration): the study corpus must track new bank domains.
- Only 1 of 50 sites showed a bot check to a passive, non-evasive browser.
