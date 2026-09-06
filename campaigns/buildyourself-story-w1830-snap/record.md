---
rec_id: rec-2026-08-30-buildyourself-story-w1830-snap
network: snap
status: reviewed
campaign_name: RA_TRAFFIC_GETW_IN_PAN_TOF_202608
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-STORY
ad_name: STORY_BUILD-YOURSELF-FIRST_A_20260830
campaign_id: 3a89d273-15b9-423d-9889-f603e2b6b91c
ad_set_id: 5d617ab4-1c7d-416c-9039-951bb888d892
ad_id: dd7a6ac2-5095-4e26-b99d-f29c57b933c3
targeting_summary: "Women 18-30, India pan-India, Android only, expansion off \u2014\
  \ new ad squad, not reusing WOMEN_18-30_CASUAL_MOVEON-LEAD, because this is a TRAFFIC/WEB_VIEW\
  \ objective (Story Ad, no lead form) under a different campaign (RA_TRAFFIC_GETW_IN_PAN_TOF_202608),\
  \ not the LEADS one"
targeting:
  gender: FEMALE
  min_age: '18'
  max_age: '30'
  countries:
  - in
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/buildyourself-carousel-w1830
destination_url: https://www.riteangle.dating/get/w
budget_cap_inr_per_day: 300.0
duration_days: 5
from_idea: null
created: '2026-08-30'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-08-30'
executed: '2026-08-30'
last_note: '2026-08-30'
verdict: not-working
reviewed: '2026-09-07'
---

## Brief (proposed)

# BUILD-YOURSELF-FIRST — Snap lead carousel (13 stills)

Re-cuts `creatives/buildyourself-lead-w1830/asset-a.mp4` (the shipped 25.2s video)
into 13 still photos, at Sree's direction (2026-08-30) to try the same argument as
a photo format rather than video. Same story, same lines, same lead-gen objective
— the difference is delivery: not one video, not one Story-Ad sequence, but 13
independent single-image `LEAD_GENERATION` ads under the standing squad
(`WOMEN_18-30_CASUAL_MOVEON-LEAD`, campaign `RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608`).
Shipped this way on Sree's explicit call — see "Format decision" below.

## Argument (unchanged from the video)

Act 1, four beats of being let down (ghosted, catfished, "how long," "enough") →
Act 2 hinge ("khud ko bana sakti ho" — you can't change him, you can build
yourself) → Act 3, six "pehle apni ___" self-development beats → close ("pehle
tum, phir koi aur") → wordmark/CTA card. Full reasoning for this arc, including
why the thesis is deliberately *not* "you weren't focused on yourself" (that
reads as blaming her for being catfished), is in
`buildyourself-lead-w1830/brief.md` and isn't repeated here.

## Format decision, recorded

Two ways to ship 13 images on Snap were on the table:
1. A true **Story Ad** — one tappable sequence a viewer swipes through. `snap.py`
   has never built a `STORY` creative, and Snap's own docs describe Story-tile CTAs
   as App Install / Website, not Lead Gen — unverified whether a Story tile can
   carry `lead_generation_form_id` at all. Would need a `snap.py` change and an
   unconfirmed API capability.
2. **13 separate single-image lead ads**, same squad — buildable today with zero
   code changes (`upload_media` IMAGE + `create_lead_creative` + `create_lead_ad`,
   looped 13 times). No user-facing swipe-through; each is its own ad in Snap's
   own reporting.

Sree chose (2), explicitly: "ship these as 13 separate ads under the same squad
for now." Per `rules/funnel.md`'s rung ladder, a true carousel/Story format stays
rung 1 — a `snap.py` change not taken here.

## Sourcing — no new generation

Every plate is re-cut from stills this account already generated for the video
(`buildyourself-lead-w1830/_source/frames/`), plus one frame pulled from that
asset's Grok animation (`g-win/asset-a.jpg` — see `_derived/README.md`). No new Grok
prompt was written for this creative; `sourcing.md` maps every slide to its exact
source file, in place of a `prompts.md` (which is for new generations).

## Naming

Ad names use variant letters A–M for what's really 13 sequential story beats, not
a true A/B test of one hook — a stated deviation from `naming.md`'s letter-per-a/b-
variant convention, chosen because the alternative (13 distinct hook slugs) is
worse: these are one story, not 13 unrelated ideas. Recorded here rather than
silently reusing the convention's letter for something it wasn't written for.

`BUILD-YOURSELF-FIRST` is added to `creative-style.md`'s registered hook
vocabulary in this same session, closing a gap the shipped video already opened
(it used this slug before the thread was registered).

## Compliance — re-checked per slide, not just inherited from the video

Every slide passed `creative-generation.md` §1 (POV rule) and §4 (negative list)
individually, not merely because the source video passed as a whole:

- **`c-alone/asset-a.jpg`** replaces a frame that would have put a man in sharp,
  prominent focus in the foreground (the "raja beta" gaming-couch beat) — swapped
  for a solo restaurant still instead. That gaming-couch frame exists and is
  arguably closer to the video's actual Act 1, but wasn't used here; ask before
  reintroducing it.
- **`g-win/asset-a.jpg`** carries the video's known wardrobe deviation (jeans, not
  tennis kit) forward — see `_derived/README.md`.
