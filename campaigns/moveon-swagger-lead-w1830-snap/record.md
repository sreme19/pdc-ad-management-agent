---
rec_id: rec-2026-08-31-moveon-swagger-lead-w1830-snap
network: snap
status: reviewed
campaign_name: RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-LEAD
ad_name: VID_MOVE-ON-PROPER_B_20260831
campaign_id: 1326aa05-902c-4cec-be92-0a7440ac536d
ad_set_id: 85c2e782-ea07-4216-8986-f272bdb5d4d7
ad_id: 0bb15d8b-d9c8-40f8-ad1e-e755c1ece01b
targeting_summary: 'Women 18-30, pan-India, Android, expansion off as recorded. A
  pure creative swap into the existing women''s Snap lead squad: same campaign, same
  ad squad, same lead form (1897accc, already Google-Sheets-connected 2026-08-30),
  same /get/w-apply end page. Only the creative changes - the swagger single-take
  Flow cut (loud coral/pink, 18-22 register) against variant A''s four-clip Grok stitch,
  same MOVE-ON-PROPER hook. Success metric is lead-form submissions and the FEMALE
  SHARE of them, not installs. Three live conditions degrade the read and are human
  fixes before enabling: the squad currently reads enable_targeting_expansion true
  with auto_expansion_type SMART_TARGETING despite the record asserting expansion
  off; the squad already carries two active ads under a Rs 300/day campaign-capped
  budget, so a third makes it ~Rs 100/day each; and the squad ends 2026-09-03T07:50Z.
  Reusing the form keeps delivery working but costs per-ad lead attribution - the
  form''s end-page URL is fixed at creation and still names ad A - so read the creative
  comparison off Snap''s own ad-level columns, not off marketing_leads.'
targeting:
  gender: FEMALE
  min_age: '18'
  max_age: '30'
  countries:
  - in
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-swagger-video
destination_url: https://www.riteangle.dating/get/w-apply
budget_cap_inr_per_day: 300.0
duration_days: 5
from_idea: null
created: '2026-08-31'
campaign_daily_cap_inr: 300.0
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-08-31'
executed: '2026-09-01'
verdict: inconclusive
reviewed: '2026-09-07'
---

## Brief (proposed)

# Deployment brief — MOVE-ON-PROPER swagger cut into the women's Snap lead form

A creative swap, not a new funnel. The swagger video already runs on Snap as a
**web-view** ad to `/get/w` (`rec-2026-08-28-moveon-swagger-w2530-snap`, women
25–30). This puts the same asset behind an **on-platform lead form** in the women's
18–30 lead squad that is already live, already form-connected, and already
delivering. Every structural piece is reused; only the creative is new.

## What is reused, and what that reuse actually means

| Level | Reused object | Consequence |
|---|---|---|
| Campaign | `RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608` (`1326aa05-902c-4cec-be92-0a7440ac536d`) | `snap-push-lead` finds it by name and creates nothing |
| Ad squad | `WOMEN_18-30_CASUAL_MOVEON-LEAD` (`85c2e782-ea07-4216-8986-f272bdb5d4d7`) | found by name; **targeting and budget are NOT re-pushed** — the squad keeps whatever it already has |
| Lead form | `RA_LEAD_WOMEN_18-30_CASUAL_MOVEON-LEAD_SNAP` (`1897accc-cd6b-4f60-9269-d76ec149842d`) | bound by `--form-id`; already Google-Sheets-connected 2026-08-30, so `rules/lead-delivery.md` §"mandatory step" is **already satisfied** and does not need redoing |
| Creative | new — `creatives/moveon-swagger-video/asset-a.mp4` | a Snap creative's attachment type is fixed at creation, so the approved **web-view** creative in the library cannot be re-pointed at a lead form. The same media is re-uploaded into a new `LEAD_GENERATION` creative. This is the only thing being built |

**Reusing the form costs per-ad lead attribution, and that is a real trade.** A Snap
lead form's end-page URL is fixed at creation and Snap documents no update, so this
form's URL still carries `utm_content=VID_MOVE-ON-PROPER_A_20260829` — ad A's name.
Snap already has no per-lead macro, so attribution was squad-level anyway
(accepted by the app owner 2026-08-29); what this adds is that the **three** ads now
in this squad are indistinguishable in the lead data. Read the creative comparison
off Snap's own ad-level impression/swipe/form-open columns, not off `marketing_leads`.
The alternative — a new form — would restart the manual Sheets connection and the
Apps Script trigger from scratch, and leads would silently not arrive until it was
done. Reuse is the right call; the attribution loss is recorded, not wished away.

## The bet

