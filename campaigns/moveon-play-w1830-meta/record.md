---
rec_id: rec-2026-09-06-moveon-play-w1830-meta
network: meta
status: live
campaign_name: RA_TRAFFIC_GETW_IN_BLR_TOF_202608
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-PLAY-INSTALL
ad_name: VID_MOVE-ON-PROPER_E_20260906
campaign_id: '6984035763681'
ad_set_id: '6986393942081'
ad_id: '6986393974881'
targeting_summary: 'Women 18-30, pan-India, Android only, Advantage Audience off.
  The Meta arm of the direct-to-store test the Snap ad (rec-2026-09-05-moveon-getw-w1830-snap,
  VID_MOVE-ON-PROPER_D_20260905) ran to zero installs. Reuses campaign RA_TRAFFIC_GETW_IN_BLR_TOF_202608
  (6984035763681) - OUTCOME_TRAFFIC, no campaign-level budget, so no CBO refusal and
  no cap trap; the leads campaign was refused on both counts. Creative reuses the
  video ALREADY in Meta''s library from the 2026-08-29 lead ad (video 1719740729289211,
  thumb 313ef6f30e5fb19f365729e55c7c9132) so the viewer sees byte-identical approved
  footage; a new creative object is still needed because Meta binds a CTA at creation
  and the existing one points at lead form 1979788699404507. Destination is the India
  Play storefront (gl=IN, hl=en_IN) per the owner''s explicit instruction, twice.
  THE INSTRUMENTATION LIMIT IS THE POINT: no page of ours renders, so the account
  pixel 2286986682092608 cannot fire and marketing-conversions.ts''s Meta CAPI forward
  (healthy, 65/65 store clicks week of 2026-08-31) is bypassed. Meta gets no conversion
  signal and can only optimise LINK_CLICKS - the cheapest tap, which is the same target
  the Snap arm''s SWIPES bought when it returned zero. Tracking therefore goes URL-encoded
  inside Play''s referrer= (never url_tags, which Meta appends and Play discards),
  carrying utm_content as the ad id per traffic-quality.ts, utm_source=fb, and ra_lp=meta_ad_direct
  - a third label so the Meta and Snap direct-to-store arms stay distinguishable in
  user_acquisition. Android only is load-bearing: iOS has no install referrer and
  no store listing, and unlike the /get/w route there is not even a form for an iPhone
  arrival to fill. Success metric is link clicks, then user_acquisition rows carrying
  this ad''s utm_content (SIGN-UPS, not installs), then Play Console installs at a
  six-day lag with no per-ad split.'
targeting:
  gender: FEMALE
  min_age: '18'
  max_age: '30'
  countries:
  - in
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-lead-w1830
destination_url: https://play.google.com/store/apps/details?id=com.riteangle.app&gl=IN&hl=en_IN
budget_cap_inr_per_day: 300.0
duration_days: 2
from_idea: null
created: '2026-09-06'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-09-06'
last_note: '2026-09-07'
executed: '2026-09-07'
---

## Brief (proposed)

# Deployment brief — MOVE-ON-PROPER direct-to-Play, women 18–30, Meta

Direct ask from the app owner, 2026-09-06: the Snap direct-to-store ad
(`rec-2026-09-05-moveon-getw-w1830-snap`, ad `VID_MOVE-ON-PROPER_D_20260905`) produced **no
installs**. Run the same creative on Meta, into an existing suitable campaign, CTA landing her in the
Play listing, instrumented end to end.

The destination was confirmed twice, explicitly, as
`https://play.google.com/store/apps/details?id=com.riteangle.app&gl=IN&hl=en_IN` — the India
storefront in Indian English, no page of ours in between.

## 1. Campaign: reuse `RA_TRAFFIC_GETW_IN_BLR_TOF_202608` (6984035763681)

Read off the live account 2026-09-06, not off the ledger — **which is stale: all 8 Meta campaigns are
currently PAUSED**, including three the ledger marks `live`.

| Candidate | id | Objective | Verdict |
|---|---|---|---|
| `RA_TRAFFIC_GETW_IN_BLR_TOF_202608` | 6984035763681 | `OUTCOME_TRAFFIC` | **chosen** — no campaign-level budget |
| `RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608` | 6984366120881 | `OUTCOME_LEADS` | refused: ₹300/day *campaign* budget = CBO, which `meta-push` rejects with no escape hatch, and the wrong objective for a website link ad |
| 6 older `FB_*` campaigns | — | mixed | pre-date `rules/naming.md`'s current generation |

