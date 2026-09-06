"""The destination gate.

`ad-agent propose` refuses to write a record whose ad-set audience doesn't match
the framing of the page it sends traffic to. See rules/destinations.yaml for the
registry and the reasoning; this module is only the enforcement.

There is deliberately no override flag. A blocked proposal is unblocked by
building the destination and registering it in rules/destinations.yaml — which
is the point of the gate, not a gap in it.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

import yaml

GENDER_TOKENS = {
    "WOMEN": "women",
    "WOMAN": "women",
    "FEMALE": "women",
    "MEN": "men",
    "MAN": "men",
    "MALE": "men",
}


class DestinationGateError(Exception):
    """Raised when a proposal's audience and destination don't match."""


def load_registry(rules_dir: Path) -> dict:
    path = rules_dir / "destinations.yaml"
    if not path.exists():
        raise DestinationGateError(
            f"destination registry missing: {path}\n"
            "The gate cannot be evaluated without it. Restore the file from git."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("destinations") or {}


def audience_of_ad_set_name(ad_set_name: str) -> str | None:
    """Read the gender band out of an ad-set name.

    rules/naming.md gives [AUDIENCE]_[AGE]_[GENDER]_[SIGNAL], and every live name
    carries the gender as a whole token (WOMEN_18-22_CASUAL_LPV,
    MEN_25-40_CASUAL_STORY_IND-LPV). rules/targeting.md forbids a mixed-gender ad
    set outright, so a name with no gender token is itself the error.
    """
    for token in ad_set_name.upper().replace("-", "_").split("_"):
        if token in GENDER_TOKENS:
            return GENDER_TOKENS[token]
    return None


#: Hosts whose pages are ours, and which therefore register under a bare path.
#: Anything else registers under `host/path`, see normalize_path.
OWN_HOSTS = ("riteangle.dating",)


def normalize_path(destination_url: str) -> str:
    """Reduce a destination URL to its registry key.

    Our own pages key on the path alone (`/get/w-apply`) — that is how the
    registry has always been written and every existing entry keeps working.

    AN OFF-SITE DESTINATION KEYS ON `host/path` INSTEAD, and that distinction is
    load-bearing rather than tidy. Added 2026-09-04 for the Play listing, when a
    Snap lead form's end page became the store rather than a page of ours. Keyed
    on the path alone, the Play listing would have registered as
    `/store/apps/details` — which is App Store's path shape too, and any other
    site's, so the gate would have been opened for a whole class of URLs nobody
    read. The gate exists because an unread page is how women's traffic reached a
    men's page; a key that cannot name the host cannot say which page was read.
    """
    parts = urlsplit(destination_url.strip())
    path = parts.path or "/"
    # A token-gated route like /beta/<token> registers under its parent, /beta.
    if len(path) > 1:
        path = "/" + path.strip("/")

    host = (parts.hostname or "").lower().removeprefix("www.")
    if host and not any(host == own or host.endswith("." + own) for own in OWN_HOSTS):
        return f"{host}{path}"
    return path


def _registry_lookup(registry: dict, path: str) -> tuple[str, dict] | None:
    if path in registry:
        return path, registry[path]
    # Fall back to the longest registered prefix, so /beta/<token> resolves to /beta.
    candidates = [k for k in registry if path.startswith(k.rstrip("/") + "/")]
    if not candidates:
        return None
    key = max(candidates, key=len)
    return key, registry[key]


def check(ad_set_name: str, destination_url: str, rules_dir: Path) -> None:
    """Raise DestinationGateError unless this ad set may point at this destination."""
    registry = load_registry(rules_dir)
    audience = audience_of_ad_set_name(ad_set_name)

    if audience is None:
        raise DestinationGateError(
            f"ad set name {ad_set_name!r} carries no gender token.\n"
            "rules/targeting.md forbids a mixed-gender ad set, and rules/naming.md puts the\n"
            "gender in the ad-set name as a whole token (e.g. WOMEN_18-22_CASUAL_LPV).\n"
            "Fix the name, then propose again."
        )

    path = normalize_path(destination_url)
    found = _registry_lookup(registry, path)

    if found is None:
        raise DestinationGateError(
            f"destination {path!r} is not in rules/destinations.yaml.\n"
            "The gate fails closed on an unregistered page — the same way\n"
            "rules/tracking.md's parsing fails closed rather than guessing — because an\n"
            "unread page is exactly how women's traffic ended up on a men's page.\n"
            f"Read the page, then add {path!r} to the registry with its audience,\n"
            "paid_traffic flag, and the date you read it."
        )

    key, entry = found
    page_audience = (entry.get("audience") or "").lower()
    note = (entry.get("note") or "").strip()

    if not entry.get("paid_traffic", False):
        raise DestinationGateError(
            f"destination {key!r} is registered as paid_traffic: false — it cannot receive\n"
            f"paid traffic at all.\n\n{note}\n\n"
            "Point this ad set at a page that can, or change the registry if that's wrong."
        )

    if page_audience not in {"men", "women", "neutral"}:
        raise DestinationGateError(
            f"destination {key!r} has audience {page_audience!r} in rules/destinations.yaml;\n"
            "expected one of: men, women, neutral."
        )

    if page_audience == "neutral" or page_audience == audience:
        return

    raise DestinationGateError(
        f"BLOCKED: ad set {ad_set_name!r} targets {audience}, but its destination {key!r}\n"
        f"is written for {page_audience}.\n\n"
        f"{note}\n\n"
        "This is the hard gate from rules/destinations.yaml. There is no override flag —\n"
        "sending this audience to this page is the failure the gate exists to stop.\n\n"
        "To unblock: build the destination that speaks to this audience, then register it in\n"
        "rules/destinations.yaml and propose again with --destination-url pointing at it."
    )
