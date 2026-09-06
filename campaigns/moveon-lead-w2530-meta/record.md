---
rec_id: rec-2026-08-29-moveon-lead-w2530-meta
network: meta
status: reviewed
campaign_name: RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608
ad_set_name: WOMEN_25-30_CASUAL_MOVEON-LEAD
ad_name: VID_MOVE-ON-PROPER_A_20260829
campaign_id: '6984366120881'
ad_set_id: '6984368402281'
ad_id: '6984368441881'
targeting_summary: "Women 25-30, pan-India, Android only, Advantage Audience OFF.\
  \ Second band of the same campaign as rec-2026-08-29-moveon-lead-w1824-meta \u2014\
  \ same objective (OUTCOME_LEADS), same instant form, same thank-you handoff to /get/w-apply\
  \ via ra_lead, same 30 percent male-mix kill number, same knowingly-accepted Rs\
  \ 300 learning-phase consequence. The two bands share the campaign but are separate\
  \ ad sets so the age split stays readable; at this budget the comparison between\
  \ them is directional only."
targeting:
  gender: FEMALE
  min_age: '25'
  max_age: '30'
  countries:
  - in
  os: ANDROID
  expansion: false
  regulated_content: true
creative_ref: creatives/moveon-lead-w1830
destination_url: https://www.riteangle.dating/get/w-apply
budget_cap_inr_per_day: 300.0
duration_days: 5
from_idea: null
created: '2026-08-29'
last_note: '2026-08-29'
campaign_daily_cap_inr: null
campaign_lifetime_cap_inr: null
campaign_caps_verified: '2026-08-29'
executed: '2026-08-29'
verdict: inconclusive
reviewed: '2026-09-07'
---

## Brief (proposed)

# Deployment brief — MOVE-ON lead funnel, women 18–30, Meta

**Status: DRAFT, local only. Not proposed, not pushed, not committed.** Written 2026-08-28 from a
requirements session with the app owner. Target go-live 2026-08-29.

This is the first proposal that leaves the running funnel cell. `rules/funnel.md` describes the
women's funnel as a three-axis matrix with exactly one cell live (static image → landing page →
Play Store). This changes two axes at once: **capture point** moves to an on-platform lead form, and
the **destination** becomes a new post-submit page. That is rung 3 of funnel.md §2's ladder, and it
is deliberate, not accidental scope creep — see "Why now" below.

## The bet

A woman gives her contact details inside Meta, where the form is autofilled and friction is near
zero. She is then told she is one step from being qualified, and the last step is real: an age
declaration. Passing it is a genuine 18+ eligibility check, so the celebratory "you're in" is true.
The install is framed as the thing she earned rather than the thing we want.

**Hypothesis, stated as the app owner stated it:** the prize framing raises install intent enough to
beat the current direct-to-Play funnel. This is a hunch being tested, not a finding.

**Stage 1 measures one thing only: do actual women submit the form?** Whether they then install is
stage 2 and is not what this test is powered to answer.

## Why now, and why this isn't a repeat of the 98/2 failure

On-platform lead forms already ran and returned 98% male submissions. `rules/funnel.md` §3 records
that the diagnosis blames **creative POV plus a submit-optimised objective**, and leaves the format
itself unjudged — it is explicitly a re-run candidate. Two things have changed since: the POV rule
now exists in `creative-generation.md` §1, and a women-framed destination exists.

**The third thing, which is this brief's own argument:** the compounding mechanism described in
§1 — "on a submit-optimized objective the delivery algorithm compounds it, because men submit dating
lead forms far more readily" — requires men in the deliverable pool to drift toward. Both ad sets
below are hard-set `gender: FEMALE` with `expansion: false`. With those two set, the algorithm can
only optimise within women.

**This makes `expansion: false` the single most load-bearing setting in the build.** Commit
`a29fe59` exists because omitting expansion means it is ON. It is a hard gate on push, alongside
tracking. Meta's gender signal is self-reported and leaks, so a kill number is still required.

## Plan

