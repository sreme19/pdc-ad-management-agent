# Prompt pack — FOURTEEN-SUITORS, women 18–22

- **rec_id:** `rec-2026-08-21-women-1822-casual-lpv`
- **Hook:** `FOURTEEN-SUITORS` (`creative-style.md` ad-ready thread: "the flooded woman who closes the
  tab — fourteen suitors, no order, tab closed"), delivered in the 18–22 feminist-coded register per
  `targeting.md`.
- **Network / format:** Snap Story, 9:16, 1080×1920. Meta Stories/Reels reuse the same plates.
- **Governed by:** `rules/creative-generation.md` (POV rule §1, plate/type split §2, negative list §4,
  palette §5, Grok-vs-Figma §6, safe areas §7, variant discipline §8).
- **Status:** prompts written, nothing generated yet. QA gate (§10) not run.

## Naming drift to fix before this ships

The record's `ad_name` is `STORY_ATTENTION-SEEKERS_A_20260821`. `ATTENTION-SEEKERS` is not in
`creative-style.md`'s ad-ready-threads vocabulary, which `naming.md` requires `[HOOK]` to come from.
The line *"Stop scrolling through guys who just want attention"* is the 18–22 register from
`targeting.md`, not the hook itself — the hook underneath it is the flood. Correct name:
`STORY_FOURTEEN-SUITORS_{A,B,C}_20260824`. The record's `creative_ref` needs repointing here too.

## The type layer — held constant across all three variants

Per §2 none of this is generated. It is overlaid in Figma/Canva, Gabarito throughout, ink `#1B1020`,
brand pink `#FF3B6B` on the accent words only.

| Beat | Copy | Notes |
|---|---|---|
| 0–2s | **Stop scrolling through guys who just want attention.** | `targeting.md`'s tested 18–22 line. Lands in the first two seconds per `creative-style.md`'s production constraint. |
| 2–4s | **In the order you asked for.** | Over the shortlist render. See the judgment call below. |
| 4–6s | **You finally have a shortlist that means something.** + lowercase `riteangle` wordmark | The women-specific site-native tagline from `creative-style.md`, not the primary one. |

**CTA:** `More` — matches the LPV objective. Not `Sign up`, which is what the current live lead-form
ads use and which promises a form this ad set isn't running.

**Judgment call, flagged rather than decided:** `/get` says "Ranked by what she asked for." Rendering
that in second person as "Ranked by what you asked for" is truer to the product, but
`creative-style.md`'s Don't list includes "ranking people" and `compliance.md` #5 forbids copy implying a
hard numeric ranking. An ordered shortlist is explicitly sanctioned elsewhere in the same file
("an ordered shortlist is the product"), so I read this as permitted — but I've used **"In the order you
asked for"** to keep the meaning and drop the contested word. Your call if you want "ranked" back.

**Stat deliberately not used:** "the median woman has 14 suitors" is quotable per `creative-style.md`,
but to *her* fourteen unordered suitors is the problem, not the benefit. Using it as a selling point
inverts the hook. It stays in the name, out of the copy.

---

## Variant A — `STORY_FOURTEEN-SUITORS_A_20260824` · the closed tab

The FLOODED-WOMAN language cue rendered literally ("I closed the tab"), with no person as the subject.
Cheapest to generate, lowest compliance surface — nobody is in frame to be objectified.

```
Vertical 9:16 photograph, shot from just above and behind a seated person's own eyeline so the
viewer occupies her point of view. A smartphone lying face-down on a small wooden table, pushed
slightly away. Beside it a half-finished cup of chai in a plain glass, gone cold, no steam. A
woman's hand at the lower edge of frame, relaxed, withdrawing from the phone — hand only, no face,
no body. Ordinary Indian apartment interior, late morning, soft natural daylight from a window off
to the left. Plain contemporary surroundings, warm cream and pale terracotta tones, no styling, no
decor staging. Shot on 35mm, shallow depth of field, clean and photographic. Upper two-thirds of
the frame is uncluttered wall and table surface, left deliberately empty for text.

Do not include: any face, any full figure, gowns, formalwear, jewellery, luxury interiors, marble,
chandeliers, hotel corridors, staircases, cars, cash, branded goods, anyone kneeling or serving,
nightclub or neon lighting, dark backgrounds, text or lettering of any kind, watermarks, logos,
AI-tool labels, glitched or extra fingers.
```

## Variant B — `STORY_FOURTEEN-SUITORS_B_20260824` · over her shoulder

Her POV on her own phone, with the screen left blank so the shortlist render from §6 composites in.
This is the variant that carries the product, and the one variable changed from A is the plate — the
type layer is identical.

```
Vertical 9:16 photograph, over-the-shoulder point-of-view shot taken from directly behind a seated
woman's head so the viewer is looking through her eyes at her own phone. Only the back of her
shoulder and a soft edge of dark hair are visible, out of focus, at the bottom of frame — her face
is never seen. Both hands hold a smartphone at a natural reading angle. The phone screen is
completely blank matte white, no interface, no glow. She is sitting on the edge of an unmade bed in
an ordinary Indian hostel or shared flat, plain painted wall, a folded dupatta beside her. Morning
daylight from a window behind the camera. Warm cream and pale neutral tones. Shot on 50mm, the
phone screen in sharp focus, everything else falling off softly. Clean and photographic.

Do not include: her face, any front-facing portrait, gowns, formalwear, lingerie, slip dresses,
cropped bodies, over-the-shoulder glances at the camera, jewellery display, luxury interiors,
marble, chandeliers, cars, cash, branded goods, anyone kneeling or serving, nightclub or neon
lighting, dark backgrounds, any text or interface on the screen, watermarks, logos, AI-tool labels,
glitched or extra fingers.
```

**Composite step (not Grok):** the blank screen receives the woman's ranked-shortlist render —
`creative-style.md` records that this interface already exists, so brief from it rather than
commissioning illustration. Check with whoever holds the mockups first.

## Variant C — `STORY_FOURTEEN-SUITORS_C_20260824` · no photograph at all

**Nothing to generate. This variant does not use Grok.** Per §6, the asset here *is* the interface:
cream ground `#FFF3F0`, the type layer above, and the shortlist render as the only image. Built
entirely in Figma.

It is in the set on purpose, as the control. Three reasons: it is the strongest read on whether
photography contributes anything at all for this audience; it is the cheapest and fastest to produce
and revise; and per §5 it is the most differentiated asset in a feed where every rival — and all four
of our own current ads — ships dark photographic creative.

---

## If QA returns `regenerate`

Per §10, name the clause. The two most likely failures on A and B:

- **A face appears.** Both prompts forbid it twice; if the model renders one anyway, tighten to
  "photographed from behind, subject's head out of frame entirely" rather than adding more negatives.
- **The plate comes back dark.** Grok defaults warm-dark for interior scenes. Escalate the daylight
  clause to "bright overcast daylight, high-key, no shadows deeper than mid-grey" before adding
  "cream" again — naming the light works better than naming the colour.

## Verdict — written back after `log-review` (§9, stage 10)

| Variant | QA verdict | Live verdict | Metric | Note |
|---|---|---|---|---|
| A | *pending* | — | — | — |
| B | *pending* | — | — | — |
| C | *pending* | — | — | — |

## Outcome — rec-2026-08-21-women-1822-casual-lpv (2026-09-07)

**not-working** — RECONCILED 2026-09-07; squad 1b993192 PAUSED, ledger had carried it live since 21 August. Delivered 55,333 impressions, 174 swipes, Rs 359.90 - a 0.31% swipe rate, the worst of any Snap squad here. Our side: 100 page views on /get/w, 2 store clicks, ZERO signups. n=100 page views is above MIN_SAMPLE=30, so the conversion read is a finding. TWO CAVEATS. (1) This is the record budget.md cites as the campaign-cap incident: planned Rs 1,000/day x 5d = Rs 5,000, actual total spend Rs 359.90, because a campaign-level cap silently overrode the squad budget. So the COST read is meaningless and the creative never got a funded test. (2) The verdict is against conversion, which the volume does support: 55k impressions bought 100 page views and nothing beyond.

- Ad set: `WOMEN_18-22_CASUAL_LPV`
- Audience: Snapchat, women only, 18-22, pan-India, Android-weighted. CASUAL-SELECTIVE perso
- Spend: Rs 300/day x 5d
