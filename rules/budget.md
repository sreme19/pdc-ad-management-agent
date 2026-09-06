# Budget guardrails

Source: Sree's Aug 7 log. Every `ad-setup-loop` recommendation must state a budget cap and duration
(SPEC.md decision #5) and should default to these figures unless there's a specific reason to deviate
— state the reason plainly if it does.

## Operating envelope

- **Total operating budget: ~₹50,000/month.** Concentrate on learning speed, not scale, until unit
  economics are cracked (cost to acquire one active woman, one active man).
- **Split:** 40–50% testing (new creative + audience variants) · 40–50% exploitation of proven winners
  · 10% retargeting/engagement once there's signal to retarget against.
- **Default daily spend: ₹300 per ad set** — set by the app owner on 2026-08-28, applied live to the
  first Meta ad set the same day, and the default `propose --budget-cap` uses. This is the operating
  level, deliberately chosen for burn rate over read speed.
- **Default duration: 2 days per ad set** — set by the app owner on 2026-09-05, standing from that
  date, and the default `propose --duration-days` uses. Replaces the 5 days every record before it
  carried. ₹300 × 2 means **a test now costs ₹600**, which is the point: more shots at the same
  monthly budget.

  **Two consequences, stated rather than wished away.** First, 2 days is shorter than the kill/double
  window below, which is written as 3–5 days — so that window no longer decides when to stop; the end
  date does. A 2-day ad set stops itself, and the decision it hands back is whether to *re-run* it
  longer, not whether to pause it. Second, and this is the one that bites: `snap-push` stamps the ad
  squad's start at the moment of **creation**, not the moment of enabling, and everything is created
  PAUSED. At 5 days, a day's delay between push and enable cost a fifth of the test. At 2 days it
  costs half of it. **Push and enable the same day, or amend the duration before pushing** — nothing
  in the code will warn about this, because from Snap's side a squad that only ran one day is not an
  error, just a squad that reached its end date.
- **Full-experiment threshold: ₹800–1,200 per active ad set — kept as calibration, no longer a floor.**
  The original rule (Sree's Aug 7 log) made this a minimum, and its reasoning still stands: below
  roughly this level the platform's delivery algorithm rarely exits its learning phase, so a read is
  *directional*, not conclusive. What changed on 2026-08-28 is the decision, not the fact — running at
  ₹300 is accepted, with its consequence stated rather than wished away:

  **A ₹300/day test answers "does this deliver at all, and does anything look wrong?" It does not
  reliably answer "is this creative/audience better than that one?"** `ad-audit` should expect
  `inconclusive` as the normal verdict at this level, and a kill/double call made on a ₹300 read is a
  judgment call, not evidence. When a test matters enough that its answer must be trusted — a bake-off
  winner, a new audience thesis — raise that one ad set into the ₹800–1,200 band for its window and say
  so on the record. (The earlier version of this rule called sub-floor volume "a system check, not a
  real experiment"; that description now applies to the default itself, and is accepted.)

## Test → measure → kill/double → exploit loop

1. **Hypothesis → test.** ~70% of budget in early weeks goes to testing new creative/audience
   combinations.
2. **Measure.** Installs, landing-page views, Bestie-conversation-starts, or whatever the campaign's
   stated success metric is (see `ad-setup-loop`'s brief template — every proposal names one).
3. **Kill or double.** Pause a losing ad set after **3–5 days or 50–100 events**, whichever comes
   first. Move its budget to whatever's winning. **Since 2026-09-05 the 2-day default duration usually
   ends the set before this window opens** — so read this step as governing the *re-run* decision (does
   this ad set deserve a second, longer window?) rather than the pause decision, which the end date has
   already made.
4. **Exploit.** Scale the proven creative × audience × bid combination.

## A market's price is a budget input, not a constant — check CPM before funding a new geo

**Normative from 2026-09-07** (`lrn-2026-09-07-snap-thailand-cpm-is-27x-india`).

Every figure above was calibrated on Indian inventory, and it does not travel. The first Thailand
test spent **₹268.95 to buy 772 impressions and 3 swipes** — a **₹348 CPM**, against ₹6.50–₹12.85
across every India squad on the same account, same creative family, same 18–30 women targeting,
overlapping dates. **Roughly 27–54× the price for the same impression.**

The damage is not the ₹269. It is that the result reads like a creative failure and is not one:
3 swipes cannot say anything about a hook, so MOVE-ON-PROPER is **untested** in Thailand, not
rejected. A budget too small to buy a readable sample does not produce a weak answer, it produces a
confident-looking non-answer — and the ledger will carry it as a tested market unless someone says
otherwise.

So, before funding an ad set in a market this account has not run in:

- **Estimate the impressions the budget buys at that market's CPM, not at India's.** If it does not
  reach four figures, the test cannot be read and should not be run at the default.
- **Fund it properly or drop the market.** Re-running Thailand at ₹300/day will reproduce this exact
  non-result. There is no cheap version of this question.
- **Record the market's observed CPM** on the record when the run ends, so the next proposal in that
  geo starts from a number instead of an assumption.

The ratio is the finding, not the precise multiple: n is one squad over roughly one day.

## Signup targets (context, not a hard budget rule)

Most recent figures (Aug 17 log): **1,000 men signups at ~₹25/signup**, **100 women signups at
~₹200/signup** — the ~8x cost asymmetry reflects the platform's own gender-balance goal (women are the
scarcer, more valuable acquisition on a dating product skewed male across the market). A recommendation
targeting women should tolerate a materially higher cost-per-signup than one targeting men; treating
them as the same target is a modeling error, not a budget win.

## Confidence gating (SPEC.md decision #6)

`ad-audit` inherits `pocket-dating-coach`'s `MIN_SAMPLE = 30` floor for any claim that a specific ad set
is or isn't working. Below that sample, the correct answer is "not enough data yet" (`inconclusive`),
never a guess dressed as a finding.
