# QA — `asset-a.mp4`, MOVE-ON-PROPER Thailand type-swap

Scored against `../_bakeoff/rubric.md`'s gates, per `rules/creative-generation.md` §10.

> ## ⚠️ THIS IS NOT AN INDEPENDENT PASS
>
> The same session that built `typeset_video.py` and chose the Thai lines is
> recording this QA. Treat every line below as self-assessment, same caveat the
> original `../moveon-lead-w1830/qa.md` and `../moveon-swagger-video/qa.md`
> carry. Deployed anyway on the app owner's explicit instruction, 2026-09-01 —
> same precedent as the swagger cut's `fail`-verdict override.

**Verdict: `pass`, with one carried-over deviation and one new compromise.**

## What this asset actually is

Not a new generation. The four beats are the exact footage from the shipped,
best-performing `../moveon-lead-w1830/asset-a.mp4` (verified frame-by-frame
2026-09-01 — see `_source/clips-recovered-20260901/README.md`) with the
on-screen type swapped from Hinglish to Thai. Same models, same wardrobe, same
sets, same cut points, same music bed (the original's own AAC track, reused
byte-for-byte). Only clip 4 differs in *method*: no raw video was recovered for
that beat, so it's the wedding still animated with a slow zoom rather than the
real handheld footage — everything else is the shipped asset.

## Hard gates

| Gate | Result | Why |
|---|---|---|
| `watermark-check` | **pass** | Corner-zoomed a frame from each of the three video beats after the mandatory Grok-wordmark crop (90px bottom, per `creative-generation.md` §7) — clean. The still (clip 4) was never Grok-watermarked in the first place (checked at its own QA time, see `../moveon-lead-w1830/_source/clips-recovered-20260901/README.md`). |
| Thai type renders correctly | **pass, after a fix** | First render mis-shaped every combining tone mark (PIL's default layout engine can't do complex-script shaping). Rebuilt with `libraqm` + `Layout.RAQM` — re-checked frame-by-frame across all six cards, clean. |
| Real man's photo / AI tells / under-18 read / negative-list signifiers | **carried from the original**, not re-litigated here. The original `qa.md` scored this `pass` (28.25/37.5) and it shipped and is the best-measured-performer; this asset changes no pixel the original camera didn't already capture. |

## New deviations specific to this cut, recorded rather than hidden

1. **Clip 4 is a still + zoom, not real footage.** The original's clip 4 has
   actual motion (hand/hair shift across its ~7s run); this cut approximates
   it with a Ken Burns push-in on the one recovered frame. Visually
   convincing at normal viewing speed, not identical to the shipped clip.
2. **Thai lines are machine-drafted, unvalidated.** Same open gate the
   original Hinglish never fully closed — see `edit-script.md`'s translation
   table. **Spend gate, not a deploy gate** — flagged again here because this
   asset is now actually going live.

## Not covered by this pass

Same open items the original carries: Snap/Meta synthetic-media disclosure
unchecked, comment moderation unresolved. Both apply identically here since
the footage is identical.
