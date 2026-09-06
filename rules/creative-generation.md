# Creative generation rules — the generation pipeline, prompts, and the plate/type split

Source: Sree's 2026-08-24 session, working back from the first four live Snap/Meta assets
(`SC_AD_IMG_CONNECTION`, `SC_AD_IMG_V1_DONTSETTLE`, `RA_LEAD_WOMEN_SNAP1_20260818`,
`SC_LEAD_CASUAL_MEN_SNAP1_20260817`) and the lead-flow result they produced: **98% of lead-form
submissions were men, and 100% of the `/get` → Play Store taps were men.** Three of those four assets
put a woman in the frame as the object of it; two carry luxury/provider signifiers that
`compliance.md` rule #1 forbids. Both failures are generation-time failures — they were decided by the
prompt, not by the targeting — which is why this file exists as a rule rather than as advice.

Subject to `compliance.md` first, always. `creative-style.md` owns tone, taglines, quotable stats and
palette; this file owns how an asset actually gets produced from them.

## 1. The POV rule — read this before writing a single prompt

**The person the ad is targeting is the person whose point of view the frame occupies.** They are not
the thing being looked at.

This is the whole diagnosis of the 98/2 split. An ad that depicts a desirable woman recruits men,
whatever the ad set's gender targeting says — and on a submit-optimized objective the delivery
algorithm compounds it, because men submit dating lead forms far more readily.

- **Women's creative: no woman as the object of the frame.** Not a better-styled woman, not a more
  tasteful one — none. Occupy her POV instead: what she sees, what she's sick of, what she gets. The
  strongest available material is her *interface* (the ranked shortlist, the AI vetting him on her
  behalf) and her *frustration* (the flood, the closed tab), both already written up in
  `creative-style.md`'s ad-ready threads.
- **Men's creative:** the same rule applied symmetrically. His POV is the desert and the silence — "like
  the Martian stranded on Mars," then real choice. A woman shown as the reward is off-limits here too;
  it is the same giver/receiver framing `compliance.md` rule #1 bans, just pointed the other way.
- **Couple shots are the default failure mode.** A glamorous couple reads as an aspirational tableau
  addressed to nobody in particular. `RA_LEAD_WOMEN_SNAP1_20260818` is named for women and does exactly
  this. If a couple appears at all, one of them is the viewer, and the frame has to make that obvious.

## 2. Generate the plate, never the typography

**Prompt Grok for the scene only. Overlay every word yourself** (Canva/Figma), as a separate layer.

Reasons, in order of how much they cost when ignored:

1. `creative-style.md` makes lowercase **riteangle** in Gabarito a non-negotiable brand mark. A sampler
   cannot be trusted to hold casing, spelling, or typeface — and the lowercase "rite" spelling is what
   carries the pun.
2. Image models garble text, and garbled text on a paid asset is unshippable — but you often only see
   it at Story size, after spend.
3. A plate with no baked-in type is **re-cuttable**. All four current assets have their headline burned
   into the pixels, so testing a new hook against the same scene means regenerating the image. That is
   the single biggest drag on variant throughput, and it's self-inflicted.

The plate carries: subject, setting, lighting, wardrobe, palette, composition, and deliberate empty
space where type will land. Say where the empty space goes in the prompt.

**How the type layer actually gets rendered on this laptop.** Canva/Figma is the intended editor, but
for a fast burned-in cut the working method (established on the 2026-08-30 rough cut) is **PIL PNG
overlays composited with ffmpeg's `overlay` filter** — because this machine's ffmpeg is built without
`libfreetype`, so `drawtext` is unavailable. Render each text screen as a transparent PNG in PIL
(white text + shadow inside a semi-transparent rounded dark box, lower-third), then
`overlay=0:0` it onto the scaled clip. Two standing caveats: **Gabarito is not installed** here
(Arial Bold is the placeholder — a real cut must set the type in an editor that has Gabarito, per
`creative-style.md`), and `uv run python` is required for PIL (system python 3.9.6 is too old).

## 2b. The pipeline — Flow builds frames, Grok animates them

Established 2026-08-30 on the Riteangle BUILD-YOURSELF-FIRST cut, by A/B on the same start frame.

