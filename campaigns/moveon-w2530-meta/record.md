---
rec_id: rec-2026-08-27-moveon-w2530-meta
network: meta
status: reviewed
campaign_name: RA_TRAFFIC_GETW_IN_BLR_TOF_202608
ad_set_name: WOMEN_25-30_CASUAL_MOVEON-LPV
ad_name: STORY_MOVE-ON-PROPER_A_20260827
campaign_id: '6984035763681'
ad_set_id: '6984035818681'
ad_id: '6984036525881'
targeting_summary: "Women 25-30, Bangalore, Advantage Audience off. CASUAL-SELECTIVE\
  \ persona \u2014 the security-register end of the 18-28 band per the Aug-5 age split.\
  \ The breakup re-entry hook (MOVE-ON-PROPER thread): moving on is not in question,\
  \ how is. Expansion deliberately off because the premise is a specific age band\
  \ and Meta broadens unless told not to."
targeting:
  gender: FEMALE
  min_age: '25'
  max_age: '30'
  countries:
  - in
  os: null
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-properly-w2530
destination_url: https://www.riteangle.dating/get/w
budget_cap_inr_per_day: 1000.0
duration_days: 5
from_idea: idea-2026-08-27-breakup-reentry-second-chapter
created: '2026-08-27'
last_note: '2026-08-28'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-08-28'
executed: '2026-08-28'
verdict: not-working
reviewed: '2026-09-07'
---

## Brief (proposed)

# Deployment brief — MOVE-ON-PROPER, women 25–30, Meta

Reconstructed 2026-08-27 from `SESSION-RESUME-2026-08-27.md` §1, which recorded the
original as `/tmp/brief-moveon.md` and explicitly ephemeral. Written into the creative
folder this time so it survives the session.

**Network changed from the original brief.** The session that wrote it targeted Snap.
This proposes the same creative on **Meta**, because Meta creation became available on
2026-08-27 (`SPEC.md` decisions #3/#10, extended) and the asset is 1080×1920, which
serves Meta Reels/Stories as readily as Snap Story.

## The bet

The breakup re-entry hook, in her register: moving on is not in question, *how* is.
From `idea-2026-08-27-breakup-reentry-second-chapter` (verdict `recommend`), against the
`MOVE-ON-PROPER` thread in `rules/creative-style.md`. Reference format is Tinder's Move On
Salon — a woman narrating her own breakup rather than posed.

## Plan

| Field | Value |
|---|---|
| Campaign | `RA_TRAFFIC_GETW_IN_BLR_TOF_202608` |
| Ad set | `WOMEN_25-30_CASUAL_MOVEON-LPV` |
| Ad | `STORY_MOVE-ON-PROPER_A_20260827` |
| Targeting | Women, 25–30, India / Bangalore, Advantage Audience OFF |
| Persona | CASUAL-SELECTIVE — security-register end of the 18–28 band, per the Aug-5 age split |
| Destination | `https://www.riteangle.dating/get/w` (audience women — destination gate passes) |
| Budget | ₹1,000/day × 5 days |
| Creative | `asset-a.jpg` (1080×1920, bake-off round-1 winner c5, type set by `typeset.py`) |

Expansion is off deliberately: the whole premise is a specific age band, and Meta broadens
unless told not to. An ad set that quietly widened would answer a different question.

## Carried risks — surface these again before enabling

1. **§6.2 AI-labelling is escalated, not settled.** The §8 independent pass in `qa.md`
   returned `escalate`: the asset is an AI-generated portrait with a first-person breakup
   line, which reads as testimony from a real customer, and nothing labels it as generated.
   Covering the Gemini watermark addressed the "no tool watermark" half of §6.2 and moved
   away from the "label it" half. **App owner's decision, per `SPEC.md`'s compliance
   non-negotiables.** Note the push gate will NOT stop this: it greps `qa.md` for the string
   `pass`, and the finished-asset header still reads `pass`.
2. **No comment-moderation policy exists** for the hostility a public breakup hook attracts.
   Carried from the original brief, still unaddressed.
3. **Tracking on Meta is unproven.** Per `lrn-2026-08-27-meta-ads-carry-no-utms`, the live
   Meta ads carry no UTM parameters at all, so this will be the first Meta ad here ever to
   have them — meaning `utm_source: meta` is a convention this sets rather than matches, and
   `q-2026-08-27-meta-utm-source-spelling` is unresolved. If the spelling disagrees with
   `pocket-dating-coach`, the spend will not join to the traffic and the test reads as zero.
4. **Naming carries no network token.** `rules/naming.md`'s campaign and ad-set shapes have
   no network field, so this campaign name is identical to what a Snap push would produce.
   Harmless for the id-based joins, confusing for humans, and untested against
   `ad-analytics.ts`'s ad-set rollup with two networks in play.

## Note — creative (2026-08-27)

COMPLIANCE ESCALATION, unresolved — app owner's decision before enabling. The §8 independent pass in creatives/moveon-properly-w2530/qa.md returned escalate on rules/compliance.md §6.2 ('Label AI imagery'). The asset is a fully AI-generated portrait carrying a first-person breakup line, which reads as testimony from a real customer, and nothing in frame labels it as generated. Covering the Gemini watermark satisfied the 'no visible AI-tool watermark' half of §6.2 and moved away from the 'label it' half. Three options are written out in qa.md (label it / change the framing / narrow §6.2's scope in the rules file). Important: the push gate will NOT stop this — it greps qa.md for the string 'pass' and the finished-asset header still reads pass, so a document containing both 'pass' and 'escalate' passes the gate.

