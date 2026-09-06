# Naming convention

Source: Sree's Aug 7 log (already in production use — confirmed against live `ad_spend_daily` /
`marketing_page_views` rows in `pocket-dating-coach`, e.g. `RA_TRAFFIC_GET_IN_BLR_TOF_202608`). Every
`ad-setup-loop` recommendation must use this convention exactly — a name that doesn't parse breaks the
join between spend and traffic in `pocket-dating-coach`'s own analytics (see
`ad-analytics.ts`'s `adSetKeyOf`/name-reconciliation logic, which exists specifically to patch up
naming drift).

## Campaign

```
RA_TRAFFIC_[DEST]_[COUNTRY]_[GEO]_[FUNNEL]_[YYYYMM]
```

Example: `RA_TRAFFIC_GET_IN_BLR_TOF_202608`

| Part | Meaning | Example |
|---|---|---|
| `RA` | RiteAngle (brand short code) | `RA` |
| `TRAFFIC` | Campaign objective — see the objective tokens below | `TRAFFIC`, `LEADS` |
| `[DEST]` | Destination / landing page — see the token table below | `GET`, `GETW` |
| `[COUNTRY]` | ISO-alpha-2 country code, uppercase, matching `ad-agent propose --countries` | `IN`, `TH` |
| `[GEO]` | City/region | `BLR`, `DEL`, `HYD`, `PAN` (pan-India), `PAN` (pan-Thailand) |
| `[FUNNEL]` | Funnel stage | `TOF` (top of funnel), `MOF`, `BOF` |
| `[YYYYMM]` | Launch month | `202608` |

`[COUNTRY]` was written as the literal `IN` until 2026-09-01, because every campaign to date was
India-only. Genericised the day the first Thailand test (`moveon-lead-w1830-th`) was drafted, per this
file's own "refine the rule the same turn it's needed" instruction — no other field's meaning changed.

### `[OBJECTIVE]` tokens

Position 2 was written as the literal `TRAFFIC` when every campaign was a traffic campaign. It is
the campaign's objective and it varies:

| Token | Network objective | Added |
|---|---|---|
| `TRAFFIC` | Snap `TRAFFIC` / Meta `OUTCOME_TRAFFIC` | in production since 2026-08 |
| `LEADS` | Meta `OUTCOME_LEADS` (on-platform instant form) | 2026-08-28 |

`LEADS` was added for the women's apply funnel, whose capture point is an instant form inside Meta
rather than a page on our own site. A leads campaign named `RA_TRAFFIC_...` would misdescribe what it
optimises for in the one field a human reads first.

### `[DEST]` tokens

One token per paid-traffic destination in `destinations.yaml`, which is the registry of record — this
table follows it, never the other way round. A campaign whose `[DEST]` has no row here is not named
yet; add the row when the destination opens to paid traffic.

| Path | Token | Audience | Added |
|---|---|---|---|
| `/get` | `GET` | men | in production since 2026-08 |
| `/get/w` | `GETW` | women | 2026-08-27 |
| `/get/w-apply` | `GETW-APPLY` | women | 2026-08-28 |
| `play.google.com/store/apps/details` | `PLAY` | neutral | 2026-09-04 |

