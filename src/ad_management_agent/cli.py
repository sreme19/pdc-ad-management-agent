"""ad-agent CLI — the zero-API persistence layer for the ad-management-agent loop.

Every command here is either a deterministic file read/write or a single
plain HTTP call to pocket-dating-coach's authenticated internal analytics
endpoint. Nothing in this file calls the Anthropic API, or any LLM — the
reasoning happens live in the Claude Code session running the skill; this
CLI only persists or fetches data on that session's behalf.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

from . import budget as budgetrules
from . import destinations
from . import meta as metaapi
from . import networks as networkreg
from . import research as researchmod
from . import snap as snapapi
from . import targeting as targetingspec
from . import watermark as watermarkgate
from .config import load_config
from .ledger import STATUSES, Ledger


def _today() -> str:
    """Today in the machine's local timezone, deliberately.

    Every date this repo writes is a business date read alongside
    pocket-dating-coach's analytics, which bucket by IST day (`fetch-analytics`
    takes `--start`/`--end` as IST days). A UTC date would disagree with those
    buckets for five and a half hours out of every twenty-four, which is exactly
    the window an evening review happens in. ruff's DTZ011 is right in general and
    wrong here.
    """
    return _dt.date.today().isoformat()  # noqa: DTZ011 — IST business date, see above


def _check_network(rules_dir: Path, network: str) -> None:
    """Validate --network against the registry, at run time.

    Not an argparse `choices=` list, because the parser is built before config is
    loaded and so cannot know where the registry lives — and because a hardcoded
    pair here is exactly what this registry exists to remove. The runtime error
    carries the registered names and points at the file.
    """
    try:
        networkreg.get(rules_dir, network)
    except networkreg.NetworkError as exc:
        _fail(exc)


NETWORK_HELP = "network key from rules/networks.yaml (currently: snap, meta)"


def _add_targeting_flags(sp: argparse.ArgumentParser, *, required: bool) -> None:
    """The structured audience, as flags on both `propose` and `amend`.

    Discrete flags rather than a JSON blob or a second file: a skill calls this
    programmatically and a human reads the invocation back in the shell history,
    and both are better served by `--gender FEMALE --min-age 18` than by quoting
    YAML through argv.
    """
    g = sp.add_argument_group(
        "targeting (structured — this is what snap-push and meta-push actually push)"
    )
    g.add_argument("--gender", required=required, default=None,
                   choices=list(targetingspec.GENDERS),
                   help="single-gender only; rules/targeting.md forbids a mixed ad set")
    g.add_argument("--min-age", required=required, default=None,
                   help="18 or above — rules/compliance.md is 18+ without exception")
    g.add_argument("--max-age", required=required, default=None,
                   help="a number, or 50+ for the open-ended top band")
    g.add_argument("--countries", required=required, default=None,
                   help="comma-separated 2-letter codes, e.g. in")
    g.add_argument("--os", default=None, choices=list(targetingspec.OS_TYPES),
                   help="omit to target all devices")
    g.add_argument("--expansion", default=None, choices=["on", "off"],
                   help="Snap targeting expansion; defaults to on for a new proposal")


def _targeting_patch(args: argparse.Namespace) -> dict:
    """Only the targeting fields the caller actually passed."""
    patch: dict = {}
    if args.gender is not None:
        patch["gender"] = args.gender.upper()
    if args.min_age is not None:
        patch["min_age"] = str(args.min_age)
    if args.max_age is not None:
        patch["max_age"] = str(args.max_age)
    if args.countries is not None:
        patch["countries"] = [c.strip().lower() for c in args.countries.split(",") if c.strip()]
    if args.os is not None:
        patch["os"] = args.os.upper()
    if args.expansion is not None:
        patch["expansion"] = args.expansion == "on"
    return patch


def _fail(exc: Exception) -> None:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc


def cmd_propose(args: argparse.Namespace, ledger: Ledger) -> None:
    # Hard gate, before anything is written: an ad set may not point at a page
    # framed for a different audience. See rules/destinations.yaml — no override.
    try:
        destinations.check(
            ad_set_name=args.ad_set_name,
            destination_url=args.destination_url,
            rules_dir=ledger.root / "rules",
        )
    except destinations.DestinationGateError as exc:
        _fail(exc)

    # The structured audience, validated before anything is written, and checked
    # against the ad-set name so the record cannot disagree with itself.
    try:
        spec = targetingspec.build(
            gender=args.gender,
            min_age=args.min_age,
            max_age=args.max_age,
            countries=[c.strip() for c in args.countries.split(",")],
            os=args.os,
            expansion=(args.expansion or "on") == "on",
        )
        targetingspec.check_matches_ad_set_name(spec, args.ad_set_name)
    except targetingspec.TargetingError as exc:
        _fail(exc)

    if budgetrules.below_floor(args.budget_cap):
        print(f"note: {budgetrules.floor_note(args.budget_cap)}\n"
              "      Proposing anyway — the cap is your call, but say why in the brief.",
              file=sys.stderr)

    _check_network(ledger.root / "rules", args.network)

    rec = ledger.propose(
        slug=args.slug,
        network=args.network,
        campaign_name=args.campaign_name,
        ad_set_name=args.ad_set_name,
        ad_name=args.ad_name,
        targeting_summary=args.targeting_summary,
        targeting=spec,
        creative_ref=args.creative_ref,
        destination_url=args.destination_url,
        budget_cap_inr_per_day=args.budget_cap,
        duration_days=args.duration_days,
        brief_path=args.brief,
        from_idea=args.from_idea,
        today=_today(),
    )
    ledger.write_index()

    # Close the idea, so an approved idea that became a real record stops being
    # reported as one nobody acted on.
    if args.from_idea:
        try:
            _research(ledger).mark_idea_proposed(args.from_idea, rec_id=rec.rec_id, today=_today())
        except (researchmod.ResearchError, KeyError) as exc:
            print(f"warning: proposal written, but {args.from_idea} was not closed: {exc}",
                  file=sys.stderr)
        else:
            print(f"closed idea {args.from_idea}")

    print(f"proposed {rec.rec_id} -> {rec.path}")


def cmd_amend(args: argparse.Namespace, ledger: Ledger) -> None:
    fields = {
        "campaign_name": args.campaign_name,
        "ad_set_name": args.ad_set_name,
        "ad_name": args.ad_name,
        "targeting_summary": args.targeting_summary,
        "creative_ref": args.creative_ref,
        "destination_url": args.destination_url,
        "budget_cap_inr_per_day": args.budget_cap,
        "duration_days": args.duration_days,
    }
    changes = {k: v for k, v in fields.items() if v is not None}

    rec = ledger.find(args.rec_id)

    # Targeting is patched, not replaced: `--min-age 23` on its own should move one
    # field, not silently drop the geography. The merged result is validated as a
    # whole, so a patch cannot leave the record in a state propose would refuse.
    patch = _targeting_patch(args)
    if patch:
        merged = {**(rec.front_matter.get("targeting") or {}), **patch}
        try:
            targetingspec.validate(merged)
            targetingspec.check_matches_ad_set_name(
                merged, changes.get("ad_set_name") or rec.front_matter.get("ad_set_name", "")
            )
        except targetingspec.TargetingError as exc:
            _fail(exc)
        changes["targeting"] = merged

    if not changes:
        print("error: nothing to amend — pass at least one field to change", file=sys.stderr)
        raise SystemExit(2)

    # Close the loophole: amend must not be a way around the destination gate.
    # Re-run it whenever this amendment touches the audience or the destination,
    # against the *resulting* pair rather than only the changed half. Amendments
    # that touch neither are left alone deliberately, so a record already blocked
    # by the gate can still have unrelated fields repaired.
    if "ad_set_name" in changes or "destination_url" in changes:
        effective_ad_set = changes.get("ad_set_name", rec.front_matter.get("ad_set_name", ""))
        effective_dest = changes.get("destination_url", rec.front_matter.get("destination_url", ""))
        try:
            destinations.check(
                ad_set_name=effective_ad_set,
                destination_url=effective_dest,
                rules_dir=ledger.root / "rules",
            )
        except destinations.DestinationGateError as exc:
            _fail(exc)

        # Renaming an ad set can flip the gender token, which would leave a record
        # whose name and targeting disagree. Re-check even when the targeting itself
        # was not part of this amendment.
        if "ad_set_name" in changes and rec.front_matter.get("targeting"):
            try:
                targetingspec.check_matches_ad_set_name(
                    changes.get("targeting") or rec.front_matter["targeting"],
                    changes["ad_set_name"],
                )
            except targetingspec.TargetingError as exc:
                _fail(exc)

    try:
        rec, diff = ledger.amend(
            args.rec_id, changes=changes, reason=args.reason, today=_today()
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    if not diff:
        print(f"{rec.rec_id}: no change — every field already had that value")
        return
    ledger.write_index()
    print(f"amended {rec.rec_id} -> {rec.path}")
    for field, (old, new) in sorted(diff.items()):
        print(f"  {field}: {old!r} -> {new!r}")


def _gate_campaign_caps(caps: dict, *, squad_daily_inr: float, duration_days: int,
                        rec_id: str, accept: bool) -> None:
    """Refuse to hang an ad squad off a campaign whose own cap would starve it.

    The lower figure binds. WOMEN_18-22_CASUAL_LPV was pushed on 2026-08-26 with an
    ad squad at Rs 1,000/day under a campaign capped at Rs 300/day; the effective
    spend was 30% of the plan and below rules/budget.md's floor, which made the
    result inconclusive before a rupee was spent. The push printed nothing about it
    because nothing read the parent.

    This is not the destination gate — there IS an escape hatch here, because a low
    cap is sometimes a deliberate choice rather than an error. But it is explicit,
    it names the deviation, and it tells you where to record it.
    """
    daily_cap = caps.get("daily_inr")
    lifetime_cap = caps.get("lifetime_inr")
    planned_total = squad_daily_inr * duration_days

    binding = []
    if daily_cap is not None and daily_cap < squad_daily_inr:
        binding.append(
            f"campaign daily cap is Rs {daily_cap:.0f}/day, below this ad squad's "
            f"Rs {squad_daily_inr:.0f}/day — the cap binds, so effective spend is "
            f"Rs {daily_cap:.0f}/day"
        )
    if lifetime_cap is not None and lifetime_cap < planned_total:
        binding.append(
            f"campaign lifetime cap is Rs {lifetime_cap:.0f}, below the planned "
            f"Rs {planned_total:.0f} ({squad_daily_inr:.0f} x {duration_days}d)"
        )

    if not binding:
        if daily_cap is None and lifetime_cap is None:
            print("campaign  no spend cap on the parent — the ad squad budget is the "
                  "effective one")
        else:
            print(f"campaign  cap checked: daily={daily_cap}, lifetime={lifetime_cap} — "
                  "neither binds")
        if budgetrules.below_floor(squad_daily_inr):
            print(f"WARNING   {budgetrules.floor_note(squad_daily_inr)}")
        return

    effective = min([v for v in (daily_cap, squad_daily_inr) if v is not None])
    lines = ["", "BLOCKED: the parent campaign's own cap would override this ad squad's budget."]
    lines += [f"  - {b}" for b in binding]
    if budgetrules.below_floor(effective):
        lines += ["", "  " + budgetrules.floor_note(effective)]
    lines += [
        "",
        "  Fix the cap in Ads Manager (Campaign > Daily spend cap) and push again — or, if the",
        "  cap is deliberate, re-run with --accept-campaign-cap to create it anyway. Doing that",
        "  records the deviation rather than hiding it:",
        f"    ad-agent note {rec_id} --kind budget --text \"...\"",
    ]
    if not accept:
        print("\n".join(lines), file=sys.stderr)
        raise SystemExit(2)
    print("\n".join(lines))
    print("\n--accept-campaign-cap: proceeding with the cap above as a stated deviation.")


def _utm_query(rules_dir: Path, network: str, campaign_name: str,
               ad_squad_id: str, ad_id: str, ad_name: str) -> str:
    """rules/tracking.md's five parameters as a bare query string, no leading `?`.

    Split out from `_utm_url` because the two networks want it at different points
    in the URL. Snap takes a complete Website URL on the creative, so the params
    are appended there. Meta takes them in the ad's own `url_tags` field, which is
    query-string syntax WITHOUT a base URL or a `?` — passing a full URL there
    produces a link with the destination embedded in its own query string, which
    fails silently by still being a valid URL.

    The parameter names come from rules/networks.yaml rather than from literals
    here, because Snap and Meta genuinely disagree about which one carries the ad
    id and this function is one copy-paste away from being reused for the wrong
    one.
    """
    from urllib.parse import urlencode
    return urlencode(
        networkreg.utm_params(rules_dir, network, campaign_name=campaign_name,
                              ad_set_id=ad_squad_id, ad_id=ad_id, ad_name=ad_name)
    )


def _utm_url(rules_dir: Path, network: str, destination: str, campaign_name: str,
             ad_squad_id: str, ad_id: str, ad_name: str) -> str:
    """The destination with rules/tracking.md's scheme appended, every value literal.

    Ads Manager fills these from {{macros}}; the 2026-08-21 incident was a macro
    that silently never resolved. Pushed through the API the ids are known facts by
    the time the URL is written, so there is no macro left to fail.
    """
    return destination + "?" + _utm_query(
        rules_dir, network, campaign_name, ad_squad_id, ad_id, ad_name)


#: The `ra_lp` this repo writes when the install came straight off a Snap lead
#: form with no landing page in between. `landing_page` in
#: pocket-dating-coach's user_acquisition is free text (no check constraint, 40
#: chars at /api/attribution/install), so this is a label, not an enum member —
#: but it must never be one of that repo's real page ids, or a direct-to-store
#: install would be counted as a page that never rendered.
PLAY_DIRECT_LANDING_PAGE = "snap_lead_form"

#: The same label for a TRAFFIC ad whose swipe-up goes straight to the store with
#: no page and no form anywhere in the funnel. Distinct from
#: PLAY_DIRECT_LANDING_PAGE on purpose: both mean "no page of ours rendered", but
#: they are different funnels and collapsing them would make the two
#: indistinguishable in user_acquisition — which is the one thing the label exists
#: to prevent. Same constraint applies: never one of pocket-dating-coach's real
#: page ids.
PLAY_DIRECT_AD_LANDING_PAGE = "snap_ad_direct"

#: The Meta equivalent of PLAY_DIRECT_AD_LANDING_PAGE, added 2026-09-06 for the
#: first Meta ad pointed straight at the Play listing. A THIRD label rather than a
#: reuse of the Snap one, for the reason the comment above gives: the label is the
#: only thing in user_acquisition that says which funnel an install came off, and
#: two networks running the same creative into the same store is precisely the
#: comparison the label has to survive. Collapsing them would make the Meta arm
#: and the Snap arm indistinguishable in exactly the readout they were built for.
#: Still never one of pocket-dating-coach's real page ids — no page of ours renders.
META_PLAY_DIRECT_AD_LANDING_PAGE = "meta_ad_direct"


def _is_app_store(destination: str) -> bool:
    """Is this destination an app store listing rather than a page of ours?"""
    host = (urlsplit(destination).hostname or "").lower().removeprefix("www.")
    return host in {"play.google.com", "apps.apple.com"}


def _store_referrer_url(destination: str, utm_query: str, *, ra_src: str, ra_lp: str) -> str:
    """Fold tracking INSIDE Play's `referrer` param — the only channel an install survives.

    Shared by the lead path and the traffic path because getting this shape wrong
    is silent in both. Appending the params to a listing URL instead produces a
    link Play strips clean, and — when the listing already carries `?id=` —
    a second `?` that corrupts the app id itself, so the link may not even open
    the right listing. Both failures look like a working ad in Ads Manager.
    """
    referrer = f"{utm_query}&ra_src={ra_src}&ra_lp={ra_lp}"
    sep = "&" if urlsplit(destination).query else "?"
    return f"{destination}{sep}referrer={quote(referrer, safe='')}"


def _snap_traffic_url(rules_dir: Path, destination: str, *, campaign_name: str,
                      ad_squad_id: str, ad_id: str, ad_name: str) -> str:
    """The Website URL for a Snap TRAFFIC ad — a page of ours, or a store listing.

    Added 2026-09-05, when the first traffic ad was pointed at the Play listing and
    `_utm_url` was found building `…details?id=com.riteangle.app?utm_source=…` for
    it. Until then every traffic ad went to a page of ours, where appending the
    query string is exactly right, so nothing had exercised the store branch.

    ONE THING THIS PATH HAS THAT THE LEAD PATH CANNOT: `utm_id`, the ad id. A lead
    form's end page is fixed when the form is created, which is before the ad
    exists, so `_snap_lead_end_page` strips `utm_id` and its attribution stops at
    ad-squad level. A traffic creative's URL is rewritten AFTER the ad is created
    (cmd_snap_push does this already, for exactly this reason), so a store-bound
    traffic ad carries ad-level attribution all the way into the install referrer.
    Do not "harmonise" the two by dropping it.
    """
    if not _is_app_store(destination):
        return _utm_url(rules_dir, "snap", destination, campaign_name,
                        ad_squad_id, ad_id, ad_name)
    utms = _utm_query(rules_dir, "snap", campaign_name, ad_squad_id, ad_id, ad_name)
    return _store_referrer_url(destination, utms, ra_src="ad",
                               ra_lp=PLAY_DIRECT_AD_LANDING_PAGE)


def _meta_traffic_url(rules_dir: Path, destination: str, *, campaign_name: str,
                      ad_set_id: str, ad_id: str, ad_name: str) -> str:
    """The destination URL for a Meta TRAFFIC ad — a page of ours, or a store listing.

    Added 2026-09-06, the Meta sibling of `_snap_traffic_url`, and it exists for the
    same reason: the store branch had never been exercised on this network either.

    **The Meta-specific trap is that `url_tags` looks like it already solves this
    and does not.** Every prior Meta ad here put tracking in the ad's `url_tags`
    field, which Meta APPENDS to the outbound URL at click time. That is right for a
    page of ours, which reads the query string. Against a Play listing it is inert:
    Play strips appended parameters and honours only its own `referrer=`. So a
    store-bound Meta ad with url_tags set spends normally, resolves to the right
    listing, and produces installs carrying no identifier at all — reported in Ads
    Manager as perfectly healthy the whole time.

    Hence: on a store destination the tracking goes URL-ENCODED INSIDE `referrer=`
    via `_store_referrer_url` (the single implementation, shared with both Snap
    paths), and the caller must set it on the creative's LINK rather than in
    url_tags — see `meta.retarget_video_creative`.

    Note which parameter carries the ad id here. `_utm_query` reads it from
    rules/networks.yaml, so Meta gets `utm_content` where Snap gets `utm_id`
    (traffic-quality.ts joins on those, per network). Crossing them is a silent
    break on one network and harmless on the other, which is why neither is
    hardcoded at this call site.
    """
    if not _is_app_store(destination):
        return _utm_url(rules_dir, "meta", destination, campaign_name,
                        ad_set_id, ad_id, ad_name)
    utms = _utm_query(rules_dir, "meta", campaign_name, ad_set_id, ad_id, ad_name)
    return _store_referrer_url(destination, utms, ra_src="ad",
                               ra_lp=META_PLAY_DIRECT_AD_LANDING_PAGE)


def _snap_lead_end_page(rules_dir: Path, destination: str, *, campaign_name: str,
                        ad_squad_id: str, ad_name: str) -> str:
    """The URL a Snap lead form's end-page button sends her to, tracked.

    Two shapes, because the store and our own pages read attribution in
    completely different places, and sending one the other's URL loses it
    silently — which is the 2026-08-21 failure mode, not a cosmetic difference.

    OUR OWN PAGES take the params on the query string: the page reads them, fires
    its beacon, and rebuilds them into the Play referrer itself (see
    /get/w-apply's storeUrl builder in pocket-dating-coach).

    A STORE LISTING CANNOT DO ANY OF THAT. There is no beacon, no page view and
    no code of ours running. The only channel that survives the install is Play's
    `referrer` parameter, which the Play Store hands to the app at first launch,
    so the params have to be URL-ENCODED INSIDE that one parameter rather than
    appended to the listing URL. Appended, Play ignores them and every install off
    the ad is unattributable.

    What survives to `user_acquisition`, verified 2026-09-04 by reading the
    consuming code rather than assuming: mobile/lib/attribution.dart keeps every
    `utm_*` key plus `ra_lp` (as landingPage) and drops the rest, and the server's
    sanitizeUtm re-applies the same `^utm_` filter. So `ra_src=form` is carried
    for the human reading `referrer_raw` and is deliberately NOT the marker
    anything joins on — `ra_lp` is.

    `utm_id` (the ad id) is absent here for the same reason it is absent from the
    /get/w-apply path: Snap fixes the form's end page at creation, the form
    precedes the ad, and Snap documents no update. Attribution is at ad-squad
    level, by platform limit — the same limit the incumbent record already
    carries, so the two arms stay comparable.
    """
    utms = _utm_query(rules_dir, "snap", campaign_name, ad_squad_id, "", ad_name)
    utms = "&".join(q for q in utms.split("&") if not q.startswith("utm_id="))

    if not _is_app_store(destination):
        return f"{destination}?{utms}&ra_src=form"

    return _store_referrer_url(destination, utms, ra_src="form",
                               ra_lp=PLAY_DIRECT_LANDING_PAGE)


def cmd_snap_leads(args: argparse.Namespace, ledger: Ledger) -> None:
    """Manage where Snap delivers lead-form submissions.

    WHY THIS COMMAND EXISTS AT ALL. Snap has no endpoint that lists or downloads
    submitted leads — the only programmatic route off the platform is a webhook,
    registered per form. Until one is registered, every lead lives in Ads Manager
    and is deleted after 90 days. This command registers the destination; it never
    reads a lead, and no lead PII passes through this repo.

    THE RECEIVER IS IN pocket-dating-coach, deliberately. Leads are contact
    details; this repo records ad plans and outcomes. The webhook writes to
    marketing_leads with the service role from inside that app, and the read-only
    ads_agent_ro role is not granted that table.
    """
    # argparse cannot say "required, but only for these actions", and the failure
    # it produces otherwise is a TypeError deep in a URL f-string. Checked here so
    # a missing flag reads as a missing flag.
    needs = {
        "list": [("--form-id", args.form_id)],
        "register": [("--form-id", args.form_id), ("--url", args.url)],
        "test": [("--integration-id", args.integration_id)],
        "delete": [("--integration-id", args.integration_id)],
    }
    missing = [flag for flag, value in needs.get(args.action, []) if not value]
    if missing:
        print(f"error: snap-leads {args.action} needs {', '.join(missing)}", file=sys.stderr)
        raise SystemExit(2)

    if args.action == "register" and not args.url.startswith("https://"):
        # Snap posts lead PII to this URL. Plain http would put a phone number on
        # the wire in clear, and Snap's own signature does nothing about that.
        print("error: --url must be https", file=sys.stderr)
        raise SystemExit(2)

    config = load_config()
    client = snapapi.SnapClient(config.get("snap") or {})

    if args.action == "forms":
        forms = client.list_lead_forms()
        if not forms:
            print("no lead forms on this account")
            return
        for f in forms:
            hooks = client.list_lead_webhooks(f.get("id", ""))
            where = (client.webhook_url(hooks[0]) if hooks
                     else "-- no webhook, leads stay in Ads Manager")
            print(f"{f.get('id')}  {f.get('name')}\n    -> {where}")
        return

    if args.action == "list":
        hooks = client.list_lead_webhooks(args.form_id)
        if not hooks:
            print(f"form {args.form_id} has no webhook integration")
            return
        for h in hooks:
            print(f"{client.webhook_id(h)}  {client.webhook_url(h)}")
        return

    if args.action == "register":
        integration = client.register_lead_webhook(
            form_id=args.form_id, webhook_url=args.url)
        secret = client.webhook_secret(integration)
        print(f"registered: {client.webhook_id(integration)} -> {args.url}")
        if secret:
            # Printed once, on purpose. Snap does not return it from the list
            # endpoint later, and the receiver cannot authenticate a single
            # delivery without it. It is NOT written to the ledger or to any file
            # here: this repo's records are committed to git, and this is a
            # signing key.
            print()
            print("hmac secret (shown once — Snap will not return it again):")
            print(f"  {secret}")
            print()
            print("Set it on the receiver before the first lead arrives, or every")
            print("delivery is rejected 401 and retried until it expires:")
            print("  vercel env add SNAP_LEAD_HMAC_SECRET production")
        print()
        print("Snap does NOT backfill. Leads submitted before now exist only in the")
        print("Ads Manager export, and Snap deletes them after 90 days.")
        return

    if args.action == "test":
        client.test_lead_webhook(args.integration_id)
        print(f"test delivery fired at integration {args.integration_id}")
        print("check the receiver's logs — a 401 there means the hmac secret does not match")
        return

    if args.action == "delete":
        client.delete_lead_webhook(args.integration_id)
        print(f"deleted integration {args.integration_id}")
        print("leads submitted from now on are NOT queued — they stay in Ads Manager only")
        return


def cmd_snap_audience(args: argparse.Namespace, ledger: Ledger) -> None:
    """Create/grow a Snap Custom Audience or build a Lookalike from one — no clicking.

    Added 2026-09-01 so a female-lead Lookalike didn't have to be built by hand
    in Ads Manager again. `upsert` is additive: run it again next month with a
    longer --file and it grows the same audience by name rather than making a
    second one. This command still cannot attach an audience to an ad squad's
    targeting — that stays a human action in Ads Manager, same as every other
    live-account edit this repo refuses to automate.
    """
    del ledger  # unused — audiences aren't ledger objects
    config = load_config()
    client = snapapi.SnapClient(config.get("snap") or {})

    if args.action == "list":
        audiences = client.list_audiences()
        if not audiences:
            print("no audiences on this account")
            return
        for a in audiences:
            size = a.get("approximate_number_of_users", a.get("num_of_users", "?"))
            print(f"{a.get('id')}  {a.get('name')!r}  {a.get('source_type')}  users~{size}")
        return

    if args.action == "upsert":
        if not args.name or not args.file:
            print("error: snap-audience upsert needs --name and --file", file=sys.stderr)
            raise SystemExit(2)
        path = Path(args.file).expanduser()
        if not path.exists():
            print(f"error: {path} not found", file=sys.stderr)
            raise SystemExit(2)
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if lines and lines[0].lower() in ("email", "emails"):
            lines = lines[1:]
        if not lines:
            print(f"error: {path} has no emails after the header", file=sys.stderr)
            raise SystemExit(2)
        audience = client.upsert_customer_list_audience(
            args.name, lines, description=args.description or "")
        print(f"{audience['id']}  {args.name!r}  {len(lines)} email(s) uploaded")
        print("Snap takes time to process matches — a new upload reads 0 users for a while,")
        print("not an error.")
        return

    if args.action == "lookalike":
        if not args.name or not args.seed_name:
            print("error: snap-audience lookalike needs --name and --seed-name", file=sys.stderr)
            raise SystemExit(2)
        seed = client.find_audience(args.seed_name)
        if seed is None:
            print(f"error: no audience named {args.seed_name!r} — run 'snap-audience list' "
                  "to see what exists", file=sys.stderr)
            raise SystemExit(2)
        lookalike = client.create_lookalike_audience(
            args.name, seed_segment_id=seed["id"], country=args.country,
            similarity=args.similarity, description=args.description or "")
        print(f"{lookalike['id']}  {args.name!r}  seeded from {args.seed_name!r} "
              f"({args.country}, {args.similarity})")
        return


def cmd_snap_push(args: argparse.Namespace, ledger: Ledger) -> None:
    config = load_config()
    rec = ledger.find(args.rec_id)
    fm = rec.front_matter

    # Two checks, deliberately. This command only knows how to talk to Snap, and
    # separately the registry has to declare that creating on it is permitted at
    # all. The registry can only tighten this — editing it cannot teach this
    # function a second API.
    if fm.get("network") != "snap":
        print(f"error: {args.rec_id} is network={fm.get('network')!r}, not snap", file=sys.stderr)
        raise SystemExit(2)
    try:
        networkreg.require_creation(ledger.root / "rules", "snap", mode="paused-only")
    except networkreg.NetworkError as exc:
        _fail(exc)
    if fm.get("status") != "proposed":
        print(f"error: {args.rec_id} is {fm.get('status')!r}; push expects 'proposed'.\n"
              "A record that is already live has real ids — pushing again would create "
              "duplicates.", file=sys.stderr)
        raise SystemExit(2)

    # The destination gate applies here too: this is the moment the ad set is
    # actually pointed at a page, so it is the last useful place to catch a mismatch.
    try:
        destinations.check(ad_set_name=fm["ad_set_name"],
                           destination_url=fm["destination_url"],
                           rules_dir=ledger.root / "rules")
    except destinations.DestinationGateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    # Video first: a creative folder holding asset-a.mp4 is a video ad, and the only
    # thing that changes downstream is the media type Snap registers.
    cdir = ledger.root / fm["creative_ref"]
    asset, media_type = (cdir / "asset-a.mp4", "VIDEO")
    if not asset.exists():
        asset, media_type = (cdir / "asset-a.jpg", "IMAGE")
    qa = cdir / "qa.md"
    if not asset.exists():
        print(f"error: no creative at {cdir}/asset-a.mp4 or asset-a.jpg", file=sys.stderr)
        raise SystemExit(2)
    if not qa.exists() or "`pass`" not in qa.read_text(encoding="utf-8"):
        print(f"error: no recorded QA pass in {qa} — see rules/creative-generation.md sec 10",
              file=sys.stderr)
        raise SystemExit(2)
    # Watermark gate — same recorded-clearance requirement as snap-push-story, after
    # the 2026-08-30 live-sparkle incident. See watermark.py.
    try:
        watermarkgate.require_clearance(qa)
    except watermarkgate.WatermarkNotCleared as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if media_type == "IMAGE":
        print("watermark  qa.md clearance recorded; advisory corner scan:")
        try:
            print(f"           {watermarkgate.scan(asset)}")
        except Exception as exc:  # noqa: BLE001 — advisory only, never block a cleared push
            print(f"           (advisory scan skipped: {exc})")

    start = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)
    end = start + _dt.timedelta(days=int(fm["duration_days"]))
    def iso(d):
        return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    budget = float(fm["budget_cap_inr_per_day"])

    spec = fm.get("targeting")
    if not spec:
        print(f"error: {args.rec_id} has no structured `targeting` block, so there is nothing\n"
              "safe to push. Until 2026-08-26 this command used a hardcoded audience, which\n"
              "meant any record but the first would have been created with the first one's\n"
              "targeting and still diffed clean. Add it:\n"
              f"  ad-agent amend {args.rec_id} --reason 'add structured targeting' \\\n"
              "    --gender FEMALE --min-age 18 --max-age 22 --countries in --os ANDROID",
              file=sys.stderr)
        raise SystemExit(2)
    try:
        targetingspec.validate(spec)
        targetingspec.check_matches_ad_set_name(spec, fm["ad_set_name"])
    except targetingspec.TargetingError as exc:
        _fail(exc)
    targeting = targetingspec.to_snap(spec)

    store_bound = _is_app_store(fm["destination_url"])
    plan = [
        ("campaign   ", fm["campaign_name"]),
        ("ad squad   ", (f'{fm["ad_set_name"]}  Rs {budget:.0f}/day x '
                         f'{fm["duration_days"]}d, {args.optimization_goal}, AUTO_BID')),
        ("ad         ", fm["ad_name"]),
        ("creative   ", f'{asset.name}  headline={args.headline!r}  CTA={args.cta}'),
        ("destination", (f'{fm["destination_url"]}'
                         + ("  (app store — tracking goes inside Play's referrer=)"
                            if store_bound else ""))),
        ("targeting  ", targetingspec.describe(spec)),
    ]
    print(f"Plan for {args.rec_id} (everything created PAUSED):")
    for k, v in plan:
        print(f"  {k}  {v}")

    # A dry run still reads the parent campaign's spend cap. That check is the whole
    # reason to dry-run at all — it is the one thing that can silently invalidate the
    # test — so returning before it would leave the rehearsal unable to rehearse the
    # only failure it exists to catch. Both calls behind it are read-only GETs.
    client = None
    try:
        client = snapapi.SnapClient(config.get("snap") or {})
    except snapapi.SnapError as exc:
        if not args.dry_run:
            _fail(exc)
        print(f"\nnote: no Snap credentials, so the parent campaign's spend cap was NOT\n"
              f"      checked — the one thing most likely to make this ad set unreadable.\n"
              f"      ({exc})")

    campaign = None
    if client is not None:
        campaign = client.find_campaign(fm["campaign_name"])
        if campaign:
            print(f"\ncampaign  reusing {campaign['id']}")
        elif args.dry_run:
            print(f"\ncampaign  {fm['campaign_name']} does not exist yet; it would be created "
                  "new, with no cap to inherit")
        else:
            campaign = client.create_campaign(fm["campaign_name"], iso(start))
            print(f"\ncampaign  created {campaign['id']}")

    # Checked before the ad squad exists, not after: a cap that binds is cheaper to
    # fix while there is nothing hanging off the campaign yet.
    if campaign is not None:
        caps = client.campaign_caps(campaign["id"])
        _gate_campaign_caps(caps, squad_daily_inr=budget, duration_days=int(fm["duration_days"]),
                            rec_id=args.rec_id, accept=args.accept_campaign_cap)
        if not args.dry_run:
            ledger.record_campaign_caps(args.rec_id, daily_inr=caps.get("daily_inr"),
                                        lifetime_inr=caps.get("lifetime_inr"), today=_today())

    if args.dry_run:
        print("\n--dry-run: nothing created.")
        return

    squad = client.create_adsquad(name=fm["ad_set_name"], campaign_id=campaign["id"],
                                  targeting=targeting, daily_budget_inr=budget,
                                  start_time=iso(start), end_time=iso(end),
                                  pixel_id=(config.get("snap") or {}).get("pixel_id"),
                                  optimization_goal=args.optimization_goal)
    print(f"ad squad  created {squad['id']}")

    media = client.upload_media(f'{fm["ad_name"]}_MEDIA', asset, media_type=media_type)
    print(f"media     uploaded {media['id']}")

    # utm_id needs the ad id, which does not exist yet; the URL is rewritten below.
    provisional = _snap_traffic_url(ledger.root / "rules", fm["destination_url"],
                                    campaign_name=fm["campaign_name"],
                                    ad_squad_id=squad["id"], ad_id="",
                                    ad_name=fm["ad_name"])
    creative = client.create_creative(name=fm["ad_name"], media_id=media["id"],
                                      headline=args.headline, brand_name="Riteangle",
                                      url=provisional,
                                      profile_id=config["snap"]["profile_id"],
                                      call_to_action=args.cta)
    print(f"creative  created {creative['id']}")

    ad = client.create_ad(name=fm["ad_name"], ad_squad_id=squad["id"], creative_id=creative["id"])
    print(f"ad        created {ad['id']}")

    final_url = _snap_traffic_url(ledger.root / "rules", fm["destination_url"],
                                  campaign_name=fm["campaign_name"],
                                  ad_squad_id=squad["id"], ad_id=ad["id"],
                                  ad_name=fm["ad_name"])
    client.set_creative_url(creative, final_url)
    print("creative  landing URL rewritten with the real ad id")

    # ---- read back, and diff against what was asked for ----
    print("\nRead-back:")
    squad_live = client.get(f"/adsquads/{squad['id']}")["adsquads"][0]["adsquad"]
    ad_live = client.get(f"/ads/{ad['id']}")["ads"][0]["ad"]
    creative_live = client.get(f"/creatives/{creative['id']}")["creatives"][0]["creative"]

    checks = [
        ("ad squad status", squad_live.get("status"), "PAUSED"),
        ("ad status", ad_live.get("status"), "PAUSED"),
        ("daily budget", squad_live.get("daily_budget_micro"), int(budget * snapapi.MICRO)),
        ("optimisation goal", squad_live.get("optimization_goal"), args.optimization_goal),
        # Derived from the record's own spec, never from a literal — a read-back
        # compared against a hardcoded dict only ever validates the code against
        # itself, which is how a wrong audience would have passed silently.
        *targetingspec.snap_readback_checks(spec, squad_live),
        ("headline", creative_live.get("headline"), args.headline),
        ("call to action", creative_live.get("call_to_action"), args.cta),
        ("landing url", creative_live.get("web_view_properties", {}).get("url"), final_url),
    ]
    bad = 0
    for label, got, want in checks:
        ok = str(got) == str(want)
        bad += not ok
        print(f"  {'ok ' if ok else 'DIFF'}  {label:18} {got}")
        if not ok:
            print(f"        {'':18} expected: {want}")

    # Meta's per-feature creative enhancements, reported rather than assumed. The
    # single standard_enhancements opt-out was deprecated on 2026-08-28 and its
    # replacement names are documented only behind an internal URL, so the honest
    # thing is to print what Meta actually turned on and let a human decide. An
    # enhancement applied after rules/creative-generation.md's §10 QA gate voids the
    # sign-off that gate exists to give.
    dof = (creative_live.get("degrees_of_freedom_spec") or {}).get(
        "creative_features_spec") or {}
    opted_in = sorted(k for k, v in dof.items()
                      if str((v or {}).get("enroll_status", "")).upper() == "OPT_IN")
    if opted_in:
        print()
        print("CREATIVE ENHANCEMENTS Meta enabled by itself — the QA gate signed off on")
        print("the asset as built, and these change it after that sign-off:")
        for k in opted_in:
            print(f"  OPT_IN  {k}")
        print("  Turn them off per-ad in Ads Manager (Advantage+ creative) before enabling,")
        print("  or accept them deliberately. Names captured for a precise opt-out:")
        print(f"    {', '.join(opted_in)}")
    elif dof:
        print()
        print(f"creative enhancements: none opted in ({len(dof)} feature(s) reported)")

    print()
    if bad:
        print(f"{bad} field(s) differ from the plan. Fix in Ads Manager before enabling.")
    else:
        print("Every field matches the plan.")
    print("Nothing is live: all objects are PAUSED. Enabling is a human action in Ads Manager.")
    print(f"\nWhen you have enabled it, close the loop:\n"
          f"  ad-agent log-setup {args.rec_id} --network snap \\\n"
          f"    --campaign-id {campaign['id']} \\\n"
          f"    --ad-set-id {squad['id']} \\\n"
          f"    --ad-id {ad['id']}")


STORY_BEATS = ["a-ghosted", "b-catfish", "c-alone", "d-enough", "e-turn", "f-strength",
               "g-win", "h-calm", "i-world", "j-joy", "k-career", "l-close", "m-endcard"]


def cmd_snap_push_story(args: argparse.Namespace, ledger: Ledger) -> None:
    """Create a proposed Story Ad (COMPOSITE: a tap-through sequence) on Snap, PAUSED.

    Added 2026-08-30, after `snap-push-lead`'s 13-separate-ads run was rolled back
    for being the wrong format — Sree's actual ask was one ad the viewer taps
    through image by image. Snap's own docs exclude LEAD_GENERATION from a
    COMPOSITE's allowed child types, so this is WEB_VIEW, not lead-gen, on Sree's
    call once that conflict was surfaced.

    `creative_ref` here is a folder holding 13 subfolders in sequence order
    (STORY_BEATS), each `<beat>/asset-a.jpg` — not the single `asset-a.jpg` per
    folder that `snap-push`/`snap-push-lead` expect, because a Story ad's whole
    point is the sequence. QA is still gated at `creative_ref/qa.md`, one pass for
    the whole set, since the 13 images are unchanged from the (rolled-back) 13-ad
    attempt — only the delivery mechanism changed.
    """
    config = load_config()
    rec = ledger.find(args.rec_id)
    fm = rec.front_matter

    if fm.get("network") != "snap":
        print(f"error: {args.rec_id} is network={fm.get('network')!r}, not snap", file=sys.stderr)
        raise SystemExit(2)
    try:
        networkreg.require_creation(ledger.root / "rules", "snap", mode="paused-only")
    except networkreg.NetworkError as exc:
        _fail(exc)
    if fm.get("status") != "proposed":
        print(f"error: {args.rec_id} is {fm.get('status')!r}; push expects 'proposed'.",
              file=sys.stderr)
        raise SystemExit(2)
    try:
        destinations.check(ad_set_name=fm["ad_set_name"], destination_url=fm["destination_url"],
                           rules_dir=ledger.root / "rules")
    except destinations.DestinationGateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    cdir = ledger.root / fm["creative_ref"]
    beat_assets = [cdir / beat / "asset-a.jpg" for beat in STORY_BEATS]
    missing = [str(p) for p in beat_assets if not p.exists()]
    if missing:
        print(f"error: missing {len(missing)} of {len(STORY_BEATS)} story beats under {cdir}:\n  "
              + "\n  ".join(missing), file=sys.stderr)
        raise SystemExit(2)
    qa = cdir / "qa.md"
    if not qa.exists() or "`pass`" not in qa.read_text(encoding="utf-8"):
        print(f"error: no recorded QA pass in {qa} — see rules/creative-generation.md sec 10",
              file=sys.stderr)
        raise SystemExit(2)
    # Watermark gate (added after 2026-08-30, when a Story Ad shipped with Google's
    # "made with AI" sparkle baked into several plates). The qa.md must record an
    # explicit clearance; then print the advisory corner scan so the plates that most
    # warrant an eyeball are named. See watermark.py for why this is a recorded-check
    # gate rather than a pixel pass/fail.
    try:
        watermarkgate.require_clearance(qa)
    except watermarkgate.WatermarkNotCleared as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print("watermark  qa.md clearance recorded; advisory corner scan:")
    try:
        for hit in watermarkgate.advise(beat_assets):
            print(f"           {hit}")
    except Exception as exc:  # noqa: BLE001 — advisory only, never block a cleared push
        print(f"           (advisory scan skipped: {exc})")

    start = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)
    end = start + _dt.timedelta(days=int(fm["duration_days"]))
    def iso(d):
        return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    budget = float(fm["budget_cap_inr_per_day"])
    spec = fm.get("targeting")
    if not spec:
        print(f"error: {args.rec_id} has no structured `targeting` block.", file=sys.stderr)
        raise SystemExit(2)
    try:
        targetingspec.validate(spec)
        targetingspec.check_matches_ad_set_name(spec, fm["ad_set_name"])
    except targetingspec.TargetingError as exc:
        _fail(exc)
    targeting = targetingspec.to_snap(spec)

    plan = [
        ("campaign   ", fm["campaign_name"]),
        ("ad squad   ", (f'{fm["ad_set_name"]}  Rs {budget:.0f}/day x '
                         f'{fm["duration_days"]}d, SWIPES, AUTO_BID')),
        ("ad         ", f'{fm["ad_name"]}  (COMPOSITE, {len(STORY_BEATS)} snaps in sequence)'),
        ("sequence   ", " -> ".join(STORY_BEATS)),
        ("cta        ", f'{args.cta}  (swipe-up chip on every leaf snap)'),
        ("destination", fm["destination_url"]),
        ("targeting  ", targetingspec.describe(spec)),
    ]
    print(f"Plan for {args.rec_id} (everything created PAUSED):")
    for k, v in plan:
        print(f"  {k}  {v}")
    # Said out loud, because it is a real difference from what the record's
    # destination_url implies. LANDING_PAGE_VIEW is not offered for a STORY ad
    # squad on this account/pixel -- confirmed live, every conversion_window
    # value refused the same way -- so this squad optimises for swipe-throughs,
    # not confirmed page arrivals. The destination and its lead capture are still
    # real; only what Snap is bidding to maximise is different from a plain
    # WEB_VIEW/LANDING_PAGE_VIEW ad.
    print("  note         optimisation goal is SWIPES, not LANDING_PAGE_VIEW -- that goal is\n"
          "               not offered for a Story ad squad on this account/pixel (confirmed live)")

    client = None
    try:
        client = snapapi.SnapClient(config.get("snap") or {})
    except snapapi.SnapError as exc:
        if not args.dry_run:
            _fail(exc)
        print(f"\nnote: no Snap credentials, so the parent campaign's spend cap was NOT checked. ({exc})")

    campaign = None
    if client is not None:
        campaign = client.find_campaign(fm["campaign_name"])
        if campaign:
            print(f"\ncampaign  reusing {campaign['id']}")
        elif args.dry_run:
            print(f"\ncampaign  {fm['campaign_name']} does not exist yet; would be created new")
        else:
            campaign = client.create_campaign(fm["campaign_name"], iso(start))
            print(f"\ncampaign  created {campaign['id']}")

    if campaign is not None:
        caps = client.campaign_caps(campaign["id"])
        _gate_campaign_caps(caps, squad_daily_inr=budget, duration_days=int(fm["duration_days"]),
                            rec_id=args.rec_id, accept=args.accept_campaign_cap)
        if not args.dry_run:
            ledger.record_campaign_caps(args.rec_id, daily_inr=caps.get("daily_inr"),
                                        lifetime_inr=caps.get("lifetime_inr"), today=_today())

    if args.dry_run:
        print("\n--dry-run: nothing created.")
        return

    squad = client.find_adsquad(fm["ad_set_name"], campaign["id"])
    if squad:
        print(f"ad squad  reusing {squad['id']} (already existed under this campaign)")
    else:
        squad = client.create_adsquad(name=fm["ad_set_name"], campaign_id=campaign["id"],
                                      targeting=targeting, daily_budget_inr=budget,
                                      start_time=iso(start), end_time=iso(end),
                                      pixel_id=(config.get("snap") or {}).get("pixel_id"),
                                      optimization_goal="SWIPES")
        print(f"ad squad  created {squad['id']}")

    # utm_id needs the ad id, which does not exist until the composite ad is
    # created below — every leaf creative gets this same provisional URL first,
    # same trick set_creative_url already uses for a single-image WEB_VIEW ad.
    provisional = _utm_url(ledger.root / "rules", "snap", fm["destination_url"],
                           fm["campaign_name"], squad["id"], "", fm["ad_name"])

    # find_creative-then-create throughout: 15 creative objects for one Story ad
    # (13 leaves, 1 preview, 1 composite) is the most this module has ever made in
    # one run, and the first real attempt DID die partway (the preview media's
    # format, below) — a retry has to resume by finding what already exists
    # rather than re-uploading media and duplicating creatives it already made.
    leaf_ids = []
    print()
    for beat, asset in zip(STORY_BEATS, beat_assets):
        name = f'{fm["ad_name"]}_{beat.upper()}'
        existing = client.find_creative(name)
        if existing:
            leaf_ids.append(existing["id"])
            print(f"  snap {beat:12} reusing creative {existing['id']} (already existed)")
            continue
        media = client.upload_media(f'{name}_MEDIA', asset, media_type="IMAGE")
        creative = client.create_creative(
            name=name, media_id=media["id"],
            headline=args.headline, brand_name="riteangle", url=provisional,
            profile_id=config["snap"]["profile_id"], call_to_action=args.cta)
        leaf_ids.append(creative["id"])
        print(f"  snap {beat:12} media {media['id']}  creative {creative['id']}")

    preview_name = f'{fm["ad_name"]}_PREVIEW'
    preview = client.find_creative(preview_name)
    if preview:
        print(f"preview   reusing {preview['id']} (already existed)")
    else:
        preview_png = cdir / "preview.png"
        if not preview_png.exists():
            print(f"error: no {preview_png} — Snap's PREVIEW-tile media rejects JPEG "
                  "(\"Allowed extensions: png\"); the leaf snaps stay JPEG, only the "
                  "preview tile needs a PNG export.", file=sys.stderr)
            raise SystemExit(2)
        preview_media = client.upload_media(f'{preview_name}_MEDIA', preview_png, media_type="IMAGE")
        preview = client.create_preview_creative(
            name=preview_name, media_id=preview_media["id"], headline=args.preview_headline,
            profile_id=config["snap"]["profile_id"])
        print(f"preview   creative {preview['id']}")

    composite_name = f'{fm["ad_name"]}_COMPOSITE'
    composite = client.find_creative(composite_name)
    if composite:
        print(f"composite reusing {composite['id']} (already existed)")
    else:
        composite = client.create_composite_creative(
            name=composite_name, creative_ids=leaf_ids, preview_creative_id=preview["id"],
            profile_id=config["snap"]["profile_id"])
        print(f"composite creative {composite['id']}")

    ad = client.find_ad(fm["ad_name"], squad["id"])
    if ad:
        print(f"ad        reusing {ad['id']} (already existed under this ad squad)")
    else:
        ad = client.create_ad(name=fm["ad_name"], ad_squad_id=squad["id"], creative_id=composite["id"],
                             ad_type="STORY")
        print(f"ad        created {ad['id']}")

    final_url = _utm_url(ledger.root / "rules", "snap", fm["destination_url"],
                         fm["campaign_name"], squad["id"], ad["id"], fm["ad_name"])
    for beat, cid in zip(STORY_BEATS, leaf_ids):
        creative = client.get(f"/creatives/{cid}")["creatives"][0]["creative"]
        client.set_creative_url(creative, final_url)
    print(f"creative  all {len(leaf_ids)} leaf landing URLs rewritten with the real ad id")

    print("\nRead-back:")
    squad_live = client.get(f"/adsquads/{squad['id']}")["adsquads"][0]["adsquad"]
    ad_live = client.get(f"/ads/{ad['id']}")["ads"][0]["ad"]
    composite_live = client.get(f"/creatives/{composite['id']}")["creatives"][0]["creative"]
    first_leaf_live = client.get(f"/creatives/{leaf_ids[0]}")["creatives"][0]["creative"]

    checks = [
        ("ad squad status", squad_live.get("status"), "PAUSED"),
        ("ad status", ad_live.get("status"), "PAUSED"),
        ("daily budget", squad_live.get("daily_budget_micro"), int(budget * snapapi.MICRO)),
        ("optimisation goal", squad_live.get("optimization_goal"), "SWIPES"),
        *targetingspec.snap_readback_checks(spec, squad_live),
        ("composite creative_ids", (composite_live.get("composite_properties") or {}).get("creative_ids"),
         leaf_ids),
        ("composite preview_creative_id", composite_live.get("preview_creative_id"), preview["id"]),
        ("ad points at composite", ad_live.get("creative_id"), composite["id"]),
        ("first leaf CTA", first_leaf_live.get("call_to_action"), args.cta),
        ("first leaf landing url", first_leaf_live.get("web_view_properties", {}).get("url"), final_url),
    ]
    bad = 0
    for label, got, want in checks:
        ok = str(got) == str(want)
        bad += not ok
        print(f"  {'ok ' if ok else 'DIFF'}  {label:28} {got}")
        if not ok:
            print(f"        {'':28} expected: {want}")

    print()
    if bad:
        print(f"{bad} field(s) differ from the plan. Fix in Ads Manager before enabling.")
    else:
        print("Every field matches the plan.")
    print("Nothing is live: all objects are PAUSED. Enabling is a human action in Ads Manager.")
    print(f"\nWhen you have enabled it, close the loop:\n"
          f"  ad-agent log-setup {args.rec_id} --network snap \\\n"
          f"    --campaign-id {campaign['id']} \\\n"
          f"    --ad-set-id {squad['id']} \\\n"
          f"    --ad-id {ad['id']}")


def _gate_campaign_budget_optimization(caps: dict, *, rec_id: str) -> None:
    """Refuse to hang an ad set off a Meta campaign that holds the budget itself.

    This has no Snap equivalent and it is strictly worse than the cap problem that
    `_gate_campaign_caps` exists for. A capped campaign *reduces* the ad set's spend,
    which is at least proportional and visible in the numbers. A campaign using
    campaign-budget optimisation **ignores the ad-set budget outright** and
    distributes its own across children as it sees fit — so the `budget_cap_inr_per_day`
    the ledger record states, and that `rules/budget.md`'s floor was checked against,
    becomes a number with no relationship to what gets spent.

    There is no escape hatch, unlike the cap gate. `--accept-campaign-cap` exists
    because a low cap is sometimes deliberate; a CBO parent is not a deviation to
    accept, it is a statement that this record cannot mean what it says. Move the ad
    set to a non-CBO campaign, or turn CBO off in Ads Manager.
    """
    if not caps.get("campaign_budget_optimization"):
        return
    print(
        f"error: the parent campaign uses campaign-budget optimisation, so it holds the\n"
        f"       budget and this ad set's Rs/day would be IGNORED rather than capped.\n"
        f"       (campaign daily={caps.get('daily_inr')}, lifetime={caps.get('lifetime_inr')})\n\n"
        f"       {rec_id} states a budget cap that would not describe what gets spent, and\n"
        f"       rules/budget.md's floor was checked against that same number. Turn CBO off\n"
        f"       in Ads Manager, or point this record at a non-CBO campaign.\n\n"
        f"       There is deliberately no --accept flag for this: a low cap can be a\n"
        f"       choice, but a CBO parent means the record cannot mean what it says.",
        file=sys.stderr)
    raise SystemExit(2)


def cmd_snap_push_lead(args: argparse.Namespace, ledger: Ledger) -> None:
    """Create a proposed LEAD record on Snap, PAUSED, and diff it back.

    The Snap sibling of cmd_meta_push_lead, added the same day at the same
    request. Where Meta's push builds a provisional form and repoints the ad at a
    tracked one, Snap's cannot: the form's end-page URL is fixed at creation and
    Snap documents no update and no macro. So the URL carries ad-squad-level
    literals plus ra_src=form — the marker /get/w-apply admits without a lead id
    — and per-ad attribution is an accepted, recorded absence, not an oversight.
    """
    config = load_config()
    rec = ledger.find(args.rec_id)
    fm = rec.front_matter

    if fm.get("network") != "snap":
        print(f"error: {args.rec_id} is network={fm.get('network')!r}, not snap", file=sys.stderr)
        raise SystemExit(2)
    try:
        networkreg.require_creation(ledger.root / "rules", "snap", mode="paused-only")
    except networkreg.NetworkError as exc:
        _fail(exc)
    if fm.get("status") != "proposed":
        print(f"error: {args.rec_id} is {fm.get('status')!r}; push expects 'proposed'.",
              file=sys.stderr)
        raise SystemExit(2)
    try:
        destinations.check(ad_set_name=fm["ad_set_name"],
                           destination_url=fm["destination_url"],
                           rules_dir=ledger.root / "rules")
    except destinations.DestinationGateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    # Video and image share one path from here on: both go through
    # create_lead_creative's top_snap_media_id (snap.py's upload_media already
    # takes IMAGE or VIDEO), and Snap's LEAD_GENERATION creative type doesn't
    # care which. Added 2026-08-30 alongside the first image use of this command
    # (BUILD-YOURSELF-FIRST carousel) — video stayed the only path until then
    # because it was the only path exercised.
    asset_media_type = "VIDEO" if args.video else "IMAGE"
    asset = Path(args.video or args.image).expanduser()
    if not asset.exists():
        print(f"error: {asset_media_type.lower()} not found at {asset}", file=sys.stderr)
        raise SystemExit(2)
    qa = ledger.root / fm["creative_ref"] / "qa.md"
    if not qa.exists() or "`pass`" not in qa.read_text(encoding="utf-8"):
        print(f"error: no recorded QA pass in {qa} — see rules/creative-generation.md sec 10",
              file=sys.stderr)
        raise SystemExit(2)

    start = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)
    end = start + _dt.timedelta(days=int(fm["duration_days"]))
    def iso(d):
        return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    budget = float(fm["budget_cap_inr_per_day"])
    spec = fm.get("targeting")
    if not spec:
        print(f"error: {args.rec_id} has no structured `targeting` block.", file=sys.stderr)
        raise SystemExit(2)
    try:
        targetingspec.validate(spec)
        targetingspec.check_matches_ad_set_name(spec, fm["ad_set_name"])
    except targetingspec.TargetingError as exc:
        _fail(exc)
    targeting = targetingspec.to_snap(spec)

    privacy_url = "https://www.riteangle.dating/privacy-policy"

    plan = [
        ("campaign   ", f'{fm["campaign_name"]}  LEAD_GENERATION'),
        ("ad squad   ", (f'{fm["ad_set_name"]}  Rs {budget:.0f}/day x '
                         f'{fm["duration_days"]}d, LEAD_FORM_SUBMISSIONS, auto bid')),
        ("ad         ", fm["ad_name"]),
        ("form       ", (
            f'first name + phone + email, privacy={privacy_url}, copy='
            + repr((snapapi.FORM_COPY_STORE
                    if _is_app_store(fm["destination_url"])
                    else snapapi.FORM_COPY_PAGE)["title"])
            + ', end-page CTA ' + (snapapi.END_PAGE_CTA_STORE
                                   if _is_app_store(fm["destination_url"])
                                   else snapapi.END_PAGE_CTA_PAGE))),
        ("end page   ", (
            f'{fm["destination_url"]}&referrer=<squad-level utms + ra_lp='
            f'{PLAY_DIRECT_LANDING_PAGE}, url-encoded> (store listing: attribution '
            'rides Play\'s install referrer, nothing else survives)'
            if _is_app_store(fm["destination_url"]) else
            f'{fm["destination_url"]}?<squad-level utms>&ra_src=form '
            '(no per-lead id — Snap documents no macro)')),
        (f"{asset_media_type.lower():<11}", str(asset)),
        ("targeting  ", targetingspec.describe(spec)),
    ]
    print(f"Plan for {args.rec_id} (everything created PAUSED):")
    for k, v in plan:
        print(f"  {k}  {v}")

    client = None
    try:
        client = snapapi.SnapClient(config.get("snap") or {})
    except snapapi.SnapError as exc:
        if not args.dry_run:
            _fail(exc)
        print(f"\nnote: no Snap credentials; parent caps NOT checked. ({exc})")

    campaign = None
    if client is not None:
        campaign = client.find_campaign(fm["campaign_name"])
        if campaign:
            print(f"\ncampaign  reusing {campaign['id']}")
        elif args.dry_run:
            print(f"\ncampaign  {fm['campaign_name']} does not exist yet; would be created "
                  "new, objective LEAD_GENERATION")
        else:
            campaign = client.create_lead_campaign(fm["campaign_name"], iso(start))
            print(f"\ncampaign  created {campaign['id']}")

    if campaign is not None:
        caps = client.campaign_caps(campaign["id"])
        _gate_campaign_caps(caps, squad_daily_inr=budget, duration_days=int(fm["duration_days"]),
                            rec_id=args.rec_id, accept=args.accept_campaign_cap)
        if not args.dry_run:
            ledger.record_campaign_caps(args.rec_id, daily_inr=caps.get("daily_inr"),
                                        lifetime_inr=caps.get("lifetime_inr"), today=_today())

    if args.dry_run:
        print("\n--dry-run: nothing created.")
        return

    squad = client.find_adsquad(fm["ad_set_name"], campaign["id"])
    if squad:
        print(f"ad squad  reusing {squad['id']} (already existed under this campaign)")
    else:
        squad = client.create_lead_adsquad(
            name=fm["ad_set_name"], campaign_id=campaign["id"], targeting=targeting,
            daily_budget_inr=budget, start_time=iso(start), end_time=iso(end))
        print(f"ad squad  created {squad['id']}")

    # The end-page URL: rules/tracking.md's params as literals at squad level
    # (utm_id needs the ad id, which the form must precede), plus ra_src=form so
    # /get/w-apply admits her without a lead id.
    end_page = _snap_lead_end_page(
        ledger.root / "rules", fm["destination_url"],
        campaign_name=fm["campaign_name"], ad_squad_id=squad["id"], ad_name=fm["ad_name"])

    if args.form_id:
        form = {"id": str(args.form_id)}
        print(f"form      using existing {args.form_id}")
        # A reused form keeps the end-page URL it was CREATED with — Snap fixes it at
        # creation and documents no update — so `end_page` computed above is not what
        # this ad will actually send her to. Printing the computed one would assert an
        # attribution this push does not have: on 2026-08-31 the reused W18-30 form
        # still carried utm_content=VID_MOVE-ON-PROPER_A_20260829 while the push
        # printed _B_20260831. Read the real one back instead of guessing.
        try:
            live_form = client.get(f"/lead_generation_forms/{args.form_id}")
            row = (live_form.get("lead_generation_forms") or [{}])[0]
            props = ((row.get("lead_generation_form") or row)
                     .get("default_end_page") or {}).get("end_page_properties") or [{}]
            actual = props[0].get("url")
        except (snapapi.SnapError, LookupError, TypeError) as exc:
            # A reporting nicety must never fail a push that already created objects.
            actual = None
            print(f"          (could not read its end page back: {exc})")
        if actual:
            end_page = actual
            if fm["ad_name"] not in actual:
                print("          NOTE its end page names a DIFFERENT ad — lead-level "
                      f"attribution for {fm['ad_name']} is absent, by platform limit")
    else:
        form_name = f'RA_LEAD_{fm["ad_set_name"]}_SNAP'
        # "One step left" is only true when a step follows. On the store path
        # nothing does, so the form says the apply is done and the app is next.
        store = _is_app_store(fm["destination_url"])
        form_copy = snapapi.FORM_COPY_STORE if store else snapapi.FORM_COPY_PAGE
        form_cta = snapapi.END_PAGE_CTA_STORE if store else snapapi.END_PAGE_CTA_PAGE
        form = client.find_lead_form(form_name) or client.create_lead_form(
            name=form_name, privacy_url=privacy_url, end_page_url=end_page,
            copy=form_copy, end_page_cta=form_cta)
        print(f"form      {form['id']}")

    media = client.upload_media(f'{fm["ad_name"]}_MEDIA', asset, media_type=asset_media_type)
    print(f"{asset_media_type.lower():<9} uploaded media_id={media['id']}")

    creative = client.create_lead_creative(
        name=f'{fm["ad_name"]}_CREATIVE', media_id=media["id"],
        headline=args.headline, brand_name="riteangle",
        form_id=form["id"], profile_id=(config.get("snap") or {}).get("profile_id"))
    print(f"creative  created {creative['id']}")

    ad = client.find_ad(fm["ad_name"], squad["id"])
    if ad:
        print(f"ad        reusing {ad['id']} (already existed under this ad squad)")
    else:
        ad = client.create_lead_ad(name=fm["ad_name"], ad_squad_id=squad["id"],
                                   creative_id=creative["id"])
        print(f"ad        created {ad['id']}")

    print("\nRead-back:")
    squad_live = client.get(f"/adsquads/{squad['id']}")["adsquads"][0]["adsquad"]
    ad_live = client.get(f"/ads/{ad['id']}")["ads"][0]["ad"]
    checks = [
        ("ad squad status", squad_live.get("status"), "PAUSED"),
        ("ad status", ad_live.get("status"), "PAUSED"),
        ("ad type", ad_live.get("type"), "LEAD_GENERATION"),
        ("daily budget (micro)", squad_live.get("daily_budget_micro"),
         int(budget * snapapi.MICRO)),
        ("optimisation goal", squad_live.get("optimization_goal"), "LEAD_FORM_SUBMISSIONS"),
    ]
    for label, got, want in checks:
        ok = str(got) == str(want)
        print(f"  {'ok ' if ok else 'DIFF'}  {label}: {got!r}" + ("" if ok else f" (wanted {want!r})"))
    for label, got, want in targetingspec.snap_readback_checks(spec, squad_live):
        ok = str(got) == str(want)
        print(f"  {'ok ' if ok else 'DIFF'}  targeting {label}: {got!r}" + ("" if ok else f" (wanted {want!r})"))
    print(f"  end page  {end_page}")

    if _is_app_store(fm["destination_url"]):
        # The store test is NOT the page test with a different URL. Nothing of ours
        # runs on the listing, so "it loaded" proves nothing about attribution — the
        # referrer is only observable after an actual install, in user_acquisition.
        step2 = ("ONE end-to-end test in the Snapchat app preview: submit the form, tap the\n"
                 "     end-page button, confirm the Play listing for com.riteangle.app opens.\n"
                 "     THEN INSTALL FROM IT ON A REAL ANDROID DEVICE and sign in — the referrer is\n"
                 "     only observable after an install. Read the row back from user_acquisition\n"
                 f"     via ads_agent_ro and confirm ad_set={squad['id']} and\n"
                 f"     landing_page={PLAY_DIRECT_LANDING_PAGE}. A listing that merely opened is\n"
                 "     NOT this check — a bare listing URL opens exactly the same way and\n"
                 "     attributes nothing.")
    else:
        step2 = ("ONE end-to-end test in the Snapchat app preview: submit the form, tap the end-page\n"
                 "     button, confirm /get/w-apply LOADS (does not bounce to /get/w) and the\n"
                 "     marketing_apply_gate row lands with ra_lead null and the squad-level utm_term.")
    print(f"""
Created PAUSED. Before enabling:
  1. ad-agent log-setup {args.rec_id} --network snap --campaign-id {campaign['id']} --ad-set-id {squad['id']} --ad-id {ad['id']}
  2. {step2}
  3. Delete the test lead afterwards. Enabling is a human click in Ads Manager.""")


def cmd_meta_push_lead(args: argparse.Namespace, ledger: Ledger) -> None:
    """Create a proposed LEAD record on Meta, PAUSED, and diff it back.

    The lead-ads sibling of cmd_meta_push, built 2026-08-29 at the app owner's
    request (SPEC #3's shape: paused-only, guard at the transport, read-back). Where
    it differs from the link push, the objective forces it:

      * The creative is a VIDEO the app owner finished outside this repo, so its
        path arrives as --video rather than as creative_ref/asset-a.jpg. The QA gate
        stays: creative_ref/qa.md must record a `pass`.
      * There is no destination URL at the ad level — the form opens inside Meta.
        rules/tracking.md's five parameters ride the form's thank-you button URL
        instead, plus ra_lead={{lead_id}}, the one deliberate macro.
      * The thank-you URL needs the AD id, and the ad cannot exist before the form.
        Same resolution as attach_tracked_creative: a provisional form and creative
        get the ad made, then a tracked form carrying the real id is built and the
        ad is repointed. The provisional pair is left behind, unused — a spare
        object is the cheaper failure, as before.
    """
    config = load_config()
    rec = ledger.find(args.rec_id)
    fm = rec.front_matter

    if fm.get("network") != "meta":
        print(f"error: {args.rec_id} is network={fm.get('network')!r}, not meta", file=sys.stderr)
        raise SystemExit(2)
    try:
        networkreg.require_creation(ledger.root / "rules", "meta", mode="paused-only")
    except networkreg.NetworkError as exc:
        _fail(exc)
    if fm.get("status") != "proposed":
        print(f"error: {args.rec_id} is {fm.get('status')!r}; push expects 'proposed'.",
              file=sys.stderr)
        raise SystemExit(2)

    # The destination gate still runs even though the ad itself has no website
    # destination: the thank-you button is the moment paid traffic gets pointed at
    # a page, and that is exactly what the gate exists to check.
    try:
        destinations.check(ad_set_name=fm["ad_set_name"],
                           destination_url=fm["destination_url"],
                           rules_dir=ledger.root / "rules")
    except destinations.DestinationGateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    video = Path(args.video).expanduser()
    if not video.exists():
        print(f"error: video not found at {video}", file=sys.stderr)
        raise SystemExit(2)
    qa = ledger.root / fm["creative_ref"] / "qa.md"
    if not qa.exists() or "`pass`" not in qa.read_text(encoding="utf-8"):
        print(f"error: no recorded QA pass in {qa} — see rules/creative-generation.md sec 10\n"
              "(the finished video needs its own independent pass; compliance.md sec 8)",
              file=sys.stderr)
        raise SystemExit(2)

    start = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)
    end = start + _dt.timedelta(days=int(fm["duration_days"]))
    def iso(d):
        return d.strftime("%Y-%m-%dT%H:%M:%S+0000")

    budget = float(fm["budget_cap_inr_per_day"])
    spec = fm.get("targeting")
    if not spec:
        print(f"error: {args.rec_id} has no structured `targeting` block.", file=sys.stderr)
        raise SystemExit(2)
    try:
        targetingspec.validate(spec)
        targetingspec.check_matches_ad_set_name(spec, fm["ad_set_name"])
    except targetingspec.TargetingError as exc:
        _fail(exc)
    targeting = targetingspec.to_meta(spec)

    privacy_url = "https://www.riteangle.dating/privacy-policy"

    plan = [
        ("campaign   ", f'{fm["campaign_name"]}  OUTCOME_LEADS'),
        ("ad set     ", (f'{fm["ad_set_name"]}  Rs {budget:.0f}/day x '
                         f'{fm["duration_days"]}d, LEAD_GENERATION, instant form (ON_AD)')),
        ("ad         ", fm["ad_name"]),
        ("form       ", f'first name + phone + email, privacy={privacy_url}'),
        ("thank-you  ", f'{fm["destination_url"]}?<utms>&ra_lead={{{{lead_id}}}}'),
        ("video      ", str(video)),
        ("targeting  ", targetingspec.describe(spec)),
    ]
    print(f"Plan for {args.rec_id} (everything created PAUSED):")
    for k, v in plan:
        print(f"  {k}  {v}")
    if spec.get("regulated_content", True):
        print("  note         regulated_content has no Meta equivalent and is NOT sent; "
              "Meta gates dating at the account level instead")

    client = None
    try:
        client = metaapi.MetaClient(config.get("meta") or {})
    except metaapi.MetaError as exc:
        if not args.dry_run:
            _fail(exc)
        print(f"\nnote: no Meta credentials; parent caps NOT checked. ({exc})")

    campaign = None
    if client is not None:
        client.require_inr()
        campaign = client.find_campaign(fm["campaign_name"])
        if campaign:
            print(f"\ncampaign  reusing {campaign['id']}")
        elif args.dry_run:
            print(f"\ncampaign  {fm['campaign_name']} does not exist yet; would be created "
                  "new with objective OUTCOME_LEADS")
        else:
            campaign = client.create_campaign(fm["campaign_name"], objective="OUTCOME_LEADS")
            print(f"\ncampaign  created {campaign['id']}")

    if campaign is not None:
        caps = client.campaign_caps(campaign["id"])
        _gate_campaign_budget_optimization(caps, rec_id=args.rec_id)
        _gate_campaign_caps(caps, squad_daily_inr=budget, duration_days=int(fm["duration_days"]),
                            rec_id=args.rec_id, accept=args.accept_campaign_cap)
        if not args.dry_run:
            ledger.record_campaign_caps(args.rec_id, daily_inr=caps.get("daily_inr"),
                                        lifetime_inr=caps.get("lifetime_inr"), today=_today())

    if args.dry_run:
        print("\n--dry-run: nothing created.")
        return

    adset = client.find_adset(fm["ad_set_name"], campaign["id"])
    if adset:
        print(f"ad set    reusing {adset['id']} (already existed under this campaign)")
    else:
        adset = client.create_lead_adset(name=fm["ad_set_name"], campaign_id=campaign["id"],
                                         targeting=targeting, daily_budget_inr=budget,
                                         start_time=iso(start), end_time=iso(end))
        print(f"ad set    created {adset['id']}")

    print("video     uploading (Meta processes before it is usable; up to ~5 min) ...")
    video_id = client.upload_video(video)
    print(f"video     ready id={video_id}")

    # Thumbnail: the wedding laugh, extracted by the operator alongside the render
    # and named <video>.thumb.jpg — or fall back to the first frame Meta picks by
    # refusing, because a video creative without image_hash is rejected.
    thumb = video.with_suffix(".thumb.jpg")
    if not thumb.exists():
        print(f"error: thumbnail not found at {thumb} — export one frame (the 14.5s laugh) "
              "next to the video with that name.", file=sys.stderr)
        raise SystemExit(2)
    thumb_hash = client.upload_image(thumb)
    print(f"thumb     uploaded hash={thumb_hash}")

    def thank_you_url(with_ad_id: str | None) -> str:
        # rules/tracking.md's params as literals; utm_content (the ad id on Meta) is
        # only present once the ad exists. ra_lead stays a macro — the one value
        # that cannot be literal, because the lead does not exist until she submits.
        base = _utm_query(ledger.root / "rules", "meta", fm["campaign_name"],
                          adset["id"], with_ad_id or "", fm["ad_name"])
        if not with_ad_id:
            # drop the empty utm_content pair rather than sending utm_content=
            base = "&".join(p for p in base.split("&") if not p.startswith("utm_content="))
        return f'{fm["destination_url"]}?{base}&ra_lead={{{{lead_id}}}}'

    if args.form_id:
        form = {"id": str(args.form_id)}
        print(f"form      using existing {args.form_id} (its thank-you URL is YOURS to "
              "verify — this push cannot see or fix it)")
    else:
        form_name = f'RA_LEAD_{fm["ad_set_name"]}_PROV'
        form = client.find_lead_form(form_name) or client.create_lead_form(
            name=form_name, privacy_url=privacy_url,
            thank_you_url=thank_you_url(None))
        print(f"form      provisional {form['id']}")

    creative = client.create_lead_creative(
        name=f'{fm["ad_name"]}_CREATIVE', video_id=video_id, thumbnail_hash=thumb_hash,
        message=args.message, form_id=form["id"])
    print(f"creative  created {creative['id']}")

    ad = client.find_ad(fm["ad_name"], adset["id"])
    if ad:
        print(f"ad        reusing {ad['id']} (already existed under this ad set)")
    else:
        ad = client.create_ad(name=fm["ad_name"], adset_id=adset["id"],
                              creative_id=creative["id"])
        print(f"ad        created {ad['id']}")

    if not args.form_id:
        # Second pass: the form whose thank-you URL carries the real ad id. The ad is
        # repointed at a new creative bound to it; the provisional pair stays behind.
        tracked_name = f'RA_LEAD_{fm["ad_set_name"]}_TRACKED'
        tracked_form = client.find_lead_form(tracked_name) or client.create_lead_form(
            name=tracked_name, privacy_url=privacy_url,
            thank_you_url=thank_you_url(ad["id"]))
        tracked_creative = client.create_lead_creative(
            name=f'{fm["ad_name"]}_CREATIVE_TRACKED', video_id=video_id,
            thumbnail_hash=thumb_hash, message=args.message, form_id=tracked_form["id"])
        client.post(f"/{ad['id']}", {"creative": {"creative_id": str(tracked_creative["id"])}})
        after = client.get(f"/{ad['id']}", fields="id,status,creative")
        if (after.get("creative") or {}).get("id") != str(tracked_creative["id"]):
            print("error: ad did not repoint to the tracked creative — fix by hand in "
                  "Ads Manager before enabling.", file=sys.stderr)
            raise SystemExit(2)
        form = tracked_form
        print(f"form      tracked {form['id']} (thank-you URL carries the real ad id); "
              f"provisional pair left behind unused, as with link pushes")

    print("\nRead-back:")
    adset_live = client.get(
        f"/{adset['id']}",
        fields="id,name,status,daily_budget,optimization_goal,billing_event,"
               "destination_type,targeting,promoted_object")
    ad_live = client.get(f"/{ad['id']}", fields="id,name,status,creative")
    form_live = client.get(f"/{form['id']}", fields="id,name,status,thank_you_page")
    ty_url = (form_live.get("thank_you_page") or {}).get("website_url") or ""

    checks = [
        ("ad set status", adset_live.get("status"), "PAUSED"),
        ("ad status", ad_live.get("status"), "PAUSED"),
        ("daily budget (paise)", adset_live.get("daily_budget"),
         str(round(budget * metaapi.MINOR))),
        ("optimisation goal", adset_live.get("optimization_goal"), "LEAD_GENERATION"),
        ("destination", adset_live.get("destination_type"), "ON_AD"),
        ("promoted page", str((adset_live.get("promoted_object") or {}).get("page_id")),
         str((config.get("meta") or {}).get("page_id"))),
    ]
    for label, got, want in checks:
        ok = str(got) == str(want)
        print(f"  {'ok ' if ok else 'DIFF'}  {label}: {got!r}" + ("" if ok else f" (wanted {want!r})"))
    for label, got, want in targetingspec.meta_readback_checks(spec, adset_live):
        ok = str(got) == str(want)
        print(f"  {'ok ' if ok else 'DIFF'}  targeting {label}: {got!r}" + ("" if ok else f" (wanted {want!r})"))
    ra_ok = "ra_lead={{lead_id}}" in ty_url and ad["id"] in ty_url
    print(f"  {'ok ' if ra_ok else 'DIFF'}  thank-you URL carries ra_lead macro + real ad id")
    print(f"        {ty_url}")

    print(f"""
Created PAUSED. Before enabling (rules/tracking.md + setup-checklist.md):
  1. ad-agent log-setup {args.rec_id} --campaign-id {campaign['id']} --ad-set-id {adset['id']} --ad-id {ad['id']}
  2. ONE end-to-end test: preview the ad, submit the form, tap through, and confirm
     the marketing_apply_gate row carries a REAL ra_lead — not the literal braces.
     If it arrives as '{{{{lead_id}}}}', Meta did not resolve the macro and the join
     design falls back to ad-set-level; do not enable until this is known.
  3. Delete the test lead in Meta Lead Center afterwards.
  4. Enabling is a human click in Ads Manager, never this tool.""")


def cmd_meta_push(args: argparse.Namespace, ledger: Ledger) -> None:
    """Create a proposed record on Meta, PAUSED, and diff it back.

    The sibling of `cmd_snap_push`, and deliberately the same shape: same record
    gates, same destination gate, same QA-pass requirement, same parent-cap check,
    same read-back-and-diff. Where it differs, it differs because Meta does.
    """
    config = load_config()
    rec = ledger.find(args.rec_id)
    fm = rec.front_matter

    # Two checks, deliberately — the same pair snap-push makes. This command only
    # knows how to talk to Meta, and separately the registry has to declare that
    # creating on it is permitted at all. The registry can only tighten this;
    # editing it cannot teach this function a second API.
    if fm.get("network") != "meta":
        print(f"error: {args.rec_id} is network={fm.get('network')!r}, not meta", file=sys.stderr)
        raise SystemExit(2)
    try:
        networkreg.require_creation(ledger.root / "rules", "meta", mode="paused-only")
    except networkreg.NetworkError as exc:
        _fail(exc)
    if fm.get("status") != "proposed":
        print(f"error: {args.rec_id} is {fm.get('status')!r}; push expects 'proposed'.\n"
              "A record that is already live has real ids — pushing again would create "
              "duplicates.", file=sys.stderr)
        raise SystemExit(2)

    # The destination gate applies here too: this is the moment the ad set is
    # actually pointed at a page, so it is the last useful place to catch a mismatch.
    try:
        destinations.check(ad_set_name=fm["ad_set_name"],
                           destination_url=fm["destination_url"],
                           rules_dir=ledger.root / "rules")
    except destinations.DestinationGateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    # ---- which media, and where it comes from -----------------------------
    # Three routes, added 2026-09-06 (before that this command could only build a
    # still image from creative_ref/asset-a.jpg):
    #
    #   --video-id + --thumb-hash  reuse an asset ALREADY in this account's Meta
    #                              library. The point of this route is that the
    #                              viewer sees a byte-identical video to one the
    #                              app owner already approved and Meta already
    #                              reviewed — no re-upload, no re-encode. Meta
    #                              binds a creative's CTA at creation, so a new
    #                              creative OBJECT is still required; only the
    #                              media is shared.
    #   creative_ref/asset-a.mp4   upload the video, thumbnail expected beside it
    #                              as asset-a.thumb.jpg (Meta rejects a video
    #                              creative with no thumbnail).
    #   creative_ref/asset-a.jpg   the original still-image route, unchanged.
    #
    # The QA gate does NOT move: it is keyed on creative_ref/qa.md whichever route
    # supplies the pixels, because the gate signs off on the ASSET, and reusing a
    # library id must not become a way around it.
    cdir = ledger.root / fm["creative_ref"]
    qa = cdir / "qa.md"
    if not qa.exists() or "`pass`" not in qa.read_text(encoding="utf-8"):
        print(f"error: no recorded QA pass in {qa} — see rules/creative-generation.md sec 10",
              file=sys.stderr)
        raise SystemExit(2)

    asset = None            # local file to upload, if any
    media_type = "IMAGE"
    if args.video_id:
        if not args.thumb_hash:
            print("error: --video-id needs --thumb-hash too. Meta rejects a video creative\n"
                  "with no thumbnail, and a reused video has no local frame to extract one\n"
                  "from. Read it off the existing creative:\n"
                  "  object_story_spec.video_data.image_hash", file=sys.stderr)
            raise SystemExit(2)
        media_type = "VIDEO"
    elif (cdir / "asset-a.mp4").exists():
        asset, media_type = cdir / "asset-a.mp4", "VIDEO"
        if not (cdir / "asset-a.thumb.jpg").exists():
            print(f"error: {cdir}/asset-a.mp4 is a video, so Meta needs a thumbnail beside\n"
                  f"it at {cdir}/asset-a.thumb.jpg — export one frame. Or reuse an already\n"
                  "uploaded asset with --video-id/--thumb-hash.", file=sys.stderr)
            raise SystemExit(2)
    elif (cdir / "asset-a.jpg").exists():
        asset, media_type = cdir / "asset-a.jpg", "IMAGE"
    else:
        print(f"error: no creative at {cdir}/asset-a.mp4 or {cdir}/asset-a.jpg, and no\n"
              "--video-id given to reuse one from Meta's library", file=sys.stderr)
        raise SystemExit(2)

    # ---- what the ad set should optimise for ------------------------------
    # Derived from the destination, not passed in, because getting it wrong is
    # silent. LANDING_PAGE_VIEWS asks Meta to optimise toward a page of ours
    # loading; on a Play listing no page of ours loads, ever, so the goal names an
    # event that cannot occur. LINK_CLICKS optimises for the tap, which is
    # observably counted. Same correction the Snap arm made 2026-09-05
    # (LANDING_PAGE_VIEW -> SWIPES) for the same reason.
    store_bound = _is_app_store(fm["destination_url"])
    optimization_goal = "LINK_CLICKS" if store_bound else "LANDING_PAGE_VIEWS"

    start = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)
    end = start + _dt.timedelta(days=int(fm["duration_days"]))
    def iso(d):
        # Meta wants ISO 8601 with an offset, where Snap wants a milliseconds-and-Z
        # format. Same instant, different spelling; neither accepts the other's.
        return d.strftime("%Y-%m-%dT%H:%M:%S+0000")

    budget = float(fm["budget_cap_inr_per_day"])

    spec = fm.get("targeting")
    if not spec:
        print(f"error: {args.rec_id} has no structured `targeting` block, so there is nothing\n"
              "safe to push. Add it:\n"
              f"  ad-agent amend {args.rec_id} --reason 'add structured targeting' \\\n"
              "    --gender FEMALE --min-age 25 --max-age 30 --countries in",
              file=sys.stderr)
        raise SystemExit(2)
    try:
        targetingspec.validate(spec)
        targetingspec.check_matches_ad_set_name(spec, fm["ad_set_name"])
    except targetingspec.TargetingError as exc:
        _fail(exc)
    targeting = targetingspec.to_meta(spec)

    media_desc = (f'reusing Meta library video {args.video_id} '
                  f'(thumb {args.thumb_hash})' if args.video_id else asset.name)
    plan = [
        ("campaign   ", f'{fm["campaign_name"]}  OUTCOME_TRAFFIC'),
        ("ad set     ", (f'{fm["ad_set_name"]}  Rs {budget:.0f}/day x '
                         f'{fm["duration_days"]}d, {optimization_goal}, lowest cost')),
        ("ad         ", fm["ad_name"]),
        ("creative   ", (f'{media_type}  {media_desc}  '
                         f'headline={args.headline!r}  CTA={args.cta}')),
        ("destination", fm["destination_url"]),
        ("targeting  ", targetingspec.describe(spec)),
    ]
    print(f"Plan for {args.rec_id} (everything created PAUSED):")
    for k, v in plan:
        print(f"  {k}  {v}")
    # Said out loud in the plan for the same reason the regulated_content note
    # below is: a reader who is not told will assume the account's pixel covers
    # this ad, because it covers every other ad here.
    if store_bound:
        print("  tracking     store destination: tracking goes URL-ENCODED INSIDE Play's\n"
              "               referrer=, NOT in url_tags (Play strips appended params).\n"
              f"               ra_lp={META_PLAY_DIRECT_AD_LANDING_PAGE}, ra_src=ad")
        print("  NO PIXEL     the account pixel cannot fire on a Play listing — no page of\n"
              "               ours renders. marketing-conversions.ts's Meta CAPI forward is\n"
              "               driven by the landing page's store-click beacon, so this route\n"
              "               bypasses it too. Meta gets NO conversion signal from this ad:\n"
              "               LINK_CLICKS buys the cheapest tap, not the likeliest installer.\n"
              "               See rules/tracking.md, Meta direct-to-store coverage table.")
    # Said out loud in the plan, because it is the one field of the spec that does
    # not survive the crossing and a silent drop is how a reader comes to believe a
    # declaration was made that was not.
    if spec.get("regulated_content", True):
        print("  note         regulated_content has no Meta equivalent and is NOT sent; "
              "Meta gates dating at the account level instead")

    # A dry run still reads the parent campaign's budget state. That check is the
    # whole reason to dry-run — it is the one thing that can silently invalidate the
    # test — so returning before it would leave the rehearsal unable to rehearse the
    # only failure it exists to catch. Everything behind it is a read-only GET.
    client = None
    try:
        client = metaapi.MetaClient(config.get("meta") or {})
    except metaapi.MetaError as exc:
        if not args.dry_run:
            _fail(exc)
        print(f"\nnote: no Meta credentials, so the parent campaign's budget state was NOT\n"
              f"      checked — the one thing most likely to make this ad set unreadable.\n"
              f"      ({exc})")

    campaign = None
    if client is not None:
        # Before anything else: the currency, because every rupee figure below is
        # converted to paise on the way out and a non-INR account makes that wrong.
        client.require_inr()
        campaign = client.find_campaign(fm["campaign_name"])
        if campaign:
            print(f"\ncampaign  reusing {campaign['id']}")
        elif args.dry_run:
            print(f"\ncampaign  {fm['campaign_name']} does not exist yet; it would be created "
                  "new, with no budget of its own to inherit")
        else:
            campaign = client.create_campaign(fm["campaign_name"])
            print(f"\ncampaign  created {campaign['id']}")

    # Checked before the ad set exists, not after: a parent that would starve or
    # override this ad set is cheaper to fix while nothing hangs off it yet.
    if campaign is not None:
        caps = client.campaign_caps(campaign["id"])
        _gate_campaign_budget_optimization(caps, rec_id=args.rec_id)
        _gate_campaign_caps(caps, squad_daily_inr=budget, duration_days=int(fm["duration_days"]),
                            rec_id=args.rec_id, accept=args.accept_campaign_cap)
        if not args.dry_run:
            ledger.record_campaign_caps(args.rec_id, daily_inr=caps.get("daily_inr"),
                                        lifetime_inr=caps.get("lifetime_inr"), today=_today())

    if args.dry_run:
        print("\n--dry-run: nothing created.")
        return

    # Resume rather than duplicate. There is no rollback here and five objects to
    # create, so a run that dies partway is a normal state to recover from, not an
    # anomaly — see find_adset for the 2026-08-28 case this comes from. The read-back
    # below diffs a reused ad set against the record just as hard as a new one, so
    # reuse cannot smuggle in the wrong budget or audience.
    adset = client.find_adset(fm["ad_set_name"], campaign["id"])
    if adset:
        print(f"ad set    reusing {adset['id']} (already existed under this campaign)")
    else:
        adset = client.create_adset(name=fm["ad_set_name"], campaign_id=campaign["id"],
                                    targeting=targeting, daily_budget_inr=budget,
                                    start_time=iso(start), end_time=iso(end),
                                    pixel_id=(config.get("meta") or {}).get("pixel_id"),
                                    optimization_goal=optimization_goal)
        print(f"ad set    created {adset['id']}")

    if media_type == "VIDEO":
        if args.video_id:
            video_id, thumb_hash = str(args.video_id), args.thumb_hash
            print(f"video     reusing library id={video_id} thumb={thumb_hash} "
                  "(no re-upload — same bytes the owner approved)")
        else:
            print("video     uploading (Meta processes before it is usable; up to ~5 min) ...")
            video_id = client.upload_video(asset)
            thumb_hash = client.upload_image(asset.with_name("asset-a.thumb.jpg"))
            print(f"video     ready id={video_id} thumb={thumb_hash}")
        image_hash = None
    else:
        image_hash = client.upload_image(asset)
        video_id = thumb_hash = None
        print(f"image     uploaded hash={image_hash}")

    # The provisional creative carries the destination and the params that are known
    # now. On Meta the AD id is what the analytics joins on (utm_content, per
    # traffic-quality.ts) and the ad does not exist yet — so the id is written in
    # afterwards, by a second creative the ad is repointed at. Which FIELD it lands
    # in depends on the destination, and this is the part that is easy to get wrong:
    #
    #   a page of ours -> the ad's url_tags, which Meta appends to the query string
    #                     and the page reads.
    #   a store listing -> the creative's own LINK, with the tracking URL-encoded
    #                     inside Play's referrer=. url_tags is INERT here; Play
    #                     discards appended params, and the ad would look healthy
    #                     the entire time it produced unattributable installs.
    # The provisional link is the bare destination either way: the only thing
    # missing from it is the ad id, and that is what the repoint below adds.
    provisional_url = fm["destination_url"]
    if media_type == "VIDEO":
        creative = client.create_link_video_creative(
            name=f'{fm["ad_name"]}_CREATIVE', video_id=video_id,
            thumbnail_hash=thumb_hash, headline=args.headline, message=args.message,
            url=provisional_url, call_to_action=args.cta)
    else:
        creative = client.create_creative(
            name=f'{fm["ad_name"]}_CREATIVE', image_hash=image_hash,
            headline=args.headline, message=args.message,
            url=provisional_url, call_to_action=args.cta)
    print(f"creative  created {creative['id']}")

    ad = client.find_ad(fm["ad_name"], adset["id"])
    if ad:
        print(f"ad        reusing {ad['id']} (already existed under this ad set)")
    else:
        ad = client.create_ad(name=fm["ad_name"], adset_id=adset["id"],
                              creative_id=creative["id"])
        print(f"ad        created {ad['id']}")

    # The ad id only exists now, and utm_content has to carry it on Meta. Neither the
    # ad nor an existing creative accepts url_tags after the fact — the ad-level POST
    # returns 200 and silently does nothing — so the tracking arrives as a new
    # creative built with url_tags at creation, which the ad is then repointed at.
    # See MetaClient.attach_tracked_creative for what was tried and what persists.
    url_tags = _utm_query(ledger.root / "rules", "meta", fm["campaign_name"],
                          adset["id"], ad["id"], fm["ad_name"])
    tracked_link = _meta_traffic_url(
        ledger.root / "rules", fm["destination_url"], campaign_name=fm["campaign_name"],
        ad_set_id=adset["id"], ad_id=ad["id"], ad_name=fm["ad_name"])
    if store_bound:
        creative = client.retarget_video_creative(
            ad_id=ad["id"], creative=client.get(
                f"/{creative['id']}", fields="id,object_story_spec"),
            link=tracked_link, name=f'{fm["ad_name"]}_CREATIVE_TRACKED')
        print(f"creative  {creative['id']} attached, its CTA link carries the real ad id\n"
              f"          inside Play's referrer= (no {{{{macro}}}} to not resolve, and no\n"
              f"          url_tags, which Play would discard)")
    else:
        creative = client.attach_tracked_creative(
            ad_id=ad["id"], creative=client.get(
                f"/{creative['id']}", fields="id,object_story_spec"),
            url_tags=url_tags, name=f'{fm["ad_name"]}_CREATIVE_TRACKED')
        print(f"creative  {creative['id']} attached, url_tags carry the real ad id "
              f"(no {{{{macro}}}} to not resolve)")

    # ---- read back, and diff against what was asked for ----
    print("\nRead-back:")
    adset_live = client.get(
        f"/{adset['id']}",
        fields="id,name,status,daily_budget,optimization_goal,billing_event,targeting")
    # url_tags is NOT a readable field on an ad — asking for it 400s the whole
    # read-back ("Tried accessing nonexisting field"). It lives on the creative.
    ad_live = client.get(f"/{ad['id']}", fields="id,name,status,creative")
    creative_live = client.get(
        f"/{creative['id']}",
        fields="id,name,url_tags,object_story_spec,degrees_of_freedom_spec")
    story = creative_live.get("object_story_spec") or {}
    link_data = story.get("link_data") or {}
    video_data = story.get("video_data") or {}

    checks = [
        ("ad set status", adset_live.get("status"), "PAUSED"),
        ("ad status", ad_live.get("status"), "PAUSED"),
        # Compared in paise, in the unit Meta actually stores, so a minor-unit
        # mistake shows up here as a diff rather than as a plausible-looking number.
        ("daily budget (paise)", adset_live.get("daily_budget"),
         round(budget * metaapi.MINOR)),
        ("optimisation goal", adset_live.get("optimization_goal"), optimization_goal),
        # Derived from the record's own spec, never from a literal — a read-back
        # compared against a hardcoded dict only ever validates the code against
        # itself, which is how a wrong audience would pass silently.
        *targetingspec.meta_readback_checks(spec, adset_live),
    ]
    if media_type == "VIDEO":
        cta_link = ((video_data.get("call_to_action") or {}).get("value") or {}).get("link")
        checks += [
            ("headline", video_data.get("title"), args.headline),
            ("video id", video_data.get("video_id"),
             str(args.video_id) if args.video_id else video_id),
            ("thumbnail hash", video_data.get("image_hash"), thumb_hash),
            ("CTA link", cta_link, tracked_link),
        ]
    else:
        checks += [
            ("headline", link_data.get("name"), args.headline),
            ("landing url", link_data.get("link"),
             tracked_link if store_bound else fm["destination_url"]),
        ]
    if not store_bound:
        # url_tags is only the tracking channel for a page of ours. On a store
        # destination it is deliberately unset, so asserting it would fail on the
        # correct behaviour.
        checks.append(("url_tags", creative_live.get("url_tags"), url_tags))
    checks.append(("ad points at creative", (ad_live.get("creative") or {}).get("id"),
                   creative["id"]))
    bad = 0
    for label, got, want in checks:
        ok = str(got) == str(want)
        bad += not ok
        print(f"  {'ok ' if ok else 'DIFF'}  {label:22} {got}")
        if not ok:
            print(f"        {'':22} expected: {want}")

    # ---- the store-URL shape check, on the URL Meta actually stored ------
    # Not a comparison against our own string — that only proves the code agrees
    # with itself. This DECODES what came back and asserts the two properties that
    # were silently wrong on 2026-09-05: that Play will read the app id as the bare
    # package name (a stray second `?` made it `com.riteangle.app?utm_source=...`,
    # which would not have opened the right listing at all), and that the ad id is
    # inside the referrer rather than appended beside it where Play throws it away.
    if store_bound:
        stored = (((video_data.get("call_to_action") or {}).get("value") or {}).get("link")
                  if media_type == "VIDEO" else link_data.get("link"))
        q = parse_qs(urlsplit(stored or "").query)
        app_id = (q.get("id") or [""])[0]
        referrer = unquote((q.get("referrer") or [""])[0])
        ref = parse_qs(referrer)
        print("\nStore URL, as Meta stored it:")
        print(f"  {'ok ' if app_id == 'com.riteangle.app' else 'DIFF'}  "
              f"{'app id':22} {app_id!r}")
        if app_id != "com.riteangle.app":
            bad += 1
            print(f"        {'':22} expected: 'com.riteangle.app' — a corrupted app id "
                  "means the link may not open the right listing")
        for key, want in (("utm_content", ad["id"]), ("utm_term", adset["id"]),
                          ("utm_source", "fb"),
                          ("ra_lp", META_PLAY_DIRECT_AD_LANDING_PAGE)):
            got = (ref.get(key) or [""])[0]
            ok = got == str(want)
            bad += not ok
            print(f"  {'ok ' if ok else 'DIFF'}  {'referrer ' + key:22} {got!r}")
            if not ok:
                print(f"        {'':22} expected: {want!r}")
        print(f"  full link: {stored}")

    # Meta's per-feature creative enhancements, reported rather than assumed. The
    # single standard_enhancements opt-out was deprecated on 2026-08-28 and its
    # replacement names are documented only behind an internal URL, so the honest
    # thing is to print what Meta actually turned on and let a human decide. An
    # enhancement applied after rules/creative-generation.md's §10 QA gate voids the
    # sign-off that gate exists to give.
    dof = (creative_live.get("degrees_of_freedom_spec") or {}).get(
        "creative_features_spec") or {}
    opted_in = sorted(k for k, v in dof.items()
                      if str((v or {}).get("enroll_status", "")).upper() == "OPT_IN")
    if opted_in:
        print()
        print("CREATIVE ENHANCEMENTS Meta enabled by itself — the QA gate signed off on")
        print("the asset as built, and these change it after that sign-off:")
        for k in opted_in:
            print(f"  OPT_IN  {k}")
        print("  Turn them off per-ad in Ads Manager (Advantage+ creative) before enabling,")
        print("  or accept them deliberately. Names captured for a precise opt-out:")
        print(f"    {', '.join(opted_in)}")
    elif dof:
        print()
        print(f"creative enhancements: none opted in ({len(dof)} feature(s) reported)")

    print()
    if bad:
        print(f"{bad} field(s) differ from the plan. Fix in Ads Manager before enabling.")
        print("Meta rewrites targeting it considers suboptimal rather than rejecting it, so a\n"
              "diff on an audience field is a real change to what this test measures — not\n"
              "noise. Advantage Audience is the usual culprit.")
    else:
        print("Every field matches the plan.")
    print("Nothing is live: all objects are PAUSED. Enabling is a human action in Ads Manager.")
    print(f"\nWhen you have enabled it, close the loop:\n"
          f"  ad-agent log-setup {args.rec_id} --network meta \\\n"
          f"    --campaign-id {campaign['id']} \\\n"
          f"    --ad-set-id {adset['id']} \\\n"
          f"    --ad-id {ad['id']}")


def _pg_env(db_url: str) -> dict:
    """Split a postgres URL into PG* environment variables.

    Deliberately not passed to psql as an argv connection string: that puts the
    password in the process list for anything on the machine to read. PG* env
    vars are inherited by the child and never appear in `ps`.
    """
    import os
    from urllib.parse import unquote

    parts = urlsplit(db_url)
    if parts.scheme not in ("postgres", "postgresql"):
        raise ValueError(f"not a postgres URL: scheme {parts.scheme!r}")
    env = dict(os.environ)
    env.update({
        "PGHOST": parts.hostname or "",
        "PGPORT": str(parts.port or 5432),
        "PGUSER": unquote(parts.username or ""),
        "PGPASSWORD": unquote(parts.password or ""),
        "PGDATABASE": (parts.path or "/postgres").lstrip("/") or "postgres",
        # Supabase's pooler terminates TLS; without this psql may negotiate down.
        "PGSSLMODE": "require",
    })
    return env


#: What `user_acquisition` actually records, named here so no caller can quietly
#: believe otherwise. The row is written by pocket-dating-coach's
#: /api/attribution/install, which REQUIRES a Bearer session and keys the row on
#: user_id — so it cannot exist before sign-up completes. It is therefore a count
#: of SIGN-UPS carrying a campaign, not of installs and not of first opens.
#: Verified 2026-09-05 by reading mobile/lib/attribution.dart (returns early when
#: `Supabase.instance.client.auth.currentSession == null`) and that endpoint.
ACQUISITION_ROW_MEANS = "sign-ups (NOT installs, NOT first opens)"


def cmd_verify_tracking(args: argparse.Namespace, ledger: Ledger) -> None:
    """Run rules/tracking.md's post-launch check against live data.

    Exists because that check has been mandatory since the 2026-08-21 incident
    (54 Snap installs, zero attributable, a full week of spend) and until
    2026-09-05 nothing automated it — it depended on someone remembering to open
    a SQL client. `pdc.readonly_db_url` had been in the config schema that whole
    time with no code reading it. A mandated check that relies on memory is the
    same class of failure as the incident it was written for.

    THE THREE-WAY OUTCOME IS THE POINT. Zero rows is ambiguous — it means either
    "tracking is broken" or "nobody has signed up yet", and reporting the second
    as a failure trains people to ignore the check while reporting it as a pass
    is exactly the lie the incident was made of. So this never prints a bare
    PASS/FAIL:

      * observed   - rows exist carrying THIS ad's id. Tracking is proven.
      * suspicious - other rows landed in the window but none from this ad.
      * inconclusive - no rows at all in the window. Nothing is proven either way.

    **WHICH PARAMETER HOLDS THE AD ID IS PER-NETWORK, and this function got it
    wrong until 2026-09-07.** It hardcoded `utm_id`, which is Snap's join key.
    Meta puts the ad id in `utm_content` (rules/networks.yaml, traffic-quality.ts),
    so run against a Meta record this check looked in a column that could never
    hold the value — it would have reported 0 for this ad forever, no matter how
    perfect the tracking was, and reported `suspicious` the moment any unrelated
    row landed in the window. Found by running it against
    rec-2026-09-06-moveon-play-w1830-meta, the first Meta record it was ever
    pointed at. The param now comes from the registry, like every other place
    that needs it — see `_utm_query`, which had this right from the start.
    """
    rec = ledger.find(args.rec_id)
    fm = rec.front_matter
    ad_id = fm.get("ad_id")
    ad_set_id = fm.get("ad_set_id")
    if not ad_id:
        print(f"error: {args.rec_id} has no ad_id — run log-setup first, or the ad\n"
              "was never created. There is nothing to look for.", file=sys.stderr)
        raise SystemExit(2)

    db_url = (load_config().get("pdc") or {}).get("readonly_db_url")
    if not db_url:
        print("error: pdc.readonly_db_url is not set in config.local.yaml.",
              file=sys.stderr)
        raise SystemExit(2)

    import shutil
    import subprocess
    if not shutil.which("psql"):
        print("error: psql not found on PATH. This command shells out to psql rather\n"
              "than adding a postgres driver to a package whose only dependency is\n"
              "pyyaml. Install libpq (brew install libpq) or query by hand.",
              file=sys.stderr)
        raise SystemExit(2)

    since = args.since or fm.get("executed") or fm.get("created")
    # Snap joins the ad on utm_id, Meta on utm_content. Read it from the registry
    # rather than writing either literal here — this function hardcoded Snap's and
    # was silently unable to verify a Meta ad at all until 2026-09-07.
    join_param = networkreg.get(ledger.root / "rules",
                                fm.get("network") or "snap")["ad_join_param"]
    sql = f"""
    select
      coalesce(sum(case when utm->>'{join_param}' = '{ad_id}' then 1 else 0 end), 0) as this_ad,
      coalesce(sum(case when utm->>'{join_param}' is distinct from '{ad_id}' then 1 else 0 end), 0) as other,
      count(*) as total
    from user_acquisition
    where created_at >= '{since}'::date;
    """
    detail = f"""
    select created_at, network, campaign, ad_set, landing_page, platform,
           utm->>'{join_param}' as ad_id
    from user_acquisition
    where created_at >= '{since}'::date
    order by created_at desc limit 20;
    """
    try:
        env = _pg_env(db_url)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    def run(query: str) -> str:
        out = subprocess.run(["psql", "-At", "-F", "|", "-c", query],
                             env=env, capture_output=True, text=True,
                             timeout=60, check=False)
        if out.returncode != 0:
            print(f"psql failed:\n{out.stderr.strip()[:600]}", file=sys.stderr)
            raise SystemExit(1)
        return out.stdout.strip()

    counts = run(sql).split("|")
    this_ad, other, total = (int(x) for x in counts)

    print(f"Post-launch tracking check — {args.rec_id}")
    print(f"  ad id        {ad_id}")
    print(f"  ad set id    {ad_set_id}")
    print(f"  window       rows created on/after {since}")
    print(f"  measuring    {ACQUISITION_ROW_MEANS}")
    print()
    print(f"  rows carrying this ad's {join_param:<10} : {this_ad}")
    print(f"  rows from anything else        : {other}")
    print(f"  rows in window, total          : {total}")
    print()

    if this_ad > 0:
        print(f"OBSERVED — this ad's {join_param} reached user_acquisition. The")
        print("referrer chain is proven for this funnel shape, not merely expected.")
    elif total > 0:
        print("SUSPICIOUS — rows landed in this window but none carry this ad's")
        print(f"{join_param}. Either nobody from this ad has signed up yet, or the")
        print("referrer is being dropped. Check the rows below for the landing")
        print("page's hardcoded default (utm_campaign=get_lp with nothing else),")
        print("which is what the 2026-08-21 incident looked like.")
    else:
        print("INCONCLUSIVE — no rows at all in this window, so nothing is proven")
        print("either way. This is the expected state for a fresh ad: a row needs a")
        print("completed SIGN-UP, which is several steps past the install. Re-run")
        print("this once the ad has produced real signups.")

    if total > 0 or args.detail:
        print("\nRecent rows:")
        rows = run(detail)
        print(f"  created_at|network|campaign|ad_set|landing_page|platform|{join_param}")
        for line in (rows.splitlines() or ["  (none)"]):
            print(f"  {line}")


def cmd_log_setup(args: argparse.Namespace, ledger: Ledger) -> None:
    _check_network(ledger.root / "rules", args.network)
    rec = ledger.log_setup(
        args.rec_id,
        network=args.network,
        campaign_id=args.campaign_id,
        ad_set_id=args.ad_set_id,
        ad_id=args.ad_id,
        deviated=args.deviated,
        today=_today(),
    )
    ledger.write_index()
    print(f"logged setup for {rec.rec_id} -> status=live")


def cmd_note(args: argparse.Namespace, ledger: Ledger) -> None:
    try:
        rec = ledger.note(args.rec_id, text=args.text, kind=args.kind, today=_today())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    ledger.write_index()
    print(f"noted on {rec.rec_id} ({args.kind}) -> {rec.path}")


# A campaign verdict is evidence about a creative and evidence about a belief.
# rules/creative-generation.md sec 9 requires the first; the research loop needs
# the second. Both were written down as things someone should remember to do,
# which is how they stop happening around run four.
_VERDICT_TO_OUTCOME = {
    "working": "supported",
    "not-working": "contradicted",
    # A campaign can be unreadable for reasons that say nothing about the claim —
    # a campaign cap below the floor, broken tracking. That records the evidence
    # without moving the belief, which is the honest handling.
    "inconclusive": "inconclusive",
}


def _write_prompt_outcome(ledger: Ledger, rec, verdict: str, summary: str, today: str) -> str:
    """Append the verdict to the creative's prompt pack.

    rules/creative-generation.md sec 9: the reason the exact prompt text is kept is
    that a ranked prompt library accumulates across campaigns — which prompt
    patterns produce assets that earn taps, per persona. A prompt with no outcome
    attached taught nothing, so the audience goes in the entry too.
    """
    fm = rec.front_matter
    ref = str(fm.get("creative_ref") or "").strip("/")
    if not ref:
        return "no creative_ref on the record — prompt library not updated"
    prompts = ledger.root / ref / "prompts.md"
    if not prompts.exists():
        return f"{ref}/prompts.md does not exist — prompt library not updated"

    spec = fm.get("targeting")
    audience = targetingspec.describe(spec) if spec else str(fm.get("targeting_summary") or "")[:80]
    budget = fm.get("budget_cap_inr_per_day")
    cap = fm.get("campaign_daily_cap_inr")
    effective = min(budget, cap) if (budget is not None and cap is not None) else budget
    spend = f"Rs {float(effective):.0f}/day x {fm.get('duration_days')}d" if effective else "n/a"

    prompts.write_text(
        prompts.read_text(encoding="utf-8").rstrip()
        + f"\n\n## Outcome — {fm['rec_id']} ({today})\n\n"
        f"**{verdict}** — {summary.strip()}\n\n"
        f"- Ad set: `{fm.get('ad_set_name')}`\n"
        f"- Audience: {audience}\n"
        f"- Spend: {spend}\n",
        encoding="utf-8",
    )
    return f"{ref}/prompts.md"


def cmd_log_review(args: argparse.Namespace, ledger: Ledger) -> None:
    today = _today()
    try:
        rec = ledger.log_review(
            args.rec_id,
            verdict=args.verdict,
            summary=args.summary,
            review_log_path=args.review_log,
            today=today,
        )
    except ValueError as exc:
        _fail(exc)
    ledger.write_index()
    print(f"logged review for {rec.rec_id} -> verdict={args.verdict}")

    # --- back-edge 1: the prompt library ---
    print(f"  creative:  {_write_prompt_outcome(ledger, rec, args.verdict, args.summary, today)}")

    # --- back-edge 2: the beliefs this recommendation rested on ---
    r = _research(ledger)
    refs = list(args.learning or [])
    idea_id = rec.front_matter.get("from_idea")
    idea = r.idea_for_rec(rec.rec_id) if not idea_id else None
    if idea is not None:
        idea_id = idea.front_matter["id"]
    if idea_id:
        try:
            refs += [x for x in (r.find(idea_id).front_matter.get("learnings") or [])
                     if x not in refs]
        except KeyError:
            print(f"  warning:   {idea_id} is on the record but not in ideas/")

    if not refs:
        # Said out loud rather than passed over in silence: a verdict that updates
        # no belief means nothing in the library gets corrected by this result.
        print("  learnings: none — this record is not linked to any. Attach one with "
              f"`log-evidence <id> --from {rec.rec_id}` if it bears on a claim.")
        return

    outcome = _VERDICT_TO_OUTCOME[args.verdict]
    for ref in refs:
        try:
            updated = r.log_evidence(ref, outcome=outcome, text=args.summary,
                                     from_ref=rec.rec_id, today=today)
        except (researchmod.ResearchError, KeyError) as exc:
            print(f"  warning:   {ref} not updated: {exc}", file=sys.stderr)
        else:
            print(f"  learning:  {ref} -> {outcome} (now {updated.front_matter['status']})")


def cmd_abandon(args: argparse.Namespace, ledger: Ledger) -> None:
    rec = ledger.abandon(args.rec_id, reason=args.reason, today=_today())
    ledger.write_index()
    print(f"abandoned {rec.rec_id}")


def cmd_stats(args: argparse.Namespace, ledger: Ledger) -> None:
    records = ledger.all()
    by_status: dict[str, int] = {}
    by_verdict: dict[str, int] = {}
    for r in records:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        v = r.front_matter.get("verdict")
        if v:
            by_verdict[v] = by_verdict.get(v, 0) + 1

    print(f"total: {len(records)}")
    for s in STATUSES:
        if by_status.get(s):
            print(f"  {s}: {by_status[s]}")
    if by_verdict:
        print("verdicts (of reviewed):")
        for v, n in sorted(by_verdict.items()):
            print(f"  {v}: {n}")


def cmd_dump_ledger(args: argparse.Namespace, ledger: Ledger) -> None:
    path = ledger.write_index()
    text = path.read_text(encoding="utf-8")
    if args.status:
        lines = text.splitlines()
        header, rows = lines[:6], lines[6:]
        rows = [r for r in rows if f"| {args.status} |" in r]
        text = "\n".join(header + rows)
    print(text)


def _research(ledger: Ledger) -> researchmod.Research:
    return researchmod.Research(ledger.root)


def _research_fail(exc: Exception) -> None:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc


def cmd_ingest(args: argparse.Namespace, ledger: Ledger) -> None:
    """Store a note exactly as it was brought in. Never edited afterwards."""
    text = Path(args.file).read_text(encoding="utf-8") if args.file else (args.text or "")
    try:
        rec = _research(ledger).ingest(title=args.title, text=text, source=args.source,
                                       slug=args.slug, today=_today())
    except (researchmod.ResearchError, OSError) as exc:
        _research_fail(exc)
    print(f"ingested {rec.front_matter['id']} -> {rec.path}")
    print("Nothing has been learned from it yet. Derive the claims with `ad-agent learn "
          f"--derived-from {rec.front_matter['id']} ...` — an ingested note with no learnings "
          "is an open loose end, and `ad-agent open` will keep saying so.")


def cmd_learn(args: argparse.Namespace, ledger: Ledger) -> None:
    r = _research(ledger)
    # Surface neighbours before writing. The CLI cannot judge whether two claims
    # are the same, but it can put them in front of whoever can.
    siblings = [x for x in r.learnings()
                if x.front_matter.get("subject") == args.subject
                and x.front_matter.get("status") not in ("retired",)]
    try:
        rec = r.learn(
            claim=args.claim, subject=args.subject, source=args.source,
            confidence=args.confidence, sample_n=args.sample_n, evidence=args.evidence,
            derived_from=args.derived_from, answers=args.answers, slug=args.slug,
            today=_today(),
        )
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    print(f"learned {rec.front_matter['id']} -> {rec.path}")
    if siblings:
        print(f"\n{len(siblings)} existing learning(s) on `{args.subject}` — if this restates one "
              "of them,\nthat is `log-evidence` on the original, not a second atom:")
        for x in siblings[:8]:
            fm = x.front_matter
            print(f"  {fm['id']}  [{fm.get('confidence')}/{fm.get('status')}] {fm.get('claim')}")


def cmd_log_evidence(args: argparse.Namespace, ledger: Ledger) -> None:
    try:
        rec = _research(ledger).log_evidence(args.learning_id, outcome=args.outcome,
                                             text=args.text, from_ref=args.from_ref,
                                             today=_today())
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    print(f"{rec.front_matter['id']} -> status={rec.front_matter['status']}")


def cmd_reclassify(args: argparse.Namespace, ledger: Ledger) -> None:
    if not any((args.subject, args.source, args.confidence, args.sample_n)):
        print("error: nothing to reclassify — pass at least one of --subject, --source, "
              "--confidence, --sample-n", file=sys.stderr)
        raise SystemExit(2)
    try:
        rec, diff = _research(ledger).reclassify(
            args.learning_id, subject=args.subject, source=args.source,
            confidence=args.confidence, sample_n=args.sample_n, reason=args.reason,
            today=_today())
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    if not diff:
        print(f"{rec.front_matter['id']}: no change — every field already had that value")
        return
    print(f"reclassified {rec.front_matter['id']}")
    for field, (old, new) in sorted(diff.items()):
        print(f"  {field}: {old!r} -> {new!r}")


def cmd_promote(args: argparse.Namespace, ledger: Ledger) -> None:
    try:
        rec = _research(ledger).promote(args.learning_id, rule_file=args.rule, today=_today())
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    print(f"promoted {rec.front_matter['id']} into {args.rule}")
    print("Remember the edit itself: this records that the rule now carries the claim, it does "
          "not write it. rules/ is what skills obey.")


def cmd_retire(args: argparse.Namespace, ledger: Ledger) -> None:
    try:
        rec = _research(ledger).retire(args.learning_id, reason=args.reason, today=_today())
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    print(f"retired {rec.front_matter['id']}")


def cmd_question(args: argparse.Namespace, ledger: Ledger) -> None:
    try:
        rec = _research(ledger).question(text=args.text, kind=args.kind, why=args.why,
                                         raised_by=args.raised_by, slug=args.slug,
                                         today=_today())
    except researchmod.ResearchError as exc:
        _research_fail(exc)
    print(f"asked {rec.front_matter['id']} -> {rec.path}")


def cmd_answer(args: argparse.Namespace, ledger: Ledger) -> None:
    try:
        rec = _research(ledger).answer(args.question_id, text=args.text, learning=args.learning,
                                       dropped=args.dropped, today=_today())
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    print(f"{rec.front_matter['id']} -> {rec.front_matter['status']}")


def cmd_idea(args: argparse.Namespace, ledger: Ledger) -> None:
    _check_network(ledger.root / "rules", args.network)
    if budgetrules.below_floor(args.est_daily):
        print(f"note: {budgetrules.floor_note(args.est_daily)}\n"
              "      An idea costed below the floor is proposing a system check, not a test.",
              file=sys.stderr)
    try:
        rec = _research(ledger).idea(
            title=args.title, verdict=args.verdict, network=args.network, persona=args.persona,
            est_daily_inr=args.est_daily, est_days=args.est_days, rationale=args.rationale,
            learnings=args.learning or [], blocked_on=args.blocked_on, slug=args.slug,
            today=_today(),
        )
    except (researchmod.ResearchError, KeyError) as exc:
        _research_fail(exc)
    fm = rec.front_matter
    print(f"{fm['verdict']} {fm['id']} -> {rec.path}  "
          f"(Rs {fm['est_daily_inr']:.0f}/day x {fm['est_days']}d = Rs {fm['est_total_inr']:.0f})")


def _age_days(today: _dt.date, when) -> int | None:
    try:
        return (today - _dt.date.fromisoformat(str(when))).days
    except (TypeError, ValueError):
        return None


def _effective_daily(fm: dict) -> tuple[float | None, str]:
    """The daily spend that actually binds, and how sure we are of it.

    `budget_cap_inr_per_day` is what was proposed. A campaign-level cap silently
    overrides it. Records pushed since 2026-08-26 carry the observed cap, so the
    effective figure is knowable; older ones do not, and this says so rather than
    quietly reporting the proposed number as though it were the real one.
    """
    proposed = fm.get("budget_cap_inr_per_day")
    if proposed is None:
        return None, "no budget on record"
    proposed = float(proposed)
    if not fm.get("campaign_caps_verified"):
        return proposed, "campaign cap never checked"
    cap = fm.get("campaign_daily_cap_inr")
    if cap is None:
        return proposed, "verified: no campaign cap"
    return min(proposed, float(cap)), f"campaign cap Rs {float(cap):.0f}/day binds"


def cmd_open(args: argparse.Namespace, ledger: Ledger) -> None:
    """Every loose end the ledger can see, in one place.

    The point is not a syntax reference — it is the answer to "where was I". A
    loop-engineered system's failure mode is not a wrong decision, it is a step
    that quietly never happened: a proposal never executed, a live ad set past its
    kill window with no verdict, a creative that cleared QA and was never used.
    None of that is visible in INDEX.md, which only lists records.

    Everything below is derived. This command holds no state of its own.
    """
    today = _dt.date.fromisoformat(_today())
    records = ledger.all()
    root = ledger.root
    sections: list[tuple[str, list[str]]] = []

    # --- proposals that never became anything ---
    rows = []
    for r in records:
        if r.status != "proposed":
            continue
        age = _age_days(today, r.front_matter.get("created"))
        stale = " STALE" if (age or 0) > 7 else ""
        rows.append(f"{r.rec_id}  proposed {age}d ago{stale}  "
                    f"-> snap-push, or abandon --reason")
    if rows:
        sections.append(("Proposed, never executed", rows))

    # --- live ad sets, against their own kill/double window ---
    due, running = [], []
    for r in records:
        if r.status != "live":
            continue
        fm = r.front_matter
        since = _age_days(today, fm.get("executed"))
        window = int(fm.get("duration_days") or budgetrules.KILL_WINDOW_DAYS_MAX)
        if since is None:
            running.append(f"{r.rec_id}  live, no execution date on record")
        elif since >= window:
            due.append(f"{r.rec_id}  live {since}d, window was {window}d  "
                       f"-> ad-audit, then log-review")
        else:
            running.append(f"{r.rec_id}  live {since}d of {window}d  "
                           f"-> review from {(_dt.date.fromisoformat(str(fm['executed'])) + _dt.timedelta(days=window)).isoformat()}")
    if due:
        sections.append(("Live and past the review window — no verdict yet", due))
    if running:
        sections.append(("Live, still inside the window", running))

    # --- funding, per rules/budget.md ---
    rows = []
    for r in records:
        if r.status not in ("proposed", "live"):
            continue
        eff, why = _effective_daily(r.front_matter)
        if eff is None:
            continue
        if budgetrules.below_floor(eff):
            rows.append(f"{r.rec_id}  Rs {eff:.0f}/day effective ({why})  "
                        f"-> below the Rs {budgetrules.MIN_VIABLE_DAILY_INR:.0f} floor; "
                        f"a weak read is inconclusive, not evidence")
        elif r.status == "live" and not r.front_matter.get("campaign_caps_verified"):
            # Only meaningful once something is live: a proposal has no parent
            # campaign to have been capped by yet.
            rows.append(f"{r.rec_id}  Rs {eff:.0f}/day proposed, but {why}  "
                        f"-> the real figure may be lower")
    if rows:
        sections.append(("Funding below the floor, or unverified", rows))

    # --- creative: cleared but unused, and used but unreviewed ---
    referenced = {str(r.front_matter.get("creative_ref") or "").strip("/") for r in records}
    uncleared, unused, no_backedge = [], [], []
    for r in records:
        ref = str(r.front_matter.get("creative_ref") or "").strip("/")
        if not ref or r.status in ("abandoned",):
            continue
        qa = root / ref / "qa.md"
        if not qa.exists() or "`pass`" not in qa.read_text(encoding="utf-8"):
            uncleared.append(f"{r.rec_id}  {ref}  -> no recorded QA pass "
                             f"(rules/creative-generation.md sec 10)")
    for d in sorted((root / "creatives").glob("*/")):
        ref = f"creatives/{d.name}"
        qa = d / "qa.md"
        if not qa.exists():
            continue
        if "`pass`" in qa.read_text(encoding="utf-8") and ref not in referenced:
            unused.append(f"{ref}  cleared QA, no record uses it  -> propose one, or say why not")
    for r in records:
        if r.status != "reviewed":
            continue
        ref = str(r.front_matter.get("creative_ref") or "").strip("/")
        prompts = root / ref / "prompts.md"
        if ref and prompts.exists():
            # Look for this record's own id, not for the word "verdict". A prompt
            # pack is shared across campaigns, so the question is whether *this*
            # result is recorded against it — and a keyword scan would be satisfied
            # by some other record's outcome, or by the word appearing in a QA note.
            text = prompts.read_text(encoding="utf-8")
            if r.front_matter["rec_id"] not in text:
                no_backedge.append(
                    f"{r.rec_id}  {ref}/prompts.md carries no verdict  "
                    f"-> creative-generation.md sec 9: a prompt with no outcome taught nothing")
    if uncleared:
        sections.append(("Creative not cleared by the QA gate", uncleared))
    if unused:
        sections.append(("Creative cleared but never used", unused))
    if no_backedge:
        sections.append(("Verdict never written back to the prompt library", no_backedge))

    # --- the research loop ---
    r = _research(ledger)

    rows = []
    for q in sorted(r.questions(), key=lambda x: str(x.front_matter.get("asked"))):
        fm = q.front_matter
        if fm.get("status") != "open":
            continue
        age = _age_days(today, fm.get("asked"))
        rows.append(f"{fm['id']}  [{fm.get('kind')}] asked {age}d ago  -> research it, "
                    f"then `answer` it")
    if rows:
        sections.append(("Open research questions", rows))

    rows = [f"{n.front_matter['id']}  ingested "
            f"{_age_days(today, n.front_matter.get('captured'))}d ago, nothing derived  "
            f"-> learn --derived-from {n.front_matter['id']}"
            for n in r.notes() if not n.front_matter.get("learnings")]
    if rows:
        # An ingested note nobody derived anything from is the research loop's own
        # version of a proposal never executed.
        sections.append(("Notes ingested, no learning derived", rows))

    stale, untested = [], []
    for lrn in r.learnings():
        fm = lrn.front_matter
        if fm.get("status") in ("retired", "promoted"):
            continue
        due = _age_days(today, fm.get("review_after"))
        if due is not None and due >= 0:
            last = _age_days(today, fm.get("last_confirmed"))
            stale.append(f"{fm['id']}  [{fm.get('source')}] last confirmed {last}d ago  "
                         f"-> reconfirm or retire")
        elif fm.get("status") == "open" and (_age_days(today, fm.get("created")) or 0) >= 14:
            # A grace period, so a claim recorded this week is not nagged about as
            # though it had been sitting untested for months. After two weeks, a
            # hypothesis nobody has designed a test for is a real loose end.
            untested.append(f"{fm['id']}  [{fm.get('confidence')}/{fm.get('source')}] "
                            f"{str(fm.get('claim'))[:70]}  -> never tested")
    if stale:
        sections.append(("Learnings past their review date", stale))
    if untested:
        sections.append(("Learnings never tested against a real outcome", untested))

    rows = []
    for idea in r.ideas():
        fm = idea.front_matter
        if fm.get("status") != "open":
            continue
        age = _age_days(today, fm.get("created"))
        if fm.get("verdict") == "recommend":
            rows.append(f"{fm['id']}  recommended {age}d ago, Rs {fm.get('est_total_inr'):.0f}  "
                        f"-> propose --from-idea {fm['id']}, or drop it")
    if rows:
        sections.append(("Ideas recommended but never proposed", rows))

    # A claim that turned out wrong is only half the problem; what still leans on it
    # is the other half. Anything citing it needs revisiting, and a contradicted claim
    # sitting in a rules file is the worst state in the system, because rules/ wins.
    cited: dict[str, list[str]] = {}
    for idea in r.ideas():
        for ref in idea.front_matter.get("learnings") or []:
            cited.setdefault(ref, []).append(idea.front_matter["id"])
    promoted, plain = [], []
    for lrn in r.learnings():
        fm = lrn.front_matter
        if fm.get("status") not in ("contradicted", "mixed"):
            continue
        leans = (fm.get("recs") or []) + cited.get(fm["id"], [])
        tail = f"  still cited by {', '.join(leans)}" if leans else ""
        if fm.get("promoted_to"):
            promoted.append(f"{fm['id']}  {fm['status']}, but still normative in "
                            f"{fm['promoted_to']}{tail}  -> fix the rule or retire the claim")
        else:
            plain.append(f"{fm['id']}  {fm['status']}{tail}  -> revise, retire, or narrow it")
    if promoted:
        sections.append(("Promoted rules whose evidence has since been contradicted", promoted))
    if plain:
        sections.append(("Learnings contradicted by a real outcome", plain))

    # --- report ---
    if sections:
        for title, rows in sections:
            print(f"{title} ({len(rows)})")
            for row in rows:
                print(f"  {row}")
            print()
    else:
        print("Nothing open in the ledger.\n")

    # Absence of a section is not evidence of nothing to do — say what this command
    # cannot yet see, so a quiet report is not mistaken for a finished loop.
    empty = [label for label, store in (("questions", r.questions_dir),
                                        ("notes", r.notes_dir),
                                        ("learnings", r.learnings_dir),
                                        ("ideas", r.ideas_dir)) if not store.exists()]
    if empty:
        print("No store yet for: " + ", ".join(empty) + ".")
        print("Nothing has been written to them, so an empty report above is not evidence")
        print("that there is nothing outstanding — only that nobody has recorded it here.")


COMMANDS_BEGIN = "<!-- BEGIN GENERATED: ad-agent commands -->"
COMMANDS_END = "<!-- END GENERATED: ad-agent commands -->"
COMMANDS_DOCS = ("README.md", "wiki-export/Command-Cheatsheet.md")


def _subcommands(parser: argparse.ArgumentParser) -> list[tuple[str, str, argparse.ArgumentParser]]:
    """(name, help, parser) for every subcommand, in the order they were declared.

    Reaches into argparse's private `_actions` / `_choices_actions`, deliberately:
    the alternative is a hand-maintained list of commands, which is the exact thing
    this function exists to stop anyone from keeping.
    """
    out = []
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        helps = {ca.dest: (ca.help or "") for ca in action._choices_actions}
        for name, sub in action.choices.items():
            out.append((name, helps.get(name, ""), sub))
    return out


def _commands_markdown(parser: argparse.ArgumentParser) -> str:
    cmds = _subcommands(parser)
    lines = [
        "<!-- Generated by `ad-agent commands --write`. Do not hand-edit this block. -->",
        "",
        "| command | what it does |",
        "|---|---|",
    ]
    for name, help_text, _ in cmds:
        lines.append(f"| `{name}` | {help_text} |")
    lines.append("")
    for name, _, sub in cmds:
        usage = " ".join(sub.format_usage().replace("usage:", "", 1).split())
        lines += [f"#### `{name}`", "", "```", usage, "```", ""]
    return "\n".join(lines).rstrip()


def cmd_commands(args: argparse.Namespace, ledger: Ledger) -> None:
    """Print — or write — the command list, so no hand-maintained copy can drift.

    On 2026-08-26 both README.md and the wiki cheatsheet still said this agent
    never calls a Snap API, hours after it had created a live ad set through one,
    and neither listed `snap-push` at all. Three hand-kept copies of one list is
    why. The prose around each command stays hand-written — that is where the
    reasoning lives — but the list itself is generated from the parser.
    """
    parser = build_parser()
    block = _commands_markdown(parser)
    names = [n for n, _, _ in _subcommands(parser)]

    if args.check:
        # Drift runs both ways. The docs can fall behind the CLI (a command with no
        # written section), and a skill can run ahead of it (telling a session to
        # run something that does not exist, or that got renamed). The second is
        # worse: a wrong doc is confusing, a wrong instruction fails mid-task.
        import re as _re
        phantom = []
        for skill in sorted((ledger.root / ".claude" / "skills").glob("*/SKILL.md")):
            for token in _re.findall(r"ad-agent\s+([a-z][a-z-]*)",
                                     skill.read_text(encoding="utf-8")):
                if token not in names:
                    phantom.append(f"{skill.parent.name}: `ad-agent {token}` is not a command")

        missing_docs, undocumented = [], []
        for rel in COMMANDS_DOCS:
            path = ledger.root / rel
            if not path.exists():
                missing_docs.append(rel)
                continue
            text = path.read_text(encoding="utf-8")
            outside = text.split(COMMANDS_BEGIN)[0] + text.split(COMMANDS_END)[-1]
            for name in names:
                if f"ad-agent {name}" not in outside and rel.endswith("Command-Cheatsheet.md"):
                    undocumented.append(f"{rel}: `{name}` has no hand-written section")
        for row in missing_docs:
            print(f"missing: {row}", file=sys.stderr)
        for row in undocumented + sorted(set(phantom)):
            print(row, file=sys.stderr)
        if missing_docs or undocumented or phantom:
            raise SystemExit(1)
        skills = len(list((ledger.root / ".claude" / "skills").glob("*/SKILL.md")))
        print(f"ok — {len(names)} commands, all documented; "
              f"{skills} skills reference only real ones")
        return

    if not args.write:
        print(block)
        return

    for rel in COMMANDS_DOCS:
        path = ledger.root / rel
        text = path.read_text(encoding="utf-8")
        if COMMANDS_BEGIN not in text or COMMANDS_END not in text:
            print(f"error: {rel} has no generated block. Add these two markers where the\n"
                  f"command list should go:\n  {COMMANDS_BEGIN}\n  {COMMANDS_END}",
                  file=sys.stderr)
            raise SystemExit(2)
        head = text.split(COMMANDS_BEGIN)[0]
        tail = text.split(COMMANDS_END, 1)[1]
        path.write_text(f"{head}{COMMANDS_BEGIN}\n{block}\n{COMMANDS_END}{tail}",
                        encoding="utf-8")
        print(f"wrote {rel}")


def cmd_fetch_analytics(args: argparse.Namespace, config: dict) -> None:
    url = config.get("pdc", {}).get("analytics_url")
    api_key = config.get("pdc", {}).get("api_key")
    if not url or not api_key:
        print(
            "pdc.analytics_url / pdc.api_key are not set in config.local.yaml "
            "(see config.example.yaml). This also does nothing useful until the "
            "pocket-dating-coach PR adding /api/internal/ad-analytics has shipped "
            "— see SPEC.md, 'Data access'.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if args.network not in ("all", "other"):
        _check_network(Path(config["ledger"]["root"]) / "rules", args.network)

    qs = (
        f"?start={args.start}&end={args.end}&currency={args.currency}"
        f"&network={args.network}&audience={args.audience}"
    )
    req = urllib.request.Request(url + qs, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        raise SystemExit(1)

    if args.out:
        Path(args.out).write_text(body, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(body)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ad-agent")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("propose", help="Record a mode-5 recommendation before you execute it")
    sp.add_argument("slug", help="short campaign slug, used as the ledger folder name")
    sp.add_argument("--network", required=True, help=NETWORK_HELP)
    sp.add_argument("--campaign-name", required=True)
    sp.add_argument("--ad-set-name", required=True)
    sp.add_argument("--ad-name", required=True)
    sp.add_argument("--targeting-summary", required=True)
    sp.add_argument("--creative-ref", required=True, help="path or id under creatives/")
    sp.add_argument(
        "--destination-url",
        required=True,
        help="the landing URL this ad set sends traffic to; checked against rules/destinations.yaml",
    )
    sp.add_argument(
        "--budget-cap", type=float, default=budgetrules.DEFAULT_DAILY_INR,
        help="INR per day (default: rules/budget.md's operating default, Rs 300 as of "
             "2026-08-28). Reads below the Rs 800-1,200 full-experiment threshold are "
             "directional — propose says so on the record; raise the cap for a test "
             "whose answer must be trusted")
    sp.add_argument(
        "--duration-days", type=int, default=budgetrules.DEFAULT_DURATION_DAYS,
        help="days the ad set runs (default: rules/budget.md's operating default, 2 as "
             "of 2026-09-05). The push commands stamp the start at CREATION, not at "
             "enabling, so a day's delay before you enable costs half a 2-day test")
    sp.add_argument("--brief", required=True, help="path to a markdown brief file")
    sp.add_argument("--from-idea", default=None,
                    help="idea id this came from; marks that idea proposed so it stops "
                         "showing as an open loose end")
    _add_targeting_flags(sp, required=True)
    sp.set_defaults(func=cmd_propose)

    sp = sub.add_parser(
        "snap-leads",
        help="Register/inspect where Snap delivers lead-form submissions (webhook, per form)",
    )
    sp.add_argument("action", choices=["forms", "list", "register", "test", "delete"],
                    help="forms: every lead form and where its leads go. "
                         "register: point one form at the receiver. "
                         "test: ask Snap to fire a sample delivery. "
                         "delete: stop delivery for a form")
    sp.add_argument("--form-id", help="required by list and register")
    sp.add_argument("--url", help="receiver URL, required by register "
                                  "(e.g. https://<host>/api/marketing/snap-lead)")
    sp.add_argument("--integration-id", help="required by test and delete")
    sp.set_defaults(func=cmd_snap_leads)

    sp = sub.add_parser(
        "snap-audience",
        help="Create/grow a Snap Custom Audience or build a Lookalike from one",
    )
    sp.add_argument("action", choices=["list", "upsert", "lookalike"],
                    help="list: every audience on the account. "
                         "upsert: create-or-grow a Customer List from an email file. "
                         "lookalike: build a Lookalike seeded from an existing audience")
    sp.add_argument("--name", help="audience name, required by upsert and lookalike")
    sp.add_argument("--file", help="path to a text/csv file, one email per line "
                                   "(an 'Email' header line is skipped), required by upsert")
    sp.add_argument("--description", help="optional, shown in Ads Manager")
    sp.add_argument("--seed-name", help="existing audience name to build the lookalike "
                                        "from, required by lookalike")
    sp.add_argument("--country", default="IN", help="lookalike country, default IN")
    sp.add_argument("--similarity", default="SIMILARITY",
                    choices=["REACH", "BALANCE", "SIMILARITY"],
                    help="Snap's lookalike breadth tier, narrowest to broadest reversed "
                         "(SIMILARITY=narrowest, REACH=broadest); default SIMILARITY")
    sp.set_defaults(func=cmd_snap_audience)

    sp = sub.add_parser(
        "snap-push",
        help="Create a proposed recommendation in Snap Ads Manager, PAUSED, then diff it back",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--headline", default="A shortlist that means something.",
                    help="Snap headline, 34 chars max")
    sp.add_argument("--cta", default="APPLY_NOW",
                    help="Snap CTA-button label on the swipe-up chip (e.g. APPLY_NOW, MORE, "
                         "SIGN_UP, LEARN_MORE, INSTALL_NOW); default APPLY_NOW, matching "
                         "snap-push-story. Until 2026-09-05 this was hardcoded MORE with no "
                         "way to set it, which is not the same enum as a lead form's end-page "
                         "call_to_action — see snap.py's LEAD_END_PAGE_CTA note before "
                         "copying a value between the two")
    sp.add_argument("--optimization-goal", default="LANDING_PAGE_VIEW",
                    help="ad squad optimisation goal; default LANDING_PAGE_VIEW, which is "
                         "right when the destination is a page of ours. For a store-bound "
                         "traffic ad there is no page of ours to view, so pass SWIPES — it "
                         "optimises for the tap, which is measurable, instead of for a page "
                         "render this account has never been confirmed to count off a store "
                         "listing")
    sp.add_argument("--dry-run", action="store_true",
                    help="print the plan and create nothing")
    sp.add_argument("--accept-campaign-cap", action="store_true",
                    help="create anyway when the parent campaign's cap would bind, as a "
                         "stated deviation rather than a surprise")
    sp.set_defaults(func=cmd_snap_push)

    sp = sub.add_parser(
        "snap-push-story",
        help="Create a proposed Story Ad (COMPOSITE: a tap-through sequence of WEB_VIEW "
             "snaps) on Snap, PAUSED, then diff it back",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--headline", default="A shortlist that means something.",
                    help="Snap headline for every leaf snap, 34 chars max")
    sp.add_argument("--preview-headline", default="Move on, properly.",
                    help="headline on the Story tile shown before it's tapped open, 55 chars max")
    sp.add_argument("--cta", default="APPLY_NOW",
                    help="Snap CTA-button label on every leaf snap's swipe-up chip "
                         "(e.g. APPLY_NOW, MORE, SIGN_UP, LEARN_MORE); default APPLY_NOW to "
                         "match the end card and the /get/w-apply funnel")
    sp.add_argument("--dry-run", action="store_true",
                    help="print the plan and create nothing")
    sp.add_argument("--accept-campaign-cap", action="store_true",
                    help="create anyway when the parent campaign's cap would bind, as a "
                         "stated deviation rather than a surprise")
    sp.set_defaults(func=cmd_snap_push_story)

    sp = sub.add_parser(
        "meta-push",
        help="Create a proposed recommendation in Meta Ads Manager, PAUSED, then diff it back",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--headline", default="A shortlist that means something.",
                    help="the link headline (Meta's `name` field), ~40 chars before truncation")
    sp.add_argument("--message", default="",
                    help="primary text above the image; required by Meta for a link ad")
    sp.add_argument("--cta", default="LEARN_MORE",
                    help="call-to-action button type, e.g. LEARN_MORE, SIGN_UP, DOWNLOAD, "
                         "INSTALL_NOW")
    sp.add_argument("--video-id", default=None,
                    help="reuse a video ALREADY in this ad account's Meta library instead "
                         "of uploading one — read it off an existing creative's "
                         "object_story_spec.video_data.video_id. Needs --thumb-hash too. "
                         "The QA gate still applies: creative_ref/qa.md must record a pass")
    sp.add_argument("--thumb-hash", default=None,
                    help="image_hash of the thumbnail for --video-id (Meta rejects a video "
                         "creative without one); read it off the same video_data block")
    sp.add_argument("--dry-run", action="store_true",
                    help="print the plan and create nothing")
    sp.add_argument("--accept-campaign-cap", action="store_true",
                    help="create anyway when the parent campaign's cap would bind, as a "
                         "stated deviation rather than a surprise. Does NOT apply to a "
                         "campaign-budget-optimisation parent, which is refused outright")
    sp.set_defaults(func=cmd_meta_push)

    sp = sub.add_parser(
        "snap-push-lead",
        help="Create a proposed LEAD recommendation (video + on-platform form) on Snap, "
             "PAUSED, then diff it back",
    )
    sp.add_argument("rec_id")
    asset_group = sp.add_mutually_exclusive_group(required=True)
    asset_group.add_argument("--video", default=None, help="path to the finished 9:16 video")
    asset_group.add_argument("--image", default=None,
                             help="path to the finished 9:16 still — added 2026-08-30 for the "
                             "BUILD-YOURSELF-FIRST carousel, first non-video use of this command")
    sp.add_argument("--headline", default="Apply karo — sirf 18+",
                    help="Snap headline, hard limit 34 chars")
    sp.add_argument("--form-id", default=None,
                    help="bind an existing Snap lead form by id instead of creating one")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--accept-campaign-cap", action="store_true")
    sp.set_defaults(func=cmd_snap_push_lead)

    sp = sub.add_parser(
        "meta-push-lead",
        help="Create a proposed LEAD recommendation (video + instant form) in Meta, PAUSED, "
             "then diff it back",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--video", required=True,
                    help="path to the finished 1080x1920 video; a thumbnail is expected "
                         "beside it as <video>.thumb.jpg")
    sp.add_argument("--message", required=True,
                    help="primary text above the video")
    sp.add_argument("--form-id", default=None,
                    help="skip form creation and bind an existing instant form by id — the "
                         "fallback when the system-user token cannot act as the Page")
    sp.add_argument("--dry-run", action="store_true",
                    help="print the plan and create nothing")
    sp.add_argument("--accept-campaign-cap", action="store_true",
                    help="create anyway when the parent campaign's cap would bind")
    sp.set_defaults(func=cmd_meta_push_lead)

    sp = sub.add_parser(
        "amend",
        help="Revise a still-proposed recommendation, with an audit trail of what changed",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--reason", required=True, help="why this proposal is being revised")
    sp.add_argument("--campaign-name", default=None)
    sp.add_argument("--ad-set-name", default=None)
    sp.add_argument("--ad-name", default=None)
    sp.add_argument("--targeting-summary", default=None)
    sp.add_argument("--creative-ref", default=None)
    sp.add_argument(
        "--destination-url",
        default=None,
        help="re-runs the rules/destinations.yaml gate against the resulting pair",
    )
    sp.add_argument("--budget-cap", default=None, type=float, help="INR per day")
    sp.add_argument("--duration-days", default=None, type=int)
    _add_targeting_flags(sp, required=False)
    sp.set_defaults(func=cmd_amend)

    sp = sub.add_parser(
        "verify-tracking",
        help="Run rules/tracking.md's post-launch check against live user_acquisition "
             "data for a live recommendation",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--since", default=None,
                    help="YYYY-MM-DD; defaults to the record's executed date, else created")
    sp.add_argument("--detail", action="store_true",
                    help="print recent rows even when the window is empty")
    sp.set_defaults(func=cmd_verify_tracking)

    sp = sub.add_parser("log-setup", help="Record the real IDs after setting the ad up by hand")
    sp.add_argument("rec_id")
    sp.add_argument("--network", required=True, help=NETWORK_HELP)
    sp.add_argument("--campaign-id", required=True)
    sp.add_argument("--ad-set-id", required=True)
    sp.add_argument("--ad-id", required=True)
    sp.add_argument("--deviated", default=None, help="what changed from the brief, if anything")
    sp.set_defaults(func=cmd_log_setup)

    sp = sub.add_parser(
        "note",
        help="Append a dated note to a record — for things that change mid-run",
    )
    sp.add_argument("rec_id")
    sp.add_argument("--text", required=True, help="what happened, and why it matters to the verdict")
    sp.add_argument("--kind", default="observation",
                    choices=list(Ledger.NOTE_KINDS),
                    help="budget/targeting/creative changes, an incident, or a plain observation")
    sp.set_defaults(func=cmd_note)

    sp = sub.add_parser("log-review", help="Record mode-6's verdict on a live recommendation")
    sp.add_argument("rec_id")
    sp.add_argument("--verdict", required=True, choices=["working", "not-working", "inconclusive"])
    sp.add_argument("--summary", required=True)
    sp.add_argument("--review-log", default=None, help="path to a markdown review-detail file")
    sp.add_argument("--learning", action="append", default=None,
                    help="learning id this verdict bears on, beyond any reached via the record's "
                         "idea; repeatable")
    sp.set_defaults(func=cmd_log_review)

    sp = sub.add_parser("abandon", help="Close out a recommendation that was never executed")
    sp.add_argument("rec_id")
    sp.add_argument("--reason", required=True)
    sp.set_defaults(func=cmd_abandon)

    sp = sub.add_parser("stats", help="Deterministic counts over the ledger")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("dump-ledger", help="Print the ledger index")
    sp.add_argument("--status", default=None, choices=list(STATUSES))
    sp.set_defaults(func=cmd_dump_ledger)

    # ---- the research loop -------------------------------------------------
    sp = sub.add_parser(
        "ingest",
        help="Store a note you brought in, verbatim and immutable, as provenance for learnings",
    )
    sp.add_argument("--title", required=True, help="what this note is about")
    sp.add_argument("--source", required=True, choices=list(researchmod.SOURCES))
    g = sp.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", default=None, help="path to the note")
    g.add_argument("--text", default=None, help="the note itself")
    sp.add_argument("--slug", default=None,
                    help="short id suffix; defaults to the first few words")
    sp.set_defaults(func=cmd_ingest)

    sp = sub.add_parser(
        "learn",
        help="Record one derived claim, with the source kind and confidence that make it citable",
    )
    sp.add_argument("--claim", required=True, help="one claim, stated plainly")
    sp.add_argument("--subject", required=True, choices=list(researchmod.SUBJECTS))
    sp.add_argument("--source", required=True, choices=list(researchmod.SOURCES),
                    help="only live-data and platform-doc may be `high` confidence")
    sp.add_argument("--confidence", required=True, choices=list(researchmod.CONFIDENCES))
    sp.add_argument("--sample-n", default=None, type=int,
                    help=f"required for live-data; below MIN_SAMPLE={researchmod.MIN_SAMPLE} "
                         "the claim can only be `low`")
    sp.add_argument("--evidence", required=True, help="what actually supports this, today")
    sp.add_argument("--derived-from", default=None, help="the note id this was derived from")
    sp.add_argument("--answers", default=None, help="question id this claim closes")
    sp.add_argument("--slug", default=None,
                    help="short id suffix; defaults to the first few words")
    sp.set_defaults(func=cmd_learn)

    sp = sub.add_parser(
        "log-evidence",
        help="Attach a dated outcome to a learning — the back-edge that lets it be corrected",
    )
    sp.add_argument("learning_id")
    sp.add_argument("--outcome", required=True, choices=list(researchmod.OUTCOMES))
    sp.add_argument("--text", required=True)
    sp.add_argument("--from", dest="from_ref", default=None,
                    help="rec_id whose verdict produced this, if any")
    sp.set_defaults(func=cmd_log_evidence)

    sp = sub.add_parser(
        "reclassify",
        help="Correct how a learning is filed — subject, source, confidence — not what it claims",
    )
    sp.add_argument("learning_id")
    sp.add_argument("--reason", required=True, help="why the original filing was wrong")
    sp.add_argument("--subject", default=None, choices=list(researchmod.SUBJECTS))
    sp.add_argument("--source", default=None, choices=list(researchmod.SOURCES))
    sp.add_argument("--confidence", default=None, choices=list(researchmod.CONFIDENCES))
    sp.add_argument("--sample-n", default=None, type=int)
    sp.set_defaults(func=cmd_reclassify)

    sp = sub.add_parser(
        "promote",
        help="Record that a learning has graduated into a rules file and is now normative",
    )
    sp.add_argument("learning_id")
    sp.add_argument("--rule", required=True, help="e.g. rules/targeting.md")
    sp.set_defaults(func=cmd_promote)

    sp = sub.add_parser("retire", help="Close out a learning that is no longer worth carrying")
    sp.add_argument("learning_id")
    sp.add_argument("--reason", required=True)
    sp.set_defaults(func=cmd_retire)

    sp = sub.add_parser(
        "question",
        help="Add an open research question to the queue that drives the next research pass",
    )
    sp.add_argument("--text", required=True)
    sp.add_argument("--kind", required=True, choices=list(researchmod.SUBJECTS))
    sp.add_argument("--why", required=True, help="why it matters — what decision it unblocks")
    sp.add_argument("--raised-by", default=None, help="rec_id, learning id or idea id, if any")
    sp.add_argument("--slug", default=None,
                    help="short id suffix; defaults to the first few words")
    sp.set_defaults(func=cmd_question)

    sp = sub.add_parser("answer", help="Close an open question, optionally naming what it taught")
    sp.add_argument("question_id")
    sp.add_argument("--text", required=True)
    sp.add_argument("--learning", default=None, help="the learning id this produced")
    sp.add_argument("--dropped", action="store_true",
                    help="close it as no longer worth answering, rather than as answered")
    sp.set_defaults(func=cmd_answer)

    sp = sub.add_parser(
        "idea",
        help="Record a recommend/hold idea with the spend it would take to test it",
    )
    sp.add_argument("--title", required=True)
    sp.add_argument("--verdict", required=True, choices=list(researchmod.IDEA_VERDICTS))
    sp.add_argument("--network", required=True, help=NETWORK_HELP)
    sp.add_argument("--persona", required=True, help="from rules/targeting.md")
    sp.add_argument("--est-daily", required=True, type=float, help="INR per day to test it")
    sp.add_argument("--est-days", required=True, type=int)
    sp.add_argument("--rationale", required=True)
    sp.add_argument("--learning", action="append", default=None,
                    help="learning id this rests on; repeatable")
    sp.add_argument("--blocked-on", default=None,
                    help="required for a hold: what would make it recommendable")
    sp.add_argument("--slug", default=None,
                    help="short id suffix; defaults to the first few words")
    sp.set_defaults(func=cmd_idea)

    sp = sub.add_parser(
        "open",
        help="Every loose end the ledger can see — start here when you come back to this repo",
    )
    sp.set_defaults(func=cmd_open)

    sp = sub.add_parser(
        "commands",
        help="Print the command list, or regenerate it in README and the wiki cheatsheet",
    )
    sp.add_argument("--write", action="store_true",
                    help="splice the list into README.md and wiki-export/Command-Cheatsheet.md")
    sp.add_argument("--check", action="store_true",
                    help="fail if a command has no hand-written section in the cheatsheet")
    sp.set_defaults(func=cmd_commands)

    sp = sub.add_parser(
        "fetch-analytics",
        help="Pull pocket-dating-coach's ad analytics via the authenticated internal endpoint",
    )
    sp.add_argument("--start", required=True, help="YYYY-MM-DD, IST day, inclusive")
    sp.add_argument("--end", required=True, help="YYYY-MM-DD, IST day, inclusive")
    sp.add_argument("--currency", default="INR", choices=["INR", "USD"])
    sp.add_argument("--network", default="all",
                    help="all, other, or a key from rules/networks.yaml")
    sp.add_argument("--audience", default="all", choices=["all", "men", "women", "unknown"])
    sp.add_argument("--out", default=None, help="write JSON here instead of stdout")
    sp.set_defaults(func=cmd_fetch_analytics)

    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = load_config()

    if args.command == "fetch-analytics":
        cmd_fetch_analytics(args, config)
        return

    ledger = Ledger(Path(config["ledger"]["root"]))
    args.func(args, ledger)


if __name__ == "__main__":
    main()
