# QA — independent §8 compliance pass (two finished assets)

**Pass type:** independent second pass per `rules/compliance.md` §8 — run 2026-08-29 by a separate
agent session that did not write the ad. Verified against `rules/compliance.md`,
`rules/creative-generation.md` §1/§4/§5/§7, and this folder's own `video-direction.md` and
`brief.md`.

**Assets covered:**

1. `energy-kahan-jaati-hai-ROUGH-v3.mp4` — Meta cut (20.0s, 720×1280, h264 + mono 22050 Hz AAC)
2. `energy-kahan-jaati-hai-STITCH-v1.mp4` — Snap cut from different footage (20.0s, 720×1280)

**Ad copy (same for both):** primary text "Ghosting. Fake profiles. Teen hafte ki texting jo kahin
nahi jaati." / "Ab samajh aaya energy kahan jaati hai?" / "Date mat karo. Bas milo, aur jiyo." /
"Riteangle har aadmi ko verify karta hai — usse pehle ki woh aap tak pahunche." Headline "Apply
karo — sirf 18+". Description "Abhi sirf Android par." CTA Apply Now → Meta instant form →
`/get/w-apply` age-band gate.

**Method:** frames extracted at 1 fps across each full 20s, plus 4 fps sampling around suspect
moments (asset 1's 1–3s blink and 11–13s transition); zoomed crops of faces, hands, background
figures, and the bottom-right corner of every second; full and zoomed spectrograms; and a Whisper
(small model, VAD-filtered) transcription pass on both audio tracks, including a forced-Hindi pass
on the 13–20s tail. (An earlier draft of this file recorded the audio verdict as spectral-only;
the transcription pass did run in this session and its result is recorded below.)

---

## Asset 1 — `energy-kahan-jaati-hai-ROUGH-v3.mp4` (Meta cut)

Scenes: (1) woman on bed at night with phone, carved-wood bed, "Ghosting." / "Fake profiles.";
(2) young woman in a library with textbooks, "Cheating." / "Teen hafte…"; (3) woman at an office
desk, "Ab samajh aaya…"; (4) four women in sarees at a marigold-and-string-lights function, "Date
mat karo…" then `Apply karo` + `riteangle` pills.

### §6.2 audio — music bed only, no synthetic-person testimony
`pass` — The track is an instrumental bed: sparse low-passed bass pulse 0–8s, percussion joins at
8s on a strict metric grid, full arrangement 13–20s with straight sustained-note harmonic ladders;
no wandering vocal-formant contours anywhere in the spectrogram. VAD-filtered Whisper confirms it:
**zero** speech segments over the full file and over a forced-Hindi pass on the 13–20s tail (the
only unfiltered output was a textbook non-speech hallucination, no_speech_prob 0.76). Consistent
with `video-direction.md`'s "No dialogue. No spoken lines at all." — all words live in overlaid
type, which is brand voice, the remedy §6.2 itself names. Caveat outside this file's scope:
confirm the music source is Meta Sound Collection or Flow-generated (direction note 6), not a
commercial track.

### §6.2 imagery — AI watermark
`pass` — No legible AI-tool watermark anywhere. However, a stationary blurred-out rectangle sits
bottom-right (~x420–720, y1060–1280) in **every** scene — the watermark was smeared over rather
than cropped, and the smear is visible over the saree fabric in the party scenes and over the
chair in the office scene. Covering the mark is the settled-scope precedent (§6.2, decided
2026-08-28), so this is not a labelling violation, but the visible smudge is counted as a craft
defect under the next gate. Recommend a crop or a cleaner plate in the final cut.

### §6.2 imagery — AI glitches / craft
`fail` — Three real defects, verified frame-by-frame. (1) At ~1.5–2.2s the bedroom woman's
eye-roll renders with **fully whited-out, irisless eyes** — asymmetrically (one eye blank white
while the other is mid-lid), long enough that a 1 fps sample landed on it; on pause it reads as a
horror frame. (2) From ~11s to ~13s the frame is a **stacked duplicate of the office scene** — two
near-identical panels with a hard horizontal seam, held across two full 1 fps samples (~2s).
Whether a botched slide transition or a generation artifact, it reads as broken on a paid asset.
(3) At ~14s the gesturing hand-cluster in the party scene shows warped, tangled fingers on zoom.
Also noting: the visible watermark smear (gate above) and the 720×1280 resolution, below the
1080×1920 that the direction and `creative-generation.md` §7 specify. All fixable in the final cut
— the file says ROUGH — but as submitted the gate fails.

### §6.3 / creative-generation §4 — anyone who could read as under 18
`escalate` — Scene 2 (~4–8s): a young woman in a tank top at a wooden desk in a **library, with an
open textbook and a spiral notebook**. Her face alone reads plausibly 19–23, but the rule is "no
exceptions, no ambiguity," and the schoolwork staging actively invites a student read that the
bedroom/office/party scenes do not. Not a clear violation; not unambiguous either. Owner call —
regenerating that clip in a non-academic setting (café, hostel common room, PG balcony) removes
the ambiguity entirely.

### Men in frame
`fail` — `video-direction.md` is explicit: "Multiple women. **No man in frame at any point.**" The
party scene breaks it: at ~18–20s several men are clearly visible in the mid-background (light
kurtas, left and center-left — confirmed on zoom in both the walking shots). They are synthetic
and blurred, so this is not a §6.1 real-photo hit, but it is a hard rule of this asset's own
brief. The clip needs regenerating or reframing.

### creative-generation §1 — POV / lookbook (who is the object of the frame?)
`escalate` — Scenes 1–3 hold the documentary frame the direction demands: each woman is absorbed
in her phone, her frustration, her own moment; nobody addresses the lens. The closing party scene
is the problem: four styled, glamorous women in silk sarees, and the final shots (~19–20s) have
them **walking abreast toward the camera** — compositionally the lookbook failure the direction
itself names. They are mostly absorbed in each other, which is the mitigation the direction
allows, but §1 as written is categorical ("no woman as the object of the frame — none"), and a
closing tableau of styled desirable women is exactly the composition §1 traces the 98/2 male-lead
split to. Given the recorded tension between the categorical rule and the documentary-frame
interpretation, this is the app owner's call, not a quiet edit.

### Luxury / provider signifiers (§1 visual)
`pass` — No cars, cash, resorts, gifts, branded goods, or giver/receiver staging in any frame.
Jewellery is ordinary (thin chains, small hoops, bangles), settings are a modest bedroom, a
library, an ordinary office, and a marigold-and-string-lights function — festive, not luxe.
Nothing implies anyone pays for her lifestyle.

### Bride / groom / wedding-couple read in the party scene
`pass` — No bride, no groom, no couple staged anywhere. The venue (marigold garlands, string
lights, decorated gate) reads wedding-adjacent, but the four women read unambiguously as friends
at a function, and the cream saree does not read bridal in Indian context. Noting the venue read
only because a wedding association sits oddly under "Date mat karo" — a judgment call, not a
violation.

### Asset 1 overall
`fail` — Two hard fails: men in the party frames against the brief's own "no man in frame at any
point," and the craft/§6.2 glitch set (irisless white-eye flash at ~2s, the 11–13s duplicated
split-frame, warped hands at ~14s, visible watermark smear, 720p). Two escalations for the app
owner: the library scene's under-18 ambiguity, and the closing walking-abreast tableau against the
categorical POV rule. All the visual issues are regenerate/re-edit fixes to specific clips — the
structure, the silent-cut decision, and the copy do not need to change.

