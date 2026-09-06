---
rec_id: rec-2026-08-30-buildyourself-lead-w1830-snap
network: snap
status: reviewed
campaign_name: RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-LEAD
ad_name: VID_BUILD-YOURSELF-FIRST_A_20260830
campaign_id: 1326aa05-902c-4cec-be92-0a7440ac536d
ad_set_id: 85c2e782-ea07-4216-8986-f272bdb5d4d7
ad_id: ca0e5b76-a0c7-4028-8655-77f3e6dadcd3
targeting_summary: "Women 18-30, India pan-India, Android only, expansion off, segment\
  \ 4673160157025603 excluded \u2014 inherited unchanged from the live ad squad"
targeting:
  gender: FEMALE
  min_age: '18'
  max_age: '30'
  countries:
  - in
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/buildyourself-lead-w1830
destination_url: https://www.riteangle.dating/get/w-apply
budget_cap_inr_per_day: 300.0
duration_days: 5
from_idea: null
created: '2026-08-30'
amended: '2026-08-30'
campaign_daily_cap_inr: 300.0
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-08-30'
executed: '2026-08-30'
last_note: '2026-08-30'
verdict: inconclusive
reviewed: '2026-09-07'
---

## Brief (proposed)

# BUILD-YOURSELF-FIRST — Snap lead video

A 25.2s vertical film for the MOVE-ON lead funnel. Four women, four bad dating
experiences, one shared decision, then six beats of self-development, closing on
`riteangle` and an APPLY_NOW form.

## Argument

Act 1 (0:00–0:06) names the drain, one beat each: ghosting, catfishing,
inattention, low-effort dating. Act 2 (0:06–0:08.5) is the hinge — a four-panel
split screen where all four women lift their heads into the lens and the grade
flips from cool blue-grey to warm gold inside the shot. Act 3 (0:08.5–0:20.5) is
six "Pehle apni ___" beats. Act 4 closes on the wordmark.

The thesis is deliberately **not** "this happened because you weren't focused on
yourself" — that reads as blaming a woman for being catfished. Act 2 carries
"Khud ko bana sakti ho" instead: you can't change them, you can build yourself.
Same arc, no accusation.

## Production

Google Flow generated the frames; Grok Imagine animated them. Identity carried
because each Flow frame was fed into Grok as an image input, taking face, wardrobe
and set with it — **not** because Flow's character references held. They did not:
Flow's Characters ingredient list was empty, and Meera's saved character asset was
broken and unresolvable, which failed her frame repeatedly until the reference was
dropped and the frames themselves were attached instead
(`lrn-2026-08-30-grok-animates-what-flow-only-poses`).

The distinction matters. The compromise recorded against `moveon-swagger-video` —
the cast not carrying between scenes, so the ad read as "this happens / this is the
alternative" rather than "this happened to *her*" — was caused by relying on exactly
those character references (`lrn-2026-08-29-flow-character-reference-is-unreliable`).
What fixes it is the frame-into-Grok pipeline, not the character system. Here Meera
on the bedroom floor is the same Meera who lifts her head at the turn, verified
across Acts 1 and 2.

Audio is two Flow-generated instrumental beds. Prior practice permits this:
`moveon-lead-w1830/edit-script.md` says "Meta Sound Collection or Flow-generated
audio only; a commercial track is a licensing problem on a paid ad."

## Compliance checks done, not assumed

- **No visible AI-tool watermark** (`compliance.md` §2, sentence two). Grok's
  wordmark was cropped from every clip; Flow's sparkles appeared only on the
  office shot and were removed by cropping the top 220px.
- **No generated person narrates a first-person experience of Riteangle**
  (`compliance.md`). Nobody speaks at all — the cut is silent but for music, and
  every line is on-screen type.
- **Safe zones** (`creative-generation.md` §7). All type falls between y1235 and
  y1606 of 1920; the top 10% ends at 192 and the bottom 15% starts at 1632.
- **1080x1920, 9:16.**

## Known deviations, recorded

1. **25.2s against "six seconds is short"** (`creative-generation.md` §7). The
   emotional beat still lands at 0:02 as the rule requires, but this is a long
   asset by this account's standards and the format is unproven at this length.
2. **Wardrobe undercuts two Act 3 beats.** She serves at tennis in jeans, and
   presents to a boardroom in a vest top — both inherited from the source frames.
   Accepted for this cut; the rule is now written into the Grok prompt notes.
3. **Romanised Hinglish, not Devanagari.** Consistent with
   `lrn-2026-08-29-roman-script-is-an-audience-signal`.
4. **Type is set in Futura, not Gabarito** (`creative-style.md`). Gabarito is not
   installed locally. Cosmetic, and worth correcting before this becomes the
   house template.

