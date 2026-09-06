---
id: lrn-2026-09-07-shared-squad-destroyed-per-ad-attribution
subject: tracking
claim: Putting four lead ads in one Snap ad squad made the only 13 signups Snap has
  ever produced unattributable to any creative. A lead form's end page is fixed before
  the ad exists, so its referrer carries the SQUAD id and no ad id - there is no way,
  even in principle, to say which of the four earned them.
source: live-data
confidence: high
sample_n: 114518
status: promoted
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2027-01-05'
derived_from: null
questions: []
recs: []
promoted_to: rules/funnel.md
---

## Claim

Putting four lead ads in one Snap ad squad made the only 13 signups Snap has ever produced unattributable to any creative. A lead form's end page is fixed before the ad exists, so its referrer carries the SQUAD id and no ad id - there is no way, even in principle, to say which of the four earned them.

## Evidence

- (2026-09-07) Found 2026-09-07 reconciling the ledger. Squad 85c2e782 carries rec-2026-08-29-moveon-lead-w1830, rec-2026-08-30-buildyourself-lead-w1830, rec-2026-08-31-moveon-swagger-lead-w1830 and rec-2026-09-01-knowyourworth-lead-w1830. Squad totals: 114,518 impressions, 1,132 swipes, Rs 1,472.26, 45 page views on /get/w-apply, 36 store clicks, 13 signups. Ad-level Snap stats DO separate impressions and spend (3c9d2884 took 74% of impressions, ca0e5b76 14%, 85bde974 7%, 0bb15d8b 6%) - but user_acquisition has only the squad, so the OUTCOME cannot be split even though the COST can. rules/tracking.md already recorded that a lead ad's referrer stops at squad level and that two ads in one squad are indistinguishable; this is that warning landing on the single best result in the ledger. Three of the four hooks are consequently untested rather than unsuccessful. THE RULE: one ad per squad on the lead funnel, or accept that lead creative cannot be A/B tested on Snap at all - there is no third option, and choosing it by default is how four hooks became one unreadable number.
## Promoted (2026-09-07)

This claim is now normative, in `rules/funnel.md`. That file is what skills obey; this atom is only its origin.
