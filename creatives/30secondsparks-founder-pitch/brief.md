# 30SecondSparks — founder pitch

Not an ad. A contest entry: YourStory TechSparks' `#30SecondSparks`, a Reel pitching the startup in
30 seconds or less, posted on the founder's own profile tagging `@yourstorytechsparks`. Entries
close 2 Oct 2026, 11:59 PM IST. Prize is event passes to TechSparks 2026 (13–15 Oct, Bengaluru).
Logged in `pdc-investor-agent` as `ys-30secondsparks`.

**Audience is a jury, not a customer.** That is the single fact that shaped every choice here. The
register is English and explanatory rather than the Hinglish consumer register of the `moveon-*`
assets, the founder appears on camera, and the film spends five of its thirty seconds on the actual
product because the two rival entries read on 7 Sep spend none.

## Source

- `_source/founder-raw.mp4` — 65s phone take, 1080x1920 (stored 1920x1080 with rotation=90),
  gitignored at 124MB and re-derivable from the founder's phone. **Front camera, so mirrored**;
  `hflip` is applied in the build and without it the t-shirt lettering reads backwards.
- `_source/transcript-words.json` — word-level transcript (mlx_whisper large-v3-turbo). The nine
  spans in `build.py` were chosen off it, every boundary in a gap between words.
- `_source/app-*.png` — Android emulator captures of 1.0.9 (1108), built from source on 7 Sep
  rather than using the installed 1.0.8, because `mobile/lib` had changed the day before to remove
  a term that had drawn an App Store rejection. The status bar is cropped out in the build.
- `../moveon-swagger-video/source.mp4` — the clean plate, not `asset-a.mp4`. The finished asset has
  Hinglish captions, tagline and wordmark burnt in, which cannot sit under an English pitch.

## Still missing

- A sharper book cover. Amazon serves this ASIN at 333x500 and no larger, so the cover is seated
  at 460px wide rather than upscaled. The founder's original artwork would allow a bigger card.
- Signed-in app screens (AI conversation view, ranked shortlist, "Self declared" tag). The
  pre-auth screens stand in. This is the weakest substitution in the film.

## Decisions worth not re-arguing

- **The opening is the founder, then a typed profile card — not generated men.** The first cut
  opened on three typed cream cards and read as a slideshow, with no person on screen until 11s.
  Generated Indian portraits were prompted and then dropped by the app owner on quality grounds;
  the card is better anyway, because it shows the object the lie lives in and carries no synthetic-
  person surface at all.
- **The four-woman collage is built from `buildyourself-lead-w1830/_source/frames/`, not from the
  finished carousel slides.** The slides carry burnt-in Hinglish captions. `sourcing.md` in that
  carousel maps each slide to its origin frame, which is how the clean plates were found.

- **Tagline is "No Swipes. Ever.", not "Verified, not vibes."** The founder's call on 7 Sep, with
  the intent of retiring the old line generally. **`rules/creative-style.md` §Taglines has NOT been
  updated** — if the retirement is a standing decision and not a one-asset choice, that file is
  where it has to land, or the next asset will reach for the old line.
- **"No Swipes. Ever." was verified before use**, not assumed. `SwipeCard.svelte` exists in
  `pocket-dating-coach` but is never mounted anywhere, and the only other hit is an e2e test whose
  body is `expect(true).toBe(true)`. The live Discover feed uses buttons — Admire, Notice me, like,
  `Next →`. The claim is true of the shipped product.
- **"and earns a lot of money" was cut from the take** under `compliance.md` rule #1. Money is never
  an attraction signal, and that holds even when the line is quoting a lie.
- **Traction figures** are from production on 7 Sep, filtered `is_seed=false, is_provisional=false`.
  See `pocket-dating-coach/docs/investor-metrics-proposal.md` for why the message count must not be
  restated as conversations: 1,724 of 3,299 messages are the product's own sends.

## A clone cannot rebuild this

`creatives/*/_source/*` is ignored repo-wide (root `.gitignore:37`), so none of the sources below
are committed — the same arrangement as `girlboss-moodboard-w1830`. What is committed is the
rendered `asset-a.mp4`, this documentation, and `build.py`.

On a fresh clone the build still runs, but every missing source falls back to a typed cream card
and the film comes out as a slideshow with the right words in it. That is deliberate — it fails
visibly rather than silently — but it means **the sources have to be recovered before any re-cut**:
the camera original from the founder's phone, the app captures from an emulator, the book cover
from the Amazon listing, and the music bed from the Flow Music session.

## Build

```bash
uv run python creatives/30secondsparks-founder-pitch/build.py
# -> asset-a.mp4, 1080x1920, 28.87s
```

Captions are strings in `BEATS`. A new line costs an edit and a re-run, never a reshoot.
