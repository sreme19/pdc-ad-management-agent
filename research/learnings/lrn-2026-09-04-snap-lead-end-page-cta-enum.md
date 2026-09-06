---
id: lrn-2026-09-04-snap-lead-end-page-cta-enum
subject: channel
claim: 'A Snap lead form''s END PAGE call_to_action is a different, smaller enum than
  a creative''s: VIEW_WEBSITE, BOOK_NOW, LEARN_MORE, DONATE, SPECIAL_OFFER, SCHEDULE_NOW,
  BUY_TICKETS, TEST_DRIVE, APPLY_NOW, GET_COUPON, CLAIM_SAMPLE, FREE_TRIAL. There
  is no install-flavoured value, so a lead form whose end page is an app store has
  no button that says install.'
source: platform-doc
confidence: high
sample_n: null
status: open
created: '2026-09-04'
last_confirmed: '2026-09-04'
review_after: '2027-03-03'
derived_from: null
questions:
- q-2026-09-04-snap-lead-end-page-cta
recs: []
promoted_to: null
---

## Claim

A Snap lead form's END PAGE call_to_action is a different, smaller enum than a creative's: VIEW_WEBSITE, BOOK_NOW, LEARN_MORE, DONATE, SPECIAL_OFFER, SCHEDULE_NOW, BUY_TICKETS, TEST_DRIVE, APPLY_NOW, GET_COUPON, CLAIM_SAMPLE, FREE_TRIAL. There is no install-flavoured value, so a lead form whose end page is an app store has no button that says install.

## Evidence

- (2026-09-04) Snap's own lead-generation-ads doc lists exactly these twelve (read 2026-09-04), and a probe POST carrying INSTALL_NOW was rejected E25020 'End page CallToAction must be one of the allowed values', creating nothing. DOWNLOAD and GET_APP rejected the same way. Note the probe nearly reported the opposite: Snap returns HTTP 200 with request_status ERROR and the reason in sub_request_error_reason, so a check that only caught exceptions read all three invalid values as accepted — _one is what catches this in the real path. For riteangle the surviving choice is LEARN_MORE: FREE_TRIAL/SPECIAL_OFFER/GET_COUPON/BUY_TICKETS are purchase language forbidden by compliance.md #2, DONATE/TEST_DRIVE/BOOK_NOW/SCHEDULE_NOW/CLAIM_SAMPLE are false, and APPLY_NOW is false on an end page she reaches by having just applied.
