# Tracking verification (UTM / attribution)

Source: incident found 2026-08-21 in `pocket-dating-coach`'s admin Users table — the "Ad" column was
blank for every single row. Investigation found **0 of 54** Snap-attributed installs over the prior
week ever carried an ad-level identifier, so no install could ever be joined back to the ad that
produced it. Read this before every `ad-setup-loop` handoff, and follow the checklist below before and
after every launch — this is not optional cleanup, it is the only thing that makes `ad-audit` possible
later.

## What actually happened (why "Snap auto-appends it" is not to be trusted)

A comment in `pocket-dating-coach`'s `traffic-quality.ts` asserted that Snapchat auto-injects `utm_id`
(the ad id) on every impression, verified once against specific creatives on 2026-08-10. That assumption
does not hold in general — of 54 Snap-attributed installs checked on 2026-08-21, **zero** carried a
`utm_id`, not even as an unresolved `{{macro}}` literal. The unresolved-macro case (which the parsing
code deliberately fails closed on) did not occur — the parameter was simply never present. Whatever ad
produced those installs had a destination URL with no tracking parameters attached at all, so
`pocket-dating-coach`'s `/get` landing page fell through to its own hardcoded default
(`utm_campaign=get_lp`, no ad set, no ad), and every one of those installs is permanently
unattributable — there is no click id, no ad id, nothing stored anywhere that a fix can retroactively
join back to a specific ad.

**Separately, this repo's own UTM scheme (below, and previously in `naming.md`) was itself out of sync
with what `pocket-dating-coach`'s join code actually reads.** `adSetKeyOf()` in `traffic-quality.ts`
only ever reads `utm_id` for Snap's ad-level id — it does not read `utm_content` for Snap. So even the
handful of installs that *did* carry a populated `utm_content` (a readable creative slug, from ad sets
that had at least partially set up their tracking template) still could not populate the Ad column. Two
independent gaps compounded: the ad's URL wasn't sending an id, and the doc telling people which
parameter to put it in was pointing at the wrong one for Snap.

## The URL every ad must carry — non-negotiable, checked before launch

```
https://www.riteangle.dating/get?utm_source={snapchat|fb}&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_term={{adSet.id}}&utm_id={{ad.id}}&utm_content={{ad.name}}
```

**Corrected 2026-08-27, twice, by reading `pocket-dating-coach/src/lib/server/traffic-quality.ts`
instead of reasoning about it. Both errors were in the template above.**

1. **`utm_source` on Meta is `fb`, never `meta`.** `networkOf()` maps only
   `ig`/`fb`/`instagram`/`facebook` to `'meta'`; anything else falls through to `'other'`. Its own
   docstring: *"utm_source is the PLACEMENT on Meta — real traffic arrives as `ig` or `fb`, never as
   `meta`"*. `rules/networks.yaml` had declared `meta` since it was written, and it had never been
   exercised because no Meta ad here has ever carried UTMs at all. This closes
   `q-2026-08-27-meta-utm-source-spelling`.

2. **`utm_content` carries the ad ID on Meta, and the ad NAME on Snap.** The template above shows
   `utm_content={{ad.name}}` for both, which is right for Snap and breaks the Meta join.
   `adSetKeyOf()` reads `adId = network === 'meta' ? clean(raw.utm_content)`. Snap has both
   parameters available — `utm_id` for the id, `utm_content` for the readable name — so it keeps
   both; Meta has to spend `utm_content` on the id. This closes
   `q-2026-08-26-utm-content-on-meta` in favour of the prose, which is what `networks.utm_params`
   already implemented.

**Per-network, as actually read by the consumer:**

| Parameter | Snap | Meta |
|---|---|---|
| `utm_source` | `snapchat` | **`fb`** |
| `utm_term` | ad set id (UUID; shape-tested) | ad set id (numeric) |
| ad-level id | `utm_id` (Snap appends it itself) | **`utm_content`** |
| `utm_content` | ad name, human-readable | *unavailable — spent on the ad id* |
| `utm_campaign` | ad set NAME, not campaign name | see `q-2026-08-27-meta-utm-campaign-name-or-id` |

Any value containing `{{` is treated as absent by `adSetKeyOf`, so an unresolved macro joins to
nothing rather than to something wrong. `snap-push` and `meta-push` both write every value
literally for that reason — the ids are known facts by the time the URL is set.

## The scheme above is for a page of OURS. A store listing takes a different shape entirely.

