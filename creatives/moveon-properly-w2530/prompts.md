# Image Gen Prompt Pack — MOVE-ON-PROPER, women 25–30

- **rec_id:** pending (idea-2026-08-27-breakup-reentry-second-chapter → propose --from-idea)
- **Hook:** `MOVE-ON-PROPER` — a breakup re-entry turn on Tinder's own "move on" language: not a
  donut and a party, a real next person. Delivered in the 25–30 security/loyalty register per
  `targeting.md`'s Aug-5 age split, not the 18–22 wild-experiences one.
- **Network / format:** Snap Story, 9:16, 1080×1920. Meta Stories/Reels reuse the same plates.
- **Governed by:** `rules/creative-generation.md` (POV §1, plate/type split §2, negative list §4,
  palette §5, Grok-vs-Figma §6, safe areas §7, variant discipline §8).
- **Status:** prompts written, nothing generated yet. QA gate (§10) not run.

## New-hook flag, fix before this ships

`MOVE-ON-PROPER` is not in `creative-style.md`'s ad-ready-threads vocabulary, which `naming.md`
requires `[HOOK]` to come from. Same class of drift as FOURTEEN-SUITORS' `ATTENTION-SEEKERS` name.
Either add "the breakup handled properly" as a sanctioned thread in `creative-style.md`, or map this
to an existing one before the name is final. Provisional until then.

Also: campaign token `GETW` (for `/get/w`) is not in `naming.md` — it only defines `GET` for `/get`.
Add the row or the spend↔traffic join drifts.

## The type layer — held constant across all three variants

Per §2 none of this is generated. Overlaid in Figma/Canva, Gabarito throughout, ink `#1B1020`,
brand pink `#FF3B6B` on the accent words only.

| Beat | Copy | Notes |
|---|---|---|
| 0–2s | **Move on toh karna hai — par dhang se.** | The Hinglish hook. Interviewer-register English pivots on the English word "move on"; the turn is Hinglish. Lands in the first two seconds per `creative-style.md`. Pink on "dhang se." |
| 2–4s | **He's vetted before he ever reaches you.** | Her POV on the product — the AI vetting him on her behalf (`creative-style.md` ad-ready thread). Carries the security register the 25–30 band wants. |
| 4–6s | **Verified, not vibes.** + lowercase `riteangle` wordmark | Site-native tagline from `creative-style.md`. Pink on "Verified." |

