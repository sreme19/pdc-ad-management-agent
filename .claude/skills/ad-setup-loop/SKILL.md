---
name: ad-setup-loop
description: Recommend a new ad — campaign/ad-set/ad names, targeting, and creative — for Riteangle's Snap or Meta campaigns, write the recommendation to the ledger, create it on Snap PAUSED via snap-push (never enabled), and log the real IDs once it goes live. Use whenever the user asks to set up an ad, launch a campaign, try a new audience/creative, or asks what to build next after an ad-ideation or ad-intake idea was approved.
---

# Setting up an ad (mode 5)

## What this skill never does

This skill may create on Snap (`snap-push`, since 2026-08-26) and on Meta (`meta-push`, since
2026-08-27), and only ever `PAUSED`. It never enables, publishes, or changes the budget of anything
live, on either network — that boundary is
locked in `SPEC.md` and does not get relaxed later, even once a Claude plugin exists to "steer"
implementation. The plugin's job, if it ever exists, is telling the human what to click — never
clicking it.

## The standards to follow — read the source, don't improvise from memory

These are the actual product rules, and they may have been refined since you last read them:

- `rules/compliance.md` — hard, App-Store-enforced constraints. Read this first. Every recommendation
  gets checked against it before it's considered ready (see "Quality check" below).
- `rules/targeting.md` — audience personas, age/gender bands, geography, the provider-energy
  backend-vs-copy distinction.
- `rules/creative-style.md` — tone of voice, taglines, quotable first-party stats, visual identity,
  competitive landscape.
- `rules/creative-generation.md` — how an asset actually gets produced: the POV rule, the Grok Imagine
  prompt skeleton, the standing negative list, the plate/type split, and the QA gate every asset passes
  before it can be referenced by a proposal.
- `rules/funnel.md` — the three-axis funnel matrix and the friction ladder. Read it before promising
  a format: `snap-push` can build a static image into a web-view traffic ad and **nothing else**, so an
  approved idea calling for carousel, video or an on-platform lead form needs a `snap.py` change first.
  Say that up front rather than discovering it at push time. It also records that a phone field has no
  consumer yet and that lead forms are a re-run candidate, not a burned format.
- `rules/destinations.yaml` — the registry of landing pages and whose point of view each one's copy
  occupies. **This one is enforced in code:** `ad-agent propose` refuses to write a record whose ad-set
  audience doesn't match its destination's framing, and there is no override flag. Read it before
  promising the user an ad set can launch.
- `rules/naming.md` — the exact campaign/ad-set/ad naming convention. A name that doesn't match this
  breaks the spend/traffic join in `pocket-dating-coach`'s own analytics later — this is not cosmetic.
- `rules/budget.md` — the operating envelope, minimum viable daily spend, and the kill/double rule.
- `rules/tracking.md` — the UTM parameters every ad's Website URL must carry, and the pre-/post-launch
  verification checklist. Non-optional: a 2026-08-21 incident lost a full week of Snap spend to
  unattributable installs because this wasn't checked before launch.
- `rules/lead-delivery.md` — read before any Snap **lead-objective** ad. Snap's API-registered webhook
  silently never delivers (confirmed 2026-08-30, zero real leads reached `marketing_leads`); the
  delivery path of record is the native **Google Sheets direct integration**, connected in Ads Manager
  per form. A lead ad is not "set up" until its form is connected and a test report has landed — this
  is a manual UI step (`snap-push` cannot build lead forms), so it will never happen on its own.

If the user refines any rule mid-conversation, **edit the rule file itself in the same turn** — don't
just apply the change once and let it evaporate. The next `ad-audit` run, and the next session, both
depend on that file being current.

## Procedure

1. **Establish the brief.** What triggered this recommendation — an approved `ad-ideation` idea, an
   `ad-intake` finding, or a direct ask? Name the persona (`rules/targeting.md`), the network, and the
   one success metric this ad set is being tested against (landing-page views, taps, Bestie-conversation
   starts, signups — match it to the funnel stage in the campaign name).
