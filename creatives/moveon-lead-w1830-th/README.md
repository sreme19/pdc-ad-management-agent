# MOVE-ON-PROPER — Thailand localisation ("ENERGY KAHAN JAATI HAI" → TH)

Status **2026-09-01: prompt pack drafted, no pixels generated yet.** This is the production plan for
turning `../moveon-lead-w1830` into a Thailand-market variant — same cut, same beats, same brand
system, Thai models and Thai on-screen type.

## Why this source video, not the swagger cut

Two MOVE-ON-PROPER videos exist. This one — the four-clip Grok/Flow stitch at
`../moveon-lead-w1830` (`VID_MOVE-ON-PROPER_A_20260829`) — is the one with an actual measured
female-delivery number: **11 female / 7 male / 3 unclear out of 21 leads** in the W5 window
(`rec-2026-08-29-moveon-lead-w1830-snap`, confirmed in
`../../research/learnings/lrn-2026-08-31-snap-women-targeted-leads-deliver-male.md`), a majority-female
result on Snap's women's lead squad. The swagger cut (`../moveon-swagger-video`,
`VID_MOVE-ON-PROPER_B_20260831`) only went live 2026-09-01 as a same-squad creative swap and has no
delivery data yet — it cannot be "best performing" by any measured signal today. If it earns a better
number later, re-run this localisation against it instead; the process below doesn't change.

## What "everything else stays the same" means here

Per the brief: same hook (MOVE-ON-PROPER), same cut structure and timing (`edit-script.md` below,
copied beat-for-beat from the source), same brand system (cream ground, coral/pink accent, Gabarito
type, POV rule, negative list) — only the cast's ethnicity and the on-screen type language change.

One judgment call, flagged rather than silently made: the source prompts set scenes in "a big Indian
city" / "an ordinary Indian apartment." Prompts below say "a big Thai city" / "an ordinary Thai
apartment" instead of leaving Indian settings under Thai faces, on the read that "applicable to the
Thailand market" means the whole frame reads Thai, not just the people in it. Everything else in the
scene descriptions — wardrobe, palette, camera, lighting, composition, exclusions — is copied verbatim.
If the intent was faces-only, strike that substitution before generating; it's a one-line change per
clip.

## Tool: Flow, not Grok, for the character generation — and why that's still "a Grok thing"

The source video's four clips (`Woman_reacting_to_phone_message_...mp4`, etc.) were generated directly
in **Google Flow**, not Grok — `creative-generation.md` §2b's Grok-motion pipeline was built for a
different asset. Two ways to hit the Thai brief, in order of how much of the proven pipeline survives:

1. **Regenerate from scratch in Flow**, using the character blocks in `prompts.md` below (identical
   structure to the source's `@Meher`/`@Ira`/`@Nandita`, ethnicity swapped). This is the same tool,
   same casting workflow, same QA gate as the video that's actually shipping today — lowest-risk path.
2. **Grok Imagine restyle on the existing four source clips.** `creative-generation.md` §2b's standing
   warning is "Grok restyle re-rolls the face and breaks continuity — it is not a re-dressing tool," but
   that's a bug when the goal is holding identity and a feature when the goal is *changing* it. Restyle
   on the existing frames is the faster/cheaper route if reusing the exact footage matters more than
   starting clean; it still needs new character casting (Grok has no character system to hold the new
   Thai identity across a restyle the way Flow's `@handles` do), so path 1 is likely to need fewer
   rounds even though it's a full regeneration.

Recommend path 1, for the same reason the source video used Flow: it's what's already proven to clear
QA on this exact cut.

## Before this spends a credit

- [ ] Cast three Thai `@handles` in Flow from the blocks in `prompts.md` (age/hands/eyes check per
      `creative-generation.md` casting notes — same gate the source cast passed)
- [ ] Generate the four clips per `prompts.md`, same 5s/5s/4s/6s-ish beat split as `edit-script.md`
- [ ] Run the §10 QA gate as an independent pass — not the session that wrote these prompts
- [ ] Native Thai speaker reads the six type-card lines below **before any spend**, same gate the
      original Hinglish never got — see "Type — translated, unvalidated" in `edit-script.md`
- [ ] `strip_flow_watermark` on every still Flow exports before typesetting (§7)

## Known compromise, recorded rather than hidden

**The destination page does not change.** `/get/w-apply` is written in romanised Hinglish, has no Thai
copy, and its 18+ age-gate celebration text assumes an Indian idiom. Per the brief this stays as-is for
this first pass — the test is whether the *ad* stops a Thai scroll and taps through at all, not a
funnel that's localised end-to-end. That means a real language cliff exists between the ad and the page
a tap lands on, and the app owner accepted this trade explicitly rather than it being an oversight. If
this test's numbers look bad, that cliff — not the creative — is the first thing to rule out before
concluding the concept failed.

## Campaign plan draft (not yet proposed)

Not run through `ad-agent propose` yet — no creative exists to reference. Draft shape once the video
clears QA:

- **Campaign:** `RA_LEADS_GETW-APPLY_TH_PAN_TOF_202609` (`[COUNTRY]` token added to
  `rules/naming.md` 2026-09-01 for this)
- **Ad set:** `WOMEN_18-30_CASUAL_MOVEON-LEAD-TH` — same persona/age/gender band as the live India
  squad (`rules/targeting.md`'s Casual-Selective persona travels; nothing in it is India-specific)
- **Network:** Snap, `--countries th` (code-level: `networks.yaml`/`cli.py` place no India-only
  restriction — this is a content gap, not a code gate)
- **Destination:** `https://www.riteangle.dating/get/w-apply` (unchanged — see compromise above;
  `destinations.yaml`'s gate checks audience=women, not country, so this won't block the push)
- **Budget:** ₹300/day, 5 days — matching the India directional-test tier in `rules/budget.md`;
  revisit once real CPL/CPM data exists for Thailand, which nothing here has yet
- **Open, unresolved before launch:** whether Riteangle's Play/App Store listing is even live in
  Thailand — an install/signup funnel pointed at a store listing that doesn't exist there fails
  regardless of creative quality, and that's outside this repo's ability to check.