### Owner override — 2026-08-29 (asset 1 only)

The app owner reviewed the verdict above in session on 2026-08-29 and directed that the
ad ship as-is. Per compliance.md's own preamble, a tripped rule "is a decision for the
app owner" — this is that decision, recorded the way d68ccb2 recorded the Grok-plate
override rather than by rewriting the verdict.

**What was overridden, specifically:**
- `fail` men in frame (party-scene background, ~18-20s) — a constraint from the app
  owner's own brief, waived by him.
- `fail` AI glitches / craft (§6.2): whited-out eyes ~2s, split-frame 11-13s, warped
  fingers ~14s, the blurred watermark remnant bottom-right, 720p under the 1080p spec.
- `escalate` under-18 read (§6.3): the library scene's student staging on a face the
  reviewer put at 19-23 — resolved by the owner as acceptable.
- `escalate` POV rule (creative-generation.md §1): the closing walk-toward-camera
  tableau — resolved by the owner as acceptable.

**What was NOT overridden and still stands:** Meta's own ad review judges the same
surface independently and this override binds nothing there; the synthetic-media
disclosure question for Meta remains unchecked; the male-mix kill number (>30% week-1
male leads pauses both ad sets) stays in force as the empirical check on the POV risk.

Effective gate state after override: `pass` (by owner decision, scope: this asset,
this campaign only — the verdict above is untouched and remains citable).

*Reviewer's note on scope:* this override was recorded against the Meta cut before the
Snap cut below was reviewed. Nothing in it covers `STITCH-v1`, whose failures are
different in kind; that asset's verdict is a fresh decision.

