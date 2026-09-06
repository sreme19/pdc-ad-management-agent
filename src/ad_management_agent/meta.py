"""Meta Marketing API client.

The sibling of `snap.py`, built to the same terms. SPEC.md decisions #3 and #10 were
extended to Meta by the app owner on 2026-08-27, and that extension is explicit that
the permission is to build *this shape* — not to reach the API by any means:

  * Everything is created PAUSED. Nothing here can start spending money.
  * There is no enable/resume/activate call anywhere in this file, and none should be
    added without the app owner saying so explicitly.
  * The rule is enforced at the single choke point every request passes through
    (`_call`), so a method added later cannot skip a check it never knew about.
  * Every object is read back and diffed against what was asked for, because "the
    POST returned 200" is not evidence the ad set targets who you think it targets.

**Three things here deliberately do NOT mirror snap.py, because Meta differs.** Each
is a place where copying the Snap shape would have produced a hole or a wrong number:

1. **An update is a POST, not a PUT.** Meta has no PUT: creating is `POST
   /act_X/campaigns` and updating is `POST /{campaign_id}`. `snap.py` keys its budget
   guard off the method (`BUDGET_KEYS` + `method in ("PUT","PATCH")`), which on Meta
   would classify every budget change as a creation and wave it through. So the guard
   here keys off the **path shape** instead — a create posts to a known collection, an
   update posts to a bare object id. See `_is_create`.

2. **Meta's update is a partial patch, not a full replace.** Snap's is a replace, which
   is why `_safety_violations` there needs an `unchanged` echo exemption: omitting a
   budget field *deletes* it, so a pause had to send the budget back unchanged, and on
   2026-08-26 at 17:24 UTC an omission wiped a campaign's daily cap. Meta has no such
   trap — a field left out is a field left alone. That makes the guard here strictly
   *stronger*: any budget key on an update is refused outright, with no echo escape
   hatch, because there is never a legitimate reason to send one.

3. **Money is in minor units, not micro.** Snap is micro (1 INR = 1_000_000). Meta is
   the account currency's minor unit (1 INR = 100 paise). Getting this wrong is a
   10,000x budget error in the direction that spends money, so `MetaClient` refuses to
   create anything until it has read the ad account's own `currency` and found INR.
"""
from __future__ import annotations

import json
import mimetypes
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

# Pinned deliberately. Marketing API versions expire — v24.0 dies 2026-10-06 — and
# Meta began auto-upgrading unpinned callers on 2026-07-29. An auto-upgrade that
# silently changes a payload's meaning is not something to discover through a live
# ad account, so the version is a constant here and bumping it is a code change.
API_VERSION = "v26.0"
API = f"https://graph.facebook.com/{API_VERSION}"

# 1 INR = 100 paise. NOT snap.py's MICRO — see the module docstring, point 3.
MINOR = 100


class MetaError(RuntimeError):
    pass


class MetaSafetyError(MetaError):
    """An outbound request would have broken the paused-only rule. Never catch this."""


# Meta's own enabling value is ACTIVE; the rest are the near-synonyms a future method
# might reach for. PAUSED is deliberately absent: pausing stops spend, and stopping
# spend is always safe.
ENABLING_STATUSES = {"ACTIVE", "RUNNING", "ENABLED", "ON", "LIVE"}

# Meta deletes and archives through the same `status` field it enables through, so the
# one guard covers both hazards. These are refused for a different reason than
# ENABLING_STATUSES — not because they spend money, but because they destroy or hide
# the object a ledger record points at. `ad-audit` has to be able to read a pushed ad
# set months later to close its loop, and an ARCHIVED object drops out of Meta's
# default listings. Neither is this agent's call to make.
DESTRUCTIVE_STATUSES = {"DELETED", "ARCHIVED"}

# Changing any of these on an object that already exists is a budget change, which
# decision #3 forbids outright. Setting them at creation time is how an ad set gets a
# budget at all, so the check is scoped to updates rather than to the key alone.
BUDGET_KEYS = {
    "daily_budget",
    "lifetime_budget",
    "spend_cap",
    "bid_amount",
    "lifetime_spend_cap",
    "daily_spend_cap",
    "campaign_daily_budget",
    "campaign_lifetime_budget",
    # Not an amount, but a change to how much an ad set actually spends: flipping
    # this True on an existing campaign hands 20% of every child ad set's budget to
    # Meta to redistribute. Guarded like the amounts — settable at creation,
    # refused on an update.
    "is_adset_budget_sharing_enabled",
}

# A POST whose final path segment is one of these is creating a new object under a
# parent. A POST to anything else — i.e. to a bare object id — is an update. This is
# the load-bearing distinction on Meta; see the module docstring, point 1.
COLLECTIONS = {
    "campaigns",
    "adsets",
    "ads",
    "adcreatives",
    "adimages",
    "advideos",
    # Lead forms are created on the PAGE, not the ad account, but the guard walks
    # every outbound payload regardless of host object — a form carries no budget
    # and no status, so this entry only classifies its POST as a create.
    "leadgen_forms",
}


def _is_create(method: str, path: str) -> bool:
    """True if this request creates a new object rather than modifying one.

    Conservative by construction: anything not recognisably a create is treated as an
    update, which is the stricter classification. A new collection endpoint added to
    Meta and not listed in COLLECTIONS therefore fails closed — its creates get
    refused for carrying a budget — rather than failing open and letting a budget
    change through as if it were a creation.
    """
    if method.upper() != "POST":
        return False
    segments = [s for s in path.split("?")[0].split("/") if s]
    return bool(segments) and segments[-1] in COLLECTIONS