| Field | Value |
|---|---|
| Campaign | `RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608` |
| Ad set A | `WOMEN_18-24_CASUAL_MOVEON-LEAD` |
| Ad set B | `WOMEN_25-30_CASUAL_MOVEON-LEAD` |
| Objective | `OUTCOME_LEADS`, optimised for lead submission |
| Targeting | Women, **pan-India**, **Android only**, Advantage Audience OFF |
| Destination | Meta instant form → `/get/w-apply` (built 2026-08-28, not yet deployed) |
| Budget | ₹300/day per ad set = **₹600/day total** × 5 days = ₹3,000 |
| Success metric | **Cost per lead** |
| Creative | Google Flow, breakup hook, `MOVE-ON-PROPER` thread |

### Three naming notes, flagged rather than silently resolved

1. **`RA_LEADS_` is an extension of `naming.md`.** The convention hardcodes `TRAFFIC` in position 2
   while describing it as "campaign objective". A leads campaign needs `LEADS` there. Add the line to
   `naming.md` before this ships, so the next one isn't re-derived.
2. **`[DEST]` token for the new page is `GETW-APPLY`.** The route is `/get/w-apply` — the app owner
   asked for it to live under the women's namespace rather than at a top-level path. `naming.md` says
   to strip the slashes and uppercase, and forbids `_` in a token (it would shift every later field);
   a hyphen is fine and already appears in live ad-set signals like `MOVEON-LPV`. Field count stays
   at seven, identical to `RA_TRAFFIC_GETW_IN_BLR_TOF_202608`.
3. **`naming.md`'s stated ad-set field order is wrong.** It says `[AUDIENCE]_[AGE]_[GENDER]_[SIGNAL]`
   but its own example and every live ad set read `[GENDER]_[AGE]_[AUDIENCE]_[SIGNAL]`
   (`WOMEN_25-30_CASUAL_MOVEON-LPV`). The live shape is followed here. Worth correcting the doc.

## The funnel, step by step

| # | Where | She does | Is the claim real? |
|---|---|---|---|
| 1 | Meta ad | Taps the breakup hook, CTA "Apply" | — |
| 2 | Meta instant form | First name, phone, email — autofilled | Real capture |
| 3 | Thank-you screen | "One step left →" | **True** — she isn't done |
| 4 | New page | Taps her age band | **Real gate** — 18+ is genuine eligibility |
| 5 | Same page, new state | "You're in." | **True** — she passed a real criterion |
| 6 | Play Store | Installs, referrer carries the join key | — |

### On the qualification framing

The app owner's first framing was explicitly theatrical — tell her she qualified when nothing was
evaluated. That was raised as a Meta misleading-claims exposure on an ad account SPEC #10 records as
effectively one-way, and as a `compliance.md` #7 (hype) problem.

**The age step resolves it without losing the psychology.** 18+ is a real condition — `compliance.md`
§6.3, Meta's and Snap's dating-category rules, and the product's own verification. She is evaluated
against a real criterion and passes. No fabricated status, **no override to record.**

## Lead form spec

Fields: **first name, phone, email.** All three per the app owner.

**Phone still has no consumer.** `lrn-2026-08-27-callcentre-blocked-on-registration` stands: the call
centre is blocked on an unregistered company, so a captured number cannot lawfully be dialled today.
Phone is a WhatsApp field in practice; email is the field with a real path. The consent line must say
honestly what happens to each. Do not imply a call.

Privacy-policy URL is **mandatory** on every Meta lead form. Confirm the URL before build.

## The new page

**`/get/w` is not touched.** It is two days old, it serves organic and non-paid traffic, and its lead
form is currently the only capture path for iPhone women. This funnel gets its own page.

### Layout — state 1

Above the fold, nothing else visible. No nav, no scroll, no marketing copy competing. Everything that
had to sell her happened on Meta; this page has one job.

- **Progress bar, already two-thirds full — "Step 2 of 3".** Endowed progress, and honest: she really
  did do the work on Meta. Preferred over a "95%" figure, which edges toward `compliance.md` #5 by
  reading as a score about *her* rather than about the process.