**Two name mismatches, accepted knowingly, both precedented.** `GETW` describes a destination this ad
set will not send to, and `BLR` should be `PAN` for a pan-India ad set. `rules/naming.md` records that
nothing parses `[DEST]` or `[GEO]` — they are for human legibility and UI grouping, and the joins run
on ids. The Snap arm accepted the identical `GETW` mismatch on the app owner's instruction to reuse
campaign `3a89d273`, and `moveon-lead-play-w1830-snap` did the same with `GETW-APPLY`. Recording it
here so the next reader does not treat it as a bug.

## 2. Creative: the asset is already in Meta's library — no re-upload

The video in the screenshot is `creatives/moveon-lead-w1830/asset-a.mp4`. **The identical file is
already in this Meta ad account**, uploaded 2026-08-29 for the first Meta lead ad:

- video `1719740729289211` — 20.04s, `video_status: ready`
- thumbnail `image_hash: 313ef6f30e5fb19f365729e55c7c9132`
- carried by creative `3554715368014821` (`VID_MOVE-ON-PROPER_A_20260829_CREATIVE_TRACKED`)

Both ids are reused directly. **The viewer sees byte-identical video to the cut the app owner
approved and Meta already reviewed** — no re-encode, no re-upload, no fresh creative review risk.

A new creative *object* is still required, and that is a platform limit rather than a choice: Meta
binds a creative's call-to-action at creation, and `3554715368014821`'s CTA points at lead form
`1979788699404507`. A store-bound traffic ad needs a CTA carrying a link. Same media, different
object — exactly the situation the Snap arm hit from the other direction.

QA: `creatives/moveon-lead-w1830/qa.md` records the 2026-09-05 full-length watermark pass (1 fps scan
across all 20s plus zoomed corner crops of all four scenes, clean), on top of the 2026-08-29
independent compliance pass. The gate is keyed on that file whichever route supplies the pixels —
reusing a library id must not become a way around it, and the code enforces that.

## 3. Funnel coverage table — this shape is new on Meta

Written before anything was decided, per `rules/tracking.md`.

| Step | Signal | Source | Real-time? | Per-ad? | Verdict |
|---|---|---|---|---|---|
| Impression | impressions | Meta | yes | yes | ✅ |
| Link click (CTA tap) | link clicks | Meta | yes | yes | ✅ |
| Arrival at listing | store listing visitors | Play Console | no (~6d lag) | no (channel bucket only) | ❌ |
| Install | device acquisitions | Play Console | no (~6d lag) | no | ❌ |
| First open | device first opens | Play Console | no (~6d lag) | no | ❌ |
| Sign-up | `user_acquisition` row carrying this ad's `utm_content` | our DB | yes | yes | ❓ never observed |
| Conversion reported back to Meta | Meta CAPI event | `marketing-conversions.ts` | — | — | ❌ structurally absent on this route |

**The last row is the answer to "instrument it with the right pixels", and the answer is that this
route cannot have one.** A pixel is JavaScript on a page we own. Nothing of ours renders on the Play
listing, so the account pixel (`2286986682092608`, `riteangle.dating`, last fired 2026-09-05 15:23Z,
healthy) cannot fire even once on this funnel. Attaching it to this ad set would be decoration.

**And this route also gives up a conversion pipe that already works.** `marketing-conversions.ts`
forwards store clicks to Meta's CAPI server-side, and it is healthy — 65 of 65 store clicks in the
week of 2026-08-31. It is triggered by the landing page's store-click beacon, so removing the page
removes the forward. Meta therefore receives **no conversion signal at all** from this ad and can only
optimise on `LINK_CLICKS`.

**Named as the proxy it is, per `rules/tracking.md`:** `LINK_CLICKS` buys the cheapest tap, which
comes from the people most willing to tap and least likely to install. That is the same optimisation
target the Snap arm ran (`SWIPES`) when it returned zero installs, so **the most likely single cause of
that zero is this funnel shape, not the creative and not the network.** This ad set is therefore best
read as answering "does Meta's cheapest-tap pool convert better than Snap's" — a narrower question
than "does this creative sell installs." Stated rather than wished away; the app owner chose
direct-to-store explicitly, twice, after this trade-off was put to him.