def _safety_violations(method: str, path: str, payload: object,
                       field: str = "") -> list[str]:
    """Every reason this outbound payload must not be sent. Empty means safe.

    Walks the whole structure rather than checking the top level, because Meta nests
    the interesting fields — `object_story_spec.link_data`, `targeting.geo_locations`
    — and a `status` two levels down is still a status.

    Unlike snap.py's equivalent there is no `unchanged` echo exemption, and there
    should not be one: Meta's update is a patch, so a budget key on an update is
    always an attempt to change a budget, never the price of keeping one.
    """
    found: list[str] = []
    creating = _is_create(method, path)

    if isinstance(payload, dict):
        for key, value in payload.items():
            here = f"{field}.{key}" if field else key
            if key in ("status", "configured_status") and isinstance(value, str):
                upper = value.upper()
                if upper in ENABLING_STATUSES:
                    found.append(f"{here} = {value!r} would enable an object")
                elif upper in DESTRUCTIVE_STATUSES:
                    found.append(
                        f"{here} = {value!r} would destroy or hide an object the ledger "
                        f"may point at"
                    )
            if key in BUDGET_KEYS and not creating:
                found.append(
                    f"{here} on {method.upper()} {path} would change an existing budget"
                )
            found += _safety_violations(method, path, value, here)
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            found += _safety_violations(method, path, item, f"{field}[{i}]")
    return found