- **One question, enormous:** "Last thing. How old are you?"
- **Age bands, not an 18+ checkbox:** `18–20` `21–24` `25–30` `31+`, with *Under 18* as small plain
  text, not a button. Bands feel like a real question, are a genuine declaration, and give a free
  cross-check on whether Meta's age targeting delivered the band that was paid for.
- **An honest processing beat**, under a second, labelled truthfully ("Saving your details…"). We
  really are writing the lead.

### Layout — state 2

> ✓ **You're in, and you're early.**
> Riteangle verifies every man before he reaches you.
> Your invite is on this device.
> **[ Get the app ]**

Understated deliberately. Hype trips `compliance.md` #7, and the verification claim is the approved
one under #4 ("identity-verified and established professionals", never "high-earning").

### Four conditions, or the gate goes back to being fake

1. **Under 18 must actually stop, and the lead must be deleted** — not ignored. Her name, phone and
   email were captured *before* the gate, and under India's DPDP a child's data requires verifiable
   parental consent. Required path in v1, not a follow-up.
2. **No cold access.** No `ra_lead` in the URL means she never filled the form and "one step left" is
   nonsense. Fall back to a normal page.
3. **Do not fake the verification beat.** A spinner pretending to check credentials she never gave is
   the deceptive version of the thing we just made honest.
4. **iPhone fallback.** Android-only targeting leaks. A dead install button is worse than a waitlist.

### Personalisation — IN v1, at the app owner's call (2026-08-28)

The page greets her by first name: "Almost there, Priya."

This was originally scoped out and the app owner pulled it back in. **Be clear what it costs**, because
it converts a page build into a page build plus an integration:

- **`leads_retrieval` on the Meta system-user token.** Meta's completion URL passes `{{lead_id}}` and
  nothing else — no field values — so the name can only come from reading the lead back from Meta.
  Verify the token actually carries this permission before committing to the design; if it needs Meta
  review, the name does not happen tomorrow.
- **A server-side lookup in `pocket-dating-coach`** — takes `ra_lead`, calls Meta for the lead, returns
  the first name. Runs in the page's server load, not the browser, so the token never reaches a client.
- **Enumeration guard.** The endpoint takes an id from a query string and returns a real person's name.
  Rate-limit it, and do not return anything beyond the first name.
- **Fail open, never blocking.** Lookup fails or times out → render "Almost there." and carry on. A
  name is a nicety; a page that white-screens because Meta was slow is a dead campaign.

**One consolidation worth taking:** `leads_retrieval` is the same permission that would let us pull
leads by script instead of by hand. If we are acquiring it for the name anyway, the manual CSV step
below can be automated in the same pass — check the permission once, get both.

## Tracking

**Join key: `ra_lead`.** Meta resolves `{{lead_id}}` per submission in the thank-you screen's CTA URL.

```
https://www.riteangle.dating/<new-page>?utm_source=fb&utm_medium=paid_social
  &utm_campaign=<ad set name>&utm_term=<ad set id>&utm_content=<ad id>&ra_lead={{lead_id}}
```

Every value except `ra_lead` is written as a **literal**. That is the 2026-08-21 lesson, and
`meta-push` already works this way because the ids are known at push time. Note `utm_source=fb` and
`utm_content` carrying the **ad id** — Meta's conventions, not Snap's (`rules/tracking.md`).

`pocket-dating-coach` then persists `ra_lead` exactly where it already persists `ra_lp` — the
referrer builder at `src/routes/get/[[audience=aud]]/+page.svelte:132` is one line — after which it
flows into the Play install referrer for free.

**Chain:** Meta lead row → `ra_lead` in thank-you URL → site view → Play referrer → `user_acquisition`.

**Why a token and not email-matching:** SPEC #7 bars this agent from user tables entirely. An email
join needs exactly the data it may not touch. `lead_id` is opaque and carries no PII.

**Stated limit:** the join only holds if she taps through in that session. Submit-and-return-later
loses the key, so this is a floor on attribution, not a complete picture.

