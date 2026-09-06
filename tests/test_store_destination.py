"""Sending a Snap lead form's end page to the Play listing instead of a page of ours.

Added 2026-09-04 with `moveon-lead-play-w1830-snap`, the first ad whose funnel has
no page of ours in it at all. Two things had to change to allow it, and both are
the kind that fail silently rather than loudly, so both are pinned here:

  1. The destination gate keyed on PATH ONLY, so the Play listing would have
     registered as `/store/apps/details` — the App Store's path shape too, and
     anyone else's.
  2. The end-page URL was built by appending the UTMs to the destination. Appended
     to a store listing, Play ignores them and every install off the ad is
     unattributable — the 2026-08-21 incident with a different first step.
"""
from __future__ import annotations

from urllib.parse import parse_qs, unquote, urlsplit

import pytest
from conftest import REPO

from ad_management_agent import cli, destinations
from ad_management_agent import snap as snapapi

PLAY = "https://play.google.com/store/apps/details?id=com.riteangle.app"
OURS = "https://www.riteangle.dating/get/w-apply"


class TestGateKeysOnHostForOffSiteDestinations:
    def test_our_own_pages_still_key_on_the_bare_path(self):
        # Every pre-existing entry in the registry depends on this.
        assert destinations.normalize_path(OURS) == "/get/w-apply"
        assert destinations.normalize_path("https://riteangle.dating/get/w") == "/get/w"

    def test_an_off_site_destination_keys_on_host_and_path(self):
        assert destinations.normalize_path(PLAY) == "play.google.com/store/apps/details"

    def test_the_play_listing_is_registered_and_open_to_a_womens_ad_set(self):
        destinations.check(ad_set_name="WOMEN_18-30_CASUAL_MOVEON-LEAD-PLAY",
                           destination_url=PLAY, rules_dir=REPO / "rules")

    def test_another_store_sharing_the_path_shape_is_still_refused(self):
        # The whole point of the host in the key: registering our Play listing
        # must not open a URL pattern nobody read.
        with pytest.raises(destinations.DestinationGateError):
            destinations.check(
                ad_set_name="WOMEN_18-30_CASUAL_MOVEON-LEAD-PLAY",
                destination_url="https://evil.example/store/apps/details?id=com.riteangle.app",
                rules_dir=REPO / "rules")


class TestStoreEndPageCarriesAttributionInThePlayReferrer:
    def build(self, destination):
        return cli._snap_lead_end_page(
            REPO / "rules", destination,
            campaign_name="RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608",
            ad_squad_id="squad-uuid", ad_name="VID_MOVE-ON-PROPER_A_20260904")

    def referrer(self):
        url = self.build(PLAY)
        return parse_qs(unquote(parse_qs(urlsplit(url).query)["referrer"][0]))

    def test_the_listing_id_survives_intact(self):
        # A second `?` here would be a malformed URL, which is what appending
        # produced before this branch existed.
        q = parse_qs(urlsplit(self.build(PLAY)).query)
        assert q["id"] == ["com.riteangle.app"]
        assert self.build(PLAY).count("?") == 1

    def test_the_utms_ride_inside_the_referrer_parameter(self):
        # Not on the listing URL: Play only hands the app what is in `referrer`.
        assert "utm_source" not in parse_qs(urlsplit(self.build(PLAY)).query)
        r = self.referrer()
        assert r["utm_source"] == ["snapchat"]
        assert r["utm_medium"] == ["paid_social"]
        assert r["utm_term"] == ["squad-uuid"]
        assert r["utm_content"] == ["VID_MOVE-ON-PROPER_A_20260904"]

    def test_ra_lp_names_the_form_and_not_a_page_that_never_rendered(self):
        # mobile/lib/attribution.dart keeps ra_lp as landingPage. Reusing a real
        # page id here would count a direct-to-store install as a page view that
        # never happened.
        assert self.referrer()["ra_lp"] == ["snap_lead_form"]
        assert cli.PLAY_DIRECT_LANDING_PAGE not in {"get", "get_w", "get_w_apply", "get_w_drip"}

    def test_no_ad_level_id_is_claimed(self):
        # Snap fixes the form's end page at creation and the form precedes the ad,
        # so utm_id cannot be known. Absent by platform limit, never faked.
        assert "utm_id" not in self.referrer()

    def test_no_unresolved_macro_survives(self):
        assert "{{" not in self.build(PLAY)

    def test_our_own_pages_are_built_exactly_as_before(self):
        assert self.build(OURS) == (
            "https://www.riteangle.dating/get/w-apply"
            "?utm_source=snapchat&utm_medium=paid_social"
            "&utm_campaign=RA_LEADS_GETW-APPLY_IN_PAN_TOF_202608"
            "&utm_term=squad-uuid&utm_content=VID_MOVE-ON-PROPER_A_20260904&ra_src=form")


class TestEndPageCallToAction:
    """The end page's enum is NOT the creative's, and that is the whole trap.

    A creative takes INSTALL_NOW; an end page does not (E25020, probed live
    2026-09-04). See lrn-2026-09-04-snap-lead-end-page-cta-enum.
    """

    def test_install_flavoured_values_are_not_in_the_enum(self):
        for cta in ("INSTALL_NOW", "DOWNLOAD", "GET_APP"):
            assert cta not in snapapi.END_PAGE_CTAS

    def test_the_store_cta_is_a_value_snap_actually_accepts(self):
        assert snapapi.END_PAGE_CTA_STORE in snapapi.END_PAGE_CTAS
        assert snapapi.END_PAGE_CTA_PAGE in snapapi.END_PAGE_CTAS

    def test_the_store_cta_carries_no_purchase_language(self):
        # compliance.md #2: no purchases, no subscriptions, no credits, and copy
        # may never imply otherwise. Four values in the enum do.
        assert snapapi.END_PAGE_CTA_STORE not in {
            "FREE_TRIAL", "SPECIAL_OFFER", "GET_COUPON", "BUY_TICKETS"}

    def test_the_store_cta_does_not_re_ask_for_the_apply_she_just_did(self):
        assert snapapi.END_PAGE_CTA_STORE != "APPLY_NOW"

    def test_an_invalid_cta_is_refused_before_it_reaches_the_api(self):
        # Snap answers a bad form POST with HTTP 200 and the failure buried in
        # sub_request_error_reason, so this refuses locally instead.
        client = snapapi.SnapClient.__new__(snapapi.SnapClient)
        client.cfg = {"ad_account_id": "acct"}
        with pytest.raises(snapapi.SnapError, match="INSTALL_NOW"):
            client.create_lead_form(name="x", privacy_url="https://example.test",
                                    end_page_url=PLAY, end_page_cta="INSTALL_NOW")
