---
rec_id: rec-2026-08-28-moveon-swagger-w2530-snap
network: snap
status: reviewed
campaign_name: RA_TRAFFIC_GETW_IN_PAN_TOF_202608
ad_set_name: WOMEN_25-30_CASUAL_MOVE-ON-PROPER_LPV
ad_name: VID_MOVE-ON-PROPER_A_20260828
campaign_id: 3a89d273-15b9-423d-9889-f603e2b6b91c
ad_set_id: dee446d1-cb16-4b14-bcb0-41fd44e8531c
ad_id: cd48b86d-607b-4aca-bd22-7aaefaa67de2
targeting_summary: 'Snapchat, women only, 25-30, pan-India. CASUAL-SELECTIVE persona,
  but run in the SWAGGER register (loud coral/pink, streetwear, attitude) rather than
  the 25-30 security register the MOVE-ON-PROPER hook was written in - a deliberate
  app-owner call, so this tests medium and register at once. First video asset this
  repo has deployed. Pan-India rather than BLR-first as a stated deviation: BLR-narrow
  underperformed for women on an LPV objective, and the parallel Meta 25-30 set is
  serving pan-India anyway, which makes this the like-for-like comparison. Success
  metric: landing-page views on /get/w, not signups.'
targeting:
  gender: FEMALE
  min_age: '25'
  max_age: '30'
  countries:
  - in
  os: null
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-swagger-video
destination_url: https://www.riteangle.dating/get/w
budget_cap_inr_per_day: 300.0
duration_days: 5
from_idea: null
created: '2026-08-28'
amended: '2026-08-28'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-08-28'
last_note: '2026-08-28'
executed: '2026-08-28'
verdict: not-working
reviewed: '2026-09-07'
---

## Brief (proposed)

# Deployment brief — MOVE-ON-PROPER swagger cut, women 25-30, Snap

First video asset this repo has ever deployed, and the first push of any kind
carrying a moving creative. Bake-off round 4.

## The bet

Same hook as the live Meta still (`rec-2026-08-27-moveon-w2530-meta`), same
audience band, **different register and different medium**. The still runs the
breakup turn in the 25-30 security register: quiet, composed, cream. This runs it
loud - coral and pink, streetwear, a woman laughing - with the Hinglish line
carried entirely by the caption layer.

Two things are therefore being tested at once, and that is deliberate rather than
sloppy: does video beat a still for this audience, and does a louder register beat
the security register the hook was written in. At Rs 300/day neither will separate
cleanly; the read is directional and the question being asked is really "is this
worth funding properly".

## Why Snap and not Meta

App owner's call, 2026-08-28. It also happens to be the clean option: the Meta
still is live in `WOMEN_25-30_CASUAL_MOVEON-LPV` at Rs 300/day, and putting the
video in beside it would have had Meta's delivery starve one of the two. On a
separate network nothing competes, and the still keeps running untouched.

## Plan