---

## Asset 2 — `energy-kahan-jaati-hai-STITCH-v1.mp4` (Snap cut)

Scenes: (1) woman on bed at night, cottage-style room, "Ghosting." / "Fake profiles."; (2) woman
in a large library, magenta wrap blouse, "Cheating." / "Teen hafte…"; (3) woman at a loft office
desk in a strapless tube top, "Ab samajh aaya…"; (4) three women in silk sarees at a
marigold-and-string-lights function with buffet, "Date mat karo…" then `Apply karo` + `riteangle`.

### §6.2 audio
`pass` — Same music bed (identical volume statistics: mean −15.7 dB, max −2.3 dB). VAD-filtered
Whisper: **zero** speech segments. No testimony, no speech in any language. Same music-licensing
caveat as asset 1.

### §6.2 imagery — AI watermark
`pass` — Bottom-right corner crops at 2s, 6s, 11s, 16s, 19s are all clean. No watermark and no
blur patch anywhere in this cut.

### §6.2 imagery — AI glitches / craft
`pass` (with notes) — No split-frame defects, no eye whiteouts, no warped hands or melted
jewellery in any sampled frame; transitions are clean hard cuts. Notes: the office woman's
front-face (~9–11s) and profile (~13s) read slightly differently — plausibly the same person in
profile, but worth one deliberate per-face look per direction note 7; and the file is 720×1280
against the 1080×1920 spec, same as asset 1.

### §6.2 — "Indian models, Indian-context-appropriate"
`fail` — Compliance §6.2 carries Sree's Aug 21 note: the generated creative "needs to look clean
and Indian-context-appropriate," and `creative-generation.md` §4 makes "Indian models,
Indian-context setting" an always-specify. Three of four scenes read Western, not Indian: the
bedroom is a Western cottage room, the library is a US-style university reading room, the office
is a Western loft, and the bedroom woman's read is ethnically ambiguous. Only the party scene is
Indian-context. Judged against the rendered asset, as the rule is written.

### Garment lettering — "ATHLETIC CLUB 1994" (office scene, ~9–14s)
`fail` — Judged against the actual rule text, this hits two clauses. `creative-generation.md` §4's
never-generate list ends with "**invented text anywhere in the frame**" — the strapless tube top
carries legible invented collegiate lettering across the chest for the full scene. And §3's
wardrobe clause specifies "plain, contemporary, **unbranded**" — a named pseudo-brand garment is
not unbranded. The lettering is clean, not garbled, but garbled-vs-clean is not the test the rule
sets. The strapless-tube-top-as-office-wardrobe question is a separate concern and folds into the
POV gate below rather than standing alone.

### §6.3 / under-18 read
`pass` — All four women read unambiguously adult. The library woman (red lip, silk wrap blouse)
reads late 20s despite the textbooks; bedroom, office, and party women all read mid-20s or older.
This cut does not have asset 1's ambiguity.

### Men in frame
`fail` — Two scenes, not one. Library (~3–8s): at least three men clearly visible seated at
background tables, blurred but unambiguously male, present for the full scene (confirmed on zoom).
Party (~14–20s): a man in a grey suit at frame-left plus further male guests behind the buffet.
`video-direction.md`: "No man in frame at any point." Synthetic and background, so not a §6.1
real-photo hit — but a hard rule of the brief, broken twice.

### creative-generation §1 — POV / lookbook / midriff
`escalate` — Two parts, judged separately against the rule text. **The saree midriff is not a
violation:** §4's negative list bans "lingerie or slip-dress framing, cropped bodies" and "a woman
posed as an object of desire" — a saree worn normally shows midriff, that is ordinary Indian
dress, and the rule text does not reach it. **The framing is the real question:** the closing
scene is three glamorous, heavily styled women (silk sarees, stacked gold bangles, jhumkas, a
maang tikka) in progressively tighter close-up, ending nearly frame-filling at ~19–20s. They are
absorbed in each other — laughing together, hands over mouths, nobody addressing the lens — which
satisfies the documentary-frame interpretation. But the styling intensity plus the tube-top office
scene make this cut noticeably more "women as the thing being looked at" than the Meta cut, and §1
as written is categorical. Same owner decision as asset 1, with more weight on this cut.

### Luxury / provider signifiers (§1 visual)
`pass` — No cars, cash, gifting, or giver/receiver staging. The buffet with chafing dishes is
ordinary event catering. The gold jewellery is heavy but festive-context-normal, worn rather than
"presented as display."