`PLAY` is the first token for a destination that is **not a page of ours** — the Play listing, used by
a lead funnel whose form end page hands her straight to the store. Two things follow from that and
neither is cosmetic. Its registry key carries a host (`destinations.yaml` keys off-site destinations on
`host/path`, since `/store/apps/details` alone is also the App Store's shape). And **there is no
`ra_lp` for it in `pocket-dating-coach`'s page vocabulary**, because no page of ours renders — this
repo writes a label into the Play install referrer instead, saying where the install came from, never
a page id. There are now **three** such labels and they must stay distinct: `snap_lead_form` (Snap
lead-form end page), `snap_ad_direct` (Snap traffic straight to store) and `meta_ad_direct` (Meta
traffic straight to store, added 2026-09-06). The same creative running into the same store on two
networks is precisely the comparison these labels exist to survive — see `rules/tracking.md`.

**A store destination may carry Play's own storefront selectors and the token does not change.**
`…/details?id=com.riteangle.app&gl=IN&hl=en_IN` (the India storefront in Indian English, specified by
the app owner 2026-09-06) is the same registry entry as the bare listing: `destinations.normalize_path`
keys on host and path, so query parameters never reach the key. What they *do* affect is the URL
shape — the destination already has a query string, so `referrer=` is appended with `&`, which is
handled in `_store_referrer_url` and pinned in `tests/test_meta_store_destination.py`.

A hyphen inside a token is fine and a `_` is not — the name is parsed positionally on underscores, so
`GETW_APPLY` would shift `IN`, `[GEO]`, `[FUNNEL]` and the month one place right. Hyphens already
appear in live ad-set signals (`MOVEON-LPV`, `IND-LPV`) for the same reason.

`/beta` gets no token: `paid_traffic: false`, so no campaign can point at it.

**A token may never contain `_`.** The name is underscore-delimited and parsed positionally, so
`GET_W` would add a field and shift `IN`, `[GEO]`, `[FUNNEL]` and the month one place right —
silently, since nothing validates the shape. `GETW` keeps the field count identical to the live
`/get` campaigns, which is why it is the token and not the more readable alternative. Strip the
slashes from the path and uppercase it.

Nothing in `pocket-dating-coach` parses `[DEST]` back out of the campaign name — the landing page is
carried independently by `ra_lp` (`ra_lp=get_w`) and the joins run on ids, so this token is for human
legibility and for grouping in the network's own UI. That is also why the field count matters more
than the token's content: drift in the shape breaks the *other* fields, not this one.

## Ad set

```
[AUDIENCE]_[AGE]_[GENDER]_[SIGNAL]
```

`[AUDIENCE]` is the persona/segment name from `targeting.md` (e.g. `CASUAL`, `INVISIBLE-MAN`,
`FLOODED-WOMAN`). `[SIGNAL]` is the creative angle or landing-page variant (e.g. `STORY`, `LPV` for
landing-page-view optimized). Matches the pattern already live, e.g. `MEN_25-40_CASUAL_STORY_IND-LPV`.

## Ad (creative)

```
[FORMAT]_[HOOK]_[VARIANT]_[DATE]
```

`[FORMAT]` — `IMG`, `VID`, `STORY`, `COLLECTION`. `[HOOK]` — the slug of the emotional hook used, taken
from `creative-style.md`'s "Ad-ready emotional threads", which is the closed vocabulary: every thread
there carries its slug (`CAMERA-JUDGE`, `DESOLATE-MAN`, `FOURTEEN-SUITORS`, `VERIFIED-DELETED`,
`MONOTONIC-PROGRESS`, `MOVE-ON-PROPER`). A hook with no thread has no slug — add the thread first,
don't coin a slug at naming time. `[VARIANT]` — `A`/`B`/`C` for a/b tests of the same hook.

## Why this matters beyond tidiness

`pocket-dating-coach`'s ad-set rollup is keyed on ad set (not campaign — two live campaigns have shared
an identical name with different ids before), and it joins spend to traffic by parsing this exact
structure out of both the network's own naming and the landing-page UTM. A recommendation that doesn't
follow this convention doesn't just look messy — it produces an ad set that `ad-audit` cannot reliably
attribute spend or performance to later.

## UTM scheme (append to every landing URL)

**See `rules/tracking.md` for the full protocol and the 2026-08-21 incident that made this
non-negotiable — read it before setting up a new ad, not after.**

```
https://www.riteangle.dating/get?utm_source={snapchat|meta}&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_term={{adSet.id}}&utm_id={{ad.id}}&utm_content={{ad.name}}
```

`utm_term` carries the ad set id. **`utm_id` is the parameter `traffic-quality.ts`'s `adSetKeyOf`
actually reads as the Snap ad id — set it explicitly on every ad's own Website URL field, never assume
Snap appends it automatically.** (`utm_content` is a human-readable ad name for manual cross-checking
only — on Snap it is not what the join uses, despite an earlier version of this doc saying otherwise;
on Meta, `utm_content` is the one that matters instead. Don't mix the two networks' conventions.)