- No AI-tool watermark on any slide: Grok's mark is cropped on `g-win/asset-a.jpg`
  per the standing convention; the Flow stills used elsewhere don't carry Flow's
  sparkle mark in the crops used (checked per-slide, not assumed).
- Wordmark on `m-endcard/asset-a.jpg` is lowercase `riteangle`, correct spelling, set
  in real Gabarito (the shipped video had to fall back to Futura — Gabarito is
  available on this machine now).

Full per-slide QA checklist in `qa.md`.

## Execution

- Date: 2026-08-30
- Campaign ID: 3a89d273-15b9-423d-9889-f603e2b6b91c
- Ad set ID: 5d617ab4-1c7d-416c-9039-951bb888d892
- Ad ID: dd7a6ac2-5095-4e26-b99d-f29c57b933c3

## Note — incident (2026-08-30)

First Story Ad this account has ever built. Six live-API discoveries along the way, none in the docs clearly enough to have avoided a real attempt: (1) PREVIEW-tile media must be PNG, JPEG is rejected outright (E2002). (2) The PREVIEW tile must be 3:5 aspect ratio, not the leaf snaps' 9:16 (E2601) -- creatives/buildyourself-carousel-w1830/build.py now exports preview.png at 1080x1800 for this. (3) Both PREVIEW and COMPOSITE creatives require profile_properties (E2652), same as every other creative type, despite neither having its own CTA. (4) The ad's own type field is a SEPARATE enum from the creative's type -- a COMPOSITE creative needs ad type STORY, not 'COMPOSITE' (not a real value, E2002) and not 'SNAP_AD' (real, wrong category, E1008). (5) LANDING_PAGE_VIEW -- the goal every prior WEB_VIEW ad squad in this account has used -- is not offered for a STORY-type ad squad on this account/pixel at all: 13 different conversion_window values were tried live and every one was refused (E2899), which is the account's own eligibility system declining the goal for this ad type, not a window mismatch. Switched to SWIPES (billing_event stays IMPRESSION -- billing_event SWIPE is rejected). This ad optimises for swipe-throughs, not confirmed landing-page arrivals, unlike every other WEB_VIEW ad in this account. (6) Two probe ad-squads and a handful of probe ads were created and deleted during steps 4-5 (DELETE /adsquads/{id} and DELETE /ads/{id} both work and were used); none were ever anything but PAUSED, none carried real spend. snap.py's create_adsquad, create_ad, create_preview_creative, create_composite_creative, and find_creative all gained the fixes/idempotency this took to land cleanly; see their docstrings for the specific errors each one fixes.

## Note — incident (2026-08-30)

Retired 2026-08-30. Shipped live with the Google/Flow 'made with AI' sparkle baked into several plates and a 'More' CTA. Ad dd7a6ac2 DELETED via API (delivery + spend stopped). Superseded by rec-2026-08-30-buildyourself-story-b-w1830-snap: watermark cropped off every Flow still (strip_flow_watermark), CTA now APPLY_NOW, audio-library track added in Ads Manager UI. The 15 leaf/preview/composite creatives are orphaned but not API-deletable (Snap E3003 on DELETE /creatives) — inert, unreferenced.

## Review

- Date: 2026-09-07
- Verdict: not-working
- Summary: RECONCILED 2026-09-07; squad 5d617ab4 PAUSED since 2026-09-04. THE BIGGEST TRAFFIC RESULT HERE AND IT CONVERTED NOBODY. Squad total 38,026 impressions, 1,504 swipes, Rs 408.90, and on our side 1,095 page views on /get/w and 37 store clicks between 30 Aug and 2 Sep - the largest volume of tracked women's traffic this account has ever produced. ZERO signups. n=1,095 is 36x MIN_SAMPLE, so this is the strongest negative finding in the ledger. This record's own ad (dd7a6ac2) took 5,021 impressions, 148 swipes and Rs 63.40 of that - about 13% of the squad - so the per-ad read is thin, BUT the squad-level zero holds regardless of which ad inside it earned the traffic, which is why the verdict is not-working rather than inconclusive.


