---
rec_id: rec-2026-09-05-moveon-getw-w1830-snap
network: snap
status: live
campaign_name: RA_TRAFFIC_GETW_IN_PAN_TOF_202608
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-PLAY-INSTALL
ad_name: VID_MOVE-ON-PROPER_D_20260905
campaign_id: 3a89d273-15b9-423d-9889-f603e2b6b91c
ad_set_id: 48f165e6-ee9c-4142-ada3-7e872c2c98b0
ad_id: f83e8304-ed34-4e1f-906a-bc4eab2b1989
targeting_summary: 'Women 18-30, pan-India, Android only, expansion off. A traffic
  ad - no lead form - into the existing traffic campaign RA_TRAFFIC_GETW_IN_PAN_TOF_202608
  (3a89d273), reusing the approved and already-live MOVE-ON-PROPER video. Destination
  is /get/w rather than the Play listing, and that is the load-bearing choice: Play
  discards params appended to a listing URL, only its own referrer= survives an install,
  and this repo builds that referrer in one place only (_snap_lead_end_page, for lead
  end pages). The traffic path calls _utm_url, so a store-pointed traffic ad would
  produce installs carrying no ad identifier at all - the 2026-08-21 incident with
  a different first step. /get/w costs one tap and rebuilds the referrer itself with
  every utm_ plus ra_lp=get_w. New ad squad rather than a shared one because the squad
  id IS the attribution key: utm_term carries it and two ads in one squad are indistinguishable
  in user_acquisition. Android only is load-bearing too - the success metric is installs,
  iOS has no install referrer and no store listing for this app, so iPhone traffic
  would spend against an outcome it cannot produce. Success metric is landing-page
  views then Play taps then installs.'
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
destination_url: https://play.google.com/store/apps/details?id=com.riteangle.app
budget_cap_inr_per_day: 300.0
duration_days: 2
from_idea: null
created: '2026-09-05'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-09-05'
amended: '2026-09-05'
executed: '2026-09-05'
---

## Brief (proposed)

# Deployment brief — MOVE-ON-PROPER traffic ad into /get/w, women 18–30, Snap

Direct ask from the app owner, 2026-09-05: run a **traffic** ad — no lead form this time — against
the existing traffic campaign `3a89d273-15b9-423d-9889-f603e2b6b91c`, women, India, Android only,
reusing the MOVE-ON-PROPER creative already approved and live as a lead ad, CTA "Apply Now". The
stated goal is **installs from women**.

## The one decision that shapes everything: where she lands

The goal is installs, so the obvious destination is the Play listing. That is the option that breaks
tracking, and it is worth spelling out because the failure is silent.

Play throws away anything appended to a listing URL as query parameters. The only channel that
survives a store visit into the installed app is Play's own `referrer` parameter, which has to be
built deliberately and URL-encoded. This repo builds it in exactly one place — `_snap_lead_end_page`,
for lead-form end pages. The traffic path calls `_utm_url`, which staples `?utm_...` onto whatever
destination it is given. Point that at the store and every install arrives carrying nothing that
identifies the ad, permanently. That is the 2026-08-21 incident (54 Snap installs, zero attributable,
a full week of spend) reproduced with a different first step.

So this ad lands on **`/get/w`**, the registered women's page, which costs one extra tap and buys
back the entire measurement chain. `/get/w`'s own store button rebuilds the referrer with every
`utm_*` plus `ra_lp=get_w`. The tap is the price of being able to read the result at all.

`destinations.yaml` clears the pairing: `/get/w` is `audience: women`, `paid_traffic: true`, verified
2026-08-27, and its copy is written to her throughout.

## Ad set: new squad under the existing campaign

Campaign `RA_TRAFFIC_GETW_IN_PAN_TOF_202608` (3a89d273) is reused at the app owner's instruction. It
carries **no spend cap**, checked live 2026-09-05 — so the campaign-cap trap that throttled the first
women's set to ₹300 against a ₹1,000 plan does not bind here.

The squad is new rather than shared, for the same reason every prior women's test used a new one:
**the ad squad id is the attribution key.** `utm_term` carries it, and two ads in one squad are
indistinguishable in `user_acquisition`. Two squads already hang off this campaign
(`WOMEN_18-30_CASUAL_MOVEON-STORY`, `WOMEN_25-30_CASUAL_MOVE-ON-PROPER_LPV`), both paused; this one
does not collide with either.

## Targeting

