# Corpus plan (Indian websites)

- **Pilot (week 6):** `data/corpus/pilot_50.csv`, a convenience sample of 10 well-known public
  sites per sector. Purpose: measure real per-site cost, block rates and consent-banner handling.
  Not used for research claims.
- **Study corpus (second half):** ~1,500 sites, ~300 per sector (government, banking, health,
  e-commerce, education/ed-tech), sampled from the Chrome UX Report India list
  (`zakird/crux-top-lists`, `data/country/in/<YYYYMM>.csv.gz`, CC BY 4.0, pin the month).
  - Ranks are buckets (1K, 5K, 10K, 50K, 100K, ...) shuffled within each bucket: sample within
    buckets and use the bucket as an ordered covariate.
  - Sector labels: suffix hints (`.gov.in`, `.nic.in`, `.ac.in`, `.edu.in`) plus official
    directories (IGOD for government, RBI bank lists, UGC lists), then **two coders** label every
    site; report Cohen's kappa.
  - Screen out adult and piracy sites (present in the top buckets).
- Re-run in a second wave after the DPDP Act's core duties apply (~May 2027) if the timeline allows.