1b. **If the funnel shape is new, write the funnel coverage table BEFORE deciding anything else** —
   the template and its rules are in `rules/tracking.md` ("The funnel coverage table"). One row per
   step a real person walks, with `Real-time?` and `Per-ad?` as separate yes/no columns and a
   three-valued verdict (✅ observed working · ❌ not measurable at the needed granularity · ❓ should
   work, never observed). Standing requirement from the app owner, 2026-09-05.

   Do it here, at the top, not at reporting time. On 2026-09-05 the table was produced *after* an ad
   was built and it changed the answer: it showed that the store-bound funnel's only real-time per-ad
   signal is the swipe, that Play Console lags ~6 days so a 2-day test is judged before its data
   exists, and that our own "installs" are really first-opens (139 acquisitions vs 71 first opens —
   about half of installers never open). Any of those three could have changed the ad set's
   optimisation goal, its duration, or its stated success metric. A ❓ row becomes a question in
   `research/questions/` in the same turn; it never gets rounded up to ✅.
2. **Decide names, following `rules/naming.md` exactly.** Campaign, ad set, ad — all three, plus the
   UTM parameters that go on the landing URL.
3. **Decide targeting** — persona, age band, gender, geography, interest categories, device targeting —
   per `rules/targeting.md`. State it as a short paragraph, not just a list of fields, since that's what
   goes into the brief.
4. **Decide the creative** — which existing asset under `creatives/` to use, or a brief for a new one to
   commission, following `rules/creative-style.md`'s tone, taglines, and visual identity. If it's a new
   asset, produce the Grok Imagine prompt pack per `rules/creative-generation.md` and take it through
   that file's §10 QA gate before referencing it here — nothing reaches `propose` without a recorded
   `pass`. **For a Flow→Grok video asset, obey `creative-generation.md` §2b when generating frames:**
   re-dress/re-locate through Flow + Nano Banana 2 (it preserves the face; Grok restyle doesn't), and
   generate each scene's 3-angle set from **one** Flow generation, not three fresh prompts of the same
   location — a Grok multi-reference batch holds a stable background only if the frames are
   same-generation siblings, otherwise drop to a single frame or the clip travels
   (`lrn-2026-08-30-grok-multiref-must-be-same-generation`). Every Flow still passes
   `strip_flow_watermark` (150px); crop the Grok wordmark (90px) after motion.
4b. **Check the destination before you write a brief around it.** Name the landing URL this ad set will
   send traffic to and look it up in `rules/destinations.yaml`. If its `audience` doesn't match the ad
   set's gender, or `paid_traffic` is false, or the page isn't registered at all, `propose` will refuse
   the record — so surface that to the user *now*, not after the brief is written. Unblocking means
   building the page and registering it; there is no flag that skips this.
5. **State a budget cap and duration**, per `rules/budget.md` — never omit this. Default to the
   ₹800–1,200/day minimum viable range unless there's a specific reason to go higher or lower; say the
   reason if you deviate.
6. **Quality check before handing anything off.** Run the finished ad-set name, targeting summary, and
   creative brief/copy back against `rules/compliance.md` explicitly — show a short table: each
   compliance rule against how this recommendation satisfies it, or note plainly why a rule doesn't
   apply. This mirrors job-hunt-agent's own observability-trace requirement; don't skip it because the
   copy "feels obviously fine." Per Sree's own note, prefer a second, independent pass (a fresh
   session/model) over trusting the same reasoning pass that wrote it.
