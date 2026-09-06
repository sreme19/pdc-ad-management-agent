---
id: lrn-2026-09-05-snap-creatives-are-not-deletable
subject: channel
claim: 'Snap will DELETE an ad and an ad squad but refuses to delete a creative: DELETE
  /creatives/{id} returns HTTP 400 E3003 ''Resource can not be found'' on a creative
  that demonstrably exists and was just read back. So a rolled-back push leaves an
  orphan creative behind permanently. That is harmless - a creative with no ad attached
  cannot deliver - but it means creative NAMES are consumed forever, and find_creative()
  will keep matching the orphan.'
source: own-research
confidence: medium
sample_n: null
status: open
created: '2026-09-05'
last_confirmed: '2026-09-05'
review_after: '2027-01-03'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

Snap will DELETE an ad and an ad squad but refuses to delete a creative: DELETE /creatives/{id} returns HTTP 400 E3003 'Resource can not be found' on a creative that demonstrably exists and was just read back. So a rolled-back push leaves an orphan creative behind permanently. That is harmless - a creative with no ad attached cannot deliver - but it means creative NAMES are consumed forever, and find_creative() will keep matching the orphan.

## Evidence

- (2026-09-05) Probed live 2026-09-05 while rolling back the first push of rec-2026-09-05-moveon-getw-w1830-snap. DELETE /ads/4169645b -> SUCCESS, DELETE /adsquads/593db242 -> SUCCESS, DELETE /creatives/2d614c3d -> HTTP 400 E3003, request_id 59023f5b-b2d2-45ec-948f-91ebe7589fc8. The creative had been created minutes earlier by the same session and read back clean in that push's own read-back diff, so 'can not be found' is Snap's error text for 'not deletable', not a real absence.
