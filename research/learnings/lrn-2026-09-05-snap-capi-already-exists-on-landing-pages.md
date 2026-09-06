---
id: lrn-2026-09-05-snap-capi-already-exists-on-landing-pages
subject: tracking
claim: 'Riteangle ALREADY HAS a working server-side Snap Conversions API integration,
  attached to the landing pages, not to the ads. pocket-dating-coach/src/lib/server/marketing-conversions.ts
  posts CUSTOM_EVENT_1 to https://tr.snapchat.com/v2/conversion against pixel 0657d30b-4d65-414b-b9a9-65edb4aa1e07
  - the same pixel this repo attaches to every ad squad. It uses a keepalive beacon
  to our own server because the client pixel flushes on a ~1s timer while every CTA
  leaves for Play in ~6ms, which is why Snap''s Custom event 1 read zero while landing
  page views climbed. Consequence that matters: a DIRECT-TO-STORE ad cannot use any
  of it, because no page of ours renders to fire the beacon. Removing the interstitial
  tap removes the only channel that can teach Snap to optimise for anything past the
  tap. Also: Snap CAPI accepts a hashed email as a match key, so a SIGN-UP conversion
  needs no click id surviving swipe->store->install->signup - which was assumed to
  be the blocking problem.'
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

Riteangle ALREADY HAS a working server-side Snap Conversions API integration, attached to the landing pages, not to the ads. pocket-dating-coach/src/lib/server/marketing-conversions.ts posts CUSTOM_EVENT_1 to https://tr.snapchat.com/v2/conversion against pixel 0657d30b-4d65-414b-b9a9-65edb4aa1e07 - the same pixel this repo attaches to every ad squad. It uses a keepalive beacon to our own server because the client pixel flushes on a ~1s timer while every CTA leaves for Play in ~6ms, which is why Snap's Custom event 1 read zero while landing page views climbed. Consequence that matters: a DIRECT-TO-STORE ad cannot use any of it, because no page of ours renders to fire the beacon. Removing the interstitial tap removes the only channel that can teach Snap to optimise for anything past the tap. Also: Snap CAPI accepts a hashed email as a match key, so a SIGN-UP conversion needs no click id surviving swipe->store->install->signup - which was assumed to be the blocking problem.

## Evidence

- (2026-09-05) Read 2026-09-05: marketing-conversions.ts (SNAP_CAPI endpoint, SNAP_EVENT=CUSTOM_EVENT_1, SNAP_PIXEL_ID matching this repo's config, event_id dedup across browser and server copies). Verified live against marketing_store_clicks via ads_agent_ro the same day: /get/w 57 store clicks and 57 snap_forwarded, /get 291 and 290, /get/w-apply 38 and 38. Weekly health shows Meta forwarding broken through mid-August (125 of 125 errors, OAuthException code 200 'API access blocked') and both networks clean at 65/65/65 for the week of 2026-08-31.
