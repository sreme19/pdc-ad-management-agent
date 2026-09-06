---
id: lrn-2026-09-07-verify-tracking-was-blind-to-meta
subject: tracking
claim: 'A per-network convention hardcoded in one place will be silently wrong for
  the other network, and the check built to catch that class of error was itself the
  thing carrying the bug: verify-tracking hardcoded utm_id (Snap''s ad join key) and
  so could never find a Meta ad''s rows, which carry the id in utm_content.'
source: source-code
confidence: medium
sample_n: null
status: open
created: '2026-09-07'
last_confirmed: '2026-09-07'
review_after: '2026-11-06'
derived_from: null
questions: []
recs: []
promoted_to: null
---

## Claim

A per-network convention hardcoded in one place will be silently wrong for the other network, and the check built to catch that class of error was itself the thing carrying the bug: verify-tracking hardcoded utm_id (Snap's ad join key) and so could never find a Meta ad's rows, which carry the id in utm_content.

## Evidence

- (2026-09-07) Found 2026-09-07 by running verify-tracking against rec-2026-09-06-moveon-play-w1830-meta, the first Meta record it had ever been pointed at. The SQL read utm->>'utm_id' unconditionally. rules/networks.yaml has declared ad_join_param per network since it was written, and cli._utm_query has always read it from there - so the convention was correctly centralised and this one call site simply did not use it. The failure mode is the worst available: with perfect tracking it reports 0 for the ad forever, and reports SUSPICIOUS (i.e. tracking looks broken) the moment any unrelated row lands in the window. NO HISTORICAL DAMAGE: this was the first Meta record the command had been run against, so no past result was wrong. Fixed by reading ad_join_param from the registry; both arms re-run green afterwards - Meta now reports on utm_content, Snap still on utm_id.