Everything above assumes the destination is a page we run, where appending a query string is exactly
right because our own code reads it. **An app store listing reads none of it.** Play strips any
`utm_*` you append to a listing URL, and the only channel that survives from the tap through to the
installed app is Play's own `referrer` parameter — so the whole tracking string has to be
**URL-encoded inside `referrer=`**, not appended alongside it.

```
https://play.google.com/store/apps/details?id=com.riteangle.app&referrer=<the utm string, URL-encoded>
```

**Appending it instead does not merely lose attribution — it can break the link.** The listing URL
already carries `?id=…`, so a second `?` corrupts the app id itself: on 2026-09-05 `_utm_url` was
found producing `…details?id=com.riteangle.app?utm_source=snapchat&…`, which Play would read as a
package named `com.riteangle.app?utm_source=snapchat`. That ad would have failed to open the right
listing at all, and Ads Manager would have reported a healthy ad the entire time. Nothing tested it
because no traffic ad had ever pointed at a store before — see
`lrn-2026-09-05-store-url-shape-did-not-travel-to-traffic-path`.

`cli._store_referrer_url` is the single implementation; `_snap_traffic_url`, `_snap_lead_end_page`
and `_meta_traffic_url` all go through it. **Do not hand-build a store URL anywhere else.**

### On Meta the same rule has a different trap: `url_tags` is inert against a store listing

Added 2026-09-06 with `rec-2026-09-06-moveon-play-w1830-meta`, the first Meta ad pointed at the Play
listing. Everything above about the store shape applies unchanged. What is Meta-specific is *where
the tracking is set*, and the wrong answer looks completely correct.

**Every Meta ad in this repo before that one put its tracking in the ad's `url_tags` field**, and
that is right for a page of ours. Meta implements `url_tags` by *appending* the string to the
outbound URL at click time, and our own pages read the query string. **Play does not.** Play strips
appended parameters and honours only its own `referrer=`, so a store-bound Meta ad carrying its
tracking in `url_tags` spends normally, resolves to the correct listing, reports healthy in Ads
Manager — and delivers installs that carry no ad identifier at all. That is the 2026-08-21 incident
with a third first step (`lrn-2026-09-06-meta-url-tags-inert-against-store`).

So on a store destination the tracking has to live **in the creative's own link**, URL-encoded inside
`referrer=`. That has a consequence worth stating, because it is why the code looks the way it does:
a link is part of `object_story_spec`, Meta creatives are effectively immutable once created, and the
ad id does not exist when the first creative is built. `meta.retarget_video_creative` therefore
builds a *second* creative carrying the final link and repoints the ad at it — the same dance
`attach_tracked_creative` does, on a different field, and it deliberately leaves `url_tags` unset so
the next reader cannot conclude the tracking lives somewhere it does not.

`ra_lp=meta_ad_direct` for this funnel — a **third** label, alongside `snap_ad_direct` (Snap traffic
straight to store) and `snap_lead_form` (Snap lead-form end page). Never collapse them. The label is
the only field in `user_acquisition` that says which funnel an install came off, and the same creative
running into the same store on two networks is exactly the comparison it exists to survive.

**And on Meta there is no pixel to attach on this route, at all.** The account's pixel
(`2286986682092608`) is JavaScript on a page we own; nothing of ours renders on a store listing, so
it cannot fire once. `pocket-dating-coach`'s `marketing-conversions.ts` *does* forward store clicks
to Meta's CAPI server-side and is healthy (65 of 65 in the week of 2026-08-31) — but it is triggered
by the landing page's store-click beacon, so a direct-to-store ad bypasses that too. Meta receives no
conversion signal from such an ad and can only optimise `LINK_CLICKS`. **Say that out loud in any
brief that proposes this shape**, because `LINK_CLICKS` buys the cheapest tap, and the cheapest tap
comes from the people most willing to tap and least likely to install. Meta's app-promotion objective
is not an escape: it is unavailable to this account
(`lrn-2026-09-06-meta-app-promotion-blocked-no-play-url`). The open question is
`q-2026-09-06-can-meta-optimise-toward-installers-not-tappers`.

**The optimisation goal must move with the destination.** `LANDING_PAGE_VIEWS` names an event that
cannot occur when no page of ours loads, so a store-bound Meta ad set takes `LINK_CLICKS` — the exact
correction the Snap arm made on 2026-09-05 (`LANDING_PAGE_VIEW` → `SWIPES`) for the identical reason.
`cmd_meta_push` derives it from the destination rather than accepting it as a flag, because getting
it wrong is silent.

