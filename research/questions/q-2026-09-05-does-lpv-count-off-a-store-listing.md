---
id: q-2026-09-05-does-lpv-count-off-a-store-listing
kind: tracking
status: open
asked: '2026-09-05'
raised_by: rec-2026-09-05-moveon-getw-w1830-snap
answered: null
learning: null
---

## Question

Does Snap count a Play Store listing render as a LANDING_PAGE_VIEW on this ad account, or is LPV only countable for a page we control? Asked because rec-2026-09-05-moveon-getw-w1830-snap was pushed on SWIPES specifically to sidestep this, and SWIPES optimises for the tap rather than for the arrival - which is a weaker proxy for an install if LPV would in fact have worked.

## Why it matters

Decides the optimisation goal for every future direct-to-store traffic ad. If LPV counts off a store listing it is the better goal (closer to the install). If it does not, an LPV squad would optimise toward an event it can never observe and could under-deliver or fail to exit learning entirely - the same class of failure as the Story squad's E2899 refusal, which was account/pixel eligibility rather than a config mistake. Answerable by pushing one PAUSED store-bound squad on LANDING_PAGE_VIEW and reading whether Snap reports any.
