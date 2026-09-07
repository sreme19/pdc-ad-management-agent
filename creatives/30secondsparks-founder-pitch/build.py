"""30SecondSparks founder pitch — cut, typeset and assemble.

    uv run python creatives/30secondsparks-founder-pitch/build.py

Sibling of moveon-swagger-video/typeset_video.py and follows the same rule: the
plate carries no words, every glyph is set here in real Gabarito, so a new hook
costs a string edit rather than a reshoot (rules/creative-generation.md §2).

What is different from that one: the picture here is not a single generated
plate. It is a 65-second phone take cut down to nine pieces, intercut with
generated portraits, one existing plate, real app screens and a book cover. So
this script owns the CUT as well as the type.

Pipeline, in order:
  1. VO — pull the nine chosen spans out of the camera original, concatenate,
     nudge to 1.05x so 30.4s of speech lands under the 30s cap.
  2. Picture — build one 1080x1920 clip per beat, from whichever source that
     beat uses. Missing sources fall back to a typed cream card, so the film
     always assembles end to end and a gap is visible rather than fatal.
  3. Type — one transparent PNG per beat, composited over its clip.
  4. Mix — VO only for now. Music is added in a later pass, deliberately: per
     §7b the finished mix is never loudness-normalised, so the bed has to be
     cut to picture that already exists.

The camera original is a front-camera recording: it is MIRRORED, and the
t-shirt lettering reads backwards until hflip is applied. It also carries a
rotation=90 display matrix, which ffmpeg honours on decode, so the working
frame is 1080x1920 with no manual transpose.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from ad_management_agent.watermark import strip_flow_watermark  # noqa: E402

D = Path(__file__).parent
SRC = D / "_source"
BUILD = D / "_build"
DEST = D / "asset-a.mp4"

FONT = "/Users/performek5/Desktop/Code/pocket-dating-coach/mobile/assets/fonts/Gabarito.ttf"

# rules/creative-style.md visual identity
INK = "#1B1020"
PINK = "#FF3B6B"
CREAM = (255, 243, 240)
CREAM_HEX = "#FFF3F0"
WHITE = "#FFFFFF"

OUT = (1080, 1920)
FPS = 30
MARGIN = 84
SAFE_TOP, SAFE_BOTTOM = 192, 1632  # §7 — platform chrome sits outside these

SPEED = 1.05  # 30.4s of speech -> 28.9s, leaving a beat of air under the 30s cap
SPLICE_XFADE = 0.060   # crossfade at each VO join; hard splices sounded choppy
TYPE_FADE = 0.22       # type eases in rather than snapping on

FOUNDER = SRC / "founder-raw.mp4"
MOVEON = Path(
    "/Users/performek5/Desktop/Code/pdc-ad-management-agent/creatives"
    "/moveon-swagger-video/source.mp4"
)
BOOK = SRC / "book-cover.jpg"

# Flow Music, generated 2026-09-07 on the founder's own account, take 1 of two.
# A single ~2:32 song, so the bed is 28.5 CONTIGUOUS seconds of it — not a short
# clip looped, which rules/creative-generation.md §7b forbids because repetition
# reads as interruptive however clean the crossfades are.
BED = SRC / "bed-take1.m4a"

# Where in the song the bed starts. Chosen off its energy envelope, not by ear-
# balling the waveform: the track is near-silent to 2s, sparse from 2-14s, and
# opens out from 16s. Starting at 1.5s therefore puts the sparse section under
# the problem beats and lands the lift within a second of "I built Riteangle".
BED_IN = 1.5
BED_FADE_IN, BED_FADE_OUT = 0.6, 1.8

# Measured, not guessed. The raw VO is -20.5 LUFS and the bed window is -17.8 —
# the music is LOUDER than the voice before any correction. These two gains put
# the voice around -18 and the bed around -29, a ~11 LU gap that keeps the bed
# audible without ever competing.
#
# Each stem is set to its own target and the SUM is only peak-limited, never
# loudness-normalised (§7b): normalising the finished mix once flattened an
# intentional 11 dB quiet-to-loud arc down to 1.1 dB.
VO_GAIN_DB = 4.7
BED_GAIN_DB = -8.8
TRUE_PEAK_CEILING = -1.5
# alimiter's ceiling is SAMPLE peak and inter-sample peaks ride above it, so the
# ceiling is set this far below the true-peak target. `level=disabled` matters
# just as much: alimiter auto-levels its output by DEFAULT, which silently
# re-normalises the sum. Lowering the ceiling made the mix LOUDER (-16.6 to
# -15.7 LUFS) until that was switched off — the §7b "never normalise the
# finished mix" rule was being broken by a filter default, not by a choice.
INTERSAMPLE_HEADROOM = 0.15

# ── the cut ──────────────────────────────────────────────────────────────────
# Spans chosen off the word-level transcript in _source/transcript-words.json.
# Every boundary sits in a gap between words, never inside one.
VO_SPANS = [
    (4.00, 8.98),   # "a guy who's claiming that he's a founder, six foot, well travelled"
    (11.22, 14.40),  # "there is nobody to check if that is true or not"
    (21.98, 25.00),  # "catfishing, ghosting, situationships"
    (25.52, 28.54),  # "I am Sree. I built Riteangle"
    (29.14, 33.42),  # "working on this problem since 2019 when I wrote a book about it"
    (34.28, 37.20),  # "this app is primarily focused for women in India"
    (38.88, 41.00),  # "who are tired of being lied to"
    (51.26, 56.16),  # "every man ... back it up with documents, photos or video"
    (61.96, 63.90),  # "Riteangle. No swipes. Ever."
]

# Dropped on purpose, recorded so the decision is not re-argued:
#   8.98-10.84  "and earns a lot of money"  — compliance.md rule #1, money is
#               never an attraction signal, not even as an example of a lie.
#   14.44-17.26 "and that's the problem in the dating world today" — the bridge
#               survives as type; the words cost 2.8s the cut does not have.
#   40.92-51.26 "we have created an AI system that ... speak on behalf of her" —
#               tangled on the take and 6.4s long. Type says it cleanly instead.
#   56.16-59.50 "so we are still very new, it's pre-revenue" — moved to type.

# ── the beats ────────────────────────────────────────────────────────────────
# One entry per picture change. `src` picks the footage; `lines` is the type.
# Times are on the FINISHED timeline (after the VO concat, before the speed-up).
BEATS = [
    # Opens on the founder, not on a card. The first cut of this film opened on
    # three typed cream cards and read as a slideshow: nothing to look at for
    # five seconds, and no person until 11s.
    dict(t=(0.00, 2.62), src=("founder", 4.00), lines=[]),
    # Then his claims fill in on a profile card, one field at a time, and the
    # card is stamped. Generated portraits were the first plan and were dropped:
    # three handsome men read as a dating ad, and the card shows the object the
    # lie actually lives in. It also carries no synthetic-person surface at all.
    dict(t=(2.62, 3.96), src=("profile", 2, False), lines=[]),
    dict(t=(3.96, 4.98), src=("profile", 3, False), lines=[]),
    dict(t=(4.98, 6.40), src=("profile", 3, True), lines=[]),
    dict(t=(6.40, 8.16), src=("cream",), lines=[("That's the problem.", INK)]),
    dict(t=(8.16, 11.18), src=("collage",),
         lines=[("Catfishing.", WHITE), ("Ghosting.", WHITE), ("Situationships.", PINK)]),
    dict(t=(11.18, 14.20), src=("founder", 25.52), lines=[]),
    dict(t=(14.20, 18.48), src=("book",), lines=[("Writing about this", INK),
                                                 ("since 2019.", INK)]),
    dict(t=(18.48, 21.40), src=("moveon",), lines=[("For women in India", INK)]),
    dict(t=(21.40, 23.52), src=("founder", 38.88), lines=[]),
    # The third element is where the card window starts in the 1080x1920
    # screenshot. Chosen per beat so the window always frames a whole element:
    # a blanket scroll sliced a headline in half at the card's edge.
    # Both app beats are signed-in screens, captured 2026-09-07 on 1.0.9. The
    # pre-auth screens they replace only DESCRIBED verification; "Earn your
    # profile" shows the gate itself, in the product's own words - "prove you're
    # real", "prove you're solid" - directly under the line about backing claims
    # up. The AI Bestie conversation and the "Self declared" tag would be better
    # still and are NOT here: both sit behind identity verification, which needs
    # a real selfie on a real account.
    # Type says what THIS screen proves, not what we wish it proved. It shows
    # the matcher naming who you will and will not see, so it carries "no
    # swiping" - which the end card then lands. The earlier draft put "Her AI
    # does the talking on her behalf" here, over a screen showing a MAN's
    # archetype card: the claim and the picture disagreed, and the picture wins
    # with anyone who reads it. That claim now lives only in the post caption,
    # because no screen in this build supports it.
    dict(t=(23.52, 26.00), src=("app", "app-match-logic.png", 300),
         lines=[("Nobody swipes.", INK), ("The matcher decides.", INK)]),
    dict(t=(26.00, 28.42), src=("app", "app-earn-profile.png", 90),
         lines=[("He has to prove it.", PINK)]),
    dict(t=(28.42, 30.40), src=("endcard",), lines=[]),
]

# Small persistent strip under the app beats. Every figure verified against
# production on 2026-09-07, filtered is_seed=false / is_provisional=false, and
# messages counted whole rather than only the human ones — see
# pocket-dating-coach/docs/investor-metrics-proposal.md.
STAT_STRIP = "170 members · 573 matches · 3,000 messages · pre-revenue"
STAT_BEATS = {10, 11}

CAPTION_SIZE = 82
LINE_GAP = 14

# The app screen sits in this window, on cream, with type on clean ground above.
CARD_W, CARD_H = 760, 930
CARD_Y = 640

END_TAGLINE = "No Swipes. Ever."

# Amazon serves this ASIN's cover at 333x500 and no larger, so it is seated
# small rather than upscaled 2.3x into mush. A sharper original would allow more.
BOOK_W = 460

# The unverified profile that opens the film.
PROFILE_NAME = "Rohan, 32"
PROFILE_FIELDS = ["Founder", "6'0\"", "Travels constantly"]


# The four women from the BUILD-YOURSELF carousel, in the states the jargon
# names. Taken from the ORIGINAL frames, not the finished carousel slides: those
# carry burnt-in Hinglish captions ("Phir se ghost kar diya?") which cannot sit
# under an English pitch. sourcing.md maps each slide to the frame it came from.
FRAMES = Path("/Users/performek5/Desktop/Code/pdc-ad-management-agent/creatives"
              "/buildyourself-lead-w1830/_source/frames")
COLLAGE = [
    FRAMES / "Woman_sitting_on_bedroom_floor_202608292351.jpeg",   # A — ghosted
    FRAMES / "Woman_reading_laptop_at_cafe_202608292356.jpeg",     # B — catfished
    FRAMES / "Woman_sitting_alone_at_table_202608292351.jpeg",     # C — alone
    # Cell 4 comes from a different creative on purpose. The obvious pick,
    # `Tired_woman_looking_at_phone`, is the SAME model in the SAME bedroom as
    # cell 1 — the collage read as one woman twice. The rest of that frame set
    # holds only three distinct women (the cafe woman appears as both the laptop
    # and the covering-mouth shots), so the fourth had to come from elsewhere.
    Path("/Users/performek5/Desktop/Code/pdc-ad-management-agent/creatives"
         "/moveon-properly-w2530/clean-c5.jpg"),                   # D — a fourth face
]
GUTTER = 10

# Android status bar on the 1080x1920 emulator captures; every app beat starts
# at or below it so the emulator clock never appears.
STATUS_BAR_PX = 66


def run(args, **kw):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw)


def face(size, weight="ExtraBold"):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def fit(dr, text, size, weight, max_w):
    while size > 24:
        f = face(size, weight)
        if dr.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return face(size, weight)


def wordmark(dr, x, y, size=64):
    """'rite' in ink, 'angle' in pink — two draws so the pun is exact."""
    f = face(size, "Bold")
    dr.text((x, y), "rite", font=f, fill=INK)
    dr.text((x + dr.textlength("rite", font=f), y), "angle", font=f, fill=PINK)


def type_png(beat, index, path):
    """One transparent full-frame type layer for a beat."""
    im = Image.new("RGBA", OUT, (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    max_w = OUT[0] - 2 * MARGIN
    lines = beat["lines"]

    if lines:
        fonts = [fit(dr, t, CAPTION_SIZE, "ExtraBold", max_w) for t, _ in lines]
        heights = [f.getbbox("Ag")[3] for f in fonts]
        block = sum(heights) + LINE_GAP * (len(lines) - 1)
        # Where the type can go depends on what else is in the frame.
        kind = beat["src"][0]
        if kind in ("cream", "endcard", "collage"):
            y = (OUT[1] - block) // 2
        elif kind == "app":
            y = CARD_Y - block - 100         # clean cream above the card
        else:
            y = SAFE_BOTTOM - block - 150
        for (text, colour), f, h in zip(lines, fonts, heights):
            dr.text((MARGIN, y), text, font=f, fill=colour)
            y += h + LINE_GAP

    if index in STAT_BEATS:
        f = fit(dr, STAT_STRIP, 38, "Bold", max_w)
        dr.text((MARGIN, CARD_Y + CARD_H + 28), STAT_STRIP, font=f, fill=INK)

    if beat["src"][0] == "endcard":
        wordmark(dr, MARGIN, OUT[1] // 2 - 200, size=104)
        f = fit(dr, END_TAGLINE, 92, "ExtraBold", max_w)
        dr.text((MARGIN, OUT[1] // 2 - 40), END_TAGLINE, font=f, fill=INK)

    if beat["src"][0] in ("founder", "moveon"):
        # Small mark on footage beats so the brand is present without competing.
        # Top, not bottom: ink on the dark olive shirt was invisible, and the
        # wall behind his head is the brightest part of the frame.
        wordmark(dr, MARGIN, SAFE_TOP + 18, size=46)

    im.save(path)
    return path


def profile_png(n_fields, stamped, path):
    """The unverified profile card: fields fill in, then it gets stamped.

    Deliberately a grey silhouette rather than a face. The point is that the
    claims have nothing behind them, and a photorealistic man would have made it
    a picture of a person instead of a picture of unverified assertions.
    """
    im = Image.new("RGB", OUT, CREAM)
    dr = ImageDraw.Draw(im)
    x0, x1 = 120, 960
    row_h = 118
    card_h = 270 + row_h * len(PROFILE_FIELDS)
    # Centred on the frame, and sized off the FULL field list so the card does
    # not grow as fields arrive — only the fields inside it appear.
    y0 = (OUT[1] - card_h) // 2 - 60
    dr.rounded_rectangle([x0, y0, x1, y0 + card_h], radius=32, fill="white")

    # avatar: a grey disc with no face in it
    av = 132
    dr.ellipse([x0 + 56, y0 + 52, x0 + 56 + av, y0 + 52 + av], fill="#E7DAD5")
    dr.ellipse([x0 + 96, y0 + 88, x0 + 96 + 52, y0 + 88 + 52], fill="#D6C4BD")
    dr.rounded_rectangle([x0 + 78, y0 + 148, x0 + 78 + 88, y0 + 190], radius=30, fill="#D6C4BD")

    f_name = face(62, "ExtraBold")
    dr.text((x0 + 232, y0 + 88), PROFILE_NAME, font=f_name, fill=INK)
    f_sub = face(34, "Bold")
    dr.text((x0 + 232, y0 + 158), "2.4 km away", font=f_sub, fill="#9B8A84")

    f_field = face(46, "Bold")
    f_tag = face(28, "Bold")
    y = y0 + 250
    for i, field in enumerate(PROFILE_FIELDS[:n_fields]):
        dr.text((x0 + 56, y), field, font=f_field, fill=INK)
        # every field carries its own little "nobody checked this" tag
        tw = dr.textlength("UNVERIFIED", font=f_tag)
        dr.rounded_rectangle([x1 - 76 - tw, y + 6, x1 - 40, y + 52], radius=22,
                             fill="#F3E7E2")
        dr.text((x1 - 58 - tw, y + 15), "UNVERIFIED", font=f_tag, fill="#9B8A84")
        y += row_h

    if stamped:
        # Below the card, not across it. Across it the band covered the third
        # claim, so the frame that makes the point hid a third of the evidence.
        f = fit(dr, "Nobody checks.", 96, "ExtraBold", OUT[0] - 2 * MARGIN)
        h = f.getbbox("Ag")[3]
        band_y = y0 + card_h + 46
        dr.rectangle([0, band_y, OUT[0], band_y + h + 76], fill=PINK)
        dr.text((MARGIN, band_y + 30), "Nobody checks.", font=f, fill="white")

    im.save(path)
    return path


def collage_png(path):
    """Four women, one plate, cream gutters. Darkened so type can sit over it.

    A single 2x2 rather than four cuts: the words name four different things and
    the point is that they happen at once, to different people, all the time.
    """
    im = Image.new("RGB", OUT, CREAM)
    cw = (OUT[0] - GUTTER) // 2
    ch = (OUT[1] - GUTTER) // 2
    for i, src in enumerate(COLLAGE):
        cell = Image.open(src).convert("RGB")
        # MANDATORY, not judgement (rules/creative-generation.md §7). These are
        # Flow exports and one of them carries the four-point "made with AI"
        # sparkle bottom-right — visible in the laptop frame, and exactly the
        # mark that reached a live Story Ad on 2026-08-30 because a QA note
        # asserted the stills were clean without zooming the corners.
        cell = strip_flow_watermark(cell)
        # cover-fit: scale to fill, then centre-crop
        scale = max(cw / cell.width, ch / cell.height)
        cell = cell.resize((round(cell.width * scale), round(cell.height * scale)),
                           Image.LANCZOS)
        left = (cell.width - cw) // 2
        top = (cell.height - ch) // 3      # bias up: keeps faces, drops floor
        cell = cell.crop((left, top, left + cw, top + ch))
        im.paste(cell, ((i % 2) * (cw + GUTTER), (i // 2) * (ch + GUTTER)))

    # Scrim, so white type reads over four different exposures rather than only
    # over the dark ones.
    scrim = Image.new("RGBA", OUT, (16, 8, 18, 120))
    im = Image.alpha_composite(im.convert("RGBA"), scrim).convert("RGB")
    im.save(path)
    return path


def cream_png(path, footage=False):
    """Ground for a typed beat. `footage` adds a bottom scrim instead."""
    im = Image.new("RGB", OUT, CREAM)
    im.save(path)
    return path


def vo_track():
    """Nine spans out of the camera original, concatenated, then nudged."""
    parts = []
    for i, (a, b) in enumerate(VO_SPANS):
        p = BUILD / f"vo{i}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b),
             "-i", str(FOUNDER), "-vn", "-ac", "2", "-ar", "48000", str(p)])
        parts.append(p)
    # Crossfaded, not butt-joined. Concatenating nine spans of continuous
    # speech with hard splices puts a step change in room tone and breath at
    # every join, and 30 seconds carrying eight of those sounds choppy however
    # clean the picture is. 45ms is long enough to hide the seam and short
    # enough that no syllable is lost.
    joined = BUILD / "vo-joined.wav"
    args = ["ffmpeg", "-v", "error", "-y"]
    for part in parts:
        args += ["-i", str(part)]
    chain, prev = [], "0:a"
    for i in range(1, len(parts)):
        label = f"x{i}"
        chain.append(f"[{prev}][{i}:a]acrossfade=d={SPLICE_XFADE}:c1=tri:c2=tri[{label}]")
        prev = label
    args += ["-filter_complex", ";".join(chain), "-map", f"[{prev}]", str(joined)]
    run(args)
    out = BUILD / "vo-final.wav"
    # atempo preserves pitch; 1.05 is well inside its clean range.
    run(["ffmpeg", "-v", "error", "-y", "-i", str(joined),
         "-af", f"atempo={SPEED},highpass=f=80,afftdn=nf=-24,alimiter=limit=0.89",
         str(out)])
    return out


def picture_clip(beat, index):
    """One 1080x1920 clip for a beat, from whatever source it names."""
    kind = beat["src"][0]
    dur = (beat["t"][1] - beat["t"][0]) / SPEED
    out = BUILD / f"pic{index:02d}.mp4"
    # -frames:v is the guarantee, not -t. zoompan's `d=` repeats each input
    # frame, so a looped still under -t ran to 137 seconds; capping the frame
    # count holds the length whatever a filter does downstream.
    nframes = max(1, round(dur * FPS))
    common = ["-r", str(FPS), "-frames:v", str(nframes), "-pix_fmt", "yuv420p",
              "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-an"]

    if kind == "founder":
        start = beat["src"][1]
        # Take SPEED x as much source and speed it to match, or his lips run 5%
        # behind the voice they belong to — visible on a talking head this size.
        # hflip undoes the front-camera mirror; the t-shirt reads backwards
        # without it.
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur * SPEED),
             "-i", str(FOUNDER), "-vf",
             f"hflip,setpts=PTS/{SPEED},"
             f"scale={OUT[0]}:{OUT[1]}:force_original_aspect_ratio=increase,"
             f"crop={OUT[0]}:{OUT[1]},setsar=1", *common, str(out)])
        return out

    if kind == "moveon" and MOVEON.exists():
        # Flow seated a near-square picture on white; cropdetect finds the real
        # frame so a later full-bleed export needs no code change here.
        run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-t", str(dur),
             "-i", str(MOVEON), "-vf",
             f"cropdetect=24:2:0,scale={OUT[0]}:{OUT[1]}:force_original_aspect_ratio=increase,"
             f"crop={OUT[0]}:{OUT[1]},setsar=1", *common, str(out)])
        return out

    if kind == "collage":
        ground = collage_png(BUILD / f"collage{index:02d}.png")
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(ground),
             "-vf", "setsar=1", *common, str(out)])
        return out

    if kind == "profile":
        n_fields, stamped = beat["src"][1], beat["src"][2]
        ground = profile_png(n_fields, stamped, BUILD / f"profile{index:02d}.png")
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(ground),
             "-vf", "setsar=1", *common, str(out)])
        return out

    if kind == "app":
        still = SRC / beat["src"][1]
        # Seated as a card on cream rather than full-bleed. Full-bleed put our
        # type straight on top of the app's own type and neither could be read;
        # the card also matches moveon-swagger-video's treatment. The crop
        # window travels down the screenshot over the beat, so a still reads as
        # someone scrolling rather than as a freeze.
        sw = CARD_W
        sh = round(1920 * sw / 1080)          # screenshot is itself 1080x1920
        # Start below the Android status bar. Leaving the emulator's clock,
        # wifi and battery in frame reads as a screenshot of a simulator, not
        # as the product.
        top = round(beat["src"][2] * sw / 1080)
        # A short travel, not the full height: running the crop to the bottom
        # sliced a headline in half at the card's edge, which reads as a crop
        # mistake rather than as scrolling.
        travel = min(70, max(0, sh - top - CARD_H))
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(still), "-vf",
             f"scale={sw}:{sh},"
             f"crop={sw}:{CARD_H}:0:'{top}+min({travel},t/{dur}*{travel})',"
             f"pad={OUT[0]}:{OUT[1]}:{(OUT[0]-sw)//2}:{CARD_Y}:color={CREAM_HEX},"
             "setsar=1", *common, str(out)])
        return out

    if kind == "book" and BOOK.exists():
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(dur),
             "-i", str(BOOK), "-vf",
             f"scale={BOOK_W}:-1,pad={OUT[0]}:{OUT[1]}:(ow-iw)/2:560:color={CREAM_HEX},setsar=1",
             *common, str(out)])
        return out

    # Fallback: a plain cream ground. Reached when a source has not landed yet,
    # so the film still assembles and the gap is visible instead of fatal.
    ground = cream_png(BUILD / f"ground{index:02d}.png")
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(dur),
         "-i", str(ground), "-vf", "setsar=1", *common, str(out)])
    return out


def main():
    BUILD.mkdir(exist_ok=True)
    if not FOUNDER.exists():
        sys.exit(f"missing founder take: {FOUNDER}")

    missing = [n for n, p in [("book cover", BOOK)] if not p.exists()]
    if missing:
        print("PLACEHOLDER cream cards standing in for: " + ", ".join(missing))

    vo = vo_track()
    vo_dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(vo)]).stdout.strip())
    # The crossfades take SPLICE_XFADE off every join, so the finished voice is
    # shorter than the beat table assumes. Scale the beats to what the audio
    # actually is rather than to what it was planned to be; otherwise picture
    # leads sound by a third of a second by the end, which lands on the
    # founder's own lips.
    nominal = BEATS[-1]["t"][1] / SPEED
    fit_scale = vo_dur / nominal
    print(f"VO: {vo_dur:.2f}s after {SPEED}x  (beats scaled x{fit_scale:.4f} to match)")
    for beat in BEATS:
        beat["t"] = (beat["t"][0] * fit_scale, beat["t"][1] * fit_scale)

    clips = []
    for i, beat in enumerate(BEATS):
        pic = picture_clip(beat, i)
        layer = type_png(beat, i, BUILD / f"type{i:02d}.png")
        comped = BUILD / f"beat{i:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(pic), "-loop", "1", "-i", str(layer),
             "-filter_complex",
             f"[1:v]fade=in:st=0:d={TYPE_FADE}:alpha=1[t];[0:v][t]overlay=0:0:format=auto:shortest=1[v]",
             "-map", "[v]", "-r", str(FPS), "-pix_fmt", "yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-an", str(comped)])
        clips.append(comped)
        print(f"  beat {i:02d}  {beat['src'][0]:8s}  {beat['t'][0]:5.2f}-{beat['t'][1]:5.2f}")

    lst = BUILD / "beats.txt"
    lst.write_text("".join(f"file '{c.name}'\n" for c in clips))
    picture = BUILD / "picture.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(picture)], cwd=BUILD)

    if BED.exists():
        # The bed is carved slightly at 2 kHz so the voice keeps its
        # intelligibility band, and the sum is limited rather than normalised.
        mix = (
            f"[1:a]volume={VO_GAIN_DB}dB[v];"
            f"[2:a]atrim=0:{vo_dur},asetpts=N/SR/TB,"
            f"afade=t=in:st=0:d={BED_FADE_IN},"
            f"afade=t=out:st={max(0, vo_dur - BED_FADE_OUT)}:d={BED_FADE_OUT},"
            f"highpass=f=60,equalizer=f=2000:t=q:w=1.2:g=-3,"
            f"volume={BED_GAIN_DB}dB[b];"
            f"[v][b]amix=inputs=2:duration=first:normalize=0,"
            f"alimiter=limit={10 ** ((TRUE_PEAK_CEILING - INTERSAMPLE_HEADROOM) / 20):.4f}"
            f":level=disabled[a]"
        )
        run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(vo),
             "-ss", str(BED_IN), "-i", str(BED),
             "-filter_complex", mix, "-map", "0:v", "-map", "[a]",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(DEST)])
    else:
        print("NO MUSIC BED — voice only")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(vo),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(DEST)])
    final = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                       "-of", "csv=p=0", str(DEST)]).stdout.strip())
    print(f"\n-> {DEST}  {final:.2f}s")
    if final > 30.0:
        print(f"   OVER the 30s cap by {final - 30:.2f}s — raise SPEED or drop a beat")


if __name__ == "__main__":
    main()
