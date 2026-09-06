---
id: q-2026-09-06-can-meta-optimise-toward-installers-not-tappers
kind: channel
status: open
asked: '2026-09-06'
raised_by: rec-2026-09-06-moveon-play-w1830-meta
answered: null
learning: null
---

## Question

Can Meta ever be pointed at installers rather than the cheapest tap, given that app-promotion is unavailable to this account (lrn-2026-09-06-meta-app-promotion-blocked-no-play-url) and a direct-to-store funnel fires no pixel and no CAPI event? Three candidate routes, none costed: (a) register the Android app on the FB app with a Play store URL and add the Meta SDK or an MMP, unlocking a real app-install objective; (b) keep the store as the destination but send a server-side CAPI conversion off the SIGN-UP, matching on hashed email as marketing-conversions.ts already does for Snap - no click id needed; (c) put /get/w back in the funnel, where the pixel and the existing CAPI forward already work, and accept the extra tap.

## Why it matters

It decides whether direct-to-store is a fixable funnel or a structurally blind one. Right now every store-bound ad on both networks optimises for a tap, which is the single most likely explanation for the Snap arm's zero installs - so this question, not the creative, is probably what the next round of spend should be aimed at. Route (b) is the cheapest and reuses a module that exists and is healthy; route (c) needs no build at all and is what was recommended and declined for this ad set on 2026-09-06. The app owner's call, and it should be made before more direct-to-store budget is committed rather than after.
