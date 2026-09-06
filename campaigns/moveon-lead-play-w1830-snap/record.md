---
rec_id: rec-2026-09-04-moveon-lead-play-w1830-snap
network: snap
status: proposed
campaign_name: RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-LEAD-PLAY
ad_name: VID_MOVE-ON-PROPER_A_20260904
campaign_id: null
ad_set_id: null
ad_id: null
targeting_summary: 'Women 18-30, pan-India, Android only. A copy of the live MOVEON
  lead ad with exactly one axis changed: the form''s end page hands her to the Play
  listing instead of to /get/w-apply, removing one interstitial tap. New ad squad
  under the same campaign (1326aa05) because the squad id IS the attribution key on
  Snap - two ads in one squad are indistinguishable in user_acquisition, and LEAD_FORM_SUBMISSIONS
  optimisation is blind to everything after the submit. Attribution rides Play''s
  install referrer, built literally at push time: utm_source/medium/campaign/term/content
  plus ra_lp=snap_lead_form, all URL-encoded inside referrer= because Play ignores
  params appended to the listing URL. utm_id is absent by platform limit (form precedes
  ad, no form update), so attribution is at squad level - same limit the incumbent
  carries. Android only is load-bearing: iOS has no install referrer and this funnel
  has no TestFlight fallback. Success metric is installs per lead.'
targeting:
  gender: FEMALE
  min_age: '18'
  max_age: '30'
  countries:
  - in
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-lead-w1830
destination_url: https://play.google.com/store/apps/details?id=com.riteangle.app
budget_cap_inr_per_day: 300.0
duration_days: 5
from_idea: null
created: '2026-09-04'
campaign_daily_cap_inr: 300.0
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-09-04'
last_note: '2026-09-04'
---

## Brief (proposed)

# Deployment brief — MOVE-ON lead funnel, direct to Play, women 18–30, Snap

A copy of the live `rec-2026-08-29-moveon-lead-w1830-snap` ad with exactly one axis changed: the
lead form's end page hands her to the **Play listing** instead of to `/get/w-apply`. Same campaign,
same creative, same targeting, same budget, same form fields. Requested by the app owner 2026-09-04
in as many words, together with the standing requirement that installs and signups off it must be
attributable.

## The one change, and what it actually is

The incumbent already ends at an install — `/get/w-apply`'s terminal CTA is "Get the app" → Play. So
this does not add a destination; **it removes one interstitial tap.** The bet is that the tap costs
more installs than the page earns. That is the whole hypothesis and it is worth stating narrowly,
because two other things ride on that tap and both are given up here deliberately:

1. **The 18+ age gate goes.** `destinations.yaml` records the gate as the reason `/get/w-apply` is
   allowed to tell her she qualified. No page, no claim — so the exposure goes with it rather than
   being left dangling. Nothing in this funnel now asserts a status she was not evaluated for.
   The ad's own headline ("Apply karo — sirf 18+") and Snap's 18–30 targeting still carry the age
   condition, and the Play listing is Rated 18+.
2. **The form's end-page copy has to change.** The incumbent form says "Bas ek step baaki hai" /
   "Aapka apply almost complete hai", which is true when a real step follows. Here the next tap is
   the store, so it becomes false. `snap.py`'s `create_lead_form` hardcodes those two strings — this
   push needs them replaced with copy that promises the app, not a step. **Open item, see below.**

## Ad set: a NEW ad squad under the SAME campaign

Campaign `1326aa05-902c-4cec-be92-0a7440ac536d` is reused at the app owner's instruction. The squad
is new, and that is not a preference — it is the only way this test can be read at all:

- **Squad id IS the attribution key.** Snap documents no per-lead macro for the form's end-page URL,
  so every UTM on it is a squad-level literal and `utm_term` is the squad id. Two ads in one squad
  are indistinguishable in `user_acquisition`. The thing being tested would be unmeasurable.
- **Snap optimises on `LEAD_FORM_SUBMISSIONS`**, which is blind to everything after the form. In a
  shared squad it would split budget on a metric that cannot see the difference between the arms.
- **The incumbent squad carries a running verdict** (the W5 11F/7M/3-unclear read). A second ad
  dropped into it mid-flight contaminates that record.

Cost of the reuse, recorded rather than hidden: the campaign name's `[DEST]` token says `GETW-APPLY`
and this squad does not go there. Nothing parses `[DEST]` back out (`naming.md`), so it is a human
legibility cost only — but it is a real one, and the squad's `-PLAY` signal is what carries the truth.

## Attribution — the part the app owner asked for explicitly

**A store listing cannot be instrumented the way our pages can.** No beacon, no page view, no
`marketing_page_views` row, no code of ours running. The only channel that survives an install is
Play's `referrer` parameter. So this repo builds it, at push time, with every value literal:

```
https://play.google.com/store/apps/details?id=com.riteangle.app&referrer=<url-encoded>
  utm_source=snapchat&utm_medium=paid_social&utm_campaign=<campaign name>
  &utm_term=<ad squad id>&utm_content=<ad name>&ra_src=form&ra_lp=snap_lead_form
```

Appending those to the listing URL instead of encoding them inside `referrer` is the failure mode
this is written to avoid: Play ignores them, the ad still runs, and every install is unattributable —
the 2026-08-21 incident with a different first step.

**What survives to `user_acquisition`, verified 2026-09-04 by reading the consuming code, not by
assuming it:** `mobile/lib/attribution.dart` keeps every `utm_*` key plus `ra_lp` (as `landingPage`)
and drops the rest; the server's `sanitizeUtm` re-applies the same `^utm_` filter. So:

| Field | Lands in | From |
|---|---|---|
| network / medium / campaign | `user_acquisition.network` / `.medium` / `.campaign` | `utm_source` / `utm_medium` / `utm_campaign` |
| **ad squad** | `user_acquisition.ad_set` | `utm_term` — **this is the join** |
| creative (ad name) | `user_acquisition.creative` | `utm_content` |
| where it came from | `user_acquisition.landing_page` = `snap_lead_form` | `ra_lp` |
| the whole string | `user_acquisition.referrer_raw` | verbatim |

`ra_src=form` rides along for a human reading `referrer_raw` and is deliberately not a join key —
`sanitizeUtm` drops it. `ra_lp=snap_lead_form` is a **label, not a page id**: reusing a real page id
would count a direct-to-store install as a page view that never rendered.

**No pixel is involved and none is needed.** The lead conversion happens inside Snap, so
`LEAD_FORM_SUBMISSIONS` needs no pixel (that is why `create_lead_adsquad` does not require one), and
the install is measured by the Play referrer above, not by a pixel. Two limits stated up front:

- **`utm_id` (the ad id) is absent, by platform limit.** Snap fixes the form's end page at creation,
  the form precedes the ad, and Snap documents no form update. Attribution is at **ad-squad level** —
  the same limit the incumbent record already carries, so the arms stay comparable. It is only a
  limit at all because this squad will hold one ad.