Women 18–30, pan-India, **Android only**, expansion off, regulated content on.

Android is load-bearing rather than a preference: the success metric is installs, the install
destination is the Play listing, and iOS has no install referrer and no store presence for this app —
an iPhone arrival on `/get/w` can fill the email/WhatsApp form but cannot install, so iOS traffic
would spend budget against an outcome it structurally cannot produce.

18–30 matches the register the MOVE-ON-PROPER creative was built and QA'd for, and matches the band
every prior women's ad on this hook has run at, which keeps this comparable to them.

## Creative

`creatives/moveon-lead-w1830/asset-a.mp4` — the same 20s video the app owner reviewed and approved,
currently live as lead ad B (`VID_MOVE-ON-PROPER_B_20260904`, creative `b7cdbfad`).

**The existing creative object cannot be reused, and that is a platform limit, not a choice.** Snap
binds a creative to a lead form at creation and documents no update — three separate attempts to
repoint one on 2026-09-04 failed (E2023 `Property could not be updated`). A traffic ad needs a
`WEB_VIEW` creative carrying a website URL, which a lead creative does not have. So this push uploads
the same media file and creates a new creative object around it. **The viewer sees the identical
video**; only the object Snap hangs it on differs.

Watermark clearance recorded in that folder's `qa.md` on 2026-09-05: full 1 fps scan across all 20s
plus zoomed corner crops of all four scenes, clean. That pass also found the folder's older QA text
describes `energy-kahan-jaati-hai-ROUGH-v3.mp4`, a file no longer present — the three craft defects
and the watermark smear it recorded are all absent from `asset-a.mp4`, checked frame by frame at the
timestamps it names.

## Copy

- **Headline (34 max):** `Verified, usse pehle ki woh aaye` — 32 chars. A Hinglish rendering of
  `/get/w`'s own opening line ("Vetted before he reaches you"), so the ad and the page do not change
  the subject between the tap and the scroll.
- **CTA:** `APPLY_NOW`. `/get/w` carries a real email/WhatsApp capture form below its store button, so
  there is something to apply to; the CTA is not promising a decision nothing renders.
- On-asset type is unchanged from the approved cut.

## Budget and duration

**₹300/day × 2 days = ₹600**, per `rules/budget.md` as amended 2026-09-05.

Stated rather than wished away: at this level the read is **directional**. It answers "does this
deliver, and does anything look broken," not "is traffic better than the lead form." `ad-audit` should
expect `inconclusive` and that is the normal verdict here, not a disappointment.

**The 2-day window starts at creation, not at enabling.** Everything is created PAUSED and enabling is
the app owner's click. A day between the two costs half this test, and nothing in the code will warn
about it.

## Success metric

Landing-page views on `/get/w` (Snap's native count and the page's own beacon, independently), then
Play taps, then installs carrying `ra_lp=get_w` and this squad's `utm_term` in `user_acquisition`.

The comparison this is being set up against is the running lead funnel on the same hook and the same
creative: does sending her straight to a page and a store button produce more installs per rupee than
asking her for details on-platform first?

## Compliance check (rules/compliance.md)

| Rule | How this satisfies it |
|---|---|
| #1 money never an attraction signal | No money, provider, luxury or lifestyle-affordance language in headline, CTA or on-asset type. Cleared on this asset at its original QA. |
| #2 no purchase language | "Apply now" is an application, not a transaction. No price, trial, offer or subscription anywhere. |
| #3 referral cash never a figure | Not referenced. |
| #4 never "high-earning" | Not referenced; the page's own claim is identity verification. |
| #5 scores never verdicts on worth | No ranking, percentile or score in ad or headline. |
| #6.1 no unenhanced man's photo | No man's photo in the asset; the men visible are background figures in generated footage. |
| #6.2 label AI imagery / no tool watermark | Watermark clearance recorded 2026-09-05, full-length scan, clean. No first-person testimony from a generated person — all copy is overlaid type in brand voice, no dialogue. |
| #6.3 18+ without exception | `min_age` 18, enforced by `propose`. Play listing rated 18+. The library-scene under-18 escalation was the owner's call on 2026-08-29 and is unchanged by this push. |
| #7 tone | No hype, no jargon, no urgency. Hinglish in her register. |
| #8 independent second pass | The asset's compliance pass was run 2026-08-29 by a separate session that did not write the ad; the 2026-09-05 watermark scan is a second, independent check of that gate specifically. |

