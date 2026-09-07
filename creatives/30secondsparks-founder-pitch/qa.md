# QA — 30secondsparks-founder-pitch

Status: **NOT PASSED — asset is incomplete.** The signed-in app screens are still substituted by
pre-auth ones and there is no music bed. Recorded here rather than left implicit so the file cannot
be mistaken for a cleared asset.

watermark-check: pass — 2026-09-07. The four BUILD-YOURSELF frames used in the collage are Flow
exports and are run through `strip_flow_watermark()` in `build.py`. This was not a formality: the
`Woman_reading_laptop_at_cafe` frame carries the four-point sparkle bottom-right, it was visible in
the first rendered collage, and it is the same mark that reached a live Story Ad on 2026-08-30. All
four cell corners were then zoomed on the rendered plate and are clean. The crop is the guarantee;
the eyeball was the check; both were done.

## Checked so far

| Check | Verdict | Evidence |
|---|---|---|
| 9:16, 1080x1920 | pass | `ffprobe` on `asset-a.mp4` |
| Under the 30s cap | pass | 28.87s; the build prints a warning if it goes over |
| Mirror corrected | pass | `hflip`; t-shirt lettering reads correctly, checked on a frame |
| Safe areas (§7) | pass | type between y=192 and y=1632; checked on rendered frames |
| Type legible over picture | pass, after a fix | full-bleed app screens put our type on the app's own type and neither could be read; the screen is now a card on cream |
| Emulator status bar removed | pass, after a fix | the clock and battery were visible in the first cut |
| Gabarito, real glyphs | pass | set in `build.py`, not burnt into any source |
| Wordmark lowercase, two-tone | pass | `rite` ink + `angle` pink, drawn separately |
| Money as an attraction signal (§1) | pass | "and earns a lot of money" cut from the take |
| Generated person, §6.2 scope | pass | generated portraits were dropped entirely; the opening is the founder himself plus a typed profile card with a silhouette avatar. Narration is the founder's own voice throughout, so the prohibited first-person-synthetic-testimonial form is not reachable |
| Flow watermark crop (150px) | pass | `strip_flow_watermark()` on all four collage frames; corners zoomed on the rendered plate |
| Burnt-in foreign-language type | pass | collage built from the ORIGINAL frames, not the finished carousel slides, which carry Hinglish captions |
| Banned-vocabulary gate (§6.4) | pass, both ways | see below |
| Audio target | deferred | VO only; §7b targets apply once the bed exists |

## Banned-vocabulary gate — 2026-09-07

Ran `pocket-dating-coach/scripts/check-banned-strings.sh`'s own three pattern arrays (31 phrase,
5 case-sensitive, 5 referral), sourced from the script rather than retyped, against every on-screen
string and every word spoken in the finished cut. **No pattern matched.**

The literal match is not the check, though. That gate has twice reported clean while a banned term
was live: once because a Discover label was title-cased from a database key at runtime so no static
string existed, and once because the sign-up gate said "Spoilt", the British spelling of a word
listed only in its hyphenated form. Both were found by looking at the screen. So:

- **The app screenshots carry product text nobody here authored** — the runtime-assembly case
  exactly. The archetype list is the exposure, since `Casual-Generous` and `Spoiled-Casual` were
  named in the rejection. Visible in the two crop windows actually used: SERIOUS CONNECTION,
  Traditional-Matrimony, Forever-Focused, Hopeless-Romantic, and a COLLAPSED LOW-PRESSURE group.
  Neither rejected archetype appears. **If a future cut expands that group or scrolls further, this
  check has to be redone — the crop window is what makes it pass.**
- **"We verify identity, photos, lifestyle & intent"** sits one word from the banned phrase
  `photos, spending`. It reads *lifestyle*. Clean, and worth knowing how close it is.
- **"and earns a lot of money" is gone from the audio**, not just from the captions — confirmed
  against the word-level transcript of the nine surviving spans, not assumed from the edit list.

## Open

- **Signed-in screens are in as of 2026-09-07**, captured on 1.0.9 on a throwaway account: the
  archetype match card and "Earn your profile". The latter is a real upgrade — "He has to prove it."
  now sits over the product saying *prove you're real* and *prove you're solid*, not over a screen
  that merely describes verification.
- **The AI Bestie conversation view and the "Self declared" tag are still NOT in the film.** Both
  sit behind identity verification, which needs a real selfie on a real account; faking it was not
  on the table. They remain the strongest available upgrade.
- **"Her AI does the talking on her behalf" is no longer claimed on screen.** It was type over the
  man's archetype card, and the screen contradicted the claim. It now appears only in the post
  caption. Nothing in this build shows the woman's AI doing anything — that is the film's biggest
  remaining gap between what Riteangle does and what this asset can prove.
- No independent second-pass review has been run.
