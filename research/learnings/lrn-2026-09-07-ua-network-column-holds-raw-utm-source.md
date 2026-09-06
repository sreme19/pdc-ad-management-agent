---
id: lrn-2026-09-07-ua-network-column-holds-raw-utm-source
subject: tracking
claim: user_acquisition.network stores the RAW utm_source ('fb', 'ig', 'snapchat',
  'google-play', 'brevo'), not the normalised network name. Querying network='meta'
  returns zero forever - not because Meta produced nothing, but because that string
  never appears in the column. Meta traffic is fb + ig, and they must be summed.
source: live-data
confidence: high
sample_n: 120
status: open
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2027-01-05'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

user_acquisition.network stores the RAW utm_source ('fb', 'ig', 'snapchat', 'google-play', 'brevo'), not the normalised network name. Querying network='meta' returns zero forever - not because Meta produced nothing, but because that string never appears in the column. Meta traffic is fb + ig, and they must be summed.

## Evidence

- (2026-09-07) Read 2026-09-07 by grouping the column instead of filtering it: snapchat 68, ig 27, google-play 11, '(not set)' 7, fb 4, null 2, brevo 1, across 120 rows. networkOf()'s fb/ig -> 'meta' normalisation lives in pocket-dating-coach's read path (traffic-quality.ts), not in what gets stored. This had already produced one wrong finding the same day: a filter on network='meta' was read as 'no Meta ad has ever produced a signup' when the true figure is 31. It also means any per-network rollup written against this column must sum fb+ig or it silently undercounts Meta by whatever share of impressions Instagram took - here 27 of 31, so 87%. Note the '(not set)' and null buckets too: 9 rows carry no network at all.