7. **Write the brief to a file**, then log the proposal — this is a pure file write, no API call:
   ```
   ad-agent propose <slug> \
     --network <key from rules/networks.yaml> \
     --campaign-name "..." --ad-set-name "..." --ad-name "..." \
     --targeting-summary "..." --creative-ref "creatives/<path-or-id>" \
     --destination-url "https://www.riteangle.dating/<page>" \
     --budget-cap <INR/day> --duration-days <n> \
     --brief /tmp/brief.md \
     --gender FEMALE|MALE --min-age <n> --max-age <n|50+> --countries in \
     [--os ANDROID|IOS] [--expansion on|off] \
     [--from-idea <idea-id>]
   ```
   **The record carries its audience twice, and both are required.** `--targeting-summary` is the prose
   reasoning a human reads; the `--gender`/`--min-age`/`--max-age`/`--countries`/`--os` flags build the
   normalized block `snap-push` actually pushes. Prose cannot be pushed and a spec cannot explain
   itself. Two checks will refuse the proposal: `--min-age` below 18 (`rules/compliance.md`, no
   exceptions), and targeting that disagrees with the gender token in the ad-set name — one of the two
   is wrong and it is not safe to guess which.

   **If this came from an approved `ad-ideation`/`ad-intake` idea, pass `--from-idea <idea-id>`.** That
   closes the idea out, so it stops appearing in `ad-agent open` as one nobody acted on.

   This prints the generated `rec_id` and the record's path. Show the user the full brief and the
   `rec_id` plainly — that id is what they'll need for the next step.
8. **Build it, or hand it back — which one depends on the network.**

   **On Snap, offer to create it.** `ad-agent snap-push <rec_id>` creates the campaign, ad squad,
   creative and ad — **always `PAUSED`** — then reads each object back and diffs it against the plan.
   Start with `--dry-run`, which prints the plan, checks the parent campaign's spend cap, and creates
   nothing:
   ```
   ad-agent snap-push <rec_id> [--headline "..."] --dry-run
   ad-agent snap-push <rec_id> [--headline "..."]
   ```
   It will refuse a record with no structured targeting, a creative with no recorded QA `pass`, and —
   the one worth explaining to the user — **an ad squad whose parent campaign carries a lower spend
   cap.** A campaign-level cap silently overrides a larger ad-squad budget; that is how the first live
   women's set ended up running at ₹300/day against a ₹1,000/day plan, below `rules/budget.md`'s floor,
   which made its result inconclusive before a rupee was spent. Fixing the cap in Ads Manager is one
   click. `--accept-campaign-cap` proceeds anyway as a stated deviation, and prints the `note` command
   to record it.

   **On Meta, use `ad-agent meta-push <rec_id> --dry-run` first, then the real run.** Same shape as
   `snap-push` and the same gates. Three Meta-specific things to surface to the user rather than
   discover mid-run: **no pixel is needed** (Meta binds the dataset at account level, unlike Snap —
   don't tell the user to go set one up); the ad account must settle in **INR** or the client refuses,
   because Meta budgets are paise and Snap's are micro (the live account is INR, confirmed
   2026-08-27); and a **campaign-budget-optimisation parent is refused outright with no escape
   hatch**, because it ignores the ad-set budget rather than capping it, which makes the record's
   stated budget meaningless.

   Read the read-back diff rather than skimming it: **Meta rewrites targeting it considers suboptimal
   instead of rejecting it**, so an ad set created with Advantage Audience off can come back on with
   the POST still returning 200. On an age-banded women's test that silently answers a different
   question than the record was created to ask — treat it as a decision for the user, not a shrug.

   If there is no `meta:` block in `config.local.yaml` yet, this stays a hand-back: tell the user
   exactly what to name each level and what to paste into targeting/budget fields — a checklist they
   can follow without re-deriving anything. Include the full UTM string verbatim; note that Meta reads
   `utm_content` as the ad-level id where Snap reads `utm_id` (`rules/networks.yaml`), so don't cross
   the two conventions.
8b. **Lead-form connection — for Snap lead-objective ads only, before the ad goes live.** Per
   `rules/lead-delivery.md`: a Snap lead ad's form must be connected to a Riteangle leads Google Sheet
   (Ads Manager → the ad → Edit → Lead form → Connect form to CRM → Google Sheets → sign in → pick a
   dedicated per-form sheet → Send test report → confirm the row lands). The API webhook does not
   deliver, and `snap-push` cannot build lead forms, so this is a manual UI step that must be done and
   verified explicitly — the ad is not "set up" without it. It is not retroactive: pull any pre-connection
   backlog by hand (Ads Manager → Download → Account leads, 90-day clock).
