---
id: lrn-2026-09-05-store-url-shape-did-not-travel-to-traffic-path
subject: tracking
claim: A destination-shape assumption baked into one code path does not travel to
  the sibling path. cli._snap_lead_end_page knew since 2026-09-04 that Play discards
  params appended to a listing URL and that only referrer= survives an install - but
  cli._utm_url, which every TRAFFIC ad uses, did not. Pointed at the Play listing
  it produced '...details?id=com.riteangle.app?utm_source=...' with TWO question marks,
  so Play would parse the app id as 'com.riteangle.app?utm_source=snapchat' - a package
  that does not exist. The ad would have failed to open the right listing at all,
  and Ads Manager would have shown a healthy ad the whole time.
source: source-code
confidence: high
sample_n: null
status: open
created: '2026-09-05'
last_confirmed: '2026-09-05'
review_after: '2026-11-04'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

A destination-shape assumption baked into one code path does not travel to the sibling path. cli._snap_lead_end_page knew since 2026-09-04 that Play discards params appended to a listing URL and that only referrer= survives an install - but cli._utm_url, which every TRAFFIC ad uses, did not. Pointed at the Play listing it produced '...details?id=com.riteangle.app?utm_source=...' with TWO question marks, so Play would parse the app id as 'com.riteangle.app?utm_source=snapchat' - a package that does not exist. The ad would have failed to open the right listing at all, and Ads Manager would have shown a healthy ad the whole time.

## Evidence

- (2026-09-05) Found 2026-09-05 by calling both builders on the same Play URL before pushing rec-2026-09-05-moveon-getw-w1830-snap, rather than reasoning about them. _utm_url returned the double-'?' string; _snap_lead_end_page returned the correct '&referrer=<url-encoded>' shape. Fixed the same session by extracting _store_referrer_url and adding _snap_traffic_url, so both paths now share one implementation. 333 tests passed before and after, which is the point - no test covered a store-bound traffic destination because none had ever existed.
