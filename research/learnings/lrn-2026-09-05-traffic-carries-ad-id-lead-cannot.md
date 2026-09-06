---
id: lrn-2026-09-05-traffic-carries-ad-id-lead-cannot
subject: tracking
claim: Snap's TRAFFIC path can carry the ad id into a Play install referrer but the
  LEAD path structurally cannot, so the two funnels do not have the same attribution
  granularity. A lead form's end-page URL is fixed when the form is created, which
  is before the ad exists and Snap documents no form update - so a lead ad's referrer
  stops at ad-squad level. A traffic creative's URL is rewritten AFTER the ad is created,
  so a store-bound traffic ad carries utm_id=<real ad id> all the way into the install.
  ad-audit must not compare per-ad install counts across the two arms as though they
  were measured the same way.
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

Snap's TRAFFIC path can carry the ad id into a Play install referrer but the LEAD path structurally cannot, so the two funnels do not have the same attribution granularity. A lead form's end-page URL is fixed when the form is created, which is before the ad exists and Snap documents no form update - so a lead ad's referrer stops at ad-squad level. A traffic creative's URL is rewritten AFTER the ad is created, so a store-bound traffic ad carries utm_id=<real ad id> all the way into the install. ad-audit must not compare per-ad install counts across the two arms as though they were measured the same way.

## Evidence

- (2026-09-05) Read out of cli.py 2026-09-05 and confirmed against the live creative pushed that day: creative 6ade6827's web_view_properties.url decodes to a referrer carrying utm_id=f83e8304-ed34-4e1f-906a-bc4eab2b1989 (the real ad id), where _snap_lead_end_page explicitly strips utm_id= with a comment recording the platform limit. The traffic two-pass rewrite (provisional URL, create ad, set_creative_url with the real id) already existed for exactly this reason on page destinations.
