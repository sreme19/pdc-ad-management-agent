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
status: contradicted
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2027-01-05'
derived_from: null
questions: []
recs:
- rec-2026-09-06-moveon-play-w1830-meta
promoted_to: null
---

## Claim

The RLS block that made every ads_agent_ro read return zero rows is GONE: the read-only channel now returns real data. config.local.yaml's standing warning that 'an empty result from this channel is NOT evidence of no data' is stale, and a zero from verify-tracking can now be read as a genuine zero.

## Evidence

- (2026-09-07) Queried 2026-09-07 through the same _pg_env/psql path verify-tracking uses: user_acquisition returns 120 rows all-time, 51 carrying utm_content, 27 carrying utm_id. Under the RLS condition recorded in lrn-2026-08-28-channel2-rls-blocks-every-read every one of those counts was 0. The fix landed in pocket-dating-coach (a SELECT policy per granted table for this role) and was not announced here. This matters beyond convenience: while the block was in place, every verify-tracking INCONCLUSIVE was unfalsifiable, because a blocked read and an empty window are indistinguishable at the call site. THE SAME QUERY ALSO RETURNED A FACT NOBODY ASKED FOR: network='meta' has 0 rows all-time, so no Meta ad has ever produced a user_acquisition row - consistent with lrn-2026-08-27-meta-ads-carry-no-utms, and it makes rec-2026-09-06-moveon-play-w1830-meta the first Meta ad that could ever land one.
- (2026-09-07) **contradicted** (from rec-2026-09-06-moveon-play-w1830-meta): PARTIALLY WRONG, corrected 2026-09-07 the same day it was written. The core claim stands: the RLS block is lifted and the channel returns real data. THE SECONDARY CLAIM IN THE EVIDENCE PARAGRAPH IS FALSE. It said network='meta' has 0 rows all-time and concluded that no Meta ad has ever produced a user_acquisition row. The user_acquisition.network column stores the RAW utm_source - 'fb', 'ig', 'snapchat' - and never the normalised 'meta'; networkOf()'s normalisation happens in pocket-dating-coach's read path, not in the stored column. The query therefore asked for a value that cannot appear and got the zero it was always going to get. THE TRUTH, from one group-by: Meta has produced 31 signups (ig 27, fb 4) against snapchat 68 in the same table. All 31 came from the OLD August FB_* campaigns - 6980375898281, 6980971385681, 6981912929281 - all landing on /get, all between 16 and 21 August. The conclusion drawn from the bad query, that rec-2026-09-06-moveon-play-w1830-meta would be the first Meta ad that could ever land a row, is wrong too. What IS true is narrower and still worth knowing: none of the three 2026-08-27/29 Meta records produced a single signup, and no Meta ad has ever landed a row against the women's pages. METHOD NOTE, because this is the same shape of error twice: a count against a column whose vocabulary has not been read is a claim about the query, not about the system. Reading the distribution first would have cost one statement.
