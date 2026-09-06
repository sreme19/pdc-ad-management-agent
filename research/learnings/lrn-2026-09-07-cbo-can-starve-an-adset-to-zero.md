---
id: lrn-2026-09-07-cbo-can-starve-an-adset-to-zero
subject: budget
claim: A campaign-budget-optimisation parent does not split its budget across ad sets
  - it can give one everything and another nothing. Two ad sets under a Rs 300/day
  CBO campaign ran five days and one delivered ZERO impressions, so an audience band
  recorded as tested was never tested.
source: platform-doc
confidence: high
sample_n: null
status: retired
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2027-03-06'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

A campaign-budget-optimisation parent does not split its budget across ad sets - it can give one everything and another nothing. Two ad sets under a Rs 300/day CBO campaign ran five days and one delivered ZERO impressions, so an audience band recorded as tested was never tested.

## Evidence

- (2026-09-07) Observed 2026-09-07 reconciling the Meta ledger. Campaign 6984366120881 reads campaign_budget_optimization=True, daily_budget 30000 paise. Children: WOMEN_25-30_CASUAL_MOVEON-LEAD (6984368402281) took Rs 636.37 and produced 29 leads; WOMEN_18-24_CASUAL_MOVEON-LEAD (6984366122081) took Rs 0.00, insights edge returns no data at all, zero impressions across the full five-day window. Both records read 'live' in the ledger for nine days after. DISTINCT FROM lrn-2026-08-29-lead-ad-sets-cannot-exit-learning, which is about too few conversions to leave learning: this ad set had no impressions to convert. meta-push already refuses a CBO parent because it 'ignores the ad-set budget rather than capping it'; what this adds is that the ignored budget can be ZERO, which is worse than a wrong number because it looks like a finished test. Both records predate the guard and were hand-built in Ads Manager. RULE: never put two ad sets under a CBO parent when the comparison between them is the point, and check per-ad-set delivery before concluding anything about an audience band.
## Retired (2026-09-07)

Duplicate. Created 2026-09-07 by a retry after the first write's related-learnings listing was misread as a refusal; lrn-2026-09-07-cbo-starved-an-adset-to-zero says the same thing and was first. No evidence was attached to this copy.
