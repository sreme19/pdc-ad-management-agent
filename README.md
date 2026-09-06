# ad-management-agent

A loop-engineered, harness-driven ad-operations agent for Riteangle (the product; consumer-facing
codebase is `pocket-dating-coach`). Runs entirely inside Claude Code sessions — **no Anthropic API key
anywhere in this repo.** The actual reasoning (targeting, creative, research) happens live in whichever
Claude Code session is running one of the skills below; this repo's CLI only persists results
deterministically. See `SPEC.md` for the full architecture and every locked decision behind it.

## The modes

| Skill | Mode | What it does |
|---|---|---|
| `ad-setup-loop` | 5 | Recommend campaign/ad-set/ad names, targeting, and creative; log the recommendation; create it on Snap `PAUSED`; log the real IDs once it goes live. |
| `ad-audit` | 6 | Pull live performance data, join it back to the ledger, write a working/not-working/inconclusive verdict — which propagates to the creative's prompt pack and the learnings behind it. |
| `ad-ideation` | 7 | Deep research into what to try next; every idea ends in a recommend/hold verdict with an estimated spend. Approval hands off to `ad-setup-loop`. |
| `ad-intake` | 8 | Learn from an ad you found elsewhere (screenshot, competitor link); ingest it, derive the lesson, optionally turn it into an idea. |
| `ad-research` | 9 | Work an open question, ingest notes you bring in, derive durable learnings into `research/`. |

