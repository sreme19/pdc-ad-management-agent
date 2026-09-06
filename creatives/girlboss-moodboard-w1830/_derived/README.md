# `_derived/` — three stills pulled from `asset-a.mp4`, not from Flow's plates

The women's email drip (`/get/w-drip`) needed hero photography carrying the same
breakup/move-on language as the emails. `asset-a.mp4` ("Tumse Na Ho Paayega",
QA-passed 2026-09-01, watermark-check: pass) already has three on-brand frames
with the right captions baked in — no new generation needed.

**Source:** `../asset-a.mp4`. Reproducible exactly:

```
ffmpeg -ss 11.5 -i ../asset-a.mp4 -frames:v 1 street.png    # S4, "High-maintenance?"
ffmpeg -ss 15.8 -i ../asset-a.mp4 -frames:v 1 rooftop.png   # S5, "Meri respect deal pe nahi."
ffmpeg -ss 20.0 -i ../asset-a.mp4 -frames:v 1 beach.png     # S6, "Tumse na ho paayega."
```

All three came back at the source's native 1080x1920, no watermark in frame (per
the asset's own QA pass), caption already clear of the crop windows used by
`creatives/_web/prep-get-w-drip-images.py`, which turns these into the web-ready
JPEGs in `pocket-dating-coach/static/get-w-drip/`.

The fourth frame named in the original research (t=24.0, S7 resort pool, "meri
manzil nahi") was left out here: S7 is a swimsuit + cover-up shot, and three
fully-dressed beats already cover hero/mid/close — re-extract it the same way if
a fourth image is wanted later.
