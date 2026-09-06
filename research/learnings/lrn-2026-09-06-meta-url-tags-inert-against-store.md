---
id: lrn-2026-09-06-meta-url-tags-inert-against-store
subject: tracking
claim: 'On Meta, url_tags cannot carry tracking to an app store listing: Meta APPENDS
  url_tags to the outbound URL and Play discards every appended parameter, so a store-bound
  Meta ad''s tracking must be URL-encoded inside Play''s referrer= on the creative''s
  own link instead.'
source: platform-doc
confidence: high
sample_n: null
status: open
created: '2026-09-06'
last_confirmed: '2026-09-06'
review_after: '2027-03-05'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

On Meta, url_tags cannot carry tracking to an app store listing: Meta APPENDS url_tags to the outbound URL and Play discards every appended parameter, so a store-bound Meta ad's tracking must be URL-encoded inside Play's referrer= on the creative's own link instead.

## Evidence

- (2026-09-06) Found 2026-09-06 while building rec-2026-09-06-moveon-play-w1830-meta, the first Meta ad pointed at the Play listing. Every prior Meta ad in this repo put tracking in url_tags (verified live: creatives 3546135838888885, 3381749368661464 and 3024516231218644 all carry url_tags and all point at riteangle.dating pages). Meta defines url_tags as query parameters appended to the destination; rules/tracking.md already records that Play strips appended params and honours only referrer=. The failure is silent both ways: the ad resolves to the right listing and Ads Manager reports it healthy while every install carries no ad identifier. Resolved by meta.retarget_video_creative, which rebuilds the creative with the tracked link and deliberately does NOT set url_tags; cmd_meta_push then decodes the URL Meta actually stored and asserts the app id plus utm_content/utm_term/utm_source/ra_lp against it. Read back green on ad 6986393974881, and the stored link was opened in a browser: it loads the real listing (riteangle: Pehle Tum, Phir Koi, rated 18+). NOT YET OBSERVED: a real install off this link landing a user_acquisition row.
