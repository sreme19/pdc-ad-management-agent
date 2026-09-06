---
id: lrn-2026-09-07-cbo-starved-an-adset-to-zero
subject: budget
claim: A campaign-budget-optimisation parent does not split its budget across ad sets
  - it can give one ad set everything and another nothing. Two ad sets under a Rs
  300/day CBO campaign ran for five days and one of them delivered zero impressions,
  so an audience band recorded as tested was never tested at all.
source: platform-doc
confidence: high
sample_n: null
status: open
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2027-03-06'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

A campaign-budget-optimisation parent does not split its budget across ad sets - it can give one ad set everything and another nothing. Two ad sets under a Rs 300/day CBO campaign ran for five days and one of them delivered zero impressions, so an audience band recorded as tested was never tested at all.

## Evidence

- (2026-09-07) Observed 2026-09-07 reconciling the Meta ledger. Campaign 6984366120881 reads campaign_budget_optimization=True with daily_budget 30000 paise. Its two children: WOMEN_25-30_CASUAL_MOVEON-LEAD (6984368402281) took Rs 636.37 and produced 29 leads; WOMEN_18-24_CASUAL_MOVEON-LEAD (6984366122081) took Rs 0.00 and its insights edge returns no data at all - zero impressions over the full five-day window. Both records read 'live' in the ledger for nine days afterwards. This is the documented behaviour meta-push already refuses a CBO parent for, with no escape hatch, on the grounds that it 'ignores the ad-set budget rather than capping it' - what this case adds is that the ignored budget can be ZERO, which is worse than a wrong number because it looks like a completed test. Both records predate the guard and were built by hand in Ads Manager (route a). THE RULE THAT FOLLOWS: never place two ad sets under a CBO parent when the comparison BETWEEN them is the point, and check delivery per ad set before drawing any conclusion about an audience band.
