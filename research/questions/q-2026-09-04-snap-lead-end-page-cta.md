---
id: q-2026-09-04-snap-lead-end-page-cta
kind: creative
status: answered
asked: '2026-09-04'
raised_by: rec-2026-09-04-moveon-lead-play-w1830-snap
answered: '2026-09-04'
learning: lrn-2026-09-04-snap-lead-end-page-cta-enum
---

## Question

Does Snap's lead-form end page support an install-flavoured call_to_action (INSTALL_NOW / DOWNLOAD), or is VIEW_WEBSITE the only value?

## Why it matters

The direct-to-store lead funnel sends her from the form's end page to the Play listing, but every form on this account — including the ones made in Snap's own UI — stores VIEW_WEBSITE and nothing else (read back 2026-09-04). So the button says 'View website' when the destination is the store. Guessing an enum is what produced E25022 on this same resource, so VIEW_WEBSITE ships until someone confirms an alternative in the UI. Unblocks a copy fix on the last screen before the install.

## Answer (2026-09-04)

Answered by lrn-2026-09-04-snap-lead-end-page-cta-enum: A Snap lead form's END PAGE call_to_action is a different, smaller enum than a creative's: VIEW_WEBSITE, BOOK_NOW, LEARN_MORE, DONATE, SPECIAL_OFFER, SCHEDULE_NOW, BUY_TICKETS, TEST_DRIVE, APPLY_NOW, GET_COUPON, CLAIM_SAMPLE, FREE_TRIAL. There is no install-flavoured value, so a lead form whose end page is an app store has no button that says install.