### Bride / groom / wedding-couple read
`pass` (with a note) — No couple, no groom. The center woman wears a **maang tikka**, a
bridal-leaning ornament, in a maroon silk saree at a decorated function — a viewer could read her
as bride-adjacent, but three friends laughing together does not read as a wedding-couple tableau.
Swapping the maang tikka out would remove the residual read.

### Asset 2 overall
`fail` — Three hard fails: men in frame in two scenes against the brief's "no man in frame at any
point"; the "ATHLETIC CLUB 1994" invented/branded garment text against §4 and the wardrobe clause;
and three of four scenes not Indian-context-appropriate per §6.2. One escalation: the glam-styled
closing close-up plus tube-top office wardrobe against the categorical POV rule. Craft and audio
are clean — the failures are all generation-time choices, fixable by regenerating the affected
clips. The asset-1 owner override does not extend here.

---

## Copy gates (identical copy runs with both cuts)

### §1 — money/provider framing
`pass` — Nothing in the primary text, headline, or description implies money, luxury, being kept,
or a giver/receiver pair. "Riteangle har aadmi ko verify karta hai" frames verification as safety,
which is the permitted anti-fraud framing.

### §2 — purchase language
`pass` — No purchase, subscription, or credits implication. "Apply karo" is a qualification frame,
not a purchase frame.

### §4 — "high-earning" ban
`pass` — Absent. The verification claim uses the anti-fraud "verify karta hai" shape, not a
membership-quality-as-wealth claim.

### §5 — numeric verdicts on people
`pass` — No rankings, scores, or percentile claims anywhere.

### §7 — tone
`pass` — No hype, no urgency, no jargon. The drain-list is lived-feeling language; "Date mat karo.
Bas milo, aur jiyo." is the flip, stated flat.

### Truth of "Apply karo — sirf 18+"
`pass` — The funnel behind the CTA carries a real qualification step: the instant form captures
contact details and the `/get/w-apply` page gates the install link on a genuine 18+ age-band
declaration. "Sirf 18+" is literally true, and "apply" describes a flow where an eligibility
criterion actually exists (argued stage-by-stage in `brief.md`).

### §6.4 — banned-vocabulary gate
`pass` — with a recorded gap. Manual scan of all copy (ad + on-screen type in both cuts) finds no
compensated-dating vocabulary in English, Hindi, or romanised Hindi (no kharcha / paisa / ameer /
bill framings). The automated gate itself lives in the app codebase, is English-only, and was not
invocable from this repo in this session — open question
`q-2026-08-29-pocket-dating-coach-s-scripts-check-banned-strings-sh`; this manual scan does not
substitute for running it before ship.

## Not on the checklist, flagged anyway

1. **"Teen hafte ki texting" is a Meta/Snap review hazard.** In romanised Hindi "teen" = three,
   but an English-reading human or automated reviewer sees the word **"Teen"** next to
   **"texting"** in a dating ad that also says "sirf 18+". That juxtaposition is exactly what
   minor-safety classifiers key on. Consider "3 hafte ki texting" — same meaning, zero misread.
2. **Both videos add a "Cheating." beat** (~5–6s) that is in neither the ad copy nor
   `video-direction.md`'s beat table (verified against the table: Ghosting / Fake profiles / Teen
   hafte / the turn / the flip). It targets no named competitor, so it clears the platform-policy
   boundary the direction draws, but it should be a deliberate addition, not drift.
3. **Dark palette, no stated reason.** The night scenes in both cuts; `creative-generation.md` §5
   treats cream as the bought differentiator and asks dark creative to carry a stated reason. None
   is recorded in this folder.
4. **Native-speaker pass on the Hinglish lines is still listed as open** in `video-direction.md`
   ("draft — needs a native-speaker pass") — confirm it happened before spend.
5. **Wordmark check:** `riteangle` pill is present in the CTA scenes of both cuts, lowercase,
   correct spelling, pink "angle" — consistent with the brand mark. Typeface not verifiable from
   pixels; confirm Gabarito in the edit project.
6. **Platform synthetic-media disclosure is unchecked for both.** The people in these assets are
   synthetic; the §6.2 scope note itself records that Meta's — and for asset 2, Snap's — own
   AI-disclosure and dating-category rules bind independently of this file and override it.
   Confirm the ad-level disclosure toggle before spend. The asset-1 owner override explicitly
   left this standing.

---

## Overall

- **Asset 1** (`ROUGH-v3`, Meta): `fail` — men in the party frames; the craft/§6.2 glitch set
  (white-eye flash, 11–13s split-frame, warped hands, watermark smear, 720p); escalations on the
  library under-18 ambiguity and the closing walking-abreast tableau vs the categorical POV rule.
  An owner override recorded above sets the effective gate state to ship for this asset and
  campaign; the verdict itself stands.