- **Snap's own dashboard will report leads, not installs.** There is no MMP and no Snap app registration,
  so Snap cannot close its own install loop. Install and signup counts come from `user_acquisition`,
  and the two numbers must be reconciled rather than mixed (`rules/lead-delivery.md` #2).
- **Android only, and it is load-bearing here.** iOS has no install referrer at all, and this funnel
  offers no TestFlight fallback — an iPhone woman reaches a Play listing she cannot use. `os: ANDROID`
  is not a preference on this record.

## Lead delivery — the manual step that must not be skipped

A new squad means a new form (`RA_LEAD_WOMEN_18-30_CASUAL_MOVEON-LEAD-PLAY_SNAP`), and a new form
means a **new Google Sheet and its own Apps Script trigger** per `rules/lead-delivery.md`. Snap's API
webhook does not deliver. Until that is connected, leads sit in Ads Manager on a 90-day clock and
nothing reaches `marketing_leads`. The ad is not "set up" until a test report has landed in the sheet.

## Success metric and kill criteria

**One metric: installs per lead** — `user_acquisition` rows carrying this squad's `utm_term`, over
leads in the sheet. That is the only number that separates this arm from the incumbent; cost per lead
should look the same in both, since nothing before the submit changed.

- **Male mix**, same 30% kill number as the incumbent.
- **Standard loop:** 3–5 days or 50–100 events, whichever comes first.
- **Read strength:** ₹300/day is below `budget.md`'s ₹800–1,200 calibration band, matched to the
  incumbent deliberately so the comparison is like-for-like. `inconclusive` is the expected verdict
  for anything comparative; this answers "does the store arm deliver at all and does anything look
  wrong", not "is it better".
- **Expect targeting expansion ON regardless of this record.** Snap forces `SMART_TARGETING` on lead
  squads (`lrn-2026-08-31-snap-forces-expansion-on-lead-squads`). Same condition as the incumbent, so
  it does not skew the comparison — but do not credit `expansion: false` for any result here.

## Open items before push

1. **Form end-page copy.** `create_lead_form` hardcodes "Bas ek step baaki hai" / "Aapka apply almost
   complete hai" and the CTA `VIEW_WEBSITE`. Both are false-to-slightly-false when the next tap is the
   store. Needs new copy and, if Snap offers it, an install-flavoured CTA on `end_page_properties`.
2. **Lead sheet + Apps Script trigger** for the new form (above).
3. **One real install on a real Android device** before spend, read back from `user_acquisition`. A
   listing that merely opened proves nothing — a bare listing URL opens identically and attributes
   nothing.

## Separate observation, not part of this build

`_utm_query` writes the **campaign name** into `utm_campaign`, while `rules/tracking.md`'s own table
says Snap's `utm_campaign` carries the **ad set name**. Every live row was written the code's way, so
this record follows the code for consistency rather than changing it mid-flight. Worth resolving
deliberately, in its own pass, against `traffic-quality.ts`.

Also carried forward from the incumbent: `ra_lead` is forwarded onto the Play referrer by
`/get/w-apply`, but `sanitizeUtm` drops any non-`utm_` key, so it never reaches `user_acquisition`.
That is the Meta funnel's per-lead join, and it appears to die at the endpoint. Not this ad's problem
— this ad never had a per-lead id — but it should be checked before anyone quotes a lead-to-install
join off the Meta arm.

## Note — budget (2026-09-04)

Campaign 1326aa05 carries a Rs 300/day CAMPAIGN cap and now has two squads under it: the incumbent WOMEN_18-30_CASUAL_MOVEON-LEAD (Rs 300/day, currently PAUSED) and this one (Rs 300/day). The cap gate passed because it compares ONE squad against the cap, and a single squad at Rs 300 does not exceed Rs 300 — but a campaign cap is shared, so enabling BOTH throttles the pair to Rs 300/day total, roughly Rs 150 each, below even the accepted operating default and degrading the incumbent's own read as a side effect. Three ways out, and it is the app owner's click either way: raise the campaign cap to Rs 600 and run both head-to-head; leave the incumbent paused and run this arm alone at the full Rs 300 (sequential, not head-to-head, so incumbent numbers come from its own earlier window); or accept Rs 150 each, which is not advised. Recorded 2026-09-04, read live off the campaign.

## Note — creative (2026-09-04)

END-PAGE CTA CORRECTED 2026-09-04, and the correction needed a whole new ad because the chain is immutable. Ad A (VID_MOVE-ON-PROPER_A_20260904, 0fb006ae) shipped with end-page call_to_action VIEW_WEBSITE against a Play listing that is not a website of ours. Snap's lead-form end page takes a SMALLER enum than a creative does - no INSTALL_NOW, no DOWNLOAD (E25020, probed live; see lrn-2026-09-04-snap-lead-end-page-cta-enum) - so the right value is LEARN_MORE: it is true, claims nothing, and implies no purchase, where FREE_TRIAL/SPECIAL_OFFER/GET_COUPON/BUY_TICKETS are purchase language compliance.md #2 forbids and APPLY_NOW is false on a page she reaches by having just applied. The instruction itself sits in the end-page copy ('Ab app download karo'), which is not enum-constrained. Three attempts to correct A in place all failed on immutability: a lead form is fixed at creation (no update documented), a creative's lead_generation_form_id is refused with E2023 'Property could not be updated', and an ad's creative_id is not updatable at all while its PUT REQUIRES status - which this repo may not send as ACTIVE. So ad B (VID_MOVE-ON-PROPER_B_20260904, de518b58) was created PAUSED on the same squad with form e6c55711 and creative b7cdbfad, same media, same headline, referrer rebuilt to name B in utm_content. Swapping A for B is the app owner's click. Form ad0a73e0 (V2) was created during the same pass and is unused - do not connect a sheet to it.

## Note — incident (2026-09-04)

AD A AND ITS SQUAD WERE ENABLED OUTSIDE THIS FLOW. snap-push-lead created both PAUSED at 05:10-05:11Z on 2026-09-04 and read them back PAUSED; reading them again at 05:2xZ, squad 0c4a937f and ad 0fb006ae both read ACTIVE with updated_at 05:12:42 and 05:12:47. Not this repo - snap.py refuses any outbound payload carrying an enabling status at the transport choke point - so it was an Ads Manager click. Stated plainly because it went live BEFORE two things the setup explicitly gates on: (1) the lead form is NOT connected to a Google Sheet, so per rules/lead-delivery.md any submission from this point reaches Ads Manager only, on a 90-day clock, and nothing reaches marketing_leads - and the connection is not retroactive, so a backlog must be downloaded by hand; (2) no test install has been done, so the Play referrer this record's whole attribution rests on is verified only by read-back of the stored URL, never by a real device. Squad stats at the time of writing read 0 impressions, 0 swipes, 0 spend (finalized to 02:00Z, so it lags), and the squad started 05:10:35Z, so nothing had served yet. Not logged via log-setup: the ad that should be live is B, not A.