9. **Pre-launch tracking check — before the ad goes live, every time.** Per `rules/tracking.md`: open
   the ad's actual Website URL field and confirm every macro (`utm_term`, `utm_id`, `utm_content`) is
   present and set at the ad level, then click the ad's own preview/swipe-up link and confirm the
   resulting URL has every macro resolved to a real value, not left blank or literal
   (`{{adSet.id}}`/`{{ad.id}}`). Tell the user to do this and confirm back before spend starts — do not
   treat it as implied by "the ad is set up."

## Closing the loop — do this every time, don't let it go unresolved

Once the user says the ad is live (or comes back later with the real IDs), log it — this is what lets
`ad-audit` later join a real outcome back to this exact recommendation:

```
ad-agent log-setup <rec_id> --network <key> \
  --campaign-id <real> --ad-set-id <real> --ad-id <real> \
  [--deviated "what changed from the brief, and why"]
```

After a `snap-push` this command is printed for you with the real ids already filled in — but it is
still not run until the user has *enabled* the ad, because `live` means spending, not created.

**Then, within the first hour of real traffic, run the post-launch check from `rules/tracking.md`:**
confirm `pocket-dating-coach`'s `user_acquisition` rows for this network since launch carry the real
`utm_term`/`utm_id`, not the landing page's hardcoded default. `log-setup` is not done until this has
been checked once against live data — an id logged without a verified live check is exactly the gap
that let the 2026-08-21 incident run for a full week undetected. If the check shows the default is
firing, tell the user immediately and treat it as a live incident, not a note for the next `ad-audit`.

If the proposal needs correcting before it's executed — a name that doesn't parse against
`rules/naming.md`, a creative ref pointing at the wrong folder, a budget the user revised — amend it
rather than hand-editing the record, so the change is recorded instead of silently overwriting what was
proposed:

```
ad-agent amend <rec_id> --reason "why" [--ad-name "..."] [--creative-ref "..."] [...]
```

Only works while the record is still `proposed`. Once it's `live`, a difference between brief and
reality is a `log-setup --deviated` note, not an amendment — the record has to keep saying what was
actually built. Amending `--ad-set-name` or `--destination-url` re-runs the destination gate.

If anything changes while the ad set is running — the budget raised, a day paused, a tracking wobble —
record it. `amend` will refuse a live record, and that is deliberate; use a note instead:

```
ad-agent note <rec_id> --kind budget|targeting|creative|incident|observation --text "what changed, and why it matters to the verdict"
```

This is what stops `ad-audit` judging a result against conditions that moved underneath it.

If the user decides not to execute a proposal at all, close it out explicitly rather than leaving it to
rot as `proposed` forever:

```
ad-agent abandon <rec_id> --reason "..."
```

## The one rule that never changes

**You never start spend.** Not by enabling an ad set, not by raising the budget of one already live,
not on any network. That is the user's action in Ads Manager, every time.

What changed, by the app owner's explicit decision, twice: on **Snap** from 2026-08-26 and on **Meta**
from 2026-08-27, you may now *create* objects — and only ever `PAUSED`, on both. The two networks are
at parity on what is permitted; they are not at parity on what is *wired*, so check for a `meta:` block
in `config.local.yaml` before promising the user a Meta push.

Be precise about why the line sits there. A paused object spends nothing, can be inspected in the UI,
and can be deleted; the moment that matters is not creation but enablement. So the agent does the
tedious, error-prone part — forty fields typed correctly, every UTM parameter written literally rather
than as a macro that can silently fail — and never the part where money starts moving. This is enforced
in `snap.py`, which refuses any outbound request carrying an enabling status or a budget change to an
existing object, not merely promised here.