**Grok Imagine setup, so it isn't rediscovered each cut:** Video mode, 720p, 6s, 9:16. Attach the
reference frames in the **prompt bar** (the file-input the composer offers), **not** the photo-edit
post-view — the post-view restyles a single image and re-rolls the face; the prompt bar is what carries
identity into motion.

- **Google Flow for still frames, Grok Imagine for motion.** Flow holds character identity, wardrobe
  and set across many frames; Grok does not have a character system at all. Grok performs the described
  action; Flow tends to return a held pose. Feeding a Flow frame into Grok as the image input carries
  identity through, and is what let the woman drained in scene 1 be the same woman at the turn — the
  failure recorded in `lrn-2026-08-29-flow-character-reference-is-unreliable`.
- **Never animate from a frame that already shows the end of the action.** The clip will hold that state
  for its whole duration. Brief every start frame as the *first* moment of the beat; the iconic moment
  is what the clip should arrive at, not start from.
- **A two-state transition works from one frame.** Posture, expression and a full colour-grade flip can
  happen inside a single Grok clip if the prompt describes it as one continuous transformation. No
  start-frame/end-frame interpolation is needed for a turning-point shot.
- **Aspect ratio follows image count in Grok.** With ONE image attached, output inherits that image's
  aspect and prompt instructions about it are ignored. With SEVERAL attached, the 9:16 control stays
  live and is respected — so the existing 16:9 frame library is usable for vertical work, and a
  multi-image upload also yields a continuous multi-beat sequence from one generation.
- **A multi-image Grok batch must be same-generation siblings, or the background travels.** This is the
  most expensive lesson of the "Tumse Na Ho Paayega" cut
  (`lrn-2026-08-30-grok-multiref-must-be-same-generation`), and it corrects the "always upload in
  batches" instinct from the aspect-ratio rule above. A multi-frame reference batch holds a stable set
  ONLY if every frame is a re-angle of **one Flow generation** — literally the same rendered scene shot
  from different angles. Frames that depict the same *kind* of place but come from *different*
  generations carry different background pixels, and Grok blends them: on S3, three separate
  "narrow Indian gali" generations morphed a blue Jodhpur wall into a Varanasi temple street inside one
  6s clip. The decision rule:
  - **Same-background trio** (siblings from one generation) → attach all three; you get a continuous
    multi-beat clip with a held set, and the 9:16 control stays live.
  - **Mixed-background trio** (same kind of place, different generations) → do NOT batch them; the clip
    will travel. Drop to a **single frame** — a single stable frame beats a same-kind-different-source
    trio every time.
  - This constrains the **Flow/graph side too**: when you generate the 3-angle set per scene, produce
    all three angles from ONE generation (Nano Banana 2 re-angling a single locked plate), never three
    fresh prompts of "the same location." Three fresh prompts of one place are useless as a Grok
    multi-ref batch.
- **Re-dress and re-locate through Flow + Nano Banana 2, which preserves the face; never through Grok
  restyle, which changes it.** Nano Banana 2 is identity-preserving — it holds the same face while
  swapping outfit or setting — which is what lets one character (a locked "Priya") carry across every
  scene. Grok's restyle re-rolls the face and breaks continuity, so it is not a re-dressing tool. Change
  wardrobe/location in Flow, then bring the resulting frame into Grok only for motion.
- **Flow's saved-character assets do not reliably resolve by name** and can be silently broken. Attach
  the actual frames as references instead of relying on an @name.

## 3. Prompt skeleton

Write every prompt in this order. It keeps the compliance-relevant clauses in fixed positions so QA can
find them.

```
[SUBJECT + POV]  who is in frame, and whose eyes we're behind
[ACTION/MOMENT]  what is happening — a moment, not a pose
[SETTING]        ordinary Indian-context specifics (see §4)
[WARDROBE]       plain, contemporary, unbranded
[LIGHT]          natural, warm, soft; daylight over nightclub
[PALETTE]        cream/warm neutrals; brand pink only as a small accent
[COMPOSITION]    9:16 vertical, and where the type-safe empty space sits
[RENDER]         photographic, clean, no artefacts
[NEGATIVE]       the standing avoid-list from §4, verbatim
```

## 3b. The Grok motion-prompt skeleton — identity locks go first, and tight