**Pre-launch:** verify `{{lead_id}}` actually resolves against one real test submission before any
spend. The 2026-08-21 incident is exactly an unverified-macro failure.

## Lead retrieval

**v1: manual CSV pull, daily, from Meta Lead Center — unless `leads_retrieval` lands for the
first-name greeting, in which case script it in the same pass.** Zero build on a day already carrying a code
change and a creative shoot; at ₹600/day the volume is small. **Needs a named owner** — a lead nobody
exports is not a lead. Note Meta deletes leads after 90 days.

**Then:** webhook into `marketing_leads`, which already exists, already has a dialer, and which
`pocket-dating-coach` already writes to from `/get/w` (`src/lib/server/marketing-leads.ts`). Build it
if women actually submit. Check whether the system-user token carries `leads_retrieval` — if it does,
a scripted pull beats CSV and is nearly free.

## Creative

Google Flow. Breakup hook, `MOVE-ON-PROPER` thread (the closed vocabulary in `creative-style.md` —
`naming.md` forbids coining a slug at naming time).

**Do not reuse the round-05 pack as-is.** `creatives/_bakeoff/round-05-getw-genz/` is written for
`/get/w` page imagery at **3:4**, and its slot 1 replaces `hero.jpg`. A Meta lead ad wants **4:5 feed
or 1080×1920 Story/Reels**. The casting carries over — `@Meher`, `@Ira`, `@Nandita` are defined and
reusable — but aspect and composition change, and the type space moves. Set this before spending
credits.

**Two gates the breakup angle keeps tripping:**

- **`creative-generation.md` §1, the POV rule.** She is not the object of the frame. A picture of an
  attractive woman recruits men whatever the targeting says — that is the whole 98/2 diagnosis. Show
  what she sees or feels: her aftermath, her POV.
- **`compliance.md` §6.2.** A generated woman may appear, photorealistic and unlabelled. She may
  **not** narrate a first-person experience of using Riteangle. That is what blocked the MOVE-ON
  *video* and drew an `escalate` on the still. "Move on toh karna hai — par dhang se" is fine;
  anything in her voice about her own results is not.

**A lead-ad creative is not an LPV creative.** The CTA is "Apply"/"Sign Up" and the tap opens a form
inside Meta, not a page. The copy sets up a form.

## Kill criteria

- **Male mix.** A number is required before launch and is not yet set. This is the open item that
  most directly guards against repeating 98/2.
- **Cost per lead.** Target not yet set. Context from `budget.md`: women have run ~₹200/signup against
  ~₹25 for men, and that ~8x asymmetry is expected, not a failure.
- **Standard loop:** pause after 3–5 days or 50–100 events, whichever comes first.
- **Read strength.** At ₹300/day per ad set this sits below `budget.md`'s ₹800–1,200 calibration band,
  so `inconclusive` is the expected verdict for anything comparative. Accepted deliberately by the app
  owner on 2026-08-28 for burn rate. It answers "do women submit at all" — not "is A better than B".

## Geo — pan-India, and what it costs

Settled by the app owner 2026-08-28, and it is the right call for Hinglish copy: Bangalore is
Kannada-speaking, so Hindi there reaches North Indian migrants rather than the default population.
The live `women-1822-casual-lpv` set already runs PAN.

**The consequence to expect, stated up front rather than discovered at review:** at Rs 300/day per ad
set across the whole country, Meta optimises toward the cheapest impressions it can find, which means
delivery will concentrate in Tier-2 and Tier-3 markets rather than metros. That is coherent with
Hindi-first creative and is arguably a feature here. It is NOT coherent with metro-coded imagery —
the round-05 casting is written around Bangalore rooftops, Indiranagar footpaths and café window
tables. If delivery lands where the budget takes it, the creative should not look like south-metro
lifestyle. Worth deciding deliberately rather than letting the two drift apart.

## Blockers, in the order they bite