**CTA:** `More` — matches the LPV objective and the `/get/w` destination. Not `Sign up` (promises a
form this ad set isn't running) — same call as the FOURTEEN-SUITORS pack.

**Compliance judgment calls, flagged not buried:**
- **"vetted" / "Verified"** is identity/anti-fraud verification, which `compliance.md` #4 explicitly
  sanctions ("identity-verified"). It is *not* a money, provider, or desirability claim, and names no
  ranking — so it clears #1 and #5. If a reviewer reads "vetted" as a status/quality ranking of men,
  that is an `escalate`, not a quiet edit.
- **Borrowing Tinder's "move on"** is deliberate contrast, not imitation — the register is dignified
  continuation, the opposite of the swipe-app re-acquisition tone. If in-feed it reads as
  Tinder-adjacent rather than a turn on it, that is the brand-fit risk the idea already carries.

---

## Variant A — `STORY_MOVE-ON-PROPER_A_20260827` · the phone set down

The exit decision rendered as her gesture, not her face. Cheapest to generate, lowest compliance
surface — nobody in frame to be objectified.

```
Vertical 9:16 photograph, shot from just above and behind a seated person's own eyeline so the
viewer occupies her point of view. A woman's own hand, seen as if it were the viewer's, setting a
smartphone face-down onto a warm wooden table in a calm deliberate motion — not a slam. The screen
is still faintly lit as it turns over, a soft indistinct colourful blur dying on it, no readable
interface. A plain glass of chai to one side, a small potted plant. Hand and forearm only, a plain
contemporary kurta sleeve — no face, no body, no other person. Ordinary Indian home interior by a
window, late morning, soft warm natural daylight. Warm cream and pale terracotta and wood tones,
no styling, no decor staging. Shot on 35mm, shallow depth of field on the phone, clean and
photographic. Upper third of the frame is uncluttered wall and table surface, left deliberately
empty for text.

Do not include: any face, any full figure, a woman posed as an object, over-the-shoulder glances at
the camera, any man, gowns, formalwear, jewellery, luxury interiors, marble, chandeliers, hotel
corridors, staircases, cars, cash, branded goods, anyone kneeling or serving, nightclub or neon
lighting, dark backgrounds, any readable text or interface or lettering, watermarks, logos, AI-tool
labels, glitched or extra fingers, anyone who could read as under 18.
```

Type-safe space: top third (hook line), bottom-centre clear band (tagline + wordmark).

## Variant B — `STORY_MOVE-ON-PROPER_B_20260827` · over her shoulder, the verified profile

Her POV on her own phone, screen left blank so the **verified-profile render composites in** — the
literal picture of "Verified, not vibes." The one variable changed from A is the plate; the type
layer is identical.

```
Vertical 9:16 photograph, over-the-shoulder point-of-view from directly behind a seated woman's head
so the viewer looks through her eyes at her own phone. Only the back of her shoulder and a soft
out-of-focus edge of dark hair show at the bottom of frame — her face is never seen. Both hands hold
a smartphone at a natural reading angle. The phone screen is completely blank matte white, no
interface, no glow. She sits by a window in an ordinary Indian flat, plain painted wall, a folded
dupatta beside her, a cup of chai. Soft warm morning daylight. Warm cream and pale neutral tones.
Shot on 50mm, the phone screen in sharp focus, everything else falling off softly. Clean and
photographic.

Do not include: her face, any front-facing portrait, a woman posed as an object, lingerie or slip
dresses, cropped bodies, over-the-shoulder glances at the camera, any man, gowns, formalwear,
jewellery display, luxury interiors, marble, chandeliers, cars, cash, branded goods, anyone kneeling
or serving, nightclub or neon lighting, dark backgrounds, any text or interface on the screen,
watermarks, logos, AI-tool labels, glitched or extra fingers, anyone who could read as under 18.
```

**Composite step (not Grok):** the blank screen receives the **verified-profile / vetting render** —
a single profile carrying the identity-verified badge and the AI-vetting-on-her-behalf state, not a
ranked list. `creative-style.md` records these interface renders exist; brief from them, check with
whoever holds the mockups first. Do not generate the interface in Grok.

## Variant C — `STORY_MOVE-ON-PROPER_C_20260827` · no photograph, the control

**Nothing to generate.** Per §6 the asset here *is* the interface: cream ground `#FFF3F0`, the type
layer above, the verified-profile render as the only image. Built entirely in Figma.

In the set on purpose as the control, for the same three reasons as the FOURTEEN-SUITORS C: it reads
whether photography contributes anything for this audience; it is cheapest to revise; and per §5 it
is the most differentiated asset in a feed where every rival ships dark photographic creative.

---

## If QA returns `regenerate`

Per §10, name the clause. Most likely failures on A and B:

- **A face appears.** Both prompts forbid it twice; if the model renders one anyway, tighten to
  "photographed from behind, subject's head out of frame entirely" rather than piling on negatives.
- **A readable interface appears on the screen** (B must stay blank for the composite; A's blur must
  stay unreadable). If Grok invents an interface, add "screen is a plain matte white rectangle, no
  content" (B) / "screen shows only an indistinct colour blur, nothing legible" (A).
- **The plate comes back dark.** Grok defaults warm-dark for interiors. Escalate the light clause to
  "bright overcast daylight, high-key, no shadows deeper than mid-grey" before re-adding "cream" —
  naming the light works better than naming the colour (learned on FOURTEEN-SUITORS).
- **Grok watermark, lower right.** Known on every FOURTEEN-SUITORS plate. Not a regenerate — crop it
  at the type pass (crop first, inpaint only if it overlaps real content). Both A and B carry dead
  space at the foot for this.

## Verdict — written back after `log-review` (§9, stage 10)

| Variant | QA verdict | Live verdict | Metric | Note |
|---|---|---|---|---|
| A | *pending* | — | — | — |
| B | *pending* | — | — | — |
| C | *pending* | — | — | — |

## Outcome — rec-2026-08-27-moveon-w2530-meta (2026-09-07)

**not-working** — RECONCILED 2026-09-07 against the live account; the ledger had carried this as 'live' for 10 days after it stopped. Ad set 6984035818681 and ad 6984036525881 are both PAUSED and the run window closed 2026-09-02. IT DID DELIVER, and well, at the top of the funnel: Rs 366.39 spend, 9,606 impressions, 606 link clicks, 465 Meta-counted landing-page views, and 611 page views recorded on OUR side for this ad set - so its url_tags worked and the traffic was tracked correctly end to end. THE VERDICT IS not-working BECAUSE OF WHAT HAPPENED NEXT: 611 tracked page views produced ZERO signups. That is well above MIN_SAMPLE=30, so this is a finding rather than a shrug - the ad bought attention on /get/w cheaply and none of it converted. Two caveats recorded rather than buried. (1) The record states Rs 1,000/day; the ad set's actual daily_budget was Rs 300/day, so this ran at under a third of its planned rate and never reached the Rs 800-1,200 band where budget.md says delivery exits learning - the CONVERSION read is solid on n=611 views, the cost-efficiency read is not. (2) Success metric as stated was landing-page views, and on that metric alone it succeeded; the verdict is against the outcome the views existed to produce.

- Ad set: `WOMEN_25-30_CASUAL_MOVEON-LPV`
- Audience: female, 25-30, IN, all devices, expansion off, regulated-content flagged
- Spend: Rs 1000/day x 5d