Nothing here is newly written copy — the asset and its on-screen type are the approved, already-live
cut. What is new is the headline, the CTA and the destination, and those are checked above.

## Amendment (2026-09-05)

- Reason: App owner 2026-09-05: the ad must land her IN the Play listing so she can install straight off the CTA - no web page in between. Three changes. (1) Destination becomes the Play listing. That is not a URL swap: _utm_url was building '...details?id=com.riteangle.app?utm_source=...' with two '?', so Play would have parsed the app id as 'com.riteangle.app?utm_source=snapchat' - the link may not even have opened the right listing, and Play strips appended params regardless. Tracking now goes URL-encoded INSIDE Play's referrer= (new _snap_traffic_url / _store_referrer_url), which is the only channel that survives an install. This path keeps utm_id, the ad id, which the lead path cannot - a lead form's end page is fixed before the ad exists - so this arm has AD-level attribution where the lead arm has squad-level. ra_lp=snap_ad_direct, a new label distinct from the lead funnel's snap_lead_form so the two direct-to-store funnels stay distinguishable in user_acquisition. (2) Ad squad optimisation goal moves LANDING_PAGE_VIEW -> SWIPES: with no page of ours in the funnel, LPV optimises toward a page render this account has never been confirmed to count off a store listing, whereas the swipe is the action we can actually observe. (3) Names follow the destination. CAMPAIGN NAME IS A KNOWN, ACCEPTED MISMATCH: it stays RA_TRAFFIC_GETW_IN_PAN_TOF_202608 because the app owner instructed reuse of campaign 3a89d273, so its GETW token now describes a destination the campaign no longer sends to. Nothing parses that token (naming.md: it is for human legibility and UI grouping), and there is precedent - moveon-lead-play-w1830-snap reused a GETW-APPLY-named campaign for a Play destination the same way. Superseded objects from the first push (squad 593db242, creative 2d614c3d, ad 4169645b, all PAUSED, zero spend) deleted before re-push so there is no second paused ad set pointing at /get/w for someone to enable by mistake.
- `ad_name`: 'VID_MOVE-ON-PROPER_C_20260905' → 'VID_MOVE-ON-PROPER_D_20260905'
- `ad_set_name`: 'WOMEN_18-30_CASUAL_MOVEON-GETW-LPV' → 'WOMEN_18-30_CASUAL_MOVEON-PLAY-INSTALL'
- `destination_url`: 'https://www.riteangle.dating/get/w' → 'https://play.google.com/store/apps/details?id=com.riteangle.app'

## Execution

- Date: 2026-09-05
- Campaign ID: 3a89d273-15b9-423d-9889-f603e2b6b91c
- Ad set ID: 48f165e6-ee9c-4142-ada3-7e872c2c98b0
- Ad ID: f83e8304-ed34-4e1f-906a-bc4eab2b1989
- Deviated from brief: THE BRIEF BODY IN THIS RECORD PREDATES THE DESTINATION PIVOT AND DESCRIBES THE WRONG FUNNEL - read the 2026-09-05 amend reason as superseding it. The brief argues at length for /get/w over the Play listing on the grounds that a store-bound traffic ad could not be attributed; the app owner then required direct-to-store, and the correct answer turned out to be to FIX the traffic path rather than route around it. What was actually built: swipe-up goes straight to the Play listing, tracking URL-encoded inside Play's referrer=, ad-level utm_id included, ra_lp=snap_ad_direct. Three further deviations from the brief as written. (1) Optimisation goal is SWIPES, not the LANDING_PAGE_VIEW the brief and every prior traffic squad used - with no page of ours in the funnel, LPV optimises toward a page render this account has never been confirmed to count off a store listing; SWIPES optimises for the tap, which is observably counted. (2) Campaign name RA_TRAFFIC_GETW_IN_PAN_TOF_202608 retains a GETW token describing a destination this squad no longer sends to - accepted by the app owner, reuse of campaign 3a89d273 was his explicit instruction, and naming.md records that nothing parses that token. (3) A first push on the same record created squad 593db242 / creative 2d614c3d / ad 4169645b against /get/w; ad and squad were deleted before re-push (Snap refused the creative, E3003 - creatives are not deletable), so creative 2d614c3d is an orphan with no ad and cannot run. Success metric is installs carrying ra_lp=snap_ad_direct and this ad's utm_id, which as of logging has NOT yet been observed in live user_acquisition data - the post-launch check in rules/tracking.md is outstanding.
