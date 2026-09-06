"""Sending a META traffic ad straight to the Play listing.

Added 2026-09-06 with `moveon-play-w1830-meta`, the first Meta ad with no page of
ours in the funnel. Its Snap sibling is pinned in `test_store_destination.py`; this
file covers the three things that are DIFFERENT on Meta, each of which fails
silently rather than loudly:

  1. **The ad id lives in a different parameter.** Snap joins on `utm_id`, Meta on
     `utm_content` (traffic-quality.ts, per network). Crossing them breaks
     ad-level attribution on one network while looking fine on the other.
  2. **`url_tags` is the wrong channel here.** Meta APPENDS url_tags to the
     outbound URL, and Play discards appended parameters — so a store-bound ad
     carrying its tracking there spends normally and produces installs nothing can
     attribute. The tracking has to be URL-encoded inside Play's `referrer=`,
     which means it lives on the creative's LINK.
  3. **`ra_lp` must not be reused across networks.** It is the only field in
     user_acquisition that says which funnel an install came off, and Snap-vs-Meta
     on the same creative into the same store is the exact comparison it has to
     survive.
"""
from __future__ import annotations

from urllib.parse import parse_qs, unquote, urlsplit

from conftest import REPO

from ad_management_agent import cli, destinations

# The India storefront, as the app owner specified it on 2026-09-06 — note it
# already carries TWO query parameters besides the app id, which is what makes the
# separator logic in _store_referrer_url load-bearing rather than incidental.
PLAY_IN = ("https://play.google.com/store/apps/details"
           "?id=com.riteangle.app&gl=IN&hl=en_IN")
OURS = "https://www.riteangle.dating/get/w"
RULES = REPO / "rules"

CAMPAIGN = "RA_TRAFFIC_GETW_IN_BLR_TOF_202608"
ADSET_ID = "6984035763999"
AD_ID = "6984036525999"
AD_NAME = "VID_MOVE-ON-PROPER_E_20260906"


def _meta_url(destination: str) -> str:
    return cli._meta_traffic_url(RULES, destination, campaign_name=CAMPAIGN,
                                 ad_set_id=ADSET_ID, ad_id=AD_ID, ad_name=AD_NAME)


def _referrer_of(url: str) -> dict[str, str]:
    q = parse_qs(urlsplit(url).query)
    return {k: v[0] for k, v in parse_qs(unquote(q["referrer"][0])).items()}


class TestTheGateAcceptsTheLocalisedListing:
    def test_extra_query_params_do_not_change_the_registry_key(self):
        # gl/hl are Play's storefront and language selectors. If they leaked into
        # the key, the listing would read as unregistered and the gate would refuse
        # a destination that is registered.
        assert destinations.normalize_path(PLAY_IN) == "play.google.com/store/apps/details"

    def test_a_womens_ad_set_may_point_at_it(self):
        destinations.check(ad_set_name="WOMEN_18-30_CASUAL_MOVEON-PLAY-INSTALL",
                           destination_url=PLAY_IN, rules_dir=RULES)


class TestTheAppIdSurvives:
    def test_referrer_is_appended_with_an_ampersand_not_a_second_question_mark(self):
        url = _meta_url(PLAY_IN)
        assert "?id=com.riteangle.app&gl=IN&hl=en_IN&referrer=" in url
        assert url.count("?") == 1

    def test_play_reads_the_bare_package_name(self):
        # The 2026-09-05 corruption: a second `?` made Play parse the app id as
        # `com.riteangle.app?utm_source=snapchat`, so the link may not even have
        # opened the right listing while Ads Manager reported a healthy ad.
        q = parse_qs(urlsplit(_meta_url(PLAY_IN)).query)
        assert q["id"] == ["com.riteangle.app"]

    def test_the_storefront_selectors_are_not_dropped(self):
        q = parse_qs(urlsplit(_meta_url(PLAY_IN)).query)
        assert q["gl"] == ["IN"] and q["hl"] == ["en_IN"]

    def test_nothing_tracking_shaped_is_left_outside_the_referrer(self):
        # Anything appended beside referrer= is discarded by Play, so its presence
        # would mean tracking we believe we have and do not.
        q = parse_qs(urlsplit(_meta_url(PLAY_IN)).query)
        assert set(q) == {"id", "gl", "hl", "referrer"}


class TestTheTrackingInsideTheReferrer:
    def test_meta_joins_the_ad_on_utm_content_not_utm_id(self):
        ref = _referrer_of(_meta_url(PLAY_IN))
        assert ref["utm_content"] == AD_ID
        assert "utm_id" not in ref

    def test_the_ad_set_id_rides_utm_term(self):
        assert _referrer_of(_meta_url(PLAY_IN))["utm_term"] == ADSET_ID

    def test_utm_source_is_fb_never_meta(self):
        # networkOf() maps only ig/fb/instagram/facebook to 'meta'; `meta` falls
        # through to 'other' and the click stops counting as ad traffic at all.
        assert _referrer_of(_meta_url(PLAY_IN))["utm_source"] == "fb"

    def test_the_landing_page_label_is_distinct_from_both_snap_funnels(self):
        ref = _referrer_of(_meta_url(PLAY_IN))
        assert ref["ra_lp"] == "meta_ad_direct"
        assert ref["ra_lp"] != cli.PLAY_DIRECT_AD_LANDING_PAGE      # snap_ad_direct
        assert ref["ra_lp"] != cli.PLAY_DIRECT_LANDING_PAGE         # snap_lead_form

    def test_it_came_off_an_ad_not_a_form(self):
        assert _referrer_of(_meta_url(PLAY_IN))["ra_src"] == "ad"


class TestOurOwnPagesAreUnaffected:
    def test_a_page_of_ours_still_takes_the_params_on_the_query_string(self):
        url = _meta_url(OURS)
        assert url.startswith(OURS + "?")
        assert "referrer=" not in url
        q = parse_qs(urlsplit(url).query)
        assert q["utm_content"] == [AD_ID]
        assert q["utm_source"] == ["fb"]