- **Asset 2** (`STITCH-v1`, Snap): `fail` — men in frame in two scenes; "ATHLETIC CLUB 1994"
  invented garment text; three of four scenes not Indian-context-appropriate. Escalation: glam
  closing close-up plus tube-top wardrobe vs the POV rule. (Saree midriff judged **not** a
  violation against the rule text; under-18 gate passes on this cut.) Not covered by the asset-1
  override.

Copy is clean across every gate for both. Every visual failure is clip-local and
regenerate/re-edit-grade; the escalations are the app owner's decisions, per compliance.md's own
instruction that a tripped rule is never a quiet edit.

### Owner override — 2026-08-29 (asset 2, the STITCH/Snap cut)

The app owner reviewed asset 2's `fail` verdict in session on 2026-08-29 and directed
deployment, in as many words: "Let's do a manual override on this... the ad is safe.
Let's go ahead and deploy it... Go for snap deploy now." Recorded the way d68ccb2
recorded the Grok-plate override — the reviewer's verdict above stands unedited; this
section is the decision that outranks it.

**What was overridden, specifically:**
- `fail` men in frame (library background; party scene) — waived explicitly: "Main
  showing is not a problem." [transcribed from voice; read as "men showing"]
- `fail` invented garment text ("ATHLETIC CLUB 1994", office scene) — waived as part
  of the blanket deploy decision.
- `fail` Western-reading settings (three of four scenes) — waived likewise.
- `escalate` glam closing close-up + tube-top wardrobe vs creative-generation.md §1 —
  waived likewise; the app owner had already ruled wardrobe his call twice this week.
- Copy flag ("Teen hafte" / English "Teen" misread): considered and kept as-is — his
  judgment that platform text classifiers will read the Hinglish context correctly.

**Not overridden, because they were not tripped:** asset 2's under-18, watermark,
glitch and audio gates all passed on their own.

Effective gate state after override: `pass` (by owner decision; scope: asset 2, this
deployment). Platform-side review is Snap's own and this override binds nothing there.

---

## Watermark clearance — `asset-a.mp4`, 2026-09-05

`watermark-check: pass`

Run for `rec-2026-09-05-moveon-getw-w1830-snap` (traffic ad into `/get/w`), because
`snap-push` refuses a folder with no recorded clearance and this folder had none.

**Method.** Every frame at 1 fps across the full 20.0s (20 frames) through
`watermark.scan`'s bottom-right corner-contrast detector, plus zoomed corner crops of
the four scenes at 4s, 6s, 11s and 19s covering the x420–720 / y1020–1280 region the
`§6.2 imagery` gate above names.

**Result.** No AI-tool watermark, no glyph, and **no smear rectangle** anywhere. Sixteen
of twenty frames scored a flat 0. The four that scored above it all resolve to real
scene content on inspection: 4s = the lit phone screen on the bedspread (58); 9–13s =
the sunlit arm and orange top against the black chair back in the office scene
(99–114). The library desk at 6s and the saree fabric at 19s are flat, clean, and would
show a smear instantly if one were there.

**Read this before trusting the `§6.2 imagery` and `§6.3 glitch` sections above: they
describe a file that is no longer in this folder.** Those sections QA'd
`energy-kahan-jaati-hai-ROUGH-v3.mp4` on 2026-08-29 and recorded a watermark smeared
over rather than cropped, plus three craft defects. `asset-a.mp4` is dated 2026-09-01,
is a later re-cut, and **all four are absent from it** — checked frame by frame at the
timestamps those sections name:

| Recorded defect (ROUGH-v3, 2026-08-29) | `asset-a.mp4`, checked 2026-09-05 |
|---|---|
| Stationary blurred-out rectangle, bottom-right, every scene | absent — corner clean in all four scenes |
| ~1.5–2.2s whited-out irisless eyes | absent — eyes closed and normally rendered at 1.8s |
| ~11–13s stacked duplicate frame with a hard horizontal seam | absent — single clean office frame at 11.5s |
| ~14s warped, tangled finger cluster | absent — hands clean at 14.2s |

Still true of this cut and NOT re-litigated here: 720×1280, under the 1080×1920 that
`creative-generation.md` §7 specifies. The 2026-08-29 owner override above covers this
asset's remaining flagged items.

**What this clearance does not cover.** The watermark gate only. The scan is a corner
detector — it answers "is there a generation mark in the corner," not "is this asset
good." Nothing here revisits the owner override, and nothing here is a platform review.