## Note — incident (2026-08-27)

TRACKING IS UNPROVEN ON THIS NETWORK. Per lrn-2026-08-27-meta-ads-carry-no-utms, every live Meta ad in account 1561367575690055 carries no UTM parameters at all (read directly from Ads Manager 2026-08-27: bare https://www.riteangle.dating/get, empty URL parameters field, Website events unchecked). So this will be the first Meta ad here ever to carry UTMs, which means utm_source=meta is a convention this record SETS rather than matches, and q-2026-08-27-meta-utm-source-spelling is still open. If that spelling disagrees with pocket-dating-coach's normalisation, the spend will not join to the traffic and this test will read as having produced nothing — the same failure as snap/snapchat, which left only 7 of 151 signups joinable. Settle the spelling before enabling.

## Note — observation (2026-08-27)

No comment-moderation policy exists for the hostility a public breakup hook attracts. Carried from the original brief on 2026-08-27 and still unaddressed. Meta comments are more exposed than Snap's, since a Meta ad IS a Page post and accumulates public replies under the Riteangle Page.

## Note — incident (2026-08-28)

Pushed to Meta PAUSED on 2026-08-28 and read back clean, 13/13 fields matching. Real ids: campaign 6984035763681, ad set 6984035818681, ad 6984036525881, tracked creative 3381749368661464. url_tags on the creative carry literal values with no macro: utm_source=fb, utm_term=6984035818681 (ad set id), utm_content=6984036525881 (ad id, which is what traffic-quality.ts joins on for Meta). Advantage Audience read back 0, so the 25-30 band held and was not silently broadened. All 83 creative enhancement features report OPT_OUT, so the QA-passed asset is intact. HOUSEKEEPING: the push took four attempts and left orphaned untracked creatives behind (1812181563532325, 3546135838888885, 982834978110685) plus duplicate uploaded images. All unused and costing nothing; meta.py cannot delete them by design, so remove them by hand in Ads Manager if the clutter matters.

## Execution

- Date: 2026-08-28
- Campaign ID: 6984035763681
- Ad set ID: 6984035818681
- Ad ID: 6984036525881

## Note — creative (2026-08-28)

COMPLIANCE ESCALATION RESOLVED 2026-08-28 by the app owner. The §6.2 AI-labelling question is settled and the scope is written into rules/compliance.md §6.2 rather than left as an inference. The line is about the claim, not the pixels: a generated person MAY appear in Riteangle creative, photorealistic and unlabelled; a generated person MAY NOT narrate a first-person experience of using Riteangle. The labelling sentence in §6.2 is an in-product obligation, and paid social owes only no-visible-AI-tool-watermark, no glitches, no false claim. This still passes on that test — its copy is a general aphorism, not a personal-results claim. Correction to the original escalation: it leaned on script.md, which is the VIDEO cut, and the still never carried those first-person lines; the concern was right about the video and overstated about the still. script.md is now blocked at the top of the file under the same rule. Independent of all this, Meta and Snap carry their own synthetic-media disclosure rules for ads, which bind separately and have not been checked.

## Note — budget (2026-08-28)

BUDGET CHANGED ON THE LIVE AD SET, 2026-08-28, by the app owner in Ads Manager: ad set 6984035818681 daily_budget is now 30000 paise = Rs 300/day, down from the Rs 1,000/day this record states in budget_cap_inr_per_day. The record's stated figure is therefore no longer what is being spent, and amend cannot correct it because the record is live — this note is the correction. Planned total for the 5-day window drops from Rs 5,000 to Rs 1,500. Two consequences for the review due 2026-09-02: Rs 300/day is below rules/budget.md's Rs 800-1,200 minimum viable floor, so delivery may never leave its learning phase and ad-audit should expect an inconclusive read rather than evidence; and this is the same effective figure that made rec-2026-08-21-women-1822-casual-lpv unreadable, though for a different reason — there a campaign cap bound below the stated budget invisibly, here the figure is a deliberate choice and the only problem is its size. The campaign itself carries no budget (daily_budget None), so this is NOT campaign-budget optimisation and the ad set figure is the effective one.

## Note — observation (2026-08-28)

Delivery confirmed 2026-08-28, first watch check (~30-45 min after enable): effective_status ACTIVE (never held in review), 703 impressions, 627 reach, 27 inline link clicks, Rs 23.95 spent. Link CTR ~3.8%, CPM Rs 34.07, cost per link click ~Rs 0.89. All Meta-side numbers — whether those 27 clicks arrive on /get/w as landing-page views is the question the pocket-dating-coach side answers, and the LPV-count learning (lrn-2026-08-26-snap-and-beacon-disagree-on-lpv) says expect the two counts to disagree. Read at Rs 300/day: directional only, per rules/budget.md as amended.

## Note — observation (2026-08-28)

Landing-side verification attempted 2026-08-28 and BLOCKED, not zero. Meta reports 87 landing_page_view actions against 111 link clicks (~78% land rate, ~Rs 0.88/LPV at Rs 76.99 spent). The beacon count on /get/w could not be read: ads_agent_ro sees 0 rows from marketing_page_views because RLS is enabled with no policy for the role (lrn-2026-08-28-channel2-rls-blocks-every-read) — a silent empty result, NOT evidence that no traffic landed. Do not read 'beacon=0' anywhere as a tracking failure until the RLS policies exist in pocket-dating-coach. Until then Meta's own LPV count is the only landing-side number available, and it is Meta grading its own homework.

## Note — observation (2026-08-28)

Beacon verification landed 2026-08-28, after the RLS fix: 138 landings on get_w carrying utm_content=6984036525881, 138 distinct visits, zero bot-like user agents, utm_source=fb arriving intact. THE JOIN WORKS END TO END — spend will attribute. Beacon reads HIGHER than Meta (138 vs 87 landing_page_view against 111 link clicks), the same direction of disagreement as the Snap/beacon LPV learning; Meta's LPV metric is the stricter render-complete count, the beacon fires earlier, and neither is wrong. Cost per beacon-verified landing ~Rs 0.56 at Rs 76.99 spent.

## Note — targeting (2026-08-28)

DEVIATION FOUND BY THE BEACON: the ad is serving PAN-INDIA, not Bangalore. City spread of its landings: Hyderabad 12, Chennai 10, New Delhi 9, Bengaluru 8, Pune 7, unknown 13. Root cause is structural, not an Ads Manager slip: the targeting spec (targeting.py) only encodes countries — it has no city/region field — so to_meta sent geo_locations={countries:[IN]} while the ad-set name says BLR and the record's targeting_summary says Bangalore. The read-back diffed clean because it compares against the SPEC, and the spec never encoded the city; check_matches_ad_set_name checks gender only. So the record contradicts itself and the live audience is broader than the brief. Decision for the app owner: restrict geo to Bengaluru in Ads Manager (targeting edit on a live ad set is allowed — it is not budget/enable), or accept pan-India and note the ad-set name is wrong for it. Either way the review must read this as a pan-India test. Structural fix belongs in targeting.py: a cities field, plus name-vs-spec geo cross-check alongside the gender one.

## Note — observation (2026-08-28)

SPEND JOIN VERIFIED 2026-08-28 05:20 UTC: the first-ever Meta row landed in ad_spend_daily via pocket-dating-coach's hourly sync, once META_MARKETING_TOKEN + META_AD_ACCOUNT_ID were set on Vercel (the earlier zero was the pre-redeploy deployment not seeing the vars). Field-for-field exact against a direct Insights read taken the same minute: spend Rs 113.93, 2736 impressions, 178 clicks, ad_set_id 6984035818681, creative_id 6984036525881, currency INR. The importer's field mapping — documented in its own comment as never verified against a live response — is correct on first contact. With this, every system in the chain is verified working for Meta: paused-only push, tracking (utm_source=fb, ad id in utm_content), beacon landings, internal analytics traffic classification, and now spend. ad-audit can compute cost-per-outcome for the 2026-09-02 review.

## Note — observation (2026-08-28)

Day-1 four-hour watch closed, 2026-08-28. Delivery arc across 8 half-hourly reads (impressions / link clicks / Rs spent): 703/27/23.95 -> 795/32/27.76 -> 1258/64/48.33 -> 1960/111/76.99 -> 2199/135/88.70 -> 2480/156/102.37 -> 2736/172/113.93 -> final 2991/196/124.99. ACTIVE throughout, never held in review. Link CTR rose 3.8% -> ~6.6% and held; CPM settled ~Rs 42; cost per link click ~Rs 0.64; spend pacing on target for Rs 300/day. Beacon verified 138 landings against Meta's 87 landing_page_view earlier in the day (platform LPV under beacon, consistent with the Snap learning, evidence logged). Spend join verified exact at 05:20 UTC: ad_spend_daily row matched a same-minute Insights read to the paisa (113.93/2736/178). Every system in the chain is verified working: paused-only push, tracking, beacon, analytics traffic classification, spend sync. OPEN at close: pan-India serving vs BLR ad-set name (app owner decision, targeting note earlier); review window opens 2026-09-02, expect a DIRECTIONAL read per rules/budget.md at Rs 300/day.

## Note — observation (2026-08-28)

Day-1 analytics read (2026-08-27..28, fetch-analytics --network meta). Spend Rs 237.01, 5950 impressions, 389 Meta link clicks, 397 beacon views on get_w, 5 store-click taps, 0 signups. Leaderboard tap rate 1.26% (5/397, CI 0.54-2.91%), cost per tap Rs 47.40, cost per view Rs 0.60. clickToViewRate 1.02 — beacon views essentially equal Meta's clicks, so the join is clean and there is no landing-side leak. TWO CAVEATS THAT CHANGE THE READ. (1) GEO: only 23 of 344 city-resolved views are Bengaluru; Hyderabad 27, Chennai 24, New Delhi 19+8, Mumbai 12. Confirms the pan-India deviation already noted — this is a pan-India test, not a BLR one. (2) THE TAPS ARE NOT INDIAN: byCountry shows IN 391 views / 1 tap, US 5 views / 4 taps, and all 4 US taps land in one city (Altoona) inside a single 00:15 bucket on 2026-08-28, before Indian delivery began. Read on India alone the tap rate is 1/391 = 0.26%. Nothing was excluded as a crawler for those 4, so they passed bot filtering. Also visitFunnel reports tapped=2 / 0.50% against the leaderboard's 5 — the two counts disagree and neither was recomputed here. Verdict deferred: review window opens 2026-09-02 and the ad set runs at Rs 300/day, below rules/budget.md's floor, so expect directional-only.

## Review

- Date: 2026-09-07
- Verdict: not-working
- Summary: RECONCILED 2026-09-07 against the live account; the ledger had carried this as 'live' for 10 days after it stopped. Ad set 6984035818681 and ad 6984036525881 are both PAUSED and the run window closed 2026-09-02. IT DID DELIVER, and well, at the top of the funnel: Rs 366.39 spend, 9,606 impressions, 606 link clicks, 465 Meta-counted landing-page views, and 611 page views recorded on OUR side for this ad set - so its url_tags worked and the traffic was tracked correctly end to end. THE VERDICT IS not-working BECAUSE OF WHAT HAPPENED NEXT: 611 tracked page views produced ZERO signups. That is well above MIN_SAMPLE=30, so this is a finding rather than a shrug - the ad bought attention on /get/w cheaply and none of it converted. Two caveats recorded rather than buried. (1) The record states Rs 1,000/day; the ad set's actual daily_budget was Rs 300/day, so this ran at under a third of its planned rate and never reached the Rs 800-1,200 band where budget.md says delivery exits learning - the CONVERSION read is solid on n=611 views, the cost-efficiency read is not. (2) Success metric as stated was landing-page views, and on that metric alone it succeeded; the verdict is against the outcome the views existed to produce.


