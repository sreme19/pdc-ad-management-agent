---
id: lrn-2026-09-06-meta-cta-enum-has-no-install-now
subject: channel
claim: Meta's call_to_action enum has no INSTALL_NOW. A website-destination creative
  pointed at a Play listing takes DOWNLOAD; the install-flavoured types (INSTALL_MOBILE_APP,
  INSTALL_APP, GET_MOBILE_APP) exist but belong to app-promotion creatives carrying
  a promoted_object.
source: platform-doc
confidence: high
sample_n: null
status: open
created: '2026-09-06'
last_confirmed: '2026-09-06'
review_after: '2027-03-05'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

Meta's call_to_action enum has no INSTALL_NOW. A website-destination creative pointed at a Play listing takes DOWNLOAD; the install-flavoured types (INSTALL_MOBILE_APP, INSTALL_APP, GET_MOBILE_APP) exist but belong to app-promotion creatives carrying a promoted_object.

## Evidence

- (2026-09-06) POST /act_1561367575690055/adcreatives returned error #100 on 2026-09-06 with the full permitted list enumerated in the message: 'call_to_action[type] must be one of the following values: BOOK_TRAVEL, CONTACT_US, DONATE, ... DOWNLOAD, ... GET_MOBILE_APP, INSTALL_MOBILE_APP, USE_MOBILE_APP, INSTALL_APP, ...'. INSTALL_NOW is absent from it. Snap's equivalent CTA on the sibling ad is APPLY_NOW, a different enum entirely - do not carry a CTA name across the two networks. DOWNLOAD was used on ad 6986393974881 and accepted. Note that only a real run exercises this: --dry-run never reaches the creative POST, so a wrong CTA is not caught in rehearsal.
