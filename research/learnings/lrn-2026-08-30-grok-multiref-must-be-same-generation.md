---
id: lrn-2026-08-30-grok-multiref-must-be-same-generation
subject: creative
claim: A multi-image Grok Imagine reference batch holds a stable background only if
  every frame is a sibling re-angle of ONE Flow generation; frames that depict the
  same kind of place but come from different generations make the background travel
  mid-clip
source: own-research
confidence: high
sample_n: 1
status: promoted
created: '2026-08-30'
last_confirmed: '2026-08-30'
review_after: '2026-12-28'
derived_from: null
questions: []
recs: []
promoted_to: rules/creative-generation.md
---

## Claim

A multi-image Grok Imagine reference batch holds a stable background only if every frame is a sibling re-angle of ONE Flow generation — the same rendered scene shot from different angles. Frames that depict the same *kind* of place (a narrow Indian gali, a European café street) but were produced by *different* Flow generations carry different background pixels, and Grok blends them, so the background travels/morphs across the clip.

## Evidence

- (2026-08-30) On the "Tumse Na Ho Paayega" S3 beat, three reference frames were uploaded to Grok that were all "a narrow Indian small-town lane" — but each came from a separate Flow generation with a different painted wall, depth and townscape. The 6s clip's background travelled from a blue Jodhpur-style gali to a Varanasi temple street inside the single generation. Re-running the beat from a SINGLE stable frame held the background. Scenes whose three angles came from one Flow generation (re-angled via Nano Banana 2, not re-prompted) animated cleanly with no travel.
- This sharpens `lrn-2026-08-30-grok-aspect-ratio-follows-image-count`: "upload in batches" is correct for aspect ratio, but the batch must be same-generation siblings, or the aspect win costs you background stability. The two rules are not in tension — batch, but batch siblings.

## Consequence for planning

- **On the Flow/graph side:** when generating the 3-angle set per scene, produce all three angles from ONE generation (Nano Banana 2 re-angling of a single locked plate), never three fresh prompts of "the same location." Three fresh prompts are useless as a Grok multi-ref batch.
- **On the Grok side:** attach a multi-frame batch ONLY when the frames share the exact same background pixels. If they don't, drop to a single frame — a single stable frame beats a same-kind-different-generation trio every time.
- Same-background trio → continuous multi-beat clip with a held set. Mixed-background trio → morph/travel. Single frame → held set, one beat.

## Promoted (2026-08-30)

This claim is now normative, in `rules/creative-generation.md` §2b. That file is what skills obey; this atom is only its origin.