## Amendment (2026-08-30)

- Reason: creative_ref must name the folder, not the asset file — the QA gate resolves <creative_ref>/qa.md and was looking for asset-a.mp4/qa.md. Matches how moveon-swagger-video and moveon-lead-w1830 are recorded.
- `creative_ref`: 'creatives/buildyourself-lead-w1830/asset-a.mp4' → 'creatives/buildyourself-lead-w1830'

## Execution

- Date: 2026-08-30
- Campaign ID: 1326aa05-902c-4cec-be92-0a7440ac536d
- Ad set ID: 85c2e782-ea07-4216-8986-f272bdb5d4d7
- Ad ID: ca0e5b76-a0c7-4028-8655-77f3e6dadcd3

## Note — observation (2026-08-30)

Pushed PAUSED 2026-08-30 and read back: 10/10 fields match. Reused campaign 1326aa05 and ad squad 85c2e782 rather than creating new ones - app owner's instruction that new creatives become ads under one standing home, not new campaigns/squads per ad. New objects are only: media a5445e2e-6f47-4903-9210-a4aadefe8ed1, creative 4dcb2a2c-8bcb-4203-b62c-e026961e1746, ad ca0e5b76-a0c7-4028-8655-77f3e6dadcd3.

The one read-back DIFF is 'ad squad status ACTIVE (wanted PAUSED)' and it is expected, not a fault: the squad was already live serving VID_MOVE-ON-PROPER_A_20260829. Our AD is PAUSED, so nothing new delivers until a human enables it in Ads Manager.

ATTRIBUTION, chosen deliberately: this ad reuses lead form 1897accc rather than getting its own. The form was verified untouched after the push - updated_at is still 2026-08-29T07:51:37 and its end-page URL still carries utm_content=VID_MOVE-ON-PROPER_A_20260829. So leads from THIS ad will land on /get/w-apply tagged with the OTHER ad's name. Ad-level separation exists only in Snap's own reporting; the beacon cannot tell the two ads apart. Note the push output prints the end-page URL with this ad's utm_content, which reads as though the shared form had been rewritten - it had not. Do not trust that line.

FIRST 25-second asset this account has run; every prior video was 8s or under. Snap accepted the upload without complaint, so the length ceiling was not hit. Whether a 25s cut holds attention on Snap is the open question this ad actually tests, alongside the creative angle.

## Correction (2026-08-30)

- The Production paragraph credited Flow's character assets with holding identity
  across acts. That is wrong and was self-contradicting: it cited the
  `moveon-swagger-video` compromise, whose cause was those same character references
  failing. Flow's Characters ingredient list was empty and Meera's saved character
  asset was broken; identity carried because the frames themselves were fed into Grok
  as image inputs. Corrected in this record and in
  `creatives/buildyourself-lead-w1830/brief.md`. No proposal field changed.

## Note — creative (2026-08-30)

App owner reviewed this session's Sarvam-AI voiceover-narrated draft of the creative (Shreya reading the on-screen captions, mixed under the existing music bed) and rejected it outright as 'terribly bad,' without diagnosing a specific defect. No change was made to the shipped asset-a.mp4 or to this ad's PAUSED status — the narration was a rough preview only, never merged in. See lrn-2026-08-30-buildyourself-vo-rejected. Do not resume the read-the-captions-aloud VO approach on this creative without a concrete diagnosis of what was wrong.

## Review

- Date: 2026-09-07
- Verdict: inconclusive
- Summary: RECONCILED 2026-09-07; squad PAUSED since 2026-09-03. This ad (ca0e5b76) delivered 15,608 impressions, 140 swipes, Rs 195.94 - 14% of its squad's impressions. THE 13 SIGNUPS THIS SQUAD PRODUCED CANNOT BE ASSIGNED TO ANY ONE OF ITS FOUR RECORDS. Squad 85c2e782 carries four separate lead ads (moveon-lead, buildyourself-lead, moveon-swagger-lead, knowyourworth-lead) and a lead form's end page is fixed before the ad exists, so its referrer stops at SQUAD level with no utm_id. rules/tracking.md warned that two ads in one squad are indistinguishable in user_acquisition; this is that warning realised, on the only Snap funnel that has ever produced a signup. Squad totals: 114,518 impressions, 1,132 swipes, Rs 1,472.26, 45 page views on /get/w-apply, 36 store clicks, 13 signups. The 13 are real and they are the best result in this ledger; they are simply unattributable to a creative. On this ad's own share the sample is far too small to read either way, so inconclusive is the honest verdict twice over: unattributable, and under-sampled.


