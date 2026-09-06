"""Snap Marketing API client.

SPEC.md decisions #3 and #10 originally kept every credential that could reach a
live ad account out of this repo, so that "never touches a live account" was true
by construction rather than by care. The app owner reversed that on 2026-08-26 to
allow programmatic setup. What replaces the structural guarantee is this module's
own discipline, and it is deliberately narrow:

  * Everything is created PAUSED. Nothing here can start spending money.
  * There is no enable/resume call anywhere in this file, and none should be added
    without the app owner saying so explicitly. Enabling stays a human action in
    Ads Manager. This is enforced rather than promised: `_call` refuses any outbound
    payload carrying an enabling status, or a budget field on a PUT, at the single
    choke point every request passes through — so a method added later cannot skip a
    check it never knew about.
  * Every object is read back from the API after creation and diffed against what
    was asked for, because "the POST returned 200" is not evidence the ad squad
    targets who you think it targets.

Amounts are micro-currency throughout: 1 INR = 1_000_000 micro.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

API = "https://adsapi.snapchat.com/v1"
TOKEN_URL = "https://accounts.snapchat.com/login/oauth2/access_token"
MICRO = 1_000_000

# The default form copy, and the reason it is a default rather than a literal.
#
# "One step left" is TRUE when the end page is /get/w-apply — a real 18+ gate
# follows. It is FALSE when the end page is the Play listing, because nothing
# follows but the install. The strings were hardcoded here until 2026-09-04,
# when the first direct-to-store lead ad would have shipped promising a step
# that did not exist. Copy that describes the funnel cannot be fixed in the
# funnel it does not describe, so it moved out here.
FORM_COPY_PAGE = {
    "title": "Bas ek step baaki hai",
    "description": "Aapka apply almost complete hai.",
}
#: For an end page that IS the store. Says what is true — the apply is done,
#: the app is next — and claims no status she was not evaluated for.
FORM_COPY_STORE = {
    "title": "Apply ho gaya",
    "description": "Ab app download karo — baaki sab wahin.",
}

# The lead form END PAGE's allowed call_to_action values. This is a DIFFERENT and
# much smaller enum than a creative's, which is the trap: a creative takes
# INSTALL_NOW, an end page does not. Confirmed 2026-09-04 both ways — Snap's own
# lead-generation-ads doc lists exactly these twelve, and a probe POST carrying
# INSTALL_NOW came back E25020 "End page CallToAction must be one of the allowed
# values" (creating nothing). Closes q-2026-09-04-snap-lead-end-page-cta.
#
# WORTH KNOWING HOW THAT PROBE NEARLY LIED. The POST returns HTTP 200 with
# request_status ERROR and the real reason one level down in
# sub_request_error_reason, so a probe that only checked for an exception read
# three invalid values as accepted. `_one` is what catches this in the real path;
# anything hand-rolled around it has to check sub_request_status itself.
END_PAGE_CTAS = {
    "VIEW_WEBSITE", "BOOK_NOW", "LEARN_MORE", "DONATE", "SPECIAL_OFFER",
    "SCHEDULE_NOW", "BUY_TICKETS", "TEST_DRIVE", "APPLY_NOW", "GET_COUPON",
    "CLAIM_SAMPLE", "FREE_TRIAL",
}

#: Our own default: the end page is a page of ours, and the button says so.
END_PAGE_CTA_PAGE = "VIEW_WEBSITE"

# For an end page that is the app store. There is no install-flavoured value in
# the enum above, so this is the best TRUE one rather than the one we wanted:
#
#   * INSTALL_NOW / DOWNLOAD / GET_APP — not in the enum. Rejected by the API.
#   * FREE_TRIAL, SPECIAL_OFFER, GET_COUPON, BUY_TICKETS — purchase and offer
#     language, which compliance.md #2 forbids outright (there are no
#     subscriptions, purchases or credits, and copy may never imply otherwise).
#     FREE_TRIAL is the worst of them: it implies a paid tier after the trial.
#   * DONATE, TEST_DRIVE, BOOK_NOW, SCHEDULE_NOW, CLAIM_SAMPLE — plainly false.
#   * APPLY_NOW — false HERE specifically. It is right on the creative, where the
#     tap opens the form; on the end page she has ALREADY applied, so a second
#     "Apply now" describes a step that no longer exists.
#   * VIEW_WEBSITE — what shipped first, and the store is not a website of ours.
#
# LEARN_MORE is true (the listing is more about the app), claims nothing, and
# implies no purchase. The instruction itself lives in the end-page copy above
# ("Ab app download karo"), which is not enum-constrained.
END_PAGE_CTA_STORE = "LEARN_MORE"


class SnapError(RuntimeError):
    pass


class SnapSafetyError(SnapError):
    """An outbound request would have broken the paused-only rule. Never catch this."""


# Snap's own enabling values, plus the near-synonyms a future method might reach for.
# PAUSED is deliberately absent: pausing stops spend, and stopping spend is always safe.
ENABLING_STATUSES = {"ACTIVE", "RUNNING", "ENABLED", "ON", "LIVE"}

# Changing any of these on an object that already exists is a budget change, which
# decision #3 forbids outright. Setting them at creation time is how an ad squad gets
# a budget at all, so the check is scoped to PUT rather than to the key alone.
BUDGET_KEYS = {
    "daily_budget_micro",
    "lifetime_budget_micro",
    "lifetime_spend_cap_micro",
    "daily_spend_cap_micro",
    "spend_cap_micro",
    "bid_micro",
}


def _safety_violations(method: str, payload: object, path: str = "",
                       unchanged: dict | None = None) -> list[str]:
    """Every reason this outbound payload must not be sent. Empty means safe.

    Walks the whole structure rather than checking the top level, because Snap wraps
    every object in a list under a plural key — `{"adsquads": [{"status": "ACTIVE"}]}`
    hides the field two levels down.

    `unchanged` is the object as it currently exists on Snap. A budget key whose
    value is byte-identical to what is already stored is an ECHO, not a change, and
    is allowed through. That distinction is load-bearing: Snap's update is a full
    replace, so a field left out is a field deleted. Without this, a pause that
    omitted daily_budget_micro to satisfy the guard silently wiped the campaign's
    daily cap — which is exactly what happened on 2026-08-26 at 17:24 UTC.
    """
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            here = f"{path}.{key}" if path else key
            if key == "status" and isinstance(value, str) and value.upper() in ENABLING_STATUSES:
                found.append(f"{here} = {value!r} would enable an object")
            is_echo = bool(unchanged) and unchanged.get(key, object()) == value
            if key in BUDGET_KEYS and method.upper() in ("PUT", "PATCH") and not is_echo:
                found.append(f"{here} on a {method.upper()} would change an existing budget")
            found += _safety_violations(method, value, here, unchanged)
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            found += _safety_violations(method, item, f"{path}[{i}]", unchanged)
    return found


class SnapClient:
    def __init__(self, cfg: dict):
        missing = [k for k in ("client_id", "client_secret", "refresh_token", "ad_account_id")
                   if not (cfg or {}).get(k)]
        if missing:
            raise SnapError(
                "config.local.yaml is missing snap." + ", snap.".join(missing) + ".\n"
                "See config.example.yaml for the expected block."
            )
        self.cfg = cfg
        self._token: str | None = None

    # ---- transport -------------------------------------------------------
    @property
    def token(self) -> str:
        """Access tokens last an hour, so they are minted per run, never stored."""
        if self._token is None:
            body = urllib.parse.urlencode({
                "client_id": self.cfg["client_id"],
                "client_secret": self.cfg["client_secret"],
                "grant_type": "refresh_token",
                "refresh_token": self.cfg["refresh_token"],
            }).encode()
            req = urllib.request.Request(
                TOKEN_URL, data=body, method="POST",
                headers={"content-type": "application/x-www-form-urlencoded"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    self._token = json.loads(r.read())["access_token"]
            except urllib.error.HTTPError as e:
                raise SnapError(
                    f"could not refresh the access token (HTTP {e.code}). The refresh token may "
                    f"have been revoked — re-run the authorize step.\n{e.read().decode()[:300]}"
                ) from e
        return self._token

    def _call(self, method: str, path: str, payload: dict | None = None,
              unchanged: dict | None = None) -> dict:
        # The paused-only rule, enforced at the one place every request passes through.
        #
        # SPEC.md decision #3 (as amended 2026-08-26) states that this module never
        # enables anything and never changes the budget of anything live, and notes
        # honestly that the guarantee is no longer structural — the repo now holds a
        # credential that can reach a live account, so "never" rests on the code being
        # careful. Prose in a docstring is not carefulness that survives the next
        # method someone adds. This is: a new call cannot forget a check it never had
        # to remember. There is no override flag, and there is not meant to be one.
        if payload is not None:
            violations = _safety_violations(method, payload, unchanged=unchanged)
            if violations:
                raise SnapSafetyError(
                    f"REFUSED: {method} {path} would break the paused-only rule.\n"
                    + "\n".join(f"  - {v}" for v in violations)
                    + "\n\nSee SPEC.md decision #3. Enabling an ad set and raising the budget of a\n"
                    "live one are human actions in Ads Manager, deliberately. If this refusal is\n"
                    "wrong, the fix is the app owner amending that decision — not this check."
                )
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            f"{API}{path}", data=data, method=method,
            headers={"Authorization": f"Bearer {self.token}", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise SnapError(f"{method} {path} -> HTTP {e.code}\n{e.read().decode()[:800]}") from e

    def get(self, path: str) -> dict:
        return self._call("GET", path)

    def post(self, path: str, payload: dict) -> dict:
        return self._call("POST", path, payload)

    def put(self, path: str, payload: dict, unchanged: dict | None = None) -> dict:
        return self._call("PUT", path, payload, unchanged=unchanged)

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _one(res: dict, key: str) -> dict:
        """Snap wraps every object in a list under a plural key, one entry per request item."""
        items = res.get(key) or []
        if not items:
            raise SnapError(f"expected one {key} in the response, got none: {json.dumps(res)[:300]}")
        obj = items[0]
        singular = key.rstrip("s") if key != "adsquads" else "adsquad"
        inner = obj.get(singular, obj)
        if obj.get("sub_request_status") not in (None, "SUCCESS"):
            raise SnapError(f"{singular} rejected: {json.dumps(obj)[:500]}")
        return inner

    # ---- campaign --------------------------------------------------------
    def find_campaign(self, name: str) -> dict | None:
        """Exact-name lookup that refuses to guess.

        Two live campaigns in this account already share the name
        RA_TRAFFIC_GET_IN_BLR_TOF_202608 with different ids, which is precisely the
        collision rules/naming.md warns about. Hanging an ad squad off the wrong one
        would be invisible until the numbers made no sense, so an ambiguous name is
        an error, never a pick-the-first.
        """
        res = self.get(f"/adaccounts/{self.cfg['ad_account_id']}/campaigns")
        hits = [c["campaign"] for c in res.get("campaigns", []) if c["campaign"].get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h["id"] for h in hits)
            raise SnapError(
                f"{len(hits)} campaigns are named {name!r} ({ids}).\n"
                "Refusing to guess which one to use — rename or delete the duplicate in Ads "
                "Manager first. See rules/naming.md."
            )
        return hits[0] if hits else None

    def campaign_caps(self, campaign_id: str) -> dict:
        """Read a campaign's own spend caps, in INR. Either may be None.

        A campaign-level cap silently overrides a larger ad-squad budget: the lower
        figure binds. On 2026-08-26 WOMEN_18-22_CASUAL_LPV was created with an ad
        squad carrying Rs 1,000/day under a campaign capped at Rs 300/day, which put
        the live test below rules/budget.md's floor and made its read inconclusive
        before a rupee was spent. Nothing in the push looked at the parent, so
        nothing caught it. This is what `snap-push` now checks before it creates
        anything.
        """
        c = self._one(self.get(f"/campaigns/{campaign_id}"), "campaigns")
        daily = c.get("daily_budget_micro")
        lifetime = c.get("lifetime_spend_cap_micro")
        return {
            "daily_inr": float(daily) / MICRO if daily else None,
            "lifetime_inr": float(lifetime) / MICRO if lifetime else None,
        }

    def create_campaign(self, name: str, start_time: str) -> dict:
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/campaigns", {"campaigns": [{
            "name": name,
            "ad_account_id": self.cfg["ad_account_id"],
            "status": "PAUSED",
            "start_time": start_time,
            "buy_model": "AUCTION",
            "objective_v2_properties": {"objective_v2_type": "TRAFFIC"},
        }]})
        return self._one(res, "campaigns")

    # ---- stopping spend --------------------------------------------------
    def pause_campaign(self, campaign_id: str) -> dict:
        """Set a live campaign to PAUSED, stopping everything beneath it.

        This is the ONE state change this module makes, and the asymmetry is the
        point: it can stop money, and it can never start it. There is still no
        resume, enable or activate anywhere here, so the worst this method can do
        is halt spend that a human chose to begin. Restarting remains a human
        action in Ads Manager, exactly as SPEC.md decision #3 requires.

        Reads back and refuses to claim success on the API's say-so.
        """
        current = self.get(f"/campaigns/{campaign_id}")["campaigns"][0]["campaign"]
        # Snap's update is a full replace, not a patch: omitting a required field
        # fails the item while the HTTP call still returns 200. Echo the current
        # values back and change only status. _one() raises on the per-item error
        # that a bare 200 would otherwise hide.
        body = {
            "id": campaign_id,
            "ad_account_id": self.cfg["ad_account_id"],
            "name": current["name"],
            "start_time": current["start_time"],
            "buy_model": current.get("buy_model", "AUCTION"),
            "status": "PAUSED",
        }
        # Echo every field that exists, budgets included. Snap's update is a full
        # replace: anything omitted is deleted, so leaving the budget out to keep the
        # guard happy destroys the cap instead of protecting it. The guard is given
        # `current` so it can verify each budget value is identical to what is already
        # stored — an echo passes, a change still does not.
        for k in ("end_time", "objective_v2_properties", "daily_budget_micro",
                  "lifetime_spend_cap_micro"):
            if current.get(k) is not None:
                body[k] = current[k]
        self._one(self.put(f"/adaccounts/{self.cfg['ad_account_id']}/campaigns",
                           {"campaigns": [body]}, unchanged=current), "campaigns")
        after = self.get(f"/campaigns/{campaign_id}")["campaigns"][0]["campaign"]
        if after.get("status") != "PAUSED":
            raise SnapError(
                f"asked Snap to pause {current['name']} but it still reads "
                f"{after.get('status')!r}. Pause it by hand in Ads Manager."
            )
        return after

    # ---- ad squad --------------------------------------------------------
    def create_adsquad(self, *, name, campaign_id, targeting, daily_budget_inr,
                       start_time, end_time, pixel_id, optimization_goal="LANDING_PAGE_VIEW") -> dict:
        """Create the ad squad, PAUSED.

        `pixel_id` is required because every other LANDING_PAGE_VIEW squad in this
        account carries the same one, and the first squad this command created did
        not. A mismatch with the account's own convention is far more likely an
        omission than a deliberate choice, so it fails rather than passing quietly.

        Note what the pixel is NOT responsible for: Snap counts landing-page views
        for a WEB_VIEW ad natively, by rendering the page in its own in-app browser,
        and reported 59 of them for the pixel-less first run. So a missing pixel does
        not blind the optimisation goal. It was briefly diagnosed that way here, from
        a `conversion_page_views: 0` reading against the wrong stats field, and that
        was wrong.

        `optimization_goal` defaults to `LANDING_PAGE_VIEW`, the only goal every
        caller before 2026-08-30 used. A `STORY`-type ad squad rejects that goal
        outright on this account/pixel — not just its default conversion window;
        every `conversion_window` value this module tried (13 of them, live) was
        refused the same way, `E2899 Invalid conversion window given for
        optimization goal`, which is Snap's account/pixel-eligibility system
        saying LANDING_PAGE_VIEW is not offered for a Story squad here at all, not
        a window mismatch. `SWIPES` was confirmed live to accept both the ad squad
        and a real STORY ad under it; pass it explicitly for a squad meant to hold
        a Story ad.
        """
        if not pixel_id:
            raise SnapError(
                "pixel_id is required for a LANDING_PAGE_VIEW ad squad.\n"
                "Without it Snap cannot see the conversion it is being asked to "
                "optimise for. Set snap.pixel_id in config.local.yaml."
            )
        res = self.post(f"/campaigns/{campaign_id}/adsquads", {"adsquads": [{
            "pixel_id": pixel_id,
            "name": name,
            "campaign_id": campaign_id,
            "type": "SNAP_ADS",
            "status": "PAUSED",
            "targeting": targeting,
            "optimization_goal": optimization_goal,
            "billing_event": "IMPRESSION",
            "bid_strategy": "AUTO_BID",
            "daily_budget_micro": int(daily_budget_inr * MICRO),
            "placement_v2": {"config": "AUTOMATIC"},
            "start_time": start_time,
            "end_time": end_time,
        }]})
        return self._one(res, "adsquads")

    # ---- lead ads (LEAD_GENERATION / on-platform forms) --------------------
    #
    # Added 2026-08-29, immediately after the Meta lead path and at the same
    # request. rules/funnel.md rung 3 priced this exactly: "new objective
    # (snap.py hardcodes TRAFFIC), new ad type, a lead-form resource snap.py has
    # no call for" — these are those three things. Same SPEC #3 shape throughout:
    # PAUSED at creation, every request through the transport guard, nothing here
    # enables or changes a live budget.
    #
    # One limit Meta does not have, recorded rather than papered over: Snap's
    # lead form has an end-page URL and documents NO macro for it, so no per-lead
    # id reaches /get/w-apply from Snap. The app owner's call (2026-08-29, in as
    # many words): proceed without it — the page accepts ra_src=form arrivals and
    # attribution falls back to the ad-squad-level UTMs the URL carries as
    # literals. utm_id is absent for the same reason the Meta path needed a
    # two-pass form: the ad does not exist when the form is made — but Snap
    # documents no form update, so the fallback is accepted instead of gamed.

    def create_lead_campaign(self, name: str, start_time: str) -> dict:
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/campaigns", {"campaigns": [{
            "name": name,
            "ad_account_id": self.cfg["ad_account_id"],
            "status": "PAUSED",
            "start_time": start_time,
            "buy_model": "AUCTION",
            "objective_v2_properties": {"objective_v2_type": "LEAD_GENERATION"},
        }]})
        return self._one(res, "campaigns")

    def find_adsquad(self, name: str, campaign_id: str) -> dict | None:
        """Exact-name lookup under one campaign, so a retry resumes instead of duplicating.

        Mirrors meta.py's find_adset, for the same reason: a push with no rollback
        and several objects to create dies partway as a normal state, and the retry
        must reuse what exists rather than mint a duplicate ad squad at another
        Rs 300/day under the same parent.
        """
        res = self.get(f"/campaigns/{campaign_id}/adsquads")
        rows = [r.get("adsquad") or r for r in res.get("adsquads", [])]
        hits = [a for a in rows if a.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h.get("id", "?") for h in hits)
            raise SnapError(
                f"{len(hits)} ad squads under campaign {campaign_id} are named {name!r} "
                f"({ids}). Refusing to guess — rename or delete the duplicate first."
            )
        return hits[0] if hits else None

    def find_ad(self, name: str, ad_squad_id: str) -> dict | None:
        """Exact-name lookup under one ad squad; the sibling of find_adsquad."""
        res = self.get(f"/adsquads/{ad_squad_id}/ads")
        rows = [r.get("ad") or r for r in res.get("ads", [])]
        hits = [a for a in rows if a.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h.get("id", "?") for h in hits)
            raise SnapError(
                f"{len(hits)} ads under ad squad {ad_squad_id} are named {name!r} "
                f"({ids}). Refusing to guess — rename or delete the duplicate first."
            )
        return hits[0] if hits else None

    def find_creative(self, name: str) -> dict | None:
        """Exact-name lookup across every creative on the account, any type.

        Added 2026-08-30 for `snap-push-story`: 15 creative objects for one Story
        ad (13 leaves, 1 preview, 1 composite) is by far the most this module
        creates in one run, and the account has no per-ad-squad scoping for
        creatives the way `find_ad` gets from `find_adsquad` — they live at the
        ad-account level. A run that dies partway (as `snap-push-story`'s first
        real attempt did, on the preview creative's media format) must resume by
        finding what already exists, not by re-uploading media and re-creating
        creatives it already made.
        """
        res = self.get(f"/adaccounts/{self.cfg['ad_account_id']}/creatives")
        rows = [r.get("creative") or r for r in res.get("creatives", [])]
        hits = [c for c in rows if c.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h.get("id", "?") for h in hits)
            raise SnapError(
                f"{len(hits)} creatives are named {name!r} ({ids}). Refusing to "
                "guess — Snap's own creatives page has no create-then-find-by-name "
                "guard, so this can happen; delete the duplicate before retrying."
            )
        return hits[0] if hits else None

    def find_lead_form(self, name: str) -> dict | None:
        """Exact-name lookup, so a retry resumes instead of duplicating a form."""
        res = self.get(f"/adaccounts/{self.cfg['ad_account_id']}/lead_generation_forms")
        rows = [r.get("lead_generation_form") or r for r in
                res.get("lead_generation_forms", [])]
        hits = [f for f in rows if f.get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h.get("id", "?") for h in hits)
            raise SnapError(
                f"{len(hits)} lead forms are named {name!r} ({ids}). Refusing to "
                "guess — archive the duplicates in Ads Manager first."
            )
        return hits[0] if hits else None

    def create_lead_form(self, *, name: str, privacy_url: str, end_page_url: str,
                         copy: dict | None = None, end_page_cta: str = END_PAGE_CTA_PAGE) -> dict:
        """Create the instant form: first name, phone, email, and the handoff.

        The end page is the funnel hinge — its button carries her to /get/w-apply
        with the UTMs as literals plus ra_src=form (the marker that lets the page
        admit her without a lead id). Everything in that URL is known at creation
        time except the ad id, which cannot be: the form precedes the ad and Snap
        documents no way to change the URL after. Ad-squad-level attribution is
        the accepted cost, on the record in the module comment above.
        """
        copy = copy or FORM_COPY_PAGE
        if end_page_cta not in END_PAGE_CTAS:
            # Refuse here rather than let the API refuse: a form POST returns 200
            # with the failure buried in sub_request_error_reason, and this is the
            # one field where a creative's own (larger) enum is the obvious wrong
            # guess. See END_PAGE_CTAS.
            raise SnapError(
                f"end_page_cta {end_page_cta!r} is not one of Snap's lead-form end page "
                f"values: {', '.join(sorted(END_PAGE_CTAS))}.\n"
                "Note this is NOT the creative's call_to_action enum — INSTALL_NOW is valid "
                "there and rejected here (E25020)."
            )
        res = self.post(
            f"/adaccounts/{self.cfg['ad_account_id']}/lead_generation_forms",
            {"lead_generation_forms": [{
                "ad_account_id": self.cfg["ad_account_id"],
                "name": name,
                "title": copy["title"],
                "description": copy["description"],
                # FIRST_NAME + LAST_NAME, not FIRST_NAME alone: Snap refuses a
                # lone first name (E25012, live rejection 2026-08-29), and the
                # account's own UI-made forms all use this pair — observed
                # convention over guessed alternative, the same rule that decided
                # meta.py's pixel question.
                "form_fields": [
                    {"type": "FIRST_NAME"},
                    {"type": "LAST_NAME"},
                    {"type": "PHONE_NUMBER"},
                    {"type": "EMAIL"},
                ],
                "privacy_policy_url": privacy_url,
                # The docs show end_page_properties at the top level; the API
                # refuses that with E25022. The shape below is what a live
                # UI-made form on this account actually stores — an ARRAY inside
                # default_end_page — read back on 2026-08-29 rather than guessed.
                "default_end_page": {
                    "headline": copy["title"],
                    "description": copy["description"],
                    "end_page_properties": [{
                        "call_to_action": end_page_cta,
                        "url": end_page_url,
                    }],
                },
            }]})
        return self._one(res, "lead_generation_forms")

    def create_lead_adsquad(self, *, name, campaign_id, targeting, daily_budget_inr,
                            start_time, end_time) -> dict:
        """Create the ad squad for a lead campaign, PAUSED.

        Differs from create_adsquad in what the objective forces: optimisation is
        the form submission, and no pixel is required — the conversion happens
        inside Snap, not on a page the pixel can see, so create_adsquad's hard
        pixel requirement would demand a signal this goal cannot use.
        """
        res = self.post(f"/campaigns/{campaign_id}/adsquads", {"adsquads": [{
            "name": name,
            "campaign_id": campaign_id,
            "type": "SNAP_ADS",
            "status": "PAUSED",
            "targeting": targeting,
            "optimization_goal": "LEAD_FORM_SUBMISSIONS",
            "billing_event": "IMPRESSION",
            "bid_strategy": "AUTO_BID",
            "daily_budget_micro": int(daily_budget_inr * MICRO),
            "placement_v2": {"config": "AUTOMATIC"},
            "start_time": start_time,
            "end_time": end_time,
        }]})
        return self._one(res, "adsquads")

    def create_lead_creative(self, *, name, media_id, headline, brand_name,
                             form_id, profile_id) -> dict:
        if len(headline) > 34:
            raise SnapError(f"headline is {len(headline)} chars; Snap's limit is 34: {headline!r}")
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/creatives", {"creatives": [{
            "ad_account_id": self.cfg["ad_account_id"],
            "name": name, "type": "LEAD_GENERATION",
            "headline": headline, "brand_name": brand_name,
            "call_to_action": "APPLY_NOW", "shareable": True,
            "top_snap_media_id": media_id,
            "lead_generation_form_id": form_id,
            "profile_properties": {"profile_id": profile_id},
        }]})
        return self._one(res, "creatives")

    def create_lead_ad(self, *, name, ad_squad_id, creative_id) -> dict:
        return self._one(self.post(f"/adsquads/{ad_squad_id}/ads", {"ads": [{
            "ad_squad_id": ad_squad_id, "creative_id": creative_id,
            "name": name, "type": "LEAD_GENERATION", "status": "PAUSED",
        }]}), "ads")

    # ---- media + creative + ad -------------------------------------------
    def upload_media(self, name: str, path: Path, media_type: str = "IMAGE") -> dict:
        """Register and upload one media object.

        `media_type` is IMAGE or VIDEO. Snap's WEB_VIEW creative takes whichever as
        its `top_snap_media_id`, so a video ad differs from an image ad only here —
        which is why this is a parameter rather than a second code path. Added
        2026-08-28 for the first video asset (creatives/moveon-swagger-video).
        """
        if media_type not in ("IMAGE", "VIDEO"):
            raise SnapError(f"media_type must be IMAGE or VIDEO, got {media_type!r}")
        media = self._one(self.post(f"/adaccounts/{self.cfg['ad_account_id']}/media", {"media": [{
            "ad_account_id": self.cfg["ad_account_id"], "name": name, "type": media_type,
        }]}), "media")

        boundary = uuid.uuid4().hex
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode(),
            f"Content-Type: {ctype}\r\n\r\n".encode(),
            path.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode(),
        ])
        req = urllib.request.Request(
            f"{API}/media/{media['id']}/upload", data=body, method="POST",
            headers={"Authorization": f"Bearer {self.token}",
                     "content-type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                r.read()
        except urllib.error.HTTPError as e:
            raise SnapError(f"media upload -> HTTP {e.code}\n{e.read().decode()[:500]}") from e
        return media

    def create_creative(self, *, name, media_id, headline, brand_name, url, profile_id,
                        call_to_action="MORE") -> dict:
        """`call_to_action` is the Snap CTA-button label enum (e.g. MORE, APPLY_NOW,
        SIGN_UP, LEARN_MORE). Defaults to MORE — the historical single-image value —
        but the Story push passes APPLY_NOW so the swipe-up chip matches the ad's own
        "Apply now" end card and the /get/w-apply funnel (Sree's call, 2026-08-30)."""
        if len(headline) > 34:
            raise SnapError(f"headline is {len(headline)} chars; Snap's limit is 34: {headline!r}")
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/creatives", {"creatives": [{
            "ad_account_id": self.cfg["ad_account_id"],
            "name": name, "type": "WEB_VIEW",
            "headline": headline, "brand_name": brand_name,
            "call_to_action": call_to_action, "shareable": True,
            "top_snap_media_id": media_id,
            "web_view_properties": {"url": url},
            "profile_properties": {"profile_id": profile_id},
        }]})
        return self._one(res, "creatives")

    def set_creative_url(self, creative: dict, url: str) -> dict:
        """Rewrite the landing URL once the real ad id exists.

        rules/tracking.md requires utm_id to carry the ad id, and the ad does not
        exist when the creative is created. Ads Manager solves this with a {{ad.id}}
        macro — the same macro whose silent non-resolution cost a week of spend on
        2026-08-21. Here the id is known for certain by the time this runs, so the
        URL is written literally and there is no macro left to fail.
        """
        body = {k: creative[k] for k in ("id", "ad_account_id", "name", "type", "headline",
                                         "brand_name", "call_to_action", "shareable",
                                         "top_snap_media_id", "profile_properties")
                if k in creative}
        body["web_view_properties"] = {"url": url}
        return self._one(self.put(f"/adaccounts/{self.cfg['ad_account_id']}/creatives",
                                  {"creatives": [body]}), "creatives")

    def set_creative_lead_form(self, creative: dict, form_id: str) -> dict:
        """Point an existing LEAD_GENERATION creative at a different form.

        A LEAD FORM IS IMMUTABLE. Snap fixes its copy, its end page and that end
        page's call_to_action at creation and documents no update, so correcting
        any of them means making a NEW form and repointing the creative — which is
        the only mutable link in the chain, and mutable even while the ad is live.

        Added 2026-09-04 to correct `moveon-lead-play`'s end-page button, which
        shipped VIEW_WEBSITE against a Play listing that is not a website of ours.

        `set_creative_url`'s field list, for its reason: Snap's update is a full
        replace, so the body is the object as it exists with exactly one key
        changed, and a field left out is a field deleted. Note the endpoint —
        PUT /creatives is 405; creatives update under the ad account (E0001).
        """
        body = {k: creative[k] for k in ("id", "ad_account_id", "name", "type", "headline",
                                         "brand_name", "call_to_action", "shareable",
                                         "top_snap_media_id", "top_snap_crop_position",
                                         "profile_properties")
                if k in creative}
        body["lead_generation_form_id"] = form_id
        return self._one(self.put(f"/adaccounts/{self.cfg['ad_account_id']}/creatives",
                                  {"creatives": [body]}, unchanged=creative), "creatives")

    def create_ad(self, *, name, ad_squad_id, creative_id, ad_type="REMOTE_WEBPAGE") -> dict:
        """`ad_type` must match the creative's own category, but not by sharing its
        name — the ad-type and creative-type enums are two different lists, and
        Snap rejects any mismatch outright (E1008). Discovered live in three
        rejections in a row: the default REMOTE_WEBPAGE against a COMPOSITE
        creative, then a guessed ad_type="COMPOSITE" (not a recognized ad type at
        all — E2002), then a guessed ad_type="SNAP_AD" (recognized, still the
        wrong category). The real mapping, per developers.snap.com's Ads page,
        which has an explicit ad-type<->creative-type table this repo had not read
        until this ad needed it: a COMPOSITE creative pairs with ad_type="STORY".
        REMOTE_WEBPAGE stays the default because every existing caller (a
        WEB_VIEW creative) needs it."""
        return self._one(self.post(f"/adsquads/{ad_squad_id}/ads", {"ads": [{
            "ad_squad_id": ad_squad_id, "creative_id": creative_id,
            "name": name, "type": ad_type, "status": "PAUSED",
        }]}), "ads")

    # ---- story ads (COMPOSITE: a tappable sequence of WEB_VIEW snaps) -----
    #
    # Added 2026-08-30, after Sree caught this session shipping 13 separate
    # single-image ads instead of the one tap-through sequence he'd actually
    # asked for. Confirmed live (tapping the reference "Qurli" ad advanced to a
    # second full-screen image under the same header/CTA) before any code was
    # written. developers.snap.com's own text: a COMPOSITE creative's
    # `composite_properties.creative_ids` holds 1-20 child creative ids, shown in
    # the listed order, immutable once created — and only SNAP_AD, APP_INSTALL,
    # WEB_VIEW and DEEP_LINK are supported as children. LEAD_GENERATION is
    # explicitly NOT in that list, which is why this ad is WEB_VIEW -> /get/w and
    # not a lead-gen ad, on Sree's own call once that conflict was surfaced.
    #
    # The exact shapes below (preview_properties, composite_properties, the ad's
    # own `type`) are read off the docs, not verified against a prior successful
    # push in this account — this is the first COMPOSITE object this module has
    # ever created. Treat the first real attempt as the check, the same way this
    # account's default_end_page shape and webhook casing were both settled by
    # what the live API actually said, not by what the docs said it would say.

    def create_preview_creative(self, *, name, media_id, headline, profile_id,
                                logo_media_id=None) -> dict:
        """The tile creative a Story Ad shows before it's tapped open.

        `headline` here is the PREVIEW's own headline (55-char limit per Snap's
        docs), a different field with a different limit than the 34-char
        `headline` on every other creative type in this file. `profile_id` is
        required here too (E2652 on a live attempt without it) even though the
        preview has no CTA of its own — every creative on this account carries a
        publisher identity, apparently including this one.
        """
        if len(headline) > 55:
            raise SnapError(f"preview headline is {len(headline)} chars; Snap's limit is 55: {headline!r}")
        props = {"preview_media_id": media_id, "preview_headline": headline}
        if logo_media_id:
            props["logo_media_id"] = logo_media_id
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/creatives", {"creatives": [{
            "ad_account_id": self.cfg["ad_account_id"],
            "name": name, "type": "PREVIEW",
            "preview_properties": props,
            "profile_properties": {"profile_id": profile_id},
        }]})
        return self._one(res, "creatives")

    def create_composite_creative(self, *, name, creative_ids, preview_creative_id, profile_id) -> dict:
        """Wrap the ordered leaf creatives (and the preview tile) into one Story Ad creative.

        `creative_ids` order is what the viewer sees and is immutable once
        created per Snap's docs — get the sequence right before calling this.
        `profile_id` required (E2652 on a live attempt without it), same as
        `create_preview_creative` — every creative type on this account seems to
        need a publisher identity regardless of whether it has its own CTA.
        """
        if not (1 <= len(creative_ids) <= 20):
            raise SnapError(f"a composite creative takes 1-20 creative_ids, got {len(creative_ids)}")
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/creatives", {"creatives": [{
            "ad_account_id": self.cfg["ad_account_id"],
            "name": name, "type": "COMPOSITE",
            "composite_properties": {"creative_ids": creative_ids},
            "preview_creative_id": preview_creative_id,
            "profile_properties": {"profile_id": profile_id},
        }]})
        return self._one(res, "creatives")

    # ---- lead delivery ---------------------------------------------------
    #
    # HOW LEAD DATA ACTUALLY LEAVES SNAP. There is no endpoint that lists or
    # downloads submitted leads. The Marketing API exposes form METADATA only;
    # submissions are delivered by webhook, one integration per form, and Snap
    # deletes leads after 90 days. So this section registers a destination — it
    # never fetches a lead, and no method here ever sees lead PII.
    #
    # WHY THIS DOES NOT WEAKEN DECISION #3. Every call below is scoped to
    # /lead_gen/* — it creates no campaign, ad squad, creative or ad, carries no
    # status and no budget, and cannot start spend. The `_call` safety check still
    # runs on the one POST, and passes because there is nothing in the payload for
    # it to refuse. Registering a webhook changes where leads go, not what runs.

    def delete(self, path: str) -> dict:
        return self._call("DELETE", path)

    def list_lead_forms(self) -> list[dict]:
        """Every lead form on the account, newest first is NOT guaranteed."""
        res = self.get(f"/adaccounts/{self.cfg['ad_account_id']}/lead_generation_forms")
        return [r.get("lead_generation_form") or r
                for r in res.get("lead_generation_forms", [])]

    # THE DOCS AND THE LIVE API DISAGREE ON CASING, so these read both.
    #
    # developers.snap.com documents the webhook response in camelCase
    # ({"webhookIntegrations": [{"webhookIntegration": {"integrationId": ...}}]}).
    # The live API answers in snake_case, like the rest of Snap
    # ({"webhook_integrations": [{"webhook_integration": {"integration_id": ...}}]}).
    # Both spellings cost real attempts to find: reading only the snake plural key
    # `integrations` made `snap-leads forms` report all seven forms as having no
    # webhook -- an empty list, no error, indistinguishable from the truth -- and
    # then reading only the documented camelCase made a SUCCESSFUL registration
    # raise, so the hmacSecret it returned was lost and the integration had to be
    # deleted and recreated to see it again.
    #
    # A secret you get exactly one chance to read is the wrong place to be
    # confident about a key name. These accept every spelling.
    # The list endpoint uses a THIRD shape again: {"partner_integrations": [...]}
    # with flat rows and the url buried in generic_webhook_handler_info. So the
    # create response, the documented create response, and the list response are
    # three different shapes for one object.
    _WEBHOOK_KEYS = ("partner_integrations", "webhook_integrations",
                     "webhookIntegrations", "integrations")

    @staticmethod
    def _webhook_rows(res: dict) -> list[dict]:
        rows = next((res[k] for k in SnapClient._WEBHOOK_KEYS if res.get(k)), [])
        return [r.get("webhook_integration") or r.get("webhookIntegration")
                or r.get("integration") or r for r in rows]

    @staticmethod
    def webhook_id(row: dict) -> str | None:
        return row.get("integration_id") or row.get("integrationId") or row.get("id")

    @staticmethod
    def webhook_url(row: dict) -> str | None:
        nested = row.get("generic_webhook_handler_info") or {}
        return (row.get("webhook_url") or row.get("webhookUrl")
                or nested.get("webhook_url") or nested.get("webhookUrl"))

    @staticmethod
    def webhook_secret(row: dict) -> str | None:
        return row.get("hmac_secret") or row.get("hmacSecret")

    def list_lead_webhooks(self, form_id: str) -> list[dict]:
        res = self.get(f"/lead_gen/forms/{form_id}/integrations?partner_type=PUBLIC_WEBHOOK")
        return self._webhook_rows(res)

    def register_lead_webhook(self, *, form_id: str, webhook_url: str) -> dict:
        """Point one form's submissions at our endpoint.

        Snap allows exactly ONE webhook integration per form, so this refuses when
        the form already has one rather than racing it. Re-pointing a form is a
        delete followed by a register, deliberately two steps: the delete is the
        moment leads stop arriving, and it should be typed on purpose.

        Requires Organization Admin on the ad account. Nothing else — there is no
        partner approval or lead-data allowlisting to clear.

        The response carries `hmacSecret`, which is how the receiver authenticates
        every later delivery. It is the same secret for every integration under the
        account, and Snap shows it here; it is NOT re-readable from the list
        endpoint later. The caller is responsible for storing it — this method
        deliberately does not write it anywhere.
        """
        existing = self.list_lead_webhooks(form_id)
        if existing:
            ids = ", ".join(self.webhook_id(e) or "?" for e in existing)
            urls = ", ".join(self.webhook_url(e) or "?" for e in existing)
            raise SnapError(
                f"form {form_id} already has a webhook integration ({ids} -> {urls}).\n"
                "Snap allows one per form. Delete it first if you mean to re-point it:\n"
                f"  ad-agent snap-leads delete --integration-id {ids}"
            )
        # Wrapped in a list under a plural key, like every other Snap creation.
        res = self.post("/lead_gen/integrations/public_webhook",
                        {"webhook_integrations": [
                            {"form_id": form_id, "webhook_url": webhook_url}]})
        rows = next((res[k] for k in self._WEBHOOK_KEYS if res.get(k)), [])
        if not rows:
            raise SnapError(f"no integration in the response: {json.dumps(res)[:400]}")
        status = rows[0].get("sub_request_status") or rows[0].get("subRequestStatus")
        if status not in (None, "200", "SUCCESS"):
            raise SnapError(f"integration rejected: {json.dumps(rows[0])[:400]}")
        return self._webhook_rows(res)[0]

    def test_lead_webhook(self, integration_id: str) -> dict:
        """Ask Snap to fire a sample delivery at the registered URL."""
        return self.get(f"/lead_gen/integrations/{integration_id}/test")

    def delete_lead_webhook(self, integration_id: str) -> dict:
        """Stop delivery. Leads submitted while no webhook exists are NOT queued."""
        return self.delete(f"/lead_gen/integrations/{integration_id}")

    # ---- audiences (Customer List / Lookalike) ----------------------------
    #
    # Added 2026-09-01, at the app owner's request, after a Custom Audience and
    # a Lookalike were built by hand in Ads Manager because this file had no
    # method for either. The ask was explicit: future audience add/update
    # should not require clicking through the UI again.
    #
    # This is a DIFFERENT object family from everything above, and the
    # paused-only rule does not apply to it the way it applies to a campaign or
    # ad squad: a segment carries no `status` an ad can be served from and no
    # budget, so there is nothing in its payload for `_call`'s safety check to
    # refuse — it passes through unmodified, which is correct. Nothing here
    # gains the ability to enable anything or move a budget; it only lets a
    # customer list be created and grown, and a lookalike be built from one.
    # Attaching an audience to a live ad squad's targeting remains a separate,
    # human action in Ads Manager, exactly like it was the day this was
    # written — this module still has no method that edits an existing ad
    # squad's targeting.

    @staticmethod
    def hash_email(email: str) -> str:
        """Snap's Customer List match key: lowercase, trimmed, SHA-256 hex.

        Getting normalization wrong doesn't error — it just fails to match, and
        a segment sitting at 0 users forever looks identical to one still being
        processed. Match Snap's own rule exactly rather than guessing: strip
        whitespace, lowercase, then hash.
        """
        return hashlib.sha256(email.strip().lower().encode()).hexdigest()

    def find_audience(self, name: str) -> dict | None:
        """Exact-name lookup, same refuse-to-guess shape as find_campaign.

        Snap does not enforce unique names on segments any more than it does
        on campaigns, so a duplicate here would have the same silent-wrong-one
        failure mode.
        """
        res = self.get(f"/adaccounts/{self.cfg['ad_account_id']}/segments")
        hits = [s.get("segment", s) for s in res.get("segments", [])
                if s.get("segment", s).get("name") == name]
        if len(hits) > 1:
            ids = ", ".join(h["id"] for h in hits)
            raise SnapError(
                f"{len(hits)} audiences are named {name!r} ({ids}).\n"
                "Refusing to guess which one to use — rename or delete the duplicate."
            )
        return hits[0] if hits else None

    def create_customer_list_audience(self, name: str, description: str = "",
                                      retention_in_days: int = 180) -> dict:
        """Create an empty Customer List segment, matched on hashed email.

        Empty on purpose: uploading is a separate call (`upload_audience_users`)
        because Snap's API treats "create the container" and "add people to it"
        as two different operations, and `upsert_customer_list_audience` below
        is what most callers actually want — create-if-missing then upload in
        one step.
        """
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/segments", {"segments": [{
            "name": name,
            "description": description,
            "source_type": "FIRST_PARTY",
            "schema": ["EMAIL_SHA256"],
            "ad_account_id": self.cfg["ad_account_id"],
            "retention_in_days": retention_in_days,
        }]})
        return self._one(res, "segments")

    def upload_audience_users(self, segment_id: str, emails: list[str]) -> dict:
        """Add people to an existing Customer List segment by email.

        Additive, not a replace: this is how the same audience is "updated" as
        new leads come in — call it again with the new emails, the old ones
        stay. Hashing happens here, not on the caller, so no plaintext email
        is ever the thing that gets logged or committed by accident.
        """
        hashed = [self.hash_email(e) for e in emails if e and e.strip()]
        if not hashed:
            raise SnapError("no usable emails to upload — every value was empty")
        return self.post(f"/segments/{segment_id}/users", {
            "users": [{"schema": ["EMAIL_SHA256"], "data": [[h] for h in hashed]}]
        })

    def upsert_customer_list_audience(self, name: str, emails: list[str],
                                      description: str = "") -> dict:
        """Find-or-create a Customer List by name, then upload emails to it.

        The one entry point most callers want: run this again next month with
        a longer email list and it grows the same audience rather than making
        a second one — the thing the app owner asked for by name.
        """
        audience = self.find_audience(name)
        if audience is None:
            audience = self.create_customer_list_audience(name, description)
        self.upload_audience_users(audience["id"], emails)
        return audience

    def create_lookalike_audience(self, name: str, *, seed_segment_id: str,
                                  country: str, similarity: str = "SIMILARITY",
                                  description: str = "") -> dict:
        """Build a Lookalike off an existing Customer List (or other) segment.

        `similarity` is Snap's own three-tier vocabulary — REACH (broadest),
        BALANCE, SIMILARITY (narrowest) — not a percentage; there is no numeric
        knob to set here despite how the Ads Manager UI's audience-naming
        convention in this account (`_1PCT_`) reads. Default is the narrowest
        tier because every seed built by this codebase so far has been small,
        and a small seed drifts fastest at the broadest tier.
        """
        res = self.post(f"/adaccounts/{self.cfg['ad_account_id']}/segments", {"segments": [{
            "name": name,
            "description": description,
            "source_type": "LOOKALIKE",
            "ad_account_id": self.cfg["ad_account_id"],
            "lookalike_spec": {
                "country": country,
                "type": similarity,
                "seed_segment_id": seed_segment_id,
            },
        }]})
        return self._one(res, "segments")

    def list_audiences(self) -> list[dict]:
        """Every Custom Audience / Lookalike on the account."""
        res = self.get(f"/adaccounts/{self.cfg['ad_account_id']}/segments")
        return [s.get("segment", s) for s in res.get("segments", [])]