All are manual-trigger-only — ask for what you want in a Claude Code session rooted here ("set up an ad
for the casual-selective women persona," "how are the live ads doing," "find me some new ideas," "look
at this ad I found," "here are my notes on Truecaller") and the relevant skill runs. You should never
need to remember a skill's name; describing the task is the interface.

### What this agent may and may not touch

Amended by the app owner on 2026-08-26, after the trade-off was put to them. Both halves matter:

- **Snap: creation is allowed, enabling is not.** `ad-agent snap-push` creates campaigns, ad squads,
  creatives and ads on Snap, **only ever with status `PAUSED`**, and reads every object back from the
  API to diff it against the plan before it exits. There is no enable, resume or activate call
  anywhere in `snap.py`, and none is to be added without the app owner saying so in as many words.
  **Starting spend is a human action in Ads Manager, every time.**
- **Meta: creation is allowed, enabling is not — same terms as Snap, since 2026-08-27.**
  `ad-agent meta-push` creates campaigns, ad sets, creatives and ads `PAUSED` and diffs each back.
  There is no enable/resume/activate call in `meta.py`, and it additionally cannot delete or archive
  anything, because `ad-audit` has to be able to read a pushed ad set months later. Three Meta-only
  guards: budgets are paise (100/rupee) not Snap's micro, so a non-INR account is refused rather than
  FX-guessed; an update is a `POST` to a bare object id rather than a `PUT`, so the budget guard keys
  off the path and not the method; and a campaign-budget-optimisation parent is refused outright,
  because it ignores the ad-set budget rather than capping it.
  **A credential still has to exist for any of this to run** — `config.local.yaml`'s `meta:` block is
  the gate, and `MetaClient` refuses construction without it.
- **Never change the budget of anything already live**, on either network.

Be clear about what this cost. The old rule ("never touches a live account") was true *by
construction* — the repo held no credential that could reach a live account. It is now true only
because this code is careful, which is a weaker guarantee. The paused-only rule is what carries the
weight instead. See `SPEC.md` decisions #3 and #10 for the full reasoning.

## Rules — the single source of truth every skill reads live

- `rules/compliance.md` — hard, App-Store-enforced constraints (money/provider language is banned from
  ad copy; the backend may still model it as a real preference — see the file for why that's not a
  contradiction).
- `rules/targeting.md` — audience personas, age/gender bands, geography.
- `rules/creative-style.md` — tone of voice, taglines, quotable first-party stats, visual identity,
  competitive landscape.
- `rules/creative-generation.md` — how an asset actually gets produced: the POV rule, the
  plate/typography split, the standing negative list, and the two-stage QA gate.
- `rules/naming.md` — the campaign/ad-set/ad naming convention already in production use.
- `rules/budget.md` — the operating envelope, the minimum viable daily spend, and the kill/double rule.
  Its three enforceable figures are mirrored in `budget.py`, which is the only place code reads them
  from — change both in the same commit.
- `rules/destinations.yaml` — the destination registry. Backs a hard gate: `propose` refuses to point
  an ad set at a page written for a different audience, and there is no override flag.
- `rules/networks.yaml` — the network registry. What each network's UTM conventions are, which
  parameter its analytics joins the ad on (Snap and Meta genuinely differ), and whether this agent may
  create anything on it. **That last field can only ever refuse** — it is consulted in addition to a
  command's own checks, never instead of them, so editing it cannot grant a capability.

`destinations.yaml` and `networks.yaml` are the two rule files the CLI reads directly; everything else
under `rules/` is prose a skill reads live.
- `rules/tracking.md` — the UTM parameters every ad must carry and the pre-/post-launch verification
  checklist; a 2026-08-21 incident lost a week of Snap spend to unattributable installs by skipping it.

If a rule gets refined mid-conversation, the skill edits the file in place — these are living
documents, not a snapshot.

## The research loop

`research/` and `ideas/` hold what the agent learns; `campaigns/` holds what it does. **They are not
`rules/`, and the precedence is absolute: `rules/` is normative and always wins, research is evidence
and hypotheses and constrains nothing.** A claim becomes binding only when a human promotes it into a
rules file. See `research/README.md` for the full reasoning and the four stores.

```
question ──→ research ──→ note ──→ learning ──→ idea ──→ propose ──→ live ──→ verdict
    ↑                                  ↑                                          │
    └───── raised by any stage ────────┴───────── log-evidence ───────────────────┘
```

Two things make it a loop rather than a growing pile:

- **The open-question queue.** A research pass starts by popping from it, not from "go look into
  women's ads". Every other mode fills it — an `inconclusive` audit verdict, an idea held pending
  research, an intake raising a why-does-this-work.
- **`log-evidence`, the back-edge.** When a campaign returns a verdict, that verdict lands on the
  learning that produced the recommendation and marks it supported, contradicted or mixed. Without
  it the library only ever grows and never corrects itself — and a store that confidently records
  wrong things is worse than no store.

Confidence is gated rather than self-declared: only `live-data` and `platform-doc` claims may be
`high`, and a `live-data` claim below `MIN_SAMPLE = 30` can only be `low` (SPEC.md decision #6). That
exists because `rules/targeting.md` already carries dated observations with no source attached, and
the live women's record cites one of them to justify a ₹5,000 spend with no way to check what it rested
on.

## The ledger

`campaigns/<slug>/record.md` — one markdown file per recommendation, YAML front matter + an appended
section per lifecycle stage (`proposed → executing → live → reviewed`, or `abandoned`). `INDEX.md` at
the repo root is generated by every ledger command — never hand-edit it.

## Commands

**Start with `ad-agent open`.** It is the one command worth remembering: every loose end the ledger
can see, in one place — proposals never executed, live ad sets past their review window, creative that
cleared QA and was never used, funding below `rules/budget.md`'s floor. Coming back to this repo after
time away, that is the "where was I" answer. Everything else is reachable from what it prints.

The rest you rarely type — a skill runs them for you. The list below is generated from the CLI itself
by `ad-agent commands --write`, so it cannot drift out of date the way its hand-maintained predecessor
did; `wiki-export/Command-Cheatsheet.md` carries the same list with the reasoning behind each command.

<!-- BEGIN GENERATED: ad-agent commands -->
<!-- Generated by `ad-agent commands --write`. Do not hand-edit this block. -->

| command | what it does |
|---|---|
| `propose` | Record a mode-5 recommendation before you execute it |
| `snap-leads` | Register/inspect where Snap delivers lead-form submissions (webhook, per form) |
| `snap-audience` | Create/grow a Snap Custom Audience or build a Lookalike from one |
| `snap-push` | Create a proposed recommendation in Snap Ads Manager, PAUSED, then diff it back |
| `snap-push-story` | Create a proposed Story Ad (COMPOSITE: a tap-through sequence of WEB_VIEW snaps) on Snap, PAUSED, then diff it back |
| `meta-push` | Create a proposed recommendation in Meta Ads Manager, PAUSED, then diff it back |
| `snap-push-lead` | Create a proposed LEAD recommendation (video + on-platform form) on Snap, PAUSED, then diff it back |
| `meta-push-lead` | Create a proposed LEAD recommendation (video + instant form) in Meta, PAUSED, then diff it back |
| `amend` | Revise a still-proposed recommendation, with an audit trail of what changed |
| `verify-tracking` | Run rules/tracking.md's post-launch check against live user_acquisition data for a live recommendation |
| `log-setup` | Record the real IDs after setting the ad up by hand |
| `note` | Append a dated note to a record — for things that change mid-run |
| `log-review` | Record mode-6's verdict on a live recommendation |
| `abandon` | Close out a recommendation that was never executed |
| `stats` | Deterministic counts over the ledger |
| `dump-ledger` | Print the ledger index |
| `ingest` | Store a note you brought in, verbatim and immutable, as provenance for learnings |
| `learn` | Record one derived claim, with the source kind and confidence that make it citable |
| `log-evidence` | Attach a dated outcome to a learning — the back-edge that lets it be corrected |
| `reclassify` | Correct how a learning is filed — subject, source, confidence — not what it claims |
| `promote` | Record that a learning has graduated into a rules file and is now normative |
| `retire` | Close out a learning that is no longer worth carrying |
| `question` | Add an open research question to the queue that drives the next research pass |
| `answer` | Close an open question, optionally naming what it taught |
| `idea` | Record a recommend/hold idea with the spend it would take to test it |
| `open` | Every loose end the ledger can see — start here when you come back to this repo |
| `commands` | Print the command list, or regenerate it in README and the wiki cheatsheet |
| `fetch-analytics` | Pull pocket-dating-coach's ad analytics via the authenticated internal endpoint |

#### `propose`

```
ad-agent propose [-h] --network NETWORK --campaign-name CAMPAIGN_NAME --ad-set-name AD_SET_NAME --ad-name AD_NAME --targeting-summary TARGETING_SUMMARY --creative-ref CREATIVE_REF --destination-url DESTINATION_URL [--budget-cap BUDGET_CAP] [--duration-days DURATION_DAYS] --brief BRIEF [--from-idea FROM_IDEA] --gender {FEMALE,MALE} --min-age MIN_AGE --max-age MAX_AGE --countries COUNTRIES [--os {ANDROID,IOS}] [--expansion {on,off}] slug
```

#### `snap-leads`

```
ad-agent snap-leads [-h] [--form-id FORM_ID] [--url URL] [--integration-id INTEGRATION_ID] {forms,list,register,test,delete}
```

#### `snap-audience`

```
ad-agent snap-audience [-h] [--name NAME] [--file FILE] [--description DESCRIPTION] [--seed-name SEED_NAME] [--country COUNTRY] [--similarity {REACH,BALANCE,SIMILARITY}] {list,upsert,lookalike}
```

#### `snap-push`

```
ad-agent snap-push [-h] [--headline HEADLINE] [--cta CTA] [--optimization-goal OPTIMIZATION_GOAL] [--dry-run] [--accept-campaign-cap] rec_id
```

#### `snap-push-story`

```
ad-agent snap-push-story [-h] [--headline HEADLINE] [--preview-headline PREVIEW_HEADLINE] [--cta CTA] [--dry-run] [--accept-campaign-cap] rec_id
```

#### `meta-push`

```
ad-agent meta-push [-h] [--headline HEADLINE] [--message MESSAGE] [--cta CTA] [--dry-run] [--accept-campaign-cap] rec_id
```

#### `snap-push-lead`

```
ad-agent snap-push-lead [-h] (--video VIDEO | --image IMAGE) [--headline HEADLINE] [--form-id FORM_ID] [--dry-run] [--accept-campaign-cap] rec_id
```

#### `meta-push-lead`

```
ad-agent meta-push-lead [-h] --video VIDEO --message MESSAGE [--form-id FORM_ID] [--dry-run] [--accept-campaign-cap] rec_id
```

#### `amend`

```
ad-agent amend [-h] --reason REASON [--campaign-name CAMPAIGN_NAME] [--ad-set-name AD_SET_NAME] [--ad-name AD_NAME] [--targeting-summary TARGETING_SUMMARY] [--creative-ref CREATIVE_REF] [--destination-url DESTINATION_URL] [--budget-cap BUDGET_CAP] [--duration-days DURATION_DAYS] [--gender {FEMALE,MALE}] [--min-age MIN_AGE] [--max-age MAX_AGE] [--countries COUNTRIES] [--os {ANDROID,IOS}] [--expansion {on,off}] rec_id
```

#### `verify-tracking`

```
ad-agent verify-tracking [-h] [--since SINCE] [--detail] rec_id
```

#### `log-setup`

```
ad-agent log-setup [-h] --network NETWORK --campaign-id CAMPAIGN_ID --ad-set-id AD_SET_ID --ad-id AD_ID [--deviated DEVIATED] rec_id
```

#### `note`

```
ad-agent note [-h] --text TEXT [--kind {budget,targeting,creative,incident,observation}] rec_id
```

#### `log-review`

```
ad-agent log-review [-h] --verdict {working,not-working,inconclusive} --summary SUMMARY [--review-log REVIEW_LOG] [--learning LEARNING] rec_id
```

#### `abandon`

```
ad-agent abandon [-h] --reason REASON rec_id
```

#### `stats`

```
ad-agent stats [-h]
```

#### `dump-ledger`

```
ad-agent dump-ledger [-h] [--status {proposed,executing,live,reviewed,abandoned}]
```

#### `ingest`

```
ad-agent ingest [-h] --title TITLE --source {live-data,platform-doc,source-code,own-research,competitor-observation,intuition} (--file FILE | --text TEXT) [--slug SLUG]
```

#### `learn`

```
ad-agent learn [-h] --claim CLAIM --subject {audience,creative,channel,tracking,competitor,product,budget} --source {live-data,platform-doc,source-code,own-research,competitor-observation,intuition} --confidence {high,medium,low} [--sample-n SAMPLE_N] --evidence EVIDENCE [--derived-from DERIVED_FROM] [--answers ANSWERS] [--slug SLUG]
```

#### `log-evidence`

```
ad-agent log-evidence [-h] --outcome {supported,contradicted,inconclusive} --text TEXT [--from FROM_REF] learning_id
```

#### `reclassify`

```
ad-agent reclassify [-h] --reason REASON [--subject {audience,creative,channel,tracking,competitor,product,budget}] [--source {live-data,platform-doc,source-code,own-research,competitor-observation,intuition}] [--confidence {high,medium,low}] [--sample-n SAMPLE_N] learning_id
```

#### `promote`

```
ad-agent promote [-h] --rule RULE learning_id
```

#### `retire`

```
ad-agent retire [-h] --reason REASON learning_id
```

#### `question`

```
ad-agent question [-h] --text TEXT --kind {audience,creative,channel,tracking,competitor,product,budget} --why WHY [--raised-by RAISED_BY] [--slug SLUG]
```

#### `answer`

```
ad-agent answer [-h] --text TEXT [--learning LEARNING] [--dropped] question_id
```

#### `idea`

```
ad-agent idea [-h] --title TITLE --verdict {recommend,hold} --network NETWORK --persona PERSONA --est-daily EST_DAILY --est-days EST_DAYS --rationale RATIONALE [--learning LEARNING] [--blocked-on BLOCKED_ON] [--slug SLUG]
```

#### `open`

```
ad-agent open [-h]
```

#### `commands`

```
ad-agent commands [-h] [--write] [--check]
```

#### `fetch-analytics`

```
ad-agent fetch-analytics [-h] --start START --end END [--currency {INR,USD}] [--network NETWORK] [--audience {all,men,women,unknown}] [--out OUT]
```
<!-- END GENERATED: ad-agent commands -->

## Setup

```
cp config.example.yaml config.local.yaml   # then fill in pdc.api_key once it exists
pip install -e .
```

On a machine whose system Python predates 3.10 (this project's floor), skip `pip` and let `uv` manage
the environment — `uv run ad-agent <command>` works with no install step at all.

## Tests

```
pip install -e ".[dev]" && pytest tests/ -q     # or: uv run --extra dev pytest tests/ -q
ruff check .                                    # or: uv run --extra dev ruff check .
ad-agent commands --check                       # docs and skills still match the CLI
```

All three run on every push and pull request via `.github/workflows/checks.yml`, plus a staleness check
on the generated command list.

The suite covers the promises this repo makes in prose, on the principle that a rule stated only in a
docstring is not a rule:

- **The paused-only invariant** (`test_snap_safety.py`) — every enabling spelling is refused, at every
  nesting depth Snap's list-wrapper format can hide one; budget fields are refused on a `PUT` but
  allowed on creation; the real create/rewrite calls still pass; and a refused request never reaches
  the network.
- **The destination gate** — an audience/page mismatch, an unregistered page, a page that can't take
  paid traffic, a name with no gender token, and that `amend` cannot launder any of them.
- **Structured targeting** — the 18+ floor, the ad-set-name agreement check, patch-not-replace on
  `amend`, and that the Snap read-back diff is derived from the record rather than a literal.
- **The campaign-cap gate** — all six branches, including the exact 2026-08-26 case.
- **The UTM scheme** — all five parameters, `utm_id` carrying the ad id, and no unresolved macro.
- **`open`** — every loose-end category, and that a quiet report still names what it cannot see.
- **The docs** — `commands --check` runs against the real README and cheatsheet, so the day this
  repo grows a command without documenting it, the suite fails.

`fetch-analytics` is wired up but non-functional until a small `pocket-dating-coach` PR (adding
`/api/internal/ad-analytics`, authenticated via `ADS_AGENT_API_KEY`) ships — see `SPEC.md`, "Open /
deferred."

## Keeping your laptop in sync

This repo lives in three places: your laptop, a cloud Claude Code sandbox (ephemeral — reclaimed after
inactivity), and GitHub. The sandbox pushes to GitHub after every change, so GitHub is always current.
Your laptop needs to pull on its own — `scripts/sync.sh` does that (and pushes anything you've committed
locally), safely: it never force-pushes and never discards uncommitted work.

Run it manually, or schedule it — e.g. on macOS, `crontab -e` and add:

```
*/30 * * * * /path/to/ad-management-agent/scripts/sync.sh >> /tmp/ad-agent-sync.log 2>&1
```

## Data access

Two channels into `pocket-dating-coach`'s data, deliberately not one — see `SPEC.md` decision #7 for
the full reasoning:

1. **`fetch-analytics`** — the authenticated internal endpoint, returning the exact same computed
   metrics the admin dashboard shows. Always the answer for a rate, tap rate, or verdict.
2. **A least-privilege read-only Postgres role** (`ads_agent_ro`), scoped to marketing/spend tables
   only — never member data — for raw exploratory queries the endpoint doesn't answer. Never used to
   recompute anything channel 1 already owns.

## Creatives

`creatives/` builds up incrementally — see `creatives/README.md`.
