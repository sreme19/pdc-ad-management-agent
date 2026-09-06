---
id: lrn-2026-09-07-ads-agent-ro-rls-block-is-lifted
subject: tracking
claim: 'The RLS block that made every ads_agent_ro read return zero rows is GONE:
  the read-only channel now returns real data. config.local.yaml''s standing warning
  that ''an empty result from this channel is NOT evidence of no data'' is stale,
  and a zero from verify-tracking can now be read as a genuine zero.'
source: live-data
confidence: high
sample_n: 120
status: open
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2027-01-05'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

The RLS block that made every ads_agent_ro read return zero rows is GONE: the read-only channel now returns real data. config.local.yaml's standing warning that 'an empty result from this channel is NOT evidence of no data' is stale, and a zero from verify-tracking can now be read as a genuine zero.

## Evidence

- (2026-09-07) Queried 2026-09-07 through the same _pg_env/psql path verify-tracking uses: user_acquisition returns 120 rows all-time, 51 carrying utm_content, 27 carrying utm_id. Under the RLS condition recorded in lrn-2026-08-28-channel2-rls-blocks-every-read every one of those counts was 0. The fix landed in pocket-dating-coach (a SELECT policy per granted table for this role) and was not announced here. This matters beyond convenience: while the block was in place, every verify-tracking INCONCLUSIVE was unfalsifiable, because a blocked read and an empty window are indistinguishable at the call site. THE SAME QUERY ALSO RETURNED A FACT NOBODY ASKED FOR: network='meta' has 0 rows all-time, so no Meta ad has ever produced a user_acquisition row - consistent with lrn-2026-08-27-meta-ads-carry-no-utms, and it makes rec-2026-09-06-moveon-play-w1830-meta the first Meta ad that could ever land one.
