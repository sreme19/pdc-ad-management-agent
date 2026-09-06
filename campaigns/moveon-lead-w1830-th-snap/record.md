---
rec_id: rec-2026-09-01-moveon-lead-w1830-th-snap
network: snap
status: live
campaign_name: RA_LEADS_GETW-APPLY_TH_PAN_TOF_202609
ad_set_name: WOMEN_18-30_CASUAL_MOVEON-LEAD-TH
ad_name: VID_MOVE-ON-PROPER_A_20260901
campaign_id: 3430864b-170d-44b6-a342-c7eed598bc8b
ad_set_id: b099e09c-69b8-4c9b-9f22-fedd6885bebc
ad_id: b60533e0-ad0f-4a37-8b94-f2fcf9f8c8cd
targeting_summary: Women 18-30, Thailand, Android only, expansion off. Sister ad squad
  to the live India MOVE-ON-PROPER lead squad (85c2e782-ea07-4216-8986-f272bdb5d4d7)
  -- same persona/gender/age/OS/objective/destination/lead-form, geography swapped
  in->th. First paid test in Thailand; creative is the original shipped India footage
  (best measured female-lead ratio, 11F/7M/3 of 21) with on-screen type swapped Hinglish->Thai
  rather than a model re-cast, after a same-day Grok ethnicity-restyle attempt was
  rejected by the app owner. Destination stays /get/w-apply -- passes the destinations.yaml
  audience=women gate but the page itself is untranslated Hinglish, a deliberate accepted
  trade for this first pass, not an oversight. Lead form reused from the India squad
  (1897accc, already Sheets-connected) rather than built fresh, costing per-ad attribution
  the same way the swagger cut's reuse did -- read Thai-squad performance off Snap's
  own ad-level columns, not marketing_leads. Rs 300/day x 1 day, app-owner-directed
  directional test, not rules/budget.md's full-experiment floor.
targeting:
  gender: FEMALE
  min_age: '18'
  max_age: '30'
  countries:
  - th
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-lead-w1830-th
destination_url: https://www.riteangle.dating/get/w-apply
budget_cap_inr_per_day: 300.0
duration_days: 1
from_idea: null
created: '2026-09-01'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-09-01'
executed: '2026-09-01'
---

## Brief (proposed)

# Deployment brief — MOVE-ON-PROPER, Thailand market test

Requested by the app owner 2026-09-01 as a sister ad squad to the live India
squad `85c2e782-ea07-4216-8986-f272bdb5d4d7` (`WOMEN_18-30_CASUAL_MOVEON-LEAD`).
"Everything else remains the same" — same persona, gender, age band, OS
targeting, objective, destination, and lead form; the only things that change
are geography (`in` → `th`) and the creative's on-screen language.

## Why this creative, why now

`../moveon-lead-w1830` is the only MOVE-ON-PROPER asset with a measured female
lead-delivery ratio (11F/7M/3 unclear of 21, `rec-2026-08-29-moveon-lead-w1830-snap`)
— majority female, the best number this account has produced on a women's
squad. Rather than re-cast the models (a same-day Grok ethnicity-restyle pass
came back looking wrong and was rejected by the app owner), the creative is
the **original shipped footage** with the on-screen type swapped Hinglish→Thai.
Full production trail: `edit-script.md`, `qa.md`,
`_source/clips-recovered-20260901/README.md`.

## Targeting

Women 18-30, Thailand, Android only, expansion off — an exact geography swap
of the live India squad's targeting, nothing else touched. This is Riteangle's
first paid test in Thailand; the platform's own first-party data already shows
a small organic membership cohort outside India (per `rules/targeting.md`'s
Indonesia note), so this isn't a cold-start hypothesis about international
demand, just the first time ad spend has followed it.

## Creative

`../moveon-lead-w1830-th/asset-a.mp4` — same models, wardrobe, sets, cut
points and music bed as the live India ad; only the on-screen type is Thai.
QA in `qa.md`: `pass`, self-assessed (not an independent pass — same caveat
the original and the swagger cut both carry), two recorded deviations (clip 4
is a still+zoom, not recovered video; Thai lines are machine-drafted and
unvalidated by a native speaker).

## Destination — unchanged, and that's a real, accepted trade

`https://www.riteangle.dating/get/w-apply` — same URL the India squad uses.
`rules/destinations.yaml` gates on **audience** (women), which this ad set
still matches; it does not gate on language or country, so this passes the
code-level check cleanly. But the page itself is written in romanised
Hinglish. A Thai woman who taps through will land on a page she likely can't
read. This is a deliberate first-pass trade, not an oversight: the question
this test asks is whether the *ad* stops a Thai scroll at all, not whether the
funnel converts end-to-end. If this test's numbers look bad, that language
cliff — not the creative or the targeting — is the first thing to rule out.

## Lead form — reusing the existing one, same trade-off as the swagger cut

Binding the existing Snap lead form `1897accc-cd6b-4f60-9269-d76ec149842d`
(`RA_LEAD_WOMEN_18-30_CASUAL_MOVEON-LEAD_SNAP`), already Google-Sheets
connected since 2026-08-30. Building a fresh Thailand-specific form would
restart the manual Sheets-connection step from scratch (per
`rules/lead-delivery.md`) and leads would silently not arrive until that was
redone — reuse keeps delivery working immediately. The cost, same as the
swagger record before this one: the form's end-page URL is fixed at creation
and still carries the India ad's UTM literal, so per-ad attribution for this
Thai squad has to be read off Snap's own ad-level impression/swipe/form-open
columns, not off `marketing_leads`.

## Budget

₹300/day, 1 day — set by the app owner directly, a pure directional check
rather than `rules/budget.md`'s ₹800-1,200 full-experiment floor. Consistent
with the ₹300/day tier this same funnel has used for every prior directional
test on this squad.

## Compliance check (`rules/compliance.md`)

| Rule | How this recommendation satisfies it |
|---|---|
| #1 — no provider-energy / luxury / giver-receiver framing in copy or image | Unchanged footage from an asset already scored against this; no new imagery introduced |
| §6.1 — no real man's unenhanced photo | No man appears in any clip |
| §6.2 — no first-person narration of a Riteangle experience | Still true: no dialogue anywhere in the cut, silent throughout |
| §6.3 / both networks' dating rules — 18+ only | Unchanged; original QA scored "anyone could read under 18: pass" |
| §8 — independent QA pass | **Not met.** Same session wrote the type layer and scored it. Flagged explicitly in `qa.md`, deployed on direct app-owner instruction — same precedent as the swagger cut's `fail`-verdict override on 2026-08-31 |

## Execution

- Date: 2026-09-01
- Campaign ID: 3430864b-170d-44b6-a342-c7eed598bc8b
- Ad set ID: b099e09c-69b8-4c9b-9f22-fedd6885bebc
- Ad ID: b60533e0-ad0f-4a37-8b94-f2fcf9f8c8cd