Also, unchanged from the Snap arm and still true: `user_acquisition` counts **sign-ups, not
installs** (`lrn-2026-09-05-user-acquisition-counts-signups-not-installs`; Play showed 139 device
acquisitions against 71 first opens over 28 days). Cost-per-install cannot be computed from this
repo's data. Cost-per-signup can. Never report one as the other.

The ❓ row is `q-2026-09-05-does-the-play-referrer-reach-user-acquisition`, already open, plus a new
Meta-specific question opened in the same turn as this record.

## 4. Tracking: URL-encoded inside Play's `referrer=`, never in `url_tags`

```
https://play.google.com/store/apps/details?id=com.riteangle.app&gl=IN&hl=en_IN&referrer=<url-encoded>
```

where the encoded referrer carries, every value literal, no `{{macros}}`:

```
utm_source=fb&utm_medium=paid_social&utm_campaign=RA_TRAFFIC_GETW_IN_BLR_TOF_202608
&utm_term=<ad set id>&utm_content=<ad id>&ra_src=ad&ra_lp=meta_ad_direct
```

Four things here are load-bearing and each has a specific failure behind it:

- **`url_tags` is inert against a store listing, and it looks fine.** Every prior Meta ad in this repo
  put its tracking there, and Meta implements it by *appending* to the outbound URL. Play discards
  appended parameters and honours only its own `referrer=`. A store-bound Meta ad with `url_tags` set
  spends normally, resolves to the right listing, and delivers installs carrying no identifier at all
  — reported as a healthy ad the entire time.
- **`utm_content` carries the AD id on Meta**, where Snap uses `utm_id` (`traffic-quality.ts`
  joins per network). It is read from `rules/networks.yaml` rather than hardcoded at the call site.
- **`utm_source=fb`, never `meta`** — `networkOf()` maps only ig/fb/instagram/facebook to `'meta'`.
- **`ra_lp=meta_ad_direct` is a third label**, distinct from `snap_ad_direct` and `snap_lead_form`. It
  is the only field in `user_acquisition` that says which funnel an install came off, and Snap-vs-Meta
  on the same creative into the same store is precisely the comparison it has to survive.

The destination already carries two query parameters (`gl`, `hl`), so the separator logic matters:
`referrer=` is appended with `&`. Verified — the final URL has exactly one `?` and `id` still parses
to the bare `com.riteangle.app`. The 2026-09-05 corruption (`…details?id=com.riteangle.app?utm_source=…`,
which Play would read as a package named `com.riteangle.app?utm_source=snapchat`) cannot recur here:
the push decodes the URL Meta actually stored and asserts the app id and four referrer parameters
against it, rather than comparing our own string to itself.

## 5. Targeting

Women 18–30, pan-India, **Android only**, Advantage Audience **off**.

Android is load-bearing, not a preference: the success metric is installs, the destination is the Play
listing, and iOS has no install referrer and no store presence for this app. iPhone traffic would
spend against an outcome it structurally cannot produce — and on this funnel, unlike the `/get/w`
route, an iPhone arrival cannot even fill a form as a consolation.

18–30 matches the band the MOVE-ON-PROPER creative was built and QA'd for, matches every prior
women's ad on this hook, and matches the Snap arm exactly — which is what makes the two comparable.

`regulated_content` is dropped on the crossing: Snap has an explicit flag and Meta handles dating as
an account-level written permission, so there is no field to set. Dropped on purpose, not forgotten.

**Watch the read-back on Advantage Audience.** Meta rewrites targeting it considers suboptimal instead
of rejecting it, so an ad set created with it off can come back on with the POST still returning 200.
On an age-banded women's test that silently answers a different question than the record asks. The
existing sibling ad set (6984035818681) held `advantage_audience: 0` correctly, so precedent is good,
but it is checked rather than assumed.

## 6. Copy

- **Headline** (`video_data.title`): `Verified, usse pehle ki woh aaye` — 32 chars, identical to the
  live Snap ad, so the two arms differ in network and nothing else that a viewer sees.