`rules/funnel.md` §3 says the 98/2 male lead-form result was diagnosed as creative
POV plus a submit-optimised objective, leaving the **format** unjudged — a re-run
candidate. That re-run happened: this squad returned **11 female / 7 male / 3
unclear** in W5 (`lrn-2026-08-31-snap-women-targeted-leads-deliver-male`), the first
women-targeted Snap lead set to actually deliver women.

So the format question is provisionally answered and the open one is narrower:
**does the swagger register pull women into a lead form better than the stitch cut
does?** Variant A is the four-clip Grok stitch; this is the single-take Flow cut in
the loud coral/pink 18–22 register. Same hook, same squad, same form, same
destination — the creative is the only variable, which is the cleanest comparison
this account has been able to set up so far.

**Success metric: form submissions, and the female share of them.** Not installs.
A cheap lead of the wrong gender is the W3 failure mode and is worth less than no
lead at all.

## Three conditions that are wrong right now, and are human fixes

None of these block creating the ad paused. All three degrade the read if the ad is
enabled without addressing them.

1. **The squad is running targeting expansion ON.** It reads
   `enable_targeting_expansion: true` with `auto_expansion_type: SMART_TARGETING`
   — a key this repo never sends. The record for the live ad asserts `expansion:
   false` and calls it "the single most load-bearing setting in the build", because
   expansion is the mechanism by which a submit-optimised objective drifts toward
   men. It is not holding. The read-back below will print this as a `DIFF` and that
   `DIFF` is the point, not noise. Fix in Ads Manager before enabling.
2. **The squad already carries two active ads** — `VID_MOVE-ON-PROPER_A_20260829`
   and `VID_BUILD-YOURSELF-FIRST_A_20260830` — under a ₹300/day squad budget that
   is itself capped at ₹300/day by the parent campaign. A third ad makes it roughly
   ₹100/day each. `rules/budget.md` already calls ₹300 directional rather than
   conclusive; ₹100 split three ways will not separate two creatives. Either pause
   one of the existing ads or raise the squad and campaign to the ₹800–1,200 band.
3. **The squad ends 2026-09-03T07:50Z** — under three days out. Extend it, or the
   window closes before the comparison has a sample.

## Plan

