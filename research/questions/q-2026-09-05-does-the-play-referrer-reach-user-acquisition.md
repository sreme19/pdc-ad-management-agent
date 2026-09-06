---
id: q-2026-09-05-does-the-play-referrer-reach-user-acquisition
kind: tracking
status: open
asked: '2026-09-05'
raised_by: rec-2026-09-05-moveon-getw-w1830-snap
answered: null
learning: null
---

## Question

Does Play's install referrer actually survive into pocket-dating-coach's user_acquisition for a direct-to-store TRAFFIC ad - specifically, do rows appear carrying ra_lp=snap_ad_direct and utm_id=<ad id>? The referrer shape was verified by reading mobile/lib/attribution.dart and the server's sanitizeUtm on 2026-09-04, and the pushed URL decodes correctly, but no real install through a traffic ad has ever been observed landing a row.

## Why it matters

This is the whole measurement chain for the direct-to-store arm. If the referrer does not survive, every install off rec-2026-09-05-moveon-getw-w1830-snap is unattributable and the arm cannot be compared to the lead funnel at all - which is the 2026-08-21 incident with a different first step, and reading code is exactly the kind of proof that failed then ('should' is what was believed last time, per destinations.yaml's own note on /get/w-apply). Closes only on a real row read back from user_acquisition, not on another code read.
