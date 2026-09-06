---
id: q-2026-09-06-does-the-meta-referrer-reach-user-acquisition
kind: tracking
status: open
asked: '2026-09-06'
raised_by: rec-2026-09-06-moveon-play-w1830-meta
answered: null
learning: null
---

## Question

Does a real install off the Meta direct-to-store ad land a user_acquisition row carrying ra_lp=meta_ad_direct and this ad's utm_content? The chain is built and reads back correct at every step we can inspect - Meta stores the tracked link, the link opens the real listing, the app id parses clean, and android_play_install_referrer is in the app - but no install has been observed making the trip on the Meta arm. It is a QUESTION-MARK row in the funnel coverage table, not a tick.

## Why it matters

It decides whether the Meta arm is measurable at all. If the referrer does not arrive, the only per-ad signal left is the link click, and the whole point of this ad set - comparing Meta against the Snap arm that produced zero installs - cannot be answered from our own data at any budget, because Play Console has no per-ad breakdown. Closing it costs one manual install on a real Android device through the enabled ad, then 'ad-agent verify-tracking rec-2026-09-06-moveon-play-w1830-meta'. Note this is the Meta twin of q-2026-09-05-does-the-play-referrer-reach-user-acquisition, and the two are NOT closed by the same test: the Snap arm's referrer stops at squad level on its lead path and carries utm_id on its traffic path, while Meta joins the ad on utm_content, so a working Snap chain proves nothing about this one.