A still-plate prompt (§3) describes a scene. A **motion** prompt animating a reference frame has a
different failure mode: the model drifts the face, the outfit and the background over the clip's
duration unless each is hard-locked. Loose identity language ("a young Indian woman") is what let Grok
re-roll the face mid-clip on the first pass. Write every motion prompt in this order:

```
[IDENTITY LOCK]    "Use the uploaded reference image EXACTLY — the same specific woman;
                    do NOT change, morph, or swap her." Then her full physical description
                    (skin tone, face shape, eye colour, hair length/colour/texture) spelled out,
                    so the lock has something concrete to hold to.
[OUTFIT LOCK]      name the exact garment; "do NOT alter her outfit."
[BACKGROUND LOCK]  "Keep the SAME [specific location] the entire clip — do NOT change, morph,
                    or travel the background." (This is where the §2b same-generation rule pays off.)
[MOTION]           the first moment of the beat, arriving at the iconic moment — never starting
                    from the end-state (§2b, `lrn-2026-08-30-end-state-frames-produce-frozen-clips`).
[NO SPEECH]        "She does not speak, mouth stays closed" — otherwise the model invents lip-sync.
[RENDER]           photorealistic, cinematic, warm tones, vertical 9:16.
```

The identity/outfit/background triple is not optional padding — it is the load-bearing part. A motion
prompt that names the woman only once, at the top, is too loose; repeat the "do NOT alter her face,
features, skin tone, hair, outfit, or identity" clause explicitly. See any block in a shipped
`creatives/<slug>/grok-prompts.md` for the worked pattern.

## 4. The standing negative list — non-negotiable, paste into every prompt

`compliance.md` rule #1 covers **visual** signalling, not just copy, so the avoid-list has to name
signifiers rather than concepts — a model cannot act on "no provider framing," but it can act on "no
ballroom, no gown."

**Never generate:**

- Gowns, tuxedos, evening formalwear, ballrooms, grand staircases, marble lobbies, chandeliers, hotel
  corridors, luxury cars, cash, jewellery presented as display, designer-branded goods.