- **Primary text**: the already-approved, already-Meta-reviewed body from creative
  `3554715368014821`, verbatim: "Ghosting. Fake profiles. Teen hafte ki texting jo kahin nahi jaati.
  Ab samajh aaya energy kahan jaati hai? Date mat karo. Bas milo, aur jiyo. Riteangle har aadmi ko
  verify karta hai — usse pehle ki woh aap tak pahunche."
- **CTA: `INSTALL_NOW`**, and this is a deliberate divergence from the Snap arm's `APPLY_NOW`. The tap
  now lands in the Play listing, where the only available action is installing. "Apply now" would
  describe a decision nothing on the other side renders — `rules/compliance.md` #7 and the same
  honesty test that made `/get/w-apply`'s "you qualified" copy conditional on a real 18+ gate. If Meta
  refuses `INSTALL_NOW` on a website-destination creative, the fallback is `DOWNLOAD`, recorded as a
  deviation rather than swapped in silently.
- On-asset type is unchanged from the approved cut.

## 7. Budget and duration

**₹300/day × 2 days = ₹600**, both `rules/budget.md` defaults.

At this level the read is **directional**: it answers "does this deliver, and does anything look
broken," not "is Meta better than Snap for this creative." `ad-audit` should expect `inconclusive`,
which is the normal verdict here rather than a disappointment. The Snap arm ran the same ₹600, so the
two are at least matched in spend.

**The 2-day window starts at creation, not at enabling.** Everything is created PAUSED and enabling is
the app owner's click. A day between the two costs half this test and nothing in the code will warn
about it. Push and enable the same day, or amend the duration first.

## 8. Success metric

In order of when it becomes readable:

1. Link clicks in Meta — real-time, per-ad, the only signal this funnel measures cleanly.
2. `user_acquisition` rows carrying `ra_lp=meta_ad_direct` and **this ad's `utm_content`** — real-time
   and per-ad, but the event is a **sign-up**, two steps below install. Never labelled an install.
3. Play Console installs — six-day lag, no per-ad breakdown, so a 2-day test is judged five days
   before its own data exists. Useful for the Snap-vs-Meta total, useless for this ad specifically.

The comparison being set up: against `rec-2026-09-05-moveon-getw-w1830-snap`, same creative, same
store, same ₹600, same age band — does Meta's audience install where Snap's did not?

## 9. Compliance check (`rules/compliance.md`)

| Rule | How this satisfies it |
|---|---|
| #1 money never an attraction signal | No money, provider, luxury or lifestyle-affordance language in headline, body or on-asset type. Cleared on this asset at its 2026-08-29 pass. |
| #2 no purchase language | The app is free; "Install now" is not a transaction. No price, trial, offer or subscription anywhere. |
| #3 referral cash never a figure | Not referenced. |
| #4 never "high-earning" | Not referenced. The Play listing's own claim is identity verification, which is the approved wording. |
| #5 scores never verdicts on worth | No ranking, percentile or score in ad, headline or body. |
| #6.1 no unenhanced man's photo | No man's photo in the asset; men visible are background figures in generated footage. |
| #6.2 label AI imagery / no tool watermark | Watermark clearance recorded 2026-09-05, full-length scan, clean. No first-person testimony from a generated person — all copy is overlaid type in brand voice, no dialogue. |
| #6.3 18+ without exception | `min_age` 18, enforced by `propose`. Play listing rated 18+. The library-scene escalation was the owner's call on 2026-08-29 and is unchanged. |
| #7 tone | No hype, no jargon, no urgency. Hinglish in her register. CTA describes what the tap actually does. |
| #8 independent second pass | The asset's compliance pass was run 2026-08-29 by a separate session that did not write this ad; the 2026-09-05 watermark scan is a second independent check of that gate. **What is newly written here is the CTA and the destination**, and both are checked above. |

Nothing in the media or the on-screen type is new — it is the approved, already-Meta-reviewed cut.

## Note — creative (2026-09-06)

