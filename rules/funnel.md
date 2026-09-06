# Funnel rules — the search space every idea is drawn from

Source: Sree's 2026-08-27 session direction, recorded verbatim as
`research/notes/note-2026-08-27-womens-funnel-matrix.md`. This file exists because that direction is
**normative and standing** — "keep this entire matrix in front of you" is an instruction about what a
skill is allowed to propose, not an observation about the world, and the research store explicitly
cannot bind anything.

## 1. The funnel is a matrix, not a path — read this before proposing anything

Riteangle's women's funnel has one combination running: **static image → landing page → Play Store**.
That is one cell of a three-axis space, and it is the running cell for historical reasons, not because
the other cells were tested and rejected.

| axis | running today | the rest of the axis |
|---|---|---|
| **ad format** | static image, text overlay | carousel, video |
| **capture point** | none — the page hands off to the Play Store | on-platform lead form, email capture on the landing page, phone capture |
| **follow-up channel** | none — the install is the terminal event | call centre (outbound voice), WhatsApp |

**The axes are mix-and-match.** A video ad into an email capture consumed by WhatsApp is a legitimate
proposal shape; so is a carousel into the existing Play Store handoff. An idea that only ever varies
the creative angle inside the running cell has searched one column of this table.

**Do not drop an option because its prerequisites are missing.** The operator's instruction is
explicit that the unbuilt pieces are sequencing problems he intends to solve, not refusals. A blocked
option is a `hold` with a stated `--blocked-on`, never an option that goes unmentioned.

**The stated goal is women's leads.** The app download is what the current funnel happens to aim at.
Do not treat installs as the objective when a proposal could produce a contactable lead instead.

## 2. Sequence by friction, least first — and the ladder is not the obvious one

`ad-agent propose` and `snap-push` can only build the running cell. **Every other cell on this table
costs a code change, a change in another repo, or a legal entity** — see
`lrn-2026-08-27-matrix-options-are-code-changes`, which read the literals out of `snap.py` directly.

| rung | option | what it actually costs |
|---|---|---|
| 0 | another static image | nothing — the only thing pushable today |
| 1 | carousel / video | **video is built**: `upload_media` takes `IMAGE` or `VIDEO` and every creative path is media-type agnostic. The Snap analogue of a carousel is the **Story ad** — a `COMPOSITE` creative wrapping a tappable sequence of `WEB_VIEW` snaps, paired with `ad_type="STORY"` — built as `ad-agent snap-push-story`. Its children may only be `WEB_VIEW`/`DEEP_LINK`, so **a Story ad cannot carry a lead form**: that combination is still a genuine platform limit, not a code gap |
| 2 | email capture on `/get/w` | `pocket-dating-coach` route change, plus storage and consent |
| 3 | on-platform lead form | **built — no longer a code change.** `snap.py` now has `create_lead_campaign` (`LEAD_GENERATION`), `create_lead_adsquad` (`LEAD_FORM_SUBMISSIONS`), `create_lead_form`/`find_lead_form`, `create_lead_creative` and `create_lead_ad`, driven by `ad-agent snap-push-lead`; `upload_media` takes `VIDEO` as well as `IMAGE`. First run 2026-08-29. **The remaining cost is manual, not code:** the form must be connected to a Google Sheet by hand per `rules/lead-delivery.md`, or its leads never arrive |
| 4 | phone capture | rung 2's cost, and the consumer does not exist — see §3 |
| 5 | WhatsApp | in neither `networks.yaml` nor `destinations.yaml`; would run on Meta, where `creation: none` and no credential exists |

**Re-verify rung 1 and 3 against `snap.py` before quoting them.** That row is a claim about code on a
60-day clock, and one commit invalidates it. The code is the authority, not this table.

`budget.md`'s ₹800–1,200/day floor funds one or two ad sets at a time, so the ladder is a real
constraint and not a preference — the matrix has more testable cells than the budget can read at once.

## 3. Two corrections that a proposal must not get wrong

**On-platform lead forms are not untried, and not burned.** They ran, and returned 98% male
submissions — but `creative-generation.md` §1 attributes that to creative POV plus a submit-optimised
objective, and leaves the format itself unjudged. Both causes have since changed: the POV rule now
exists, and `/get/w` exists as a women-framed destination. Treat lead forms as a **re-run candidate**.
Do not cite the 98/2 split as evidence against the format — and note that no sample size or date range
is recorded for it anywhere (`q-2026-08-27-the-98-2-split-has-no-n`).

**A phone field has no consumer today.** The call centre is blocked on a company that is not
registered. Phone capture is therefore not a reason to add a field to `/get/w`; **email is the field to
test first** on that page. Re-read this section when the registration status changes —
`lrn-2026-08-27-callcentre-blocked-on-registration` carries the review date.

## 3b. One ad per squad on the Snap lead funnel — or admit you are not testing creative

**Normative from 2026-09-07** (`lrn-2026-09-07-shared-squad-destroyed-per-ad-attribution`), and it is
a rule about what a test can *mean*, not about tidiness.

A Snap lead form's end page is fixed when the form is created, which is **before the ad exists**. So
its install referrer carries the **ad squad** id and no ad id — there is no `utm_id` to carry one. Put
four ads in one squad and the outcomes arrive as one number with four possible parents, permanently.
Not hard to untangle: impossible, because the distinguishing field was never written.

That is not hypothetical. Squad `85c2e782` carried four lead ads — MOVE-ON, BUILD-YOURSELF,
MOVE-ON-SWAGGER, KNOW-YOUR-WORTH — and produced **13 signups, the only signups any Snap funnel has
ever produced**, at ₹113 each against a ₹200 target. None of the four can claim them. Snap's own
stats split the *cost* cleanly (74% / 14% / 7% / 6% of impressions); `user_acquisition` has only the
squad, so the *outcome* cannot be split at all. **Cost is attributable and outcome is not, which is
the worst possible pairing**: it looks like four tested hooks and it is one unreadable number plus
three hooks that were never tested.

So, when proposing a Snap lead ad:

- **One ad per squad** if the point is to compare creatives. The squad id *is* the attribution key.
- If several ads must share a squad, **say in the brief that creative attribution is being given up**,
  and name the one thing the squad as a whole is testing. A shared squad is a budget decision, never
  a creative test.
- There is no third option. Choosing by default is how four hooks became one number.

**This does not apply to Snap TRAFFIC ads**, whose creative URL is rewritten after the ad exists and
so carries `utm_id` — see `lrn-2026-09-05-traffic-carries-ad-id-lead-cannot`. Do not generalise the
rule to the funnel that does not need it.

## 4. What this file does not do

It does not authorise anything. A cell on this table still passes every other gate: `compliance.md`
first, `destinations.yaml`'s audience match (no override flag), `budget.md`'s floor, `networks.yaml`'s
`creation` field. Widening the search space is not widening what may ship.
