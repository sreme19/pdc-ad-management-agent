---
id: lrn-2026-09-05-play-console-has-no-utm-and-lags-six-days
subject: tracking
claim: 'Google Play Console cannot attribute installs to a specific ad, and cannot
  report on a short campaign at all. Two hard limits, both verified in the console
  on 2026-09-05. (1) NO UTM DIMENSION: the Statistics report builder offers only Country/region,
  Android version, Device, Form factor, Language, App version, Carrier and No breakdown.
  Traffic source exists only on the Grow users page as a fixed dimension bucket (TRAFFIC_SOURCE_NAV_SEARCH_AND_DEEP_LINK_IS_PAID_DIRECT)
  - i.e. search/deep-link/paid/direct CATEGORIES, never the utm_campaign or utm_id
  string. (2) ~6 DAY LAG: on 2026-09-05 the newest available data was 2026-08-30 (''Calculated
  over the last 23 days of available data (Aug 8 - Aug 30)''). A 2-day ad set therefore
  finishes, and its verdict is due, roughly five days before Play Console has any
  data about it. Play Console is a post-hoc aggregate sanity check, NOT a KPI source
  for a running ad.'
source: platform-doc
confidence: high
sample_n: null
status: open
created: '2026-09-05'
last_confirmed: '2026-09-05'
review_after: '2027-03-04'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

Google Play Console cannot attribute installs to a specific ad, and cannot report on a short campaign at all. Two hard limits, both verified in the console on 2026-09-05. (1) NO UTM DIMENSION: the Statistics report builder offers only Country/region, Android version, Device, Form factor, Language, App version, Carrier and No breakdown. Traffic source exists only on the Grow users page as a fixed dimension bucket (TRAFFIC_SOURCE_NAV_SEARCH_AND_DEEP_LINK_IS_PAID_DIRECT) - i.e. search/deep-link/paid/direct CATEGORIES, never the utm_campaign or utm_id string. (2) ~6 DAY LAG: on 2026-09-05 the newest available data was 2026-08-30 ('Calculated over the last 23 days of available data (Aug 8 - Aug 30)'). A 2-day ad set therefore finishes, and its verdict is due, roughly five days before Play Console has any data about it. Play Console is a post-hoc aggregate sanity check, NOT a KPI source for a running ad.

## Evidence

- (2026-09-05) Read directly in Play Console 2026-09-05 for com.riteangle.app (developer 8173561937865559208, app 4973192030196533327): opened the Statistics dimension dropdown and enumerated every option; followed Store analysis, which now redirects acquisition/traffic-source data to the Grow overview page; and read the Device acquisitions tooltip stating the Aug 8 - Aug 30 window on 2026-09-05.