| Field | Value |
|---|---|
| Network | Snap |
| Campaign | `RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608` (existing) |
| Ad squad | `WOMEN_18-30_CASUAL_MOVEON-LEAD` (existing) |
| Ad | `VID_MOVE-ON-PROPER_B_20260831` |
| Objective | `LEAD_GENERATION`, optimised `LEAD_FORM_SUBMISSIONS` |
| Targeting | Women 18–30, pan-India, Android, expansion off *as recorded* (see condition 1) |
| Creative | `creatives/moveon-swagger-video/asset-a.mp4`, 1080×1920, 8.03s |
| Headline | `Move on — par dhang se.` (24 chars; Snap's limit is 34) |
| Form | existing `1897accc-…`, first name + phone + email |
| End page | `/get/w-apply` + squad-level UTMs + `ra_src=form` |
| Budget | ₹300/day (the squad's actual level — see condition 2) |
| Duration | 5 days |
| Success metric | lead-form submissions, and the female share of them |

`VID_..._B_...` is variant B per `rules/naming.md` — `[FORMAT]_[HOOK]_[VARIANT]_[DATE]`,
`MOVE-ON-PROPER` being an existing thread slug in `creative-style.md`, and A being
the stitch cut already in this squad. Two variants of one hook in one squad is
exactly what the `[VARIANT]` field is for.

## Compliance check — `rules/compliance.md`

| Rule | How this satisfies it |
|---|---|
| 1. Money is never an attraction signal | No income, wealth, luxury or provider framing in the headline, the captions or the picture. Wardrobe is a coral shirt and jeans against a painted wall. |
| 2. No purchase language | Nothing implies a purchase, subscription or credit. The form asks for contact details only. |
| 3. Referral cash never a rupee figure | No referral mechanic appears. |
| 4. Never "high-earning" | Not used. Membership quality is not claimed at all here. |
| 5. Scores are never verdicts on worth | No ranking, no percentage, no numeric judgement of a person. |
| 6.1 No man's real photo | No man appears at any point in the asset. |
| 6.2 AI imagery / no tool watermark | `watermark-check: pass`, recorded 2026-08-31 in the creative's `qa.md`: all eight frames plus the end card scanned at peak=0 and looked at. Flow's picture is an inset card, so the frame corners are bare cream and the tool mark never entered the composite. **§6.2's first-person line is the one that matters here and it holds:** nobody speaks, and "Kaise karna hai, woh koi nahi batata" / "Verified, not vibes." are general statements, not a synthetic woman narrating her own results. The blocked `moveon-properly-w2530` script fails that test; this asset does not go near it. |
| 6.3 Eighteen and over | Squad is hard-set 18–30. `/get/w-apply`'s age gate is a second, real check, and it is what makes the page's "you're in" copy true rather than fabricated. |
| 6.4 Banned vocabulary | Headline and all captions run clean: "Move on karne ko sab bolte hain", "Kaise karna hai, woh koi nahi batata", "Dhang se.", "Verified, not vibes." No money, provider, ranking or purchase vocabulary. |
| 7. Tone — Don't list | No hype, no urgency, no jargon. The register is loud but the claim is modest. |
| 8. Independent second pass | **Not satisfied, and flagged rather than glossed.** The creative's own `qa.md` says in its header that its QA was not an independent pass, and this compliance table is written by the same session that wrote this brief. The asset has been live on Snap since 2026-08-28 without a compliance complaint, which is evidence but not the check. A cold pass is worth running before this creative scales past the ₹300/day band. |

**Not covered here:** Snap's own synthetic-media disclosure rules for a fully
generated person on video. `compliance.md` §6.2 says explicitly that platform
disclosure rules bind independently and have never been checked. Still unchecked,
and now on its second ad. Worth closing rather than carrying forward again.

## Execution

- Date: 2026-09-01
- Campaign ID: 1326aa05-902c-4cec-be92-0a7440ac536d
- Ad set ID: 85c2e782-ea07-4216-8986-f272bdb5d4d7
- Ad ID: 0bb15d8b-d9c8-40f8-ad1e-e755c1ece01b
- Deviated from brief: Enabled 2026-09-01 with three of the brief's four stated conditions unaddressed, so the read is weaker than the brief assumed. (1) EXPANSION STILL ON: squad 85c2e782 reads enable_targeting_expansion=true / SMART_TARGETING, unchanged since 2026-08-31 - see lrn-2026-08-31-snap-forces-expansion-on-lead-squads and q-2026-08-31-does-snap-force-expansion-on-lead-objective. Any male drift in the delivered leads is expected under this setting and must not be blamed on the creative. (2) BUDGET UNCHANGED at Rs 300/day squad under a Rs 300/day campaign cap, so the record's Rs 300 is right but sits below the Rs 800-1200 threshold; VID_BUILD-YOURSELF-FIRST_A_20260830 WAS paused, which is the one condition that was addressed, leaving two active ads (this and VID_MOVE-ON-PROPER_A_20260829) at roughly Rs 150/day each. (3) END TIME STILL 2026-09-03T07:50Z, so the actual window is ~2 days, not the 5 the record states - expect roughly 40 percent of the planned impressions and treat any A/B verdict as directional at best. (4) NO PIXEL on the squad (pixel_id null) - deliberate, not a lapse: snap.py's create_lead_adsquad omits it because LEAD_FORM_SUBMISSIONS converts inside Snap where a pixel cannot see. Note the account's seven older hand-built lead squads all carry pixel 0657d30b because Ads Manager attaches it by default, so this squad is the odd one out by design. Consequence: Snap observes the form submit and nothing after it, so all post-form visibility comes from the page beacon and the Sheets sync, not from Snap's own reporting. Ad review status APPROVED.

## Review

- Date: 2026-09-07
- Verdict: inconclusive
- Summary: RECONCILED 2026-09-07; squad PAUSED since 2026-09-03. This ad (0bb15d8b) barely ran: 6,745 impressions, 34 swipes, Rs 54.03 - 6% of its squad's impressions and the lowest swipe rate of the four lead ads at 0.50%. THE 13 SIGNUPS THIS SQUAD PRODUCED CANNOT BE ASSIGNED TO ANY ONE OF ITS FOUR RECORDS. Squad 85c2e782 carries four separate lead ads (moveon-lead, buildyourself-lead, moveon-swagger-lead, knowyourworth-lead) and a lead form's end page is fixed before the ad exists, so its referrer stops at SQUAD level with no utm_id. rules/tracking.md warned that two ads in one squad are indistinguishable in user_acquisition; this is that warning realised, on the only Snap funnel that has ever produced a signup. Squad totals: 114,518 impressions, 1,132 swipes, Rs 1,472.26, 45 page views on /get/w-apply, 36 store clicks, 13 signups. The 13 are real and they are the best result in this ledger; they are simply unattributable to a creative. With 34 swipes this ad has no readable result of its own under any gate. Worth noting for the next swagger test: it was starved inside a shared squad rather than tested, so the swagger hook is untested on the lead funnel, not disproven.