### Meta direct-to-store coverage table

| Step | Signal | Source | Real-time? | Per-ad? | Verdict |
|---|---|---|---|---|---|
| Impression | impressions | Meta | yes | yes | ✅ |
| Link click (CTA tap) | link clicks | Meta | yes | yes | ✅ |
| Arrival at listing | store listing visitors | Play Console | **no** (~6d lag) | **no** (channel bucket) | ❌ |
| Install | device acquisitions | Play Console | **no** (~6d lag) | **no** | ❌ |
| First open | device first opens | Play Console | **no** (~6d lag) | **no** | ❌ |
| Sign-up | `user_acquisition` row w/ this ad's `utm_content` | our DB | yes | yes | ❓ never observed |
| Conversion reported to Meta | CAPI event | `marketing-conversions.ts` | — | — | ❌ structurally absent |

The ❓ row is `q-2026-09-06-does-the-meta-referrer-reach-user-acquisition`, and it is **not** closed by
the Snap twin: Meta joins the ad on `utm_content` where Snap joins on `utm_id`, so a working Snap
chain proves nothing about this one. One manual install on a real Android device through the enabled
ad, then `ad-agent verify-tracking`, closes it.

Two further things about the store shape, both load-bearing:

- **`ra_lp` is a label, never a page id.** No page of ours renders on a store arrival, so writing one
  of `pocket-dating-coach`'s real page ids there would count an install as a page view that never
  happened. `snap_lead_form` = came off a lead form's end page; `snap_ad_direct` = came straight off
  an ad's swipe-up. Keep new funnels distinguishable rather than reusing an existing label.
- **The two Snap paths do NOT have the same attribution depth, and it is a platform limit, not an
  oversight.** A lead form's end page is fixed when the form is created, before the ad exists, so a
  lead ad's referrer stops at ad-squad level. A traffic creative's URL is rewritten after the ad is
  created, so a store-bound traffic ad carries the real `utm_id`. Don't "harmonise" them by dropping
  it, and don't compare per-ad install counts across the two arms as if they were measured the same
  way (`lrn-2026-09-05-traffic-carries-ad-id-lead-cannot`).

**Verifying a store URL is not the same check as verifying a page URL.** Clicking it proves only that
the listing opens. Decode the `referrer` parameter and confirm the app id parses to the bare package
name, then confirm a real install lands a `user_acquisition` row carrying that `ra_lp` — reading the
consuming code is not proof, which is the mistake `destinations.yaml` already records against
`/get/w-apply` ("'should' is what was believed last time").

## The funnel coverage table — required for every new funnel shape

**Before building an ad whose funnel shape is new, and again when reporting on one, write out the
coverage table below.** Requested by the app owner 2026-09-05 after it was produced ad hoc for the
direct-to-store traffic ad and turned out to be the artefact that actually answered "can we measure
this?" — a question that three prior sessions had each answered "yes" about a funnel nobody had
checked step by step.

One row per funnel step, in the order a real person walks it:

| Step | Signal | Source | Real-time? | Per-ad? | Verdict |
|---|---|---|---|---|---|
| Impression | paid impressions | Snap | yes | yes | ✅ |
| Swipe (CTA tap) | swipes | Snap | yes | yes | ✅ |
| Arrival at listing | store listing visitors | Play Console | **no** (~6d lag) | **no** (channel bucket only) | ❌ |
| Install | device acquisitions | Play Console | **no** (~6d lag) | **no** | ❌ |
| First open | device first opens | Play Console | **no** (~6d lag) | **no** | ❌ |
| **Sign-up** | `user_acquisition` row | our DB | yes | yes | ❓ never observed |

**Corrected 2026-09-05, hours after this table was first written here, by reading the app instead of
assuming.** The first version of this row said the `user_acquisition` row lands on *first open*. It
does not. `mobile/lib/attribution.dart`'s `reportAcquisitionIfPending` returns early while
`Supabase.instance.client.auth.currentSession == null`, and `/api/attribution/install` requires a
Bearer token and keys the row on `user_id` — so **the row cannot exist until sign-up completes.** Two
steps further down the funnel than stated, and the error was in the optimistic direction.

