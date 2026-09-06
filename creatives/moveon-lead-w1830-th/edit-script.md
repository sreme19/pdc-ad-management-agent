# Edit script — Thailand cut · 20s · 9:16 Snap/Meta Reels-Stories

Assembly sheet, copied beat-for-beat from `../moveon-lead-w1830/edit-script.md`. Same cut, same
timecodes, same transitions — only the cast and the type layer differ. Do not re-derive the cut; reuse
this once the four Thai clips exist.

**Every type card is a machine-drafted Thai translation.** No native speaker in the target register has
read it. That is a spend gate, not an edit gate — cut it, but hold the buy. See `prompts.md`'s
translation table for the back-translations and the font note (Gabarito is Latin-only; pair with Noto
Sans Thai or IBM Plex Sans Thai for the Thai lines, brand mark stays Latin/Gabarito).

## Source clips (to be generated per `prompts.md`)

| # | cast | the beat |
|---|---|---|
| A | `@Aom`, bedroom, night | eye-roll at ~8s (of the raw clip) |
| B | `@Fah`, apartment, day | phone face-down + private stillness at ~9.6s |
| C | `@Nam`, apartment window, late morning | the turn into golden light at ~9.5s |
| D | `@Aom`, `@Fah`, `@Nam` walking, residential street | the three-way laugh at ~2.5s |

All four should be generated 1080×1920 direct from Flow if the model tier supports it (Veo 3.1
Quality does); if a tier returns 720×1280 like the source did, run the same near-square-inset check
`typeset_video.py` already performs before trusting `ffprobe`'s reported height.

## The cut

```
┌─ 0:00 ──────────────────────────────────────────────── DRAIN ─┐
0:00.0   CLIP A   (4.0s)   @Aom, bedroom, night
         0:00.3   TYPE   เท.
         0:02.0   TYPE   โปรไฟล์ปลอม
         Her face is flat. At 0:03 she rolls her eyes and drops her head
         back — CUT ON THE EYE-ROLL, not after it.
         HARD CUT

0:04.0   CLIP B   (4.0s)   @Fah, apartment, day
         0:04.3   TYPE   นอกใจ
         0:06.0   TYPE   แชทกันเป็นสัปดาห์ แต่ไม่ไปไหนสักที
         She frowns at the phone, turns it face-down, goes back to what
         she was doing. CUT ON the small private stillness.
         HARD CUT

┌─ 0:08 ───────────────────────────────────────────────── TURN ─┐
0:08.0   CLIP C   (5.0s)   @Nam, apartment window, late morning
         0:09.0   TYPE   ตอนนี้รู้แล้วว่าพลังงานหายไปไหน
         Phone face-down, pushed away. She sits back and looks out, and the
         light goes from grey to gold on her face. HOLD to the gold — this
         is the hinge of the film and it needs the extra second.
         SOFT CUT / 6-frame dissolve — the only soft transition in the cut

┌─ 0:13 ──────────────────────────────────────────────── PAYOFF ─┐
0:13.0   CLIP D   (7.0s)   @Aom, @Fah, @Nam walking, all three
         0:13.5   TYPE   ไม่ต้องเดต แค่เจอกัน แล้วใช้ชีวิต
         The three-way laugh lands at ~0:14.5. Let it play.
         0:17.0   TYPE   สมัครเลย →          + riteangle brand mark
         0:20.0   END
```

## Type treatment

- **Brand mark (`riteangle`) stays Latin, lowercase, Gabarito** — unchanged from source, non-negotiable
  per `creative-style.md`.
- **Thai type cards set in Noto Sans Thai or IBM Plex Sans Thai**, not Gabarito (Latin-only, cannot
  render Thai script). Match weight/size proportions to the source cards as closely as the substitute
  face allows.
- **All type overlaid in edit, never generated** (`creative-generation.md` §2) — same rule, same reason:
  a sampler cannot hold Thai script any more reliably than it holds Devanagari, and a garbled type card
  on a paid asset is unshippable.
- **Safe zones unchanged: nothing in the top 14% or bottom 20%.** The `สมัครเลย →` card is the one that
  must not be eaten by platform chrome — middle third, not the foot of frame.
- Drain cards are single words/short phrases, hard on and hard off, no animation. The payoff card can
  hold, same as source.

## Audio

Unchanged from source: no dialogue anywhere in the cut (`compliance.md` §6.2 still applies — a
generated woman narrating a first-person Riteangle experience is what blocked the still-image MOVE-ON
video); single music bed across the whole cut, Meta Sound Collection or Flow-generated only; the cut
must work muted, since the type carries the entire argument.

## Known compromises, carried over or new

1. **The cast does not carry across scenes** — same as source: `@Aom` in clip 1 is not necessarily the
   same face pattern-matched into clip 4 unless Flow holds the character reference. Same accepted
   trade the source made.
2. **The type translations are machine drafts** — new compromise specific to this cut, and the
   headline gate before spend (see top of this file and `prompts.md`).
3. **The destination page (`/get/w-apply`) is not translated** — recorded in `README.md`, not an
   edit-script concern but load-bearing for whether this test can be read cleanly.

## Before this spends a rupee (or baht)

- [ ] Native Thai speaker read of every Thai line, register-checked for an 18–30 casual audience
- [ ] Listen to any clip audio for generated speech, same as source
- [ ] Watermarks cropped on all four (`strip_flow_watermark`, 150px, per `creative-generation.md` §7)
- [ ] Watched muted, end to end
- [ ] §10 QA gate run as an independent pass, `watermark-check: pass` recorded in a `qa.md` before any
      `snap-push`
- [ ] Confirm what country/currency the Snap/Meta ad account should bill this under before `propose`
