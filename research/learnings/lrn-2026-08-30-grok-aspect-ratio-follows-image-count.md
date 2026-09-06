---
id: lrn-2026-08-30-grok-aspect-ratio-follows-image-count
subject: creative
claim: In Grok Imagine the output aspect ratio is inherited from a single uploaded
  image and cannot be overridden by prompt, but with multiple images attached the
  aspect control stays available and is respected
source: own-research
confidence: medium
sample_n: null
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

In Grok Imagine the output aspect ratio is inherited from a single uploaded image and cannot be overridden by prompt, but with multiple images attached the aspect control stays available and is respected

## Evidence

- (2026-08-30) A single 1376x768 landscape Flow frame uploaded to Grok with an explicit prompt instruction to output vertical 9:16 returned 16:9 video; the 9:16 chip disappears from the composer as soon as one image is attached. With five landscape frames attached the 9:16 chip remained visible and settable, and output was correctly 720x1280 from the same landscape sources. CONSEQUENCE FOR PLANNING: the entire pre-existing 16:9 storyboard library is usable for vertical ads without cropping, provided frames are uploaded in batches rather than singly. Multi-image upload is preferable anyway because one generation then yields a continuous multi-beat sequence.
## Caveat — batch, but batch siblings (2026-08-30)

"Upload in batches" is right for aspect ratio and wrong if read as "any frames will do." A multi-image
batch holds a stable background ONLY if the frames are same-generation siblings (one Flow generation,
re-angled). Same-kind-different-generation frames make the background travel mid-clip. See
`lrn-2026-08-30-grok-multiref-must-be-same-generation`, which corrects this atom on that point.

## Promoted (2026-08-30)

This claim is now normative, in `rules/creative-generation.md`. That file is what skills obey; this atom is only its origin.
