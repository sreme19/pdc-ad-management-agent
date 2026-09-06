"""Thai type layer for MOVE-ON-PROPER, built on the ORIGINAL shot footage.

    uv run python creatives/moveon-lead-w1830-th/typeset_video.py

This is the "just swap the text" version, not the Grok-restyle version — the
models stay Indian (this is the real footage that shipped and earned the
best measured female-lead ratio), only the on-screen type changes language.
Requested 2026-09-01 after a Grok ethnicity-restyle pass on the wedding photo
came back looking wrong.

Source plates are the recovered raw clips in
../moveon-lead-w1830/_source/clips-recovered-20260901/ (verified 2026-09-01
against ../moveon-lead-w1830/asset-a.mp4 frame-by-frame — these ARE the four
shipped beats, not a stand-in). Clip 4 only exists locally as a still (the
video was never recovered), so it's animated with a slow zoom instead of
using real footage — the one deliberate compromise in this cut.

Audio is the original's own AAC track, reused as-is — same music bed, so nothing
about the sound changes.

Type in Thonburi Bold (macOS system font, closest legible match to Gabarito's
geometric weight — Gabarito itself is Latin-only and cannot set Thai). The
brand wordmark stays Latin/Gabarito, per creative-style.md's non-negotiable
lowercase 'riteangle' pun, which doesn't survive translation anyway.

Every Thai line is a machine draft, unvalidated by a native speaker — same
gate the original Hinglish never fully closed. Spend gate, not a build gate.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).parent
SRC = D.parent / "moveon-lead-w1830" / "_source" / "clips-recovered-20260901"
ORIG = D.parent / "moveon-lead-w1830" / "asset-a.mp4"
BUILD = D / "_build"
BUILD.mkdir(exist_ok=True)
OUT = D / "asset-a.mp4"

W, H = 720, 1280
FPS = 24
GABARITO = "/Users/performek5/Desktop/Code/pocket-dating-coach/mobile/assets/fonts/Gabarito.ttf"
THONBURI_BOLD = ("/System/Library/Fonts/Supplemental/Thonburi.ttc", 1)

INK = (27, 16, 32, 255)
WHITE = (255, 255, 255, 255)
PINK = (255, 59, 107, 255)
CREAM = (255, 243, 240, 255)

CLIP1 = SRC / "grok-video-7be6acc5-c89d-423d-9a26-4567af66608f.mp4"
CLIP2 = SRC / "grok-video-41719975-e60a-42b5-9494-ec1a17dc2eb6.mp4"
CLIP3 = SRC / "grok-video-e90cffb4-0a83-4374-b0c0-eba5c7cee9b7.mp4"
CLIP4_STILL = SRC / "grok-image-43cc8203-872c-4e0d-ad55-35f8b64a1a5a.jpg"

# (abs_start, abs_end) per beat, verified 2026-09-01 against the real asset-a.mp4
BEATS = [(0, 4), (4, 8), (8, 13), (13, 20)]


def run(cmd):
    subprocess.run(cmd, check=True)


def font(path_or_tuple, size):
    # Thai needs complex-script shaping (tone marks/vowels stack on the
    # consonant) -- PIL's default "basic" layout renders them as separate,
    # wrong glyphs. LAYOUT_RAQM requires libraqm on the DYLD path (see README).
    layout = ImageFont.Layout.RAQM
    if isinstance(path_or_tuple, tuple):
        path, index = path_or_tuple
        return ImageFont.truetype(path, size, index=index, layout_engine=layout)
    return ImageFont.truetype(path_or_tuple, size, layout_engine=layout)


def draw_lines(draw, lines, f, cy, color, w=W):
    """Centre a block of lines vertically around cy, each line centred horizontally."""
    line_h = f.size + 14
    total_h = line_h * len(lines)
    y = cy - total_h / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f, stroke_width=6)
        tw = bbox[2] - bbox[0]
        x = (w - tw) / 2
        draw.text((x, y), line, font=f, fill=color, stroke_width=6, stroke_fill=(0, 0, 0, 130))
        y += line_h


def card(lines, size, color, cy=340):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_lines(d, lines, font(THONBURI_BOLD, size), cy, color)
    return img


def pill(text, fill, text_color, f_size, pad_x=48, pad_y=26, use_gabarito=False):
    f = font(GABARITO, f_size) if use_gabarito else font(THONBURI_BOLD, f_size)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    box_w, box_h = int(tw + pad_x * 2), int(th + pad_y * 2)
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w, box_h), radius=box_h // 2, fill=fill)
    d.text((pad_x - bbox[0], pad_y - bbox[1]), text, font=f, fill=text_color)
    return img


def wordmark():
    """riteangle, two-tone lowercase, Gabarito — brand mark, stays Latin."""
    f = font(GABARITO, 52)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    b1 = d.textbbox((0, 0), "rite", font=f)
    b2 = d.textbbox((0, 0), "angle", font=f)
    w1, w2 = b1[2] - b1[0], b2[2] - b2[0]
    pad_x, pad_y = 40, 22
    th = max(b1[3] - b1[1], b2[3] - b2[1])
    box_w, box_h = int(w1 + w2 + pad_x * 2), int(th + pad_y * 2)
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, box_w, box_h), radius=box_h // 2, fill=CREAM)
    x = pad_x - b1[0]
    d.text((x, pad_y - b1[1]), "rite", font=f, fill=INK)
    d.text((x + w1, pad_y - b2[1]), "angle", font=f, fill=PINK)
    return img


def prep_clip(src, dur, dest, from_still=False):
    """Crop the Grok wordmark (bottom 90px) and trim/animate to `dur` seconds, no audio."""
    if from_still:
        # slow Ken Burns push-in on the still, since no raw video was recovered for this beat
        zoom_frames = int(dur * FPS)
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(src),
            "-vf",
            f"scale=-2:{int(H*1.15)},crop={W}:{H},"
            f"zoompan=z='min(zoom+0.0008,1.12)':d={zoom_frames}:s={W}x{H}:fps={FPS}",
            "-t", str(dur), "-an", str(dest), "-loglevel", "error",
        ])
    else:
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-t", str(dur),
            "-vf", f"crop={W}:in_h-90:0:0,scale={W}:{H}",
            "-an", str(dest), "-loglevel", "error",
        ])


def main():
    # 1. clean plates, each trimmed to its beat's duration
    prep_clip(CLIP1, 4, BUILD / "b1.mp4")
    prep_clip(CLIP2, 4, BUILD / "b2.mp4")
    prep_clip(CLIP3, 5, BUILD / "b3.mp4")
    prep_clip(CLIP4_STILL, 7, BUILD / "b4.mp4", from_still=True)

    # 2. concat the silent base track with the `concat` FILTER, not a stream-copy
    # demux concat. b4 (from a still, via zoompan) comes out yuvj420p against
    # b1-b3's yuv420p; a `-c copy` demux concat mismatches those and produced a
    # base file that *looks* fine on direct playback but silently breaks any
    # overlay `enable` timing placed after the b3/b4 boundary (found 2026-09-01
    # debugging why the CTA card never appeared) -- the concat filter normalises
    # pix_fmt itself and re-times properly within one graph.
    run([
        "ffmpeg", "-y",
        "-i", str(BUILD / "b1.mp4"), "-i", str(BUILD / "b2.mp4"),
        "-i", str(BUILD / "b3.mp4"), "-i", str(BUILD / "b4.mp4"),
        "-filter_complex",
        "[0:v]format=yuv420p[c0];[1:v]format=yuv420p[c1];"
        "[2:v]format=yuv420p[c2];[3:v]format=yuv420p[c3];"
        "[c0][c1][c2][c3]concat=n=4:v=1:a=0[vout]",
        "-map", "[vout]", str(BUILD / "base_notext.mp4"), "-loglevel", "error",
    ])

    # 3. type cards, one transparent PNG per caption window (absolute video time)
    cards = []  # (start, end, image)

    ghosting = card(["โดนเท."], 92, WHITE, cy=290)
    fake_profiles = card(["โปรไฟล์ปลอม"], 78, WHITE, cy=290)
    cheating = card(["นอกใจ"], 92, WHITE, cy=290)
    texting = card(["แชทกันมาสามสัปดาห์", "แต่ไม่ไปไหนเลย"], 62, WHITE, cy=300)
    energy = card(["ตอนนี้รู้แล้วว่า", "พลังงานหายไปไหน"], 62, PINK, cy=300)
    payoff = card(["ไม่ต้องเดต แค่เจอกัน", "แล้วใช้ชีวิต"], 62, WHITE, cy=300)

    cards += [
        (0.3, 2.0, ghosting),
        (2.0, 4.0, fake_profiles),
        (4.3, 6.0, cheating),
        (6.0, 8.0, texting),
        (9.5, 13.0, energy),
        (13.5, 17.0, payoff),
    ]

    cta_pill = pill("สมัครเลย", PINK, WHITE, 60)
    brand_pill = wordmark()

    for start, end, img in cards:
        img.save(BUILD / f"card_{start}.png")
    cta_pill.save(BUILD / "cta.png")
    brand_pill.save(BUILD / "brand.png")

    # 4. composite everything with one ffmpeg overlay pass.
    # input_index counts every "-i" flag (0 = base video); label_n names each
    # overlay's output stream. Two independent counters -- keep them separate.
    overlay_pngs = [str(BUILD / f"card_{start}.png") for start, _, _ in cards]
    overlay_pngs += [str(BUILD / "cta.png"), str(BUILD / "brand.png")]
    windows = [(start, end) for start, end, _ in cards] + [(17.3, 20), (17.3, 20)]
    positions = [("0", "0")] * len(cards) + [("(W-w)/2", "820"), ("(W-w)/2", "940")]

    inputs = ["-i", str(BUILD / "base_notext.mp4")]
    for png in overlay_pngs:
        inputs += ["-i", png]
    audio_input_index = len(overlay_pngs) + 1  # base(0) + pngs, then ORIG is next
    inputs += ["-i", str(ORIG)]

    filter_parts = []
    last = "0:v"
    for i, (png, (start, end), (x, y)) in enumerate(zip(overlay_pngs, windows, positions), start=1):
        nxt = f"v{i}"
        filter_parts.append(
            f"[{last}][{i}:v]overlay={x}:{y}:enable='between(t,{start},{end})'[{nxt}]"
        )
        last = nxt
    filter_parts[-1] = filter_parts[-1].replace(f"[{last}]", "[vout]")

    filter_complex = ";".join(filter_parts)

    run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", f"{audio_input_index}:a",
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        str(OUT), "-loglevel", "error",
    ])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