1. **The new page does not exist.** `ad-agent propose` **refuses** a destination that is not in
   `destinations.yaml` with a matching audience, and there is deliberately no `--force`. The page must
   be built in `pocket-dating-coach`, its copy read and classified `audience: women`, and a `verified`
   date set. **This is the schedule risk, not the Meta code.** Who builds it, and are they free
   tomorrow?
2. **`meta.py` has no lead-form path.** It hardcodes `destination_type: "WEBSITE"` and builds
   `link_data`; `promoted_object` is deliberately not sent (see its line 406–422, which already says a
   different objective "is a new code path"). Needed: `OUTCOME_LEADS`, `destination_type: ON_AD`,
   `promoted_object` with `page_id` (already in config), a lead-form resource, and the paused-only
   refusal extended in `MetaClient._call` to cover all of it — SPEC #3 requires the guard at the
   transport choke point, not per method.
3. **Privacy-policy URL** for the lead form. Mandatory, not yet confirmed.
3b. **`leads_retrieval` on the system-user token**, now load-bearing for the first-name greeting. If it
   requires Meta app review, the greeting is cut and the page ships without it — it must not be allowed
   to hold up launch.
4. **Male-mix kill number.** Not set.
5. **Under-18 deletion path.** Must exist in v1.

## Separate finding, not part of this build

The live `rec-2026-08-27-moveon-w2530-meta` record has `targeting.os: null`, which on Meta means all
devices. That ad is being served to iPhone women in Bangalore who cannot install anything when they
arrive. `targeting.py` supports Android-only on Meta properly — `to_meta` emits `user_os` (line 264)
and `meta_readback_checks` verifies it on read-back (line 294) — so this is a record that predates the
decision, not a missing capability. Worth fixing independently of this brief.

**Standing request from the app owner, 2026-08-28:** before any ad is pushed, confirm Android-only is
enabled. This should become a pre-launch gate in the rules, not a habit.

## Note — observation (2026-08-29)

Same two gates closed as rec-2026-08-29-moveon-lead-w1824-meta, same date, same asset: finished 1080x1920 render with Gabarito and real music, watermark cropped; Hinglish native-speaker read done. See that record's note for detail — one asset serves both ad sets.

## Note — observation (2026-08-29)

Same section-8 FAIL and owner override as rec-2026-08-29-moveon-lead-w1824-meta — one asset serves both ad sets; see that record and creatives/moveon-lead-w1830/qa.md.

## Execution

- Date: 2026-08-29
- Campaign ID: 6984366120881
- Ad set ID: 6984368402281
- Ad ID: 6984368441881

## Note — observation (2026-08-29)

Pushed PAUSED 2026-08-29, same run as rec-2026-08-29-moveon-lead-w1824-meta: tracked form 1048266097796124, same video asset, same read-back result, same open ra_lead percent-encoding question, same do-not-enable-before-the-end-to-end-test condition.

## Review

- Date: 2026-09-07
- Verdict: inconclusive
- Summary: RECONCILED 2026-09-07. Ledger said 'live'; the ad set is status ACTIVE but effective_status CAMPAIGN_PAUSED - stopped by its paused parent, not by itself - and its window closed 2026-09-03. IT DELIVERED AND IT PRODUCED LEADS: Rs 636.37 spend, 4,626 impressions, 88 link clicks, 551 video views, and 29 leads at Rs 21.94 per lead. Against budget.md's ~Rs 200/signup context for women that is cheap, and it took the whole campaign's CBO budget while its 18-24 sibling got nothing. VERDICT IS inconclusive ON THE REPO'S OWN GATE, not on judgement: the stated success metric is cost per lead, the sample is 29 leads, and MIN_SAMPLE is 30. One short. Calling it 'working' would be a guess dressed as a finding, and the gate exists precisely so that does not happen quietly. THE MORE IMPORTANT NUMBER IS DOWNSTREAM AND IT IS BAD: those 29 leads produced 4 page views on /get/w-apply and ZERO signups. So the on-platform form converts cheaply and almost nobody completes the journey past it. Cost per lead is therefore measuring something that is not yet worth what it costs, and the next Meta lead test should be judged on signups, not on leads.