- Anyone kneeling, serving, fastening, carrying, paying, or gifting — any giver/receiver staging.
  (`SC_AD_IMG_V1_DONTSETTLE` — a man fastening a woman's shoe under the word "exclusive" — is the
  reference failure. It is rule #1 rendered literally.)
- A woman posed as an object of desire: back-to-camera reveals, over-the-shoulder glances at the
  viewer, lingerie or slip-dress framing, cropped bodies.
- AI-tool watermarks or labels of any kind. Glitched hands, extra fingers, melted jewellery, warped
  faces, invented text anywhere in the frame.
- A man's real, unenhanced photograph (`compliance.md` §6.1) — if a man appears, he is rendered the way
  the product's own AI-enhanced portraits render him.
- Anyone who could read as under 18. No exceptions, no ambiguity — Snap's dating category enforces this
  on top of our own rule.
- **A woman positioned on a bed**, even fully clothed and non-sexual — it trips the image content filter
  reliably. For the alone-at-night beat, stage her on the floor with her back against the side of the
  bed, framed chest-up. Passes first time and reads stronger.
- **Concealment verbs describing a partner** — "hiding his phone", "tilting it away so she can't see".
  Also filter-blocked. Write the behaviour neutrally: "looking down at his own phone, face turned
  away." The emotional read is identical.

**Always specify:** Indian models, Indian-context setting, contemporary and ordinary rather than
aspirational-luxury, 18+ and unambiguously adult.

**Always name the wardrobe for the activity.** Generators inherit clothing from the reference frame and
will never correct it for plausibility. Left unstated, a competitiveness beat came back with her serving
on a tennis court in jeans, and a career beat had her presenting to a boardroom in a vest top — both
arguing against the very thing the shot existed to say. On an ad about competence, wardrobe is
load-bearing: name the kit.

**Devanagari needs a shaping-capable text engine.** Overlay type set in Devanagari through a pipeline
without complex-script shaping returns mis-ordered matras — the i-matra lands after its consonant rather
than before. Latin renders correctly. This agrees, for unrelated reasons, with
`lrn-2026-08-29-roman-script-is-an-audience-signal`: romanised Hinglish is the default. A Devanagari cut
must have its type pass done in a real editor.

## 5. Palette, and the dark-creative trap

`creative-style.md` says the light palette is a deliberate differentiator: every major rival ships dark
dating creative, so cream reads as different in-feed before a word is read. **All four current assets
are dark.** In-feed they are indistinguishable from a Tinder ad, which forfeits the one visual
advantage the brand has decided to buy.

- Ground: cream `#FFF3F0`, surface `#FBEEE9`. Ask for warm daylight, not neon or nightclub.
- Accent: brand pink `#FF3B6B`, sparingly, and in the type layer where you control it exactly.
- Ink: `#1B1020` for all text.
- Amber `#F59E0B` and red `#EF4444` are functional status colours in-product and **must not appear as
  decorative accents** in creative.
- Teal, not pink, for anything aimed at networking season / platonic mode.

## 6. When not to use Grok at all

Grok Imagine generates photographic scenes. It does not generate the product.

**Route to Figma/CSS mockup instead** whenever the asset *is* an interface: her ranked shortlist, the AI
vetting him on her behalf, the hand-off banner, his four-stage progress bar, the Date/Network toggle.
`creative-style.md` records that these renders already exist — brief from them rather than commissioning
illustration, and check with whoever holds the mockups first.

This matters most for the women's lane, because §1 pushes the strongest women's asset toward *her
interface* — which means the highest-value women's creative is a mockup, not a generation. A prompt pack
is allowed to say "variant B is a UI render, not a Grok asset" and stop there.

## 7. Format and duration

- **9:16 vertical**, 1080×1920, for Snap Story and Meta Stories/Reels. Meta feed placements get a
  separate 4:5 or 1:1 crop from the same plate — plan the type-safe space so one plate survives both.
- **Six seconds is short** (`creative-style.md`'s production constraint). Where video is used, the
  emotional beat lands in the first two seconds; anything that needs a build lands better as a still.
- Keep the bottom ~15% and top ~10% clear of anything load-bearing — the platform's own chrome, CTA
  pill and profile row sit there. All four current assets crowd the CTA.
- **Brief headroom and edge margin so a watermark crop is always available.** Grok stamps a wordmark
  bottom-right; **Google Flow stamps a four-point "made with AI" sparkle in the bottom-right corner** at
  a roughly fixed offset (~98px up on its native export). Remove them by cropping and rescaling, never by
  inpainting — `delogo` leaves a smear that draws more attention than the mark did. Delivery upscales
  720×1280 to 1080×1920 anyway, so `crop=693:1232` costs nothing and holds exact 9:16.
- **The two generators need two different crops — know both numbers.** A **Flow** still: crop the bottom
  **150px** (`strip_flow_watermark`, §7's mandatory pass below). A **Grok** video clip: the wordmark
  sits lower, so crop the bottom **90px** and rescale — `crop=in_w:in_h-90:0:0,scale=720:1280`. A clip
  that is a Flow frame animated by Grok has already had the Flow sparkle removed at the still stage, so
  it only needs the Grok 90px crop; don't double-crop.
- **Every Google/Flow/Gemini-exported still MUST pass through `strip_flow_watermark`** (in
  `src/ad_management_agent/watermark.py`, 150px off the bottom) before it is used in any creative — this
  is not optional and not per-frame judgement. On 2026-08-30 a live Story Ad shipped with the sparkle
  baked into several plates because a QA note *asserted* the Flow stills were clean without zooming the
  corners. The crop is the guarantee; the eyeball is the check. Do both, on every asset, every time.

## 7b. Audio and music

The rules layer had no audio section before 2026-08-30; these come from building the first cut with a
generated score.

- **A single music bed across the whole cut**, not the clips' own audio — clip audio also masks the
  shots having been generated separately. `Meta Sound Collection or Flow-generated audio only`; a
  commercial track is a licensing problem on a paid ad.
- **Never build a bed by looping one short clip.** It reads as interruptive no matter how clean the
  crossfades are, and the objection survives changing the instrument — repetition is the cause, not
  the sound. Chain several *different* generations end to end instead. Budget for several.
- **Flow's Extend is gated on Veo AND ≥720p.** A 360p clip returns "360p videos cannot be extended"; a
  non-Veo model returns "Only Veo-generated videos can be extended". If a bed longer than one
  generation is needed, choose Veo at 720p up front — it cannot be retrofitted.
- **Never normalise the finished mix.** Loudness normalisation across the sum destroys an intentional
  quiet-to-loud arc — an 11 dB lift collapsed to 1.1 dB. Set each bed to its own target, then peak-limit
  only. −16 LUFS integrated with true peak −1.5 dB is right for Meta and Snap.
- **The cut must work muted.** Most views are silent, so the type carries the whole argument. Music
  raises the ceiling; it can never be load-bearing.
- **Snap has no audio library for a tap-through Story Ad.** Confirmed live 2026-08-30 in Ads Manager's
  own creative editor for a COMPOSITE web-view Story Ad: the story and each of its snaps expose only
  attachment / URL / CTA / favouriting / prefetch — no music, sound, or audio control anywhere. Snap's
  "Sounds" library is offered for Single Image/Video ad formats, not this one. So a Story Ad built from
  stills carries no soundtrack, full stop — do not promise "one bed across the tiles" on this format
  (the whole reason the muted-legibility rule above matters most here). If music is a hard requirement,
  the format has to be a single video ad, not a Story Ad.

## 8. Variant discipline

Per `naming.md`, `[VARIANT]` is A/B/C on the **same hook**. A variant set changes **one** variable at a
time — the hook line, or the scene, or the CTA — never several at once, or the read is uninterpretable
at the sample sizes this account actually gets (`budget.md`'s `MIN_SAMPLE = 30`).

Three variants per hook is the working default: enough to see a spread, few enough that each one clears
the floor when the ad set is funded at ₹800–1,200/day.

## 9. What gets written down, and where

- **This file** holds the conventions — refined in place whenever a pass teaches something, the same way
  every other file under `rules/` works.
- **`creatives/<slug>/prompts.md`** holds the instances: one block per variant, each carrying the hook
  slug (from `creative-style.md`'s ad-ready threads vocabulary), the full prompt text as pasted into
  Grok, the type-layer copy kept separate from it, and the `rec_id` it was generated for.
- **`creatives/<slug>/qa.md`** holds the second-pass verdict per §10.
- When `log-review` lands a verdict on the rec, **write that verdict back onto `prompts.md`.** The point
  of keeping the exact prompt text is that a ranked prompt library accumulates across campaigns — which
  prompt patterns produce assets that earn taps, per persona. A prompt with no outcome attached to it
  taught nothing.

## 10. The QA gate — a second pass, not the same one

`compliance.md` §8 requires an independent check, and generated imagery is exactly where it earns its
keep: the pass that wrote the prompt is the worst possible judge of whether the output honoured it.

Check the rendered asset **as an image**, not as copy:

1. §4's negative list — any signifier present?
2. §1's POV rule — who is the object of this frame?
3. **AI-generation watermark — zoom every corner of every asset at full resolution.** Not "the crop
   looks fine", not "the source was clean" — actually zoom the bottom-right corner of each plate (where
   Google Flow's sparkle and Grok's wordmark both sit) and confirm no mark survives. Google/Flow stills
   must already have gone through `strip_flow_watermark` (§7). When clear, record the literal line
   **`watermark-check: pass`** in `qa.md` — the Snap push (`snap-push`, `snap-push-story`) refuses to
   create a single object without it, and prints an advisory corner scan naming the plates most worth a
   second look. This is a gating item after the 2026-08-30 live-sparkle incident, not a soft reminder.
4. Other AI artefacts, garbled text, hands.
5. Wordmark: present, lowercase, Gabarito, correct spelling.
6. Legible at actual Story size on a phone, not just at desktop zoom.
7. Cream or dark — and if dark, is there a stated reason?
8. Safe areas (§7) clear of the platform's chrome.

Verdict is one of **`pass`** · **`regenerate`** (naming the exact prompt clause to change) ·
**`escalate`** (a `compliance.md` hit — the app owner's decision, never a quiet edit). Record it in
`creatives/<slug>/qa.md`. Nothing reaches `ad-agent propose` without a `pass`, and nothing reaches a
Snap push without a `watermark-check: pass`.