class MetaClient:
    def __init__(self, cfg: dict):
        missing = [k for k in ("access_token", "ad_account_id", "page_id")
                   if not (cfg or {}).get(k)]
        if missing:
            raise MetaError(
                "config.local.yaml is missing meta." + ", meta.".join(missing) + ".\n"
                "See config.example.yaml for the expected block. The token is the "
                "system-user token for riteangle-api (SPEC.md decision #10, as amended "
                "2026-08-27) — it does not expire, and Meta shows it only once."
            )
        self.cfg = cfg
        self._currency: str | None = None

    @property
    def account_path(self) -> str:
        """Meta's ad account ids are prefixed `act_`; the config may hold either form."""
        raw = str(self.cfg["ad_account_id"])
        return raw if raw.startswith("act_") else f"act_{raw}"

    # ---- transport -------------------------------------------------------
    def _call(self, method: str, path: str, payload: dict | None = None) -> dict:
        # The paused-only rule, enforced at the one place every request passes through.
        #
        # There is no override flag, and there is not meant to be one. Prose in a
        # docstring is not carefulness that survives the next method someone adds;
        # this is, because a new call cannot forget a check it never had to remember.
        if payload is not None:
            violations = _safety_violations(method, path, payload)
            if violations:
                raise MetaSafetyError(
                    f"REFUSED: {method} {path} would break the paused-only rule.\n"
                    + "\n".join(f"  - {v}" for v in violations)
                    + "\n\nSee SPEC.md decision #3 (extended to Meta 2026-08-27). Enabling an ad\n"
                    "set, raising the budget of a live one, and deleting anything are human\n"
                    "actions in Ads Manager, deliberately. If this refusal is wrong, the fix is\n"
                    "the app owner amending that decision — not this check."
                )

        data = urllib.parse.urlencode(
            {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in (payload or {}).items()}
        ).encode() if payload is not None else None

        # The token goes in a header, never in the query string. Meta's own access
        # logs, any proxy, and the browser history of anyone who pastes a URL all
        # capture query parameters; a non-expiring system-user token in one of those
        # is a credential leak with no rotation story, because there is no refresh.
        req = urllib.request.Request(
            f"{API}{path}", data=data, method=method.upper(),
            headers={"Authorization": f"Bearer {self.cfg['access_token']}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:800]
            hint = ""
            # Meta labels a great many pure validation errors `OAuthException` —
            # the missing is_adset_budget_sharing_enabled field on 2026-08-28 came
            # back as one — so keying the auth hint off that type alone printed
            # "check your asset assignments" under an error that had nothing to do
            # with permissions. Look for the words that actually mean auth.
            authish = any(w in detail.lower() for w in (
                "access token", "permission", "not authorized", "session"))
            if e.code in (400, 401, 403) and authish:
                hint = (
                    "\n\nA system-user token does not expire, so an auth failure here is more "
                    "likely a missing asset assignment than a stale token: check that "
                    "riteangle-api is assigned this ad account with Manage campaigns, and that "
                    "the riteangle app is installed on it."
                )
            raise MetaError(f"{method} {path} -> HTTP {e.code}\n{detail}{hint}") from e

    def get(self, path: str, fields: str | None = None) -> dict:
        return self._call("GET", path + (f"?fields={fields}" if fields else ""))

    def post(self, path: str, payload: dict) -> dict:
        return self._call("POST", path, payload)

    # ---- account ---------------------------------------------------------
    @property
    def currency(self) -> str:
        if self._currency is None:
            self._currency = self.get(f"/{self.account_path}", fields="currency").get("currency")
        return self._currency or ""

    def require_inr(self) -> None:
        """Refuse to convert a rupee figure into minor units for a non-INR account.

        Every budget in this repo is INR: rules/budget.md's floor is Rs 800-1,200/day
        against a Rs 50,000/month envelope, and the ledger's field is literally
        `budget_cap_inr_per_day`. If this account settles in anything else, the minor
        unit is not paise and the number sent would be wrong by whatever the FX rate
        is — in the direction that spends money. Cheaper to refuse than to discover.
        """
        cur = self.currency
        if cur != "INR":
            raise MetaError(
                f"ad account {self.account_path} settles in {cur or 'an unknown currency'}, "
                "not INR.\nEvery budget in this repo is rupees (rules/budget.md, and the "
                "ledger's own\nbudget_cap_inr_per_day), so the minor-unit conversion here would "
                "be wrong.\nRefusing rather than guessing an FX rate."
            )

    # ---- campaign --------------------------------------------------------
    def find_campaign(self, name: str) -> dict | None:
        """Exact-name lookup that refuses to guess.

        The same rule as snap.py's, for the same reason and with more evidence behind
        it on this network: this account already holds two Pages both named
        `Riteangle` (one deactivated), and six campaigns whose names collide on
        prefix. Hanging an ad set off the wrong parent is invisible until the numbers
        make no sense, so an ambiguous name is an error, never a pick-the-first.
        """
        res = self.get(f"/{self.account_path}/campaigns", fields="id,name,status")
        hits = [c for c in res.get("data", []) if c.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h["id"] for h in hits)
            raise MetaError(
                f"{len(hits)} campaigns are named {name!r} ({ids}).\n"
                "Refusing to guess which one to use — rename or delete the duplicate in Ads "
                "Manager first. See rules/naming.md."
            )
        return hits[0] if hits else None

    def campaign_caps(self, campaign_id: str) -> dict:
        """Read a campaign's own budget caps, in INR. Either may be None.

        Mirrors snap.py.campaign_caps, and exists for the same incident: on
        2026-08-26 WOMEN_18-22_CASUAL_LPV was created with an ad squad at Rs
        1,000/day under a campaign capped at Rs 300/day, which put the live test
        below rules/budget.md's floor and made its read inconclusive before a rupee
        was spent. Nothing in the push looked at the parent, so nothing caught it.

        Meta has the same trap with an extra wrinkle: a campaign using
        campaign-budget optimisation holds the budget itself, and an ad-set budget
        under it is ignored outright rather than merely capped. That is reported too.
        """
        c = self.get(
            f"/{campaign_id}",
            fields="id,name,daily_budget,lifetime_budget,spend_cap,budget_remaining",
        )
        def inr(key):
            raw = c.get(key)
            return float(raw) / MINOR if raw not in (None, "", "0") else None
        return {
            "daily_inr": inr("daily_budget"),
            "lifetime_inr": inr("lifetime_budget"),
            "spend_cap_inr": inr("spend_cap"),
            # A campaign-level daily or lifetime budget on Meta means CBO is on.
            "campaign_budget_optimization": bool(
                c.get("daily_budget") or c.get("lifetime_budget")
            ),
        }

    def create_campaign(self, name: str, objective: str = "OUTCOME_TRAFFIC") -> dict:
        """Create the campaign, PAUSED.

        `special_ad_categories` is required by Meta and is deliberately sent empty.
        Dating is not one of Meta's special ad categories — those are credit,
        employment, housing, elections/politics and gambling — so claiming one would
        be a false declaration. Note separately that Meta requires written permission
        to advertise dating at all; that is an account-level approval, not a field.
        """
        return self.post(f"/{self.account_path}/campaigns", {
            "name": name,
            "objective": objective,
            "status": "PAUSED",
            "special_ad_categories": [],
            "buying_type": "AUCTION",
            # Required by Meta whenever the campaign carries no budget of its own,
            # and there is only one defensible value here. Meta's own error text:
            # "Passing in True will enable your ad sets to share 20% of their budget
            # to optimize overall performance." That is a softer version of exactly
            # what _gate_campaign_budget_optimization refuses outright — a parent
            # that redistributes budget makes the record's budget_cap_inr_per_day
            # stop describing what actually gets spent, and rules/budget.md's floor
            # was checked against that number. 20% of Rs 1,000/day is Rs 200/day of
            # drift, which is the difference between clearing the Rs 800 floor and
            # not. So: False, always, and it is not a parameter.
            "is_adset_budget_sharing_enabled": False,
        })

    # ---- stopping spend --------------------------------------------------
    def pause_campaign(self, campaign_id: str) -> dict:
        """Set a live campaign to PAUSED, stopping everything beneath it.

        This is the ONE state change this module makes, and the asymmetry is the
        point: it can stop money, and it can never start it. There is no resume,
        enable or activate anywhere here, so the worst this method can do is halt
        spend a human chose to begin.

        Simpler than the Snap equivalent, and the difference is instructive: Snap's
        update is a full replace, so pausing there has to echo every existing field
        back or it deletes them. Meta's update is a patch, so this sends `status`
        alone — which is also why the guard above can refuse budget keys on updates
        with no exemption. Reads back and refuses to claim success on the API's word.
        """
        self.post(f"/{campaign_id}", {"status": "PAUSED"})
        after = self.get(f"/{campaign_id}", fields="id,name,status,effective_status")
        if after.get("status") != "PAUSED":
            raise MetaError(
                f"asked Meta to pause {after.get('name', campaign_id)} but it still reads "
                f"{after.get('status')!r}. Pause it by hand in Ads Manager."
            )
        return after

    # ---- ad set ----------------------------------------------------------
    def find_adset(self, name: str, campaign_id: str) -> dict | None:
        """Exact-name lookup under one campaign, so a retry resumes instead of duplicating.

        This exists because `meta-push` has no rollback and five objects to create.
        On 2026-08-28 the first real push failed at the creative — the third of five —
        leaving a campaign and an ad set behind. `find_campaign` meant the retry
        reused the campaign, but nothing looked for the ad set, so a second run would
        have created a second `WOMEN_25-30_CASUAL_MOVEON-LPV` at another Rs 1,000/day
        under the same parent. Two identically named ad sets is precisely the
        collision `find_campaign` refuses to guess through, and it would have broken
        `pocket-dating-coach`'s ad-set rollup, which is keyed on the ad set.

        Scoped to the campaign, not the account: the same audience name under a
        different campaign is a different test, and reusing across parents would
        silently attach this record to someone else's.
        """
        res = self.get(f"/{campaign_id}/adsets", fields="id,name,status,daily_budget")
        hits = [a for a in res.get("data", []) if a.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h["id"] for h in hits)
            raise MetaError(
                f"{len(hits)} ad sets under campaign {campaign_id} are named {name!r} "
                f"({ids}).\nRefusing to guess which one this record means — delete or "
                "rename the duplicate in Ads Manager first. See rules/naming.md."
            )
        return hits[0] if hits else None

    def create_adset(self, *, name, campaign_id, targeting, daily_budget_inr,
                     start_time, end_time, pixel_id=None,
                     optimization_goal: str = "LANDING_PAGE_VIEWS") -> dict:
        """Create the ad set, PAUSED, optimising for `optimization_goal`.

        **`optimization_goal` became a parameter on 2026-09-06 and defaults to the
        LANDING_PAGE_VIEWS every prior ad set used.** It has to vary because a
        landing-page view is a thing Meta observes by watching a page of ours load,
        and the direct-to-store funnel has no page of ours in it. Optimising a
        store-bound ad set for LPV points the delivery algorithm at an event that
        can never be counted off `play.google.com`, so it falls back to something
        undeclared. `LINK_CLICKS` optimises for the tap, which is observably
        counted. This is the same correction the Snap arm made on 2026-09-05 when
        `rec-2026-09-05-moveon-getw-w1830-snap` moved LANDING_PAGE_VIEW -> SWIPES,
        and for the identical reason.

        Say the consequence out loud rather than letting the field name hide it:
        LINK_CLICKS buys the CHEAPEST TAP, and the cheapest tap comes from the
        people most willing to tap and least likely to install. Nothing on this
        route can tell Meta which taps became installs — no page of ours renders,
        so the pixel cannot fire and `marketing-conversions.ts`'s CAPI forward is
        bypassed. See rules/tracking.md's Meta direct-to-store coverage table.

        **`pixel_id` is deliberately optional here, unlike snap.py's equivalent, and
        `promoted_object` is deliberately not sent.** This was wrong in the first cut of
        this module: it mirrored Snap's hard requirement and asserted that "Meta has no
        fallback, no pixel means no signal at all". Checking the account on 2026-08-27
        showed the opposite. Its own live LANDING_PAGE_VIEWS ad set,
        `FB_W_20-25_ID_Romantic`, binds no dataset at the ad-set level and has Website
        events unchecked, and the ad under it reported 36 landing-page views anyway.
        Meta's Tracking panel says the ad account's *default* conversion dataset is used
        unless told otherwise, so the binding is at the account level, not here.

        `promoted_object` carrying a pixel is required for OFFSITE_CONVERSIONS, which is
        a different optimisation goal than this one. Sending it on an OUTCOME_TRAFFIC ad
        set optimising for LANDING_PAGE_VIEWS risks a rejection for a field the account's
        own working ad set does not set — so this follows the account's observed
        convention, which is the same rule snap.py's pixel requirement came from, applied
        honestly to a network whose convention turned out to be the other way.

        A conversions-objective ad set WOULD need `promoted_object`. That is a new code
        path when someone builds it, not a flag on this one.
        """
        self.require_inr()
        # Created on the AD ACCOUNT, with campaign_id in the body — not on the
        # campaign. snap.py posts an ad squad to /campaigns/{id}/adsquads, and
        # mirroring that shape here failed on 2026-08-28 with "Object with ID ...
        # does not exist, cannot be loaded due to missing permissions, or does not
        # support this operation": Meta's campaign node exposes `adsets` as a
        # READ-ONLY edge, so the POST was to a real object that simply does not
        # accept one. The error names permissions first, which is misleading — the
        # campaign had just been created by this same token.
        return self.post(f"/{self.account_path}/adsets", {
            "name": name,
            "campaign_id": campaign_id,
            "status": "PAUSED",
            "targeting": targeting,
            "optimization_goal": optimization_goal,
            "billing_event": "IMPRESSIONS",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            # round() before sending, not truncation: Rs 999.999/day is a rounding
            # artefact of a rupee figure, and int() would floor it to 99999 paise and
            # put the ad set a paisa under rules/budget.md's floor.
            "daily_budget": round(daily_budget_inr * MINOR),
            "destination_type": "WEBSITE",
            "start_time": start_time,
            "end_time": end_time,
        })

    # ---- media + creative + ad -------------------------------------------
    def upload_image(self, path: Path) -> str:
        """Upload an image and return its `image_hash`.

        Meta identifies ad images by a content hash rather than by an id, and the
        response keys the result under the *filename* — so the hash has to be dug out
        of a dict whose only key is whatever the file happened to be called. Pulling
        the single value rather than looking up `path.name` avoids depending on Meta
        echoing the filename back byte-for-byte.
        """
        boundary = uuid.uuid4().hex
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="filename"; filename="{path.name}"\r\n'.encode(),
            f"Content-Type: {ctype}\r\n\r\n".encode(),
            path.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode(),
        ])
        req = urllib.request.Request(
            f"{API}/{self.account_path}/adimages", data=body, method="POST",
            headers={"Authorization": f"Bearer {self.cfg['access_token']}",
                     "content-type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                res = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise MetaError(f"image upload -> HTTP {e.code}\n{e.read().decode()[:500]}") from e
        images = res.get("images") or {}
        if not images:
            raise MetaError(f"image upload returned no hash: {json.dumps(res)[:300]}")
        entry = next(iter(images.values()))
        if not entry.get("hash"):
            raise MetaError(f"image upload returned no hash: {json.dumps(res)[:300]}")
        return entry["hash"]

    def create_creative(self, *, name, image_hash, headline, message, url,
                        call_to_action: str = "LEARN_MORE") -> dict:
        """Create the ad creative, bound to the Page identity.

        The Page is not optional on Meta and has no Snap equivalent: a Snap ad renders
        under a `profile_id`, while a Meta ad IS a post by a Page. That makes the
        active `Riteangle` Page (1309735922215645) load-bearing, and makes the
        deactivated duplicate of the same name a live hazard — which is why the page id
        comes from config rather than from a name lookup.
        """
        return self.post(f"/{self.account_path}/adcreatives", {
            "name": name,
            "object_story_spec": {
                "page_id": str(self.cfg["page_id"]),
                "link_data": {
                    "image_hash": image_hash,
                    "link": url,
                    "name": headline,
                    "message": message,
                    "call_to_action": {"type": call_to_action},
                },
            },
            # NOTE: no degrees_of_freedom_spec is sent, and that is not the same as
            # not caring. Meta will "improve" a creative on its own — recropping,
            # restyling, generating variants — and rules/creative-generation.md's §10
            # QA gate signs off on a specific 1080x1920 asset with specific type, so an
            # enhancement applied after that gate makes the sign-off meaningless.
            #
            # The opt-out used to be a single `standard_enhancements: OPT_OUT`. On
            # 2026-08-28 Meta began rejecting that outright: "Including standard
            # enhancements field in creative has been deprecated. Please choose to set
            # individual features instead." Its error links to fburl.com/hyth50xo,
            # which redirects to internalfb.com and is not publicly readable, so the
            # replacement key names could not be looked up.
            #
            # Rather than guess field names against a live account, the creative is
            # created without the block and `meta-push` reads
            # `degrees_of_freedom_spec` back and reports every feature Meta actually
            # switched on. That turns a guess into an observation, and the observed
            # names are what a precise per-feature opt-out should be built from.
            # See q-2026-08-28-meta-individual-creative-features.
        })

    def create_link_video_creative(self, *, name, video_id, thumbnail_hash, headline,
                                   message, url,
                                   call_to_action: str = "INSTALL_NOW") -> dict:
        """Create a VIDEO creative whose CTA opens a website (not a lead form).

        Added 2026-09-06. Three creatives now exist on this client and the
        differences are not cosmetic, so they are named here rather than rediscovered:

          * `create_creative` — `link_data` + `image_hash`. A still image. The
            headline goes in `name`, the destination in a top-level `link`.
          * `create_lead_creative` — `video_data`, CTA value carries a
            `lead_gen_form_id`. There is no destination URL at all; the form opens
            inside Meta.
          * this one — `video_data`, CTA value carries a `link`. **A video creative
            has no top-level `link` field.** Putting the URL where `link_data` puts
            it is accepted and silently ignored, producing an ad whose CTA goes
            nowhere useful, so the destination lives in
            `call_to_action.value.link` and nowhere else.

        `title` is the headline field on `video_data`, where `link_data` spells the
        same thing `name`. Crossing them is another silent drop.

        `image_hash` is not optional: Meta rejects a video creative with no
        thumbnail. It can be a hash from `upload_image`, or — for a video already in
        this account's library — the `image_hash` read back off the existing
        creative's `object_story_spec.video_data`, which is what reusing an approved
        asset means in practice.
        """
        return self.post(f"/{self.account_path}/adcreatives", {
            "name": name,
            "object_story_spec": {
                "page_id": str(self.cfg["page_id"]),
                "video_data": {
                    "video_id": str(video_id),
                    "image_hash": thumbnail_hash,
                    "title": headline,
                    "message": message,
                    "call_to_action": {
                        "type": call_to_action,
                        "value": {"link": url},
                    },
                },
            },
            # No degrees_of_freedom_spec, for the reason create_creative records at
            # length: the single standard_enhancements opt-out was deprecated
            # 2026-08-28 and its replacement names are documented only behind an
            # internal URL. meta-push reads the block back and reports what Meta
            # actually switched on instead of guessing field names at it.
        })

    def create_ad(self, *, name, adset_id, creative_id) -> dict:
        return self.post(f"/{self.account_path}/ads", {
            "name": name,
            "adset_id": adset_id,
            "creative": {"creative_id": creative_id},
            "status": "PAUSED",
        })

    def find_ad(self, name: str, adset_id: str) -> dict | None:
        """Exact-name lookup under one ad set, so a retry resumes instead of duplicating.

        The sibling of `find_adset`, and it exists for the same reason: this push has
        five objects, no rollback, and failed three separate times on 2026-08-28 —
        twice after the ad already existed. Without this, each retry minted another ad.
        """
        res = self.get(f"/{adset_id}/ads", fields="id,name,status,creative")
        hits = [a for a in res.get("data", []) if a.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h["id"] for h in hits)
            raise MetaError(
                f"{len(hits)} ads under ad set {adset_id} are named {name!r} ({ids}).\n"
                "Refusing to guess which one this record means — delete or rename the "
                "duplicate in Ads Manager first. See rules/naming.md."
            )
        return hits[0] if hits else None

    # ---- lead ads (OUTCOME_LEADS / instant forms) --------------------------
    #
    # Added 2026-08-29 at the app owner's request, for the MOVE-ON lead funnel
    # (rec-2026-08-29-moveon-lead-w1824-meta / -w2530-meta). create_adset's own
    # docstring said a different optimisation goal "is a new code path when someone
    # builds it, not a flag on this one" — this is that code path, built to the same
    # SPEC #3 shape: everything created PAUSED, every request through _call's guard,
    # nothing here can enable, delete, or change a live budget.

    def page_token(self) -> str:
        """Derive a Page access token from the system-user token.

        Lead forms live on the Page, and Meta refuses to create one with an
        ad-account token: the POST needs a token whose subject IS the page. A system
        user that has the page assigned can mint one by reading the page's own
        `access_token` field. If that field comes back empty the assignment is
        missing, and the fix is in Business Settings, not here — or create the form
        by hand in Ads Manager and pass --form-id to skip this entirely.
        """
        res = self.get(f"/{self.cfg['page_id']}", fields="access_token")
        token = res.get("access_token")
        if not token:
            raise MetaError(
                "the system-user token cannot act as the Page: reading the page's "
                "access_token returned nothing.\nEither assign the riteangle Page to "
                "the riteangle-api system user (Business Settings -> Users -> System "
                "users -> Assign assets, with Manage permission), or create the "
                "instant form by hand in Ads Manager and rerun with --form-id."
            )
        return token

    def _call_as_page(self, method: str, path: str, payload: dict | None = None) -> dict:
        """One request authorised as the Page. Same guard, different bearer.

        Deliberately funnels through the same _safety_violations check as _call —
        a page-authorised request is still this module's outbound traffic, and the
        paused-only rule does not care which token carries a violation.

        Handles GET too (payload None): the 2026-08-29 push failed live on exactly
        this — READING /{page_id}/leadgen_forms needs the Page token as much as
        posting to it does ("(#190) This method must be called with a Page Access
        Token"), and find_lead_form had gone out with the account bearer.
        """
        if payload is not None:
            violations = _safety_violations(method, path, payload)
            if violations:
                raise MetaSafetyError(
                    f"REFUSED: {method} {path} would break the paused-only rule.\n"
                    + "\n".join(f"  - {v}" for v in violations)
                )
        data = urllib.parse.urlencode(
            {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
             for k, v in payload.items()}
        ).encode() if payload is not None else None
        req = urllib.request.Request(
            f"{API}{path}", data=data, method=method.upper(),
            headers={"Authorization": f"Bearer {self.page_token()}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            raise MetaError(f"{method} {path} (as page) -> HTTP {e.code}\n"
                            f"{e.read().decode()[:800]}") from e

    def find_lead_form(self, name: str) -> dict | None:
        """Exact-name lookup on the page, so a retry resumes instead of duplicating.

        Same reason find_adset exists: this push has no rollback, and a run that
        dies after the form is created must reuse it, not mint a sibling.
        """
        res = self._call_as_page(
            "GET", f"/{self.cfg['page_id']}/leadgen_forms"
                   "?fields=id,name,status,thank_you_page")
        hits = [f for f in res.get("data", []) if f.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h["id"] for h in hits)
            raise MetaError(
                f"{len(hits)} lead forms on the page are named {name!r} ({ids}). "
                "Refusing to guess — archive the duplicates in Ads Manager first."
            )
        return hits[0] if hits else None

    def create_lead_form(self, *, name: str, privacy_url: str,
                         thank_you_url: str) -> dict:
        """Create the instant form: first name, phone, email, and the handoff.

        The thank-you page is the funnel hinge — its button is what carries her to
        /get/w-apply with the UTMs and ra_lead={{lead_id}}. The macro is the ONE
        value that stays a macro (the lead id does not exist until she submits);
        everything else in the URL is a literal, per rules/tracking.md and the
        2026-08-21 incident. Whether Meta actually resolves {{lead_id}} here is
        verified by the mandatory end-to-end test submission before enabling —
        never assume it, because /get/w-apply would store the literal braces.
        """
        return self._call_as_page("POST", f"/{self.cfg['page_id']}/leadgen_forms", {
            "name": name,
            "questions": [
                {"type": "FIRST_NAME"},
                {"type": "PHONE"},
                {"type": "EMAIL"},
            ],
            "privacy_policy": {"url": privacy_url},
            "thank_you_page": {
                "title": "Bas ek step baaki hai",
                "body": "Aapka apply almost complete hai.",
                "button_type": "VIEW_WEBSITE",
                "button_text": "Complete karo",
                "website_url": thank_you_url,
            },
        })

    def create_lead_adset(self, *, name, campaign_id, targeting, daily_budget_inr,
                          start_time, end_time) -> dict:
        """Create the ad set for an instant-form campaign, PAUSED.

        Differs from create_adset in exactly the fields the objective forces:
        destination ON_AD (the form opens inside Meta; there is no website
        destination at the ad-set level), optimisation LEAD_GENERATION, and
        promoted_object carrying the page — required here where create_adset's
        docstring records it must NOT be sent for LANDING_PAGE_VIEWS. Same INR
        guard, same paise conversion, same account-level creation path.
        """
        self.require_inr()
        return self.post(f"/{self.account_path}/adsets", {
            "name": name,
            "campaign_id": campaign_id,
            "status": "PAUSED",
            "targeting": targeting,
            "optimization_goal": "LEAD_GENERATION",
            "billing_event": "IMPRESSIONS",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "daily_budget": round(daily_budget_inr * MINOR),
            "destination_type": "ON_AD",
            "promoted_object": {"page_id": str(self.cfg["page_id"])},
            "start_time": start_time,
            "end_time": end_time,
        })

    def upload_video(self, path: Path) -> str:
        """Upload a video and wait until Meta has finished processing it.

        Returns the video id only once status reads `ready`: a creative built on a
        still-processing video fails with an error that names the video, not the
        problem, and the 2026-08-28 push failures were exactly this class of
        misleading mid-push error. Polling is bounded so a stuck encode fails loudly
        rather than hanging the push.
        """
        boundary = uuid.uuid4().hex
        ctype = mimetypes.guess_type(path.name)[0] or "video/mp4"
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="source"; filename="{path.name}"\r\n'.encode(),
            f"Content-Type: {ctype}\r\n\r\n".encode(),
            path.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode(),
        ])
        req = urllib.request.Request(
            f"{API}/{self.account_path}/advideos", data=body, method="POST",
            headers={"Authorization": f"Bearer {self.cfg['access_token']}",
                     "content-type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                res = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise MetaError(f"video upload -> HTTP {e.code}\n{e.read().decode()[:500]}") from e
        vid = res.get("id")
        if not vid:
            raise MetaError(f"video upload returned no id: {json.dumps(res)[:300]}")
        for _ in range(60):  # up to ~5 minutes
            status = (self.get(f"/{vid}", fields="status").get("status") or {})
            state = status.get("video_status")
            if state == "ready":
                return vid
            if state == "error":
                raise MetaError(f"video {vid} failed Meta-side processing: {status}")
            time.sleep(5)
        raise MetaError(f"video {vid} still processing after 5 minutes — rerun the push; "
                        "find_ad/find_adset make the retry resume rather than duplicate.")

    def create_lead_creative(self, *, name, video_id, thumbnail_hash, message,
                             form_id) -> dict:
        """Create the video creative that opens the instant form.

        video_data instead of link_data, and the call to action carries the form id
        — that binding, not any ad-set field, is what makes tapping the ad open the
        form. Thumbnail is required by Meta for video creatives; it arrives as an
        image_hash from the same upload_image path the link ads use.
        """
        return self.post(f"/{self.account_path}/adcreatives", {
            "name": name,
            "object_story_spec": {
                "page_id": str(self.cfg["page_id"]),
                "video_data": {
                    "video_id": video_id,
                    "image_hash": thumbnail_hash,
                    "message": message,
                    "call_to_action": {
                        "type": "APPLY_NOW",
                        "value": {"lead_gen_form_id": str(form_id)},
                    },
                },
            },
        })

    def attach_tracked_creative(self, *, ad_id: str, creative: dict, url_tags: str,
                                name: str) -> dict:
        """Give a live ad a creative whose tracking carries that ad's own real id.

        This is Meta's answer to the problem `snap.py.set_creative_url` solves, and it
        needs a different shape because Meta's objects are less mutable than Snap's:

          * `rules/tracking.md` requires the ad id to reach the analytics, and on Meta
            the joining parameter is `utm_content` (confirmed in traffic-quality.ts).
            The ad does not exist when its first creative is built, so the first
            creative cannot carry it.
          * `url_tags` on an **ad** looked like the answer and is not. POSTing it to
            `/{ad_id}` returns 200 and does not persist — read back as `None` on
            2026-08-28. A silent no-op is worse than an error, and it is exactly why
            decision #3 requires reading every object back rather than trusting a 200.
          * `url_tags` on an existing **creative** cannot be set either: Meta answers
            "Please specify the name, status or associated advert labels to update the
            creative." Creatives are effectively immutable once made.

        What does work, verified against the live account: create a NEW creative with
        `url_tags` set at creation — where it persists — and repoint the ad at it. The
        ad id is stable across that swap, so the literal id written into `utm_content`
        stays correct.

        The consequence, stated rather than hidden: every ad this pushes leaves one
        superfluous untracked creative behind, the provisional one built before the ad
        existed. It is unused and costs nothing, and `meta.py` cannot delete it by
        design. The alternative was Meta's `{{ad.id}}` macro, and an unresolved macro
        cost a week of unattributable spend on 2026-08-21 — while `adSetKeyOf` rejects
        any value containing `{{` as absent, so a macro that fails to resolve produces
        no attribution at all. A spare object is the cheaper failure.
        """
        link = (creative.get("object_story_spec") or {}).get("link_data") or {}
        tracked = self.post(f"/{self.account_path}/adcreatives", {
            "name": name,
            "object_story_spec": {
                "page_id": str(self.cfg["page_id"]),
                "link_data": {
                    "image_hash": link.get("image_hash"),
                    "link": link.get("link"),
                    "name": link.get("name"),
                    "message": link.get("message"),
                    "call_to_action": link.get("call_to_action"),
                },
            },
            "url_tags": url_tags,
        })
        got = self.get(f"/{tracked['id']}", fields="id,url_tags").get("url_tags")
        if got != url_tags:
            raise MetaError(
                f"creative {tracked['id']} was created but its url_tags read back as "
                f"{got!r}, not the tracking string asked for.\nRefusing to attach an "
                "untracked creative — an ad that spends without attribution is the "
                "2026-08-21 failure. Set the tracking by hand in Ads Manager."
            )
        self.post(f"/{ad_id}", {"creative": {"creative_id": str(tracked["id"])}})
        after = self.get(f"/{ad_id}", fields="id,status,creative")
        if (after.get("creative") or {}).get("id") != str(tracked["id"]):
            raise MetaError(
                f"asked Meta to point ad {ad_id} at creative {tracked['id']} but it "
                f"still reads {(after.get('creative') or {}).get('id')!r}. Fix by hand."
            )
        return tracked

    def retarget_video_creative(self, *, ad_id: str, creative: dict, link: str,
                                name: str) -> dict:
        """Repoint a video ad at a creative whose LINK carries that ad's own real id.

        The store-destination sibling of `attach_tracked_creative`, added
        2026-09-06. It solves the same problem — the ad id does not exist when the
        first creative is built, and `rules/tracking.md` requires it to reach the
        analytics — and it has to solve it a different way.

        **`url_tags` is the wrong instrument against a store listing, and it fails
        silently.** Meta implements `url_tags` by APPENDING the string to the
        outbound URL at click time. Play discards every parameter appended to a
        listing URL; only its own `referrer=` survives an install. So a store-bound
        ad carrying `url_tags` reports a healthy setup in Ads Manager, resolves to a
        real listing, and delivers installs that nothing can ever attribute — the
        2026-08-21 incident with a different first step, which is exactly what
        `lrn-2026-09-05-store-url-shape-did-not-travel-to-traffic-path` records
        against the Snap traffic path.

        The tracking therefore has to be INSIDE the link, URL-encoded in
        `referrer=` (built by `cli._store_referrer_url`, the single implementation).
        A link is part of `object_story_spec`, and Meta creatives are effectively
        immutable once made — the same wall `attach_tracked_creative` documents. So
        the fix is the same dance with a different field: build a NEW creative whose
        `call_to_action.value.link` is the final URL, and repoint the ad at it. The
        ad id is stable across the swap, so the literal id inside the referrer stays
        correct.

        `url_tags` is deliberately NOT set here. Setting it as well would append
        params Play throws away, which costs nothing but tells the next reader the
        tracking lives somewhere it does not.

        The consequence, stated rather than hidden, as before: this leaves one
        superfluous provisional creative behind, and `meta.py` cannot delete it by
        design. A spare object is the cheaper failure than an unresolved macro.
        """
        video = (creative.get("object_story_spec") or {}).get("video_data") or {}
        cta = video.get("call_to_action") or {}
        tracked = self.post(f"/{self.account_path}/adcreatives", {
            "name": name,
            "object_story_spec": {
                "page_id": str(self.cfg["page_id"]),
                "video_data": {
                    "video_id": video.get("video_id"),
                    "image_hash": video.get("image_hash"),
                    "title": video.get("title"),
                    "message": video.get("message"),
                    "call_to_action": {
                        "type": cta.get("type"),
                        "value": {"link": link},
                    },
                },
            },
        })
        # Read the link back off Meta rather than trusting the 200. This is the
        # check `attach_tracked_creative` makes against url_tags, applied to the
        # field that actually carries the tracking on this route.
        got = self.get(f"/{tracked['id']}", fields="id,object_story_spec")
        got_link = ((((got.get("object_story_spec") or {}).get("video_data") or {})
                     .get("call_to_action") or {}).get("value") or {}).get("link")
        if got_link != link:
            raise MetaError(
                f"creative {tracked['id']} was created but its CTA link read back as "
                f"{got_link!r}, not the tracked URL asked for:\n  {link}\n"
                "Refusing to attach an untracked creative — an ad that spends without "
                "attribution is the 2026-08-21 failure. Set the link by hand in Ads "
                "Manager."
            )
        self.post(f"/{ad_id}", {"creative": {"creative_id": str(tracked["id"])}})
        after = self.get(f"/{ad_id}", fields="id,status,creative")
        if (after.get("creative") or {}).get("id") != str(tracked["id"]):
            raise MetaError(
                f"asked Meta to point ad {ad_id} at creative {tracked['id']} but it "
                f"still reads {(after.get('creative') or {}).get('id')!r}. Fix by hand."
            )
        return tracked