**What follows from that, and it is the important part:** there is **no per-ad install count
anywhere.** Play has installs but cannot break them down by ad; we have per-ad detail but our
earliest observable event is a sign-up. Play's own funnel over 28 days was 139 device acquisitions →
71 first opens → sign-ups fewer still, so a per-ad "install" number computed from our rows is not
approximately right, it is a different metric entirely. **Never report `user_acquisition` counts as
installs.** Cost-per-install cannot be computed from this repo's data at all; cost-per-signup can.

The one thing that would close this gap is a server-to-network install postback (Snap CAPI or an MMP)
— see the recommendation recorded against
`q-2026-09-05-does-the-play-referrer-reach-user-acquisition`.

**The two question columns are the whole point, and they are why this is not busywork.** "Do we track
installs?" has no useful answer. A signal that exists but is not *per-ad* cannot compare two creatives.
A signal that exists but is not *real-time* cannot inform a 2-day test — Play Console's six-day lag
means a 2-day ad set is judged five days before its own data exists. Both failures are invisible if
coverage is claimed in aggregate ("we have Play Console data"), and both are obvious the moment the
row is forced to carry a yes/no.

**Verdicts are three-valued and the third one matters most:**

- ✅ measured, and observed working at least once against real data
- ❌ not measurable at the granularity this decision needs — say what would fix it
- ❓ **should work by construction, never actually observed.** This is the honest state of most new
  tracking, and collapsing it into ✅ is how the 2026-08-21 incident ran for a week. A ❓ row is a
  blocking question in `research/questions/`, not a footnote.

**Also name any step where the signal is a proxy for the thing you actually want.** Our referrer row
is written on *first open*, not on install — and Play reported 139 device acquisitions against 71
first opens over 28 days, so roughly half of installers never open. Per-ad "installs" from our own DB
is therefore first-opens, undercounting by about 2×, with the never-opened cohort permanently
invisible per ad. A proxy silently renamed as the real metric makes every cost-per-X computed off it
wrong by whatever the gap is.

```
```

- **`utm_id={{ad.id}}` is mandatory on Snap, set explicitly on the ad's own Website URL field.** Do not
  rely on Snap to append it — that assumption already failed once, silently, for a full week of spend.
- `utm_term` carries the ad set id (Snap) — already correct in `naming.md`, unaffected by this incident.
- `utm_content` carries a human-readable ad name/slug for readability and manual cross-checking. It is
  *not* what `pocket-dating-coach` joins on for Snap — `utm_id` is, so its presence in the URL is the
  one that actually matters for the Ad column and any ad-level `ad-audit` breakdown.
- On Meta, the equivalent ad-level id is `utm_content` (Meta's own macro convention;
  `traffic-quality.ts` reads it that way for the `meta` network specifically — don't cross the two
  networks' conventions).

## Pre-launch check — before a single rupee of spend, every ad, no exceptions

1. Open the ad's actual Website URL field in Ads Manager (not the campaign-level default, the specific
   ad's own field) and confirm all five parameters above are present with real macros, not left blank
   or copied from a template that predates this checklist.
2. Click the ad's own preview/swipe-up link (or paste the URL into a browser) and confirm it lands on
   `/get?...` with every macro resolved to a real value — a UUID for `utm_term`/`utm_id` on Snap, not a
   literal `{{adSet.id}}` or `{{ad.id}}` string. An unresolved macro means the platform's targeting
   step wasn't completed correctly and the ad should not go live until it is.
3. This takes under a minute and would have caught the 2026-08-21 incident before a single install was
   lost to it. Treat it as a hard gate in step 8 of `ad-setup-loop`'s procedure, not an optional nicety.

## Post-launch check — within the first hour of any campaign going live

Query `pocket-dating-coach`'s `user_acquisition` table (via the `ads_agent_ro` read-only role, or ask
the user to run it) for rows on the relevant network created since launch, and confirm they carry a
real `utm_term`/`utm_id` — not the landing page's hardcoded default (`utm_campaign=get_lp` with nothing
else). If every row since launch is hitting the default, tracking is broken for that ad and spend is
accumulating unattributable installs right now — flag it immediately rather than waiting for the next
scheduled `ad-audit` pass, since the whole week's spend in the 2026-08-21 incident was lost exactly this
way.

## Closing the loop

`log-setup` in the ledger should not be considered complete until the post-launch check above has run
at least once against real data. A recommendation whose IDs were logged but whose tracking was never
verified live is exactly the gap that produced this incident.