CTA built as DOWNLOAD, not the INSTALL_NOW the brief specified. Meta rejected INSTALL_NOW outright (error #100): it is absent from the call_to_action enum, and the install-flavoured types it does have (INSTALL_MOBILE_APP, INSTALL_APP, GET_MOBILE_APP) belong to app-promotion creatives carrying a promoted_object, which this account cannot build (lrn-2026-09-06-meta-app-promotion-blocked-no-play-url). DOWNLOAD is the fallback the brief already named and it stays honest about what the tap does - it lands in the Play listing, where the only available action is installing. Recorded rather than swapped in silently. The enum is only exercised on a real run: --dry-run never reaches the creative POST, so this could not have been caught in rehearsal. WHAT EXISTS IN ADS MANAGER NOW, ALL PAUSED, ZERO SPEND: ad set 6986393942081, ad 6986393974881, tracked creative 28557050917314819 (its CTA link carries the referrer with the real ad id), plus the expected untracked provisional creative 28150999447855965, which has no ad and cannot run - meta.py cannot delete it by design, and a spare object is the cheaper failure than an unresolved macro. Read-back was green on every field including the decoded store URL: app id parses to bare com.riteangle.app, referrer carries utm_content=6986393974881, utm_term=6986393942081, utm_source=fb, ra_lp=meta_ad_direct. The stored link was also opened in a browser and loads the real listing (riteangle: Pehle Tum, Phir Koi, Rated for 18+, Install available). Meta reported 83 creative-enhancement features with NONE opted in, so the 2026-08-29 QA sign-off on this asset is intact.

## Execution

- Date: 2026-09-07
- Campaign ID: 6984035763681
- Ad set ID: 6986393942081
- Ad ID: 6986393974881
- Deviated from brief: Three deviations from the brief as written. (1) CTA is DOWNLOAD, not the INSTALL_NOW the brief specified: Meta rejected INSTALL_NOW with error #100 because it is absent from the call_to_action enum entirely, and the install-flavoured types it does have (INSTALL_MOBILE_APP, INSTALL_APP, GET_MOBILE_APP) belong to app-promotion creatives carrying a promoted_object, which this account cannot build (lrn-2026-09-06-meta-app-promotion-blocked-no-play-url). DOWNLOAD is the fallback the brief named and stays honest about what the tap does. (2) META ADDED A GEO LOCATION TYPE THIS RECORD DID NOT ASK FOR. The ad set was created with location_types ['home','recent'] and reads back live as ['frequently_in','home','recent']. This is the documented Meta behaviour of rewriting targeting it considers suboptimal rather than rejecting it, and the push's read-back did not catch it because meta_readback_checks covers countries/gender/age/os/advantage_audience but not location_types. It is a mild broadening within IN, not an audience change - Advantage Audience is still correctly 0 and gender/age/OS all read back exactly as recorded - but it is a silent difference between the record and reality and should not be discovered later. (3) THE TEST WINDOW IS SHORT BY THE PUSH-TO-ENABLE GAP. start_time is stamped at CREATION (2026-09-06 18:50 IST) and end_time is fixed at 2026-09-08 18:50 IST; the owner enabled on 2026-09-07, so the ad set will deliver for roughly one day of its intended two, at the same Rs 300/day. Budget floor unchanged; total spend will land near Rs 300 rather than Rs 600, which makes an already-directional read thinner still. Extending end_time is a live-object change and therefore the owner's action in Ads Manager, not this agent's.

## Note — incident (2026-09-07)

Post-launch tracking check run 2026-09-07, immediately after the owner enabled. Result INCONCLUSIVE and that is the honest state: 0 user_acquisition rows in the window from any source, and a row requires a completed SIGN-UP, several steps past the install. Two things were found by running it rather than reading it. (1) verify-tracking WAS BLIND TO META and would have stayed blind: it hardcoded utm->>'utm_id', Snap's ad join key, where Meta carries the ad id in utm_content. With perfect tracking it would have reported 0 for this ad forever and flipped to SUSPICIOUS the moment any unrelated row landed. Fixed in the same turn to read ad_join_param from rules/networks.yaml; both arms re-run green. This was the first Meta record the command had ever been pointed at, so no earlier result was wrong. (2) THE ads_agent_ro RLS BLOCK IS LIFTED - the channel returns 120 user_acquisition rows all-time. config.local.yaml still warns that an empty read is not evidence of no data; that warning is now stale, which means this INCONCLUSIVE is a real empty window and not a silent block. The same query showed network='meta' has 0 rows all-time, so this ad is the first Meta ad that could ever produce one. THE CHECK IS THEREFORE STILL OUTSTANDING, not passed: re-run verify-tracking once the ad has produced signups, and close q-2026-09-06-does-the-meta-referrer-reach-user-acquisition with one manual install on a real Android device.
