---
id: lrn-2026-09-06-meta-app-promotion-blocked-no-play-url
subject: channel
claim: Meta's app-promotion objective is unavailable to this account, so Meta cannot
  be given a per-ad install signal at any budget and a store-bound ad can only be
  a traffic ad optimising LINK_CLICKS. The only advertisable application is FB app
  1020330197292995 (riteangle) and its object_store_urls holds ONLY an instant_game
  URL - no Google Play listing.
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

Meta's app-promotion objective is unavailable to this account, so Meta cannot be given a per-ad install signal at any budget and a store-bound ad can only be a traffic ad optimising LINK_CLICKS. The only advertisable application is FB app 1020330197292995 (riteangle) and its object_store_urls holds ONLY an instant_game URL - no Google Play listing.

## Evidence

- (2026-09-06) GET /act_1561367575690055/advertisable_applications on 2026-09-06 returned exactly one app: {id: 1020330197292995, name: riteangle, object_store_urls: {instant_game: 'http://www.facebook.com/gaming/play/1020330197292995/'}}. No android_store entry. Separately pocket-dating-coach/mobile/pubspec.yaml carries no Meta SDK and no MMP - its only attribution dependency is android_play_install_referrer ^0.4.0 - so even a registered app would have no event source to report installs from. This is the Meta half of the gap note-2026-09-05-install-postback-spec records for Snap, and it is the harder half: Snap has a working CAPI path in marketing-conversions.ts, Meta has one too, but both fire off OUR pages' store-click beacon and neither can see a direct-to-store install.