| Field | Value |
|---|---|
| Campaign | `RA_TRAFFIC_GETW_IN_PAN_TOF_202608` (new) |
| Ad set | `WOMEN_25-30_CASUAL_MOVE-ON-PROPER_LPV` |
| Ad | `VID_MOVE-ON-PROPER_A_20260828` |
| Targeting | Women, 25-30, India, pan-India |
| Destination | `https://www.riteangle.dating/get/w` (audience women - gate passes) |
| Creative | `creatives/moveon-swagger-video/asset-a.mp4`, 1080x1920, 8.03s |
| Headline | "Move on - par dhang se." (23 chars; Snap's limit is 34) |
| Budget | Rs 300/day x 5 days |
| Success metric | Landing-page views on `/get/w`. Not signups. |

## A NEW campaign, deliberately

The existing Snap campaign `RA_TRAFFIC_GET_IN_PAN_TOF_202608` carries a
`campaign_daily_cap_inr` of 300. A campaign cap binds every ad squad beneath it,
so a second squad added there would split Rs 300 rather than receive it - the
exact mechanism that made `rec-2026-08-21-women-1822-casual-lpv` unreadable. A new
campaign gives this test its own cap. Its `GETW` token also matches the
destination, which the older campaign's `GET` token does not.

## Pan-India, as a stated deviation

`rules/targeting.md` prefers BLR-first. Overridden here for the same reason the
18-22 Snap set overrides it: BLR-narrow underperformed for women on an LPV
objective, and yesterday's Meta 25-30 set turned out to be serving pan-India
anyway, so pan-India is also the like-for-like comparison.

## Rs 300/day is below the floor - stated deviation, app owner's instruction

`rules/budget.md` sets Rs 800-1,200/day as minimum viable. Rs 300 was chosen by
the app owner on 2026-08-28 after the floor was raised twice in session. The
consequence, recorded in advance so the review does not rediscover it: delivery
may never leave its learning phase, and `ad-audit` should expect an inconclusive
or directional read on 2026-09-02 rather than evidence. This is the third
consecutive women's test funded below the floor
(`women-1822-casual-lpv`, `moveon-w2530-meta`, this).

## Compliance check

| Rule | How this satisfies it |
|---|---|
| §1 POV | Straight-on at standing eye level throughout, fully covered, no low angle, no body crop, no pan along the body. She strides, laughs and looks at the lens with amusement - subject with agency, never the object of the frame. |
| §6.1 no real man's photo | No man appears at any point. |
| §6.2 AI labelling / watermark | No tool watermark, no AI label, no garbled type - all type is set locally in real Gabarito. Nobody speaks and the captions are general aphorisms, not a personal-results claim, so the first-person prohibition scoped on 2026-08-28 does not bite. NOT COVERED: Snap's own synthetic-media disclosure policy, which binds separately and has never been checked. |
| §6.3 18+ | Reads clearly mid-twenties; targeting floor is 25. |
| §6.4 banned vocabulary | Caption text and headline run clean: "Move on karne ko sab bolte hain", "Kaise karna hai, woh koi nahi batata", "Dhang se.", "Verified, not vibes." No money, provider, ranking or purchase language. |
| #1 money / provider framing | None. Street, plain clothes, no luxury or status signifier. |
| #4 identity verification | "Verified" is identity verification, which #4 sanctions. It names no ranking of people. |
| §2 plate/type split | Flow generated picture only; every glyph set by `typeset_video.py`. |
| §5 palette | Cream ground, coral and brand pink. Bright, never dark. |
| §7 safe areas | All type inside 192 / 1632 on a 1080x1920 frame. |
| §10 QA gate | `pass`, 28.25/37.5 - but NOT an independent pass, and the file says so at the top. See below. |

## Carried risks - surface these again before enabling

1. **QA was not independent.** The session that produced the creative also scored
   it, on the app owner's instruction to move ahead. Two concerns were found by
   inspection and recorded (two pairs of sunglasses in shot 3; soft hands); what
   cannot be trusted is the absence of further findings. A cold pass is worth
   running before this scales past a Rs 300/day test.
2. **Snap's synthetic-media disclosure policy is unchecked.** A fully generated
   person on video is more exposed than the generated still already live on Meta.
   This is a platform-policy question, not a `compliance.md` one, and neither the
   QA gate nor the push gate can catch it.
3. **No comment-moderation policy exists.** Unaddressed since 2026-08-27 and now
   carried by a second breakup asset on a second network.
4. **Craft is the weakest dimension at 2.5/5**, bounded by the Omni 1.1 Flash tier
   rather than by the prompt or the format. If this test reads at all positive,
   re-run on a higher tier before spending more.

## Amendment (2026-08-28)

- Reason: Expansion off, matching rec-2026-08-27-moveon-w2530-meta. The premise is a specific 25-30 age band; an ad set that silently broadened would answer a different question, and this test already carries two deliberate variables (video vs still, swagger vs security register) without adding an uncontrolled third.
- `targeting.expansion`: True → False

## Note — incident (2026-08-28)

Pushed to Snap PAUSED 2026-08-28 and read back clean, 10/10 fields matching. Real ids: campaign 3a89d273-15b9-423d-9889-f603e2b6b91c (new, no parent spend cap, so the Rs 300/day ad squad budget is the effective figure), ad squad dee446d1-cb16-4b14-bcb0-41fd44e8531c, creative 299f996b-40c8-4593-9d3d-cbd67fc92808, ad cd48b86d-607b-4aca-bd22-7aaefaa67de2, media 0d56316a-b513-4a7a-91c3-a479a9637fb7. FIRST VIDEO ASSET EVER PUSHED BY THIS REPO. It required a code change the same day: snap.py upload_media gained a media_type parameter (IMAGE|VIDEO) and cli.py snap-push now resolves asset-a.mp4 before asset-a.jpg. Snap's WEB_VIEW creative takes either as its top_snap_media_id, so that is genuinely the whole difference; three tests were added, including one asserting the video path is not a way around the QA gate. Tracking verified against rules/tracking.md line 59: utm_source=snapchat is the correct spelling for this network, and every macro resolved to a literal - utm_term carries the real ad squad id, utm_id the real ad id, utm_content the ad name - so there is no unresolved {{ad.id}} of the kind that cost a week of spend on 2026-08-21. NOT YET ENABLED: enabling is a human action in Ads Manager, then log-setup closes the loop.

## Execution

- Date: 2026-08-28
- Campaign ID: 3a89d273-15b9-423d-9889-f603e2b6b91c
- Ad set ID: dee446d1-cb16-4b14-bcb0-41fd44e8531c
- Ad ID: cd48b86d-607b-4aca-bd22-7aaefaa67de2

## Note — observation (2026-08-28)

ENABLED by the app owner 2026-08-28 and verified live by reading Snap directly, not from the record: campaign ACTIVE, ad squad ACTIVE, ad ACTIVE with review_status=APPROVED. It was not held in review. That approval is the first real evidence on carried risk #2 - Snap's ad review passed a fully AI-generated person on video, unlabelled. Treat it as evidence, not as clearance: an approval is Snap declining to block this asset today, not a ruling that the synthetic-media policy has been read and satisfied, and Snap can pull an ad after approving it. The policy itself is still unread. No delivery yet at first check: our ad squad does not appear in the leaderboard at all, and the only Snap row for 2026-08-28 is the older WOMEN_18-22_CASUAL_LPV set at 3 impressions / Rs 0.02. Zero here means not-yet-started, not a failure - the ad was enabled minutes earlier. WHAT TO WATCH, given this is the first video this account has ever run and the first at Rs 300/day on a new campaign with no parent cap: (1) whether impressions start at all, since a video creative is a new format for this ad account and delivery may behave differently from the static assets; (2) the beacon on get_w for utm_content=VID_MOVE-ON-PROPER_A_20260828 and utm_id=cd48b86d-607b-4aca-bd22-7aaefaa67de2, which is the join that proves tracking end to end - Snap's own LPV count is expected to read LOWER than the beacon per lrn-2026-08-26-snap-and-beacon-disagree-on-lpv; (3) whether it leaves the learning phase at all at Rs 300/day, which rules/budget.md says it may not.

## Review

- Date: 2026-09-07
- Verdict: not-working
- Summary: RECONCILED 2026-09-07; squad dee446d1 PAUSED since 2026-08-30. Delivered 17,723 impressions, 120 swipes, Rs 169.82 (CPM Rs 9.58). Our side: 92 page views on /get/w, 4 store clicks, ZERO signups. Against a plan of Rs 300/day x 5d = Rs 1,500 it spent 11% of budget, so this is a thin test and the cost-efficiency read is weak. The conversion read is not: 92 tracked page views produced no signup at all, above MIN_SAMPLE=30. Consistent with every other Snap TRAFFIC funnel reconciled today - see lrn-2026-09-07-snap-traffic-funnels-convert-nobody.


