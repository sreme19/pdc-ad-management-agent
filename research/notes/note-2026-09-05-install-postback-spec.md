# Install postback to Snap — the spec, for `pocket-dating-coach` to build

**Written 2026-09-05 in `ad-management-agent`, for a build that belongs in `pocket-dating-coach`.**
Recorded here because this repo is where the gap was found and where the consequence is felt; nothing
in this note is a change to this repo, and no branch was pushed anywhere.

## The problem, in one paragraph

The live direct-to-store Snap ad (`rec-2026-09-05-moveon-getw-w1830-snap`) optimises on `SWIPES`,
because that is the only outcome Snap can observe. Snap has no idea which swipes became installs, so
it is buying **the cheapest tap**, which is not the cheapest user and can be actively opposed to it —
the cheapest taps come from people most willing to tap and least likely to follow through. Every other
gap in the funnel table (`rules/tracking.md`) is a *reporting* problem we can work around. This one is
a *delivery* problem: the network is optimising against the wrong target, and no amount of careful
reading fixes that after the fact.

## CORRECTION, 2026-09-05, same day — most of this spec was answered before it was written

**Everything below the next two headings was drafted on the belief that no conversion postback
existed. One does. It is built, live, and healthy.** Read this section first; the routes A/B analysis
that follows is kept for the record but is largely moot.

`pocket-dating-coach/src/lib/server/marketing-conversions.ts` posts server-side conversions to
**Snap's CAPI** (`https://tr.snapchat.com/v2/conversion`) as `CUSTOM_EVENT_1`, against pixel
`0657d30b-4d65-414b-b9a9-65edb4aa1e07` — **the same pixel id this repo already attaches to every ad
squad** (`snap.pixel_id`). It is a considered implementation: a `keepalive` beacon hands the tap to
our own server so the report survives the page navigating away (the client-side pixel flushes on a
~1s timer and every CTA leaves for Play in ~6ms, which is why Custom event 1 sat at zero while page
views climbed), ad blockers cannot suppress it, and `event_id` dedups the browser and server copies.

Measured from `marketing_store_clicks` on 2026-09-05 — it works:

| Week | store clicks | forwarded to Snap | forwarded to Meta |
|---|---|---|---|
| 2026-08-31 | 65 | 65 | 65 |
| 2026-08-24 | 37 | 37 | 32 |
| 2026-08-17 | 125 | 125 | 0 |

`/get/w` alone: 57 store clicks, **57 forwarded to Snap**, most recent today. Meta forwarding was
badly broken through mid-August ("API access blocked", OAuthException code 200) and has been clean
since the week of 2026-08-31 — a resolved incident, not a live one.

**So the real finding is the opposite of this note's premise.** The conversion pipe is not missing;
it is attached to the *landing pages*. The direct-to-store ad built today
(`rec-2026-09-05-moveon-getw-w1830-snap`) is the one funnel shape that **cannot** use it, because no
page of ours renders to fire the beacon. Removing the interstitial tap also removed the only working
channel that could ever teach Snap to find installers instead of tappers.

**And the click-id problem this note calls "the hard part" mostly dissolves.** Snap's CAPI accepts a
**hashed email** as a match key, and we hold the email at sign-up. A sign-up conversion therefore
needs no click id surviving swipe → store → install → sign-up at all. What remains to build is one
more event type in a module that already exists — not an MMP, and not a new integration.

## What has to exist

A server-to-server conversion postback telling Snap "this click produced an install/signup", so Snap's
own optimiser can be pointed at installs rather than taps.

Two routes, and the choice is a real one:

**A. Snap Conversions API direct.** We post conversion events to Snap ourselves. Cheapest in money,
most work in code, and it only ever serves Snap — Meta would need the same thing built again.

**B. An MMP (AppsFlyer / Adjust / Singular).** An SDK in the app plus dashboard configuration; the MMP
does the matching and fans postbacks out to every network at once. Costs money per install, saves the
per-network rebuild, and brings deduplication and fraud filtering we would otherwise not have.

**Recommendation: B if more than one paid network is going to matter this quarter, A if Snap is the
only one that will.** Riteangle already runs Meta, which argues for B — but B's per-install pricing
against a ~₹600 test budget argues for A. This is the app owner's call, not an engineering one, and it
should be made before either is started rather than discovered halfway through A.

## The hard part, named up front

**Snap's click identifier has to survive from the swipe all the way to a signed-up user, and today
nothing carries it.** The chain we have is: Snap ad → Play listing (`referrer=` string) → install →
first open (`captureInstallReferrer` reads the referrer) → sign-up (`reportAcquisitionIfPending` posts
the row). Our `utm_id` already makes that whole trip. So the mechanism exists and is proven in shape —
what is missing is that Snap's own click id is not in the referrer, and Snap will only match a
postback it can tie to a click.

So the build is roughly:

1. Add Snap's click-id macro to the ad's `referrer` string alongside the existing `utm_*` (a change in
   **this** repo — `cli._snap_traffic_url` — once we know the macro's name and that Snap populates it
   for a store destination; that is unverified and should be checked before anything else is built).
2. Keep it through the existing chain — `attribution.dart` already keeps every `utm_*` key and would
   need one more key allowed through, plus `sanitizeUtm` server-side, which currently filters on
   `^utm_`.
3. Store it on the `user_acquisition` row.
4. Post the conversion to Snap (or the MMP) when the signup lands, carrying that click id.

## Two things that will bite, recorded so they are not rediscovered

**The event we can post is a SIGN-UP, not an install.** Per
`lrn-2026-09-05-user-acquisition-counts-signups-not-installs`, our earliest observable event is a
completed signup — Play showed 139 installs against 71 first opens, and signups are fewer still. That
is not fatal and may even be better: optimising toward signups targets a more valuable event than
installs. But it must be *declared* as a signup event, not mislabelled as an install, or Snap's
optimiser is calibrated against a volume roughly half to a third of what the label implies.

**iOS gets nothing from this.** There is no install referrer on iOS and no store presence for this app
yet. The whole chain is Android-only, which is consistent with every ad this repo has run, but it
means the postback cannot become the single source of truth later without a separate iOS answer.

## What to do first, and it is not this

**Verify the referrer chain end-to-end before building any of the above** — one manual install through
the live ad on a real Android device, then `ad-agent verify-tracking
rec-2026-09-05-moveon-getw-w1830-snap`. That is
`q-2026-09-05-does-the-play-referrer-reach-user-acquisition`, still open. Every step in this spec
assumes the referrer arrives; that assumption has been verified only by reading code, and
`destinations.yaml` already records what reading code was worth last time ("'should' is what was
believed last time"). Building a postback on top of an unproven chain would produce a system that
reports confident numbers about nothing.
