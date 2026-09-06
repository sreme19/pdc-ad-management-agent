"""Web-ready imagery for /get/w-drip, cut from the girlboss-moodboard-w1830 stills.

    uv run python creatives/_web/prep-get-w-drip-images.py

Writes into pocket-dating-coach/static/get-w-drip/. Same split as
prep-get-w-images.py: this repo holds the plates, that one holds the page, and
only the output crosses over.

Unlike prep-get-w-images.py's plates, these three frames arrive already
composed for exactly this use — captions baked in, no watermark, framed with
headroom above the caption band (see
../girlboss-moodboard-w1830/_derived/README.md). No crop is needed to remove a
mark or a pasted rectangle; this script only downscales for delivery weight.
"""
from pathlib import Path

from PIL import Image

SRC = Path("/Users/performek5/Desktop/Code/ad-management-agent/creatives/girlboss-moodboard-w1830/_derived")
OUT = Path("/Users/performek5/Desktop/Code/pocket-dating-coach/static/get-w-drip")

JPEG = dict(quality=82, optimize=True, progressive=True)


def for_web(im, width=1080):
    """Same rule as prep-get-w-images.py: 1080 is 2x the widest column this
    page renders a full-bleed image in, and these plates arrive at 1080
    already, so this is a no-op today and a safety net if a wider source ever
    lands here."""
    if im.width <= width:
        return im
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


FRAMES = {
    "hero.jpg": "street.png",  # S4, "High-maintenance?" — the top-of-page image
    "moment.jpg": "rooftop.png",  # S5, "Meri respect deal pe nahi."
    "close.jpg": "beach.png",  # S6, "Tumse na ho paayega." — the closing beat
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in FRAMES.items():
        im = Image.open(SRC / source).convert("RGB")
        for_web(im).save(OUT / name, **JPEG)

    for name in FRAMES:
        f = OUT / name
        im = Image.open(f)
        print(f"{name:10} {im.size[0]}x{im.size[1]}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
