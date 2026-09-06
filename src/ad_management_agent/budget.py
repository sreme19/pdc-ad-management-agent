"""Numbers lifted out of rules/budget.md so code can enforce them.

Every other file under `rules/` is prose read live by a skill. These figures are
the ones code has to act on — a pre-launch refusal and a loose-end report cannot
parse a paragraph — so they are mirrored here, deliberately and visibly. If
rules/budget.md changes, change these in the same commit.

From rules/budget.md as amended 2026-08-28:

  * Default daily spend: Rs 300 per ad set — the app owner's operating level,
    chosen for burn rate over read speed.
  * Full-experiment threshold: Rs 800-1,200. No longer a floor to refuse under;
    still the level below which the delivery algorithm rarely exits its learning
    phase. A read under it is DIRECTIONAL, and ad-audit should treat
    `inconclusive` as the normal verdict there, not a disappointment.
  * Kill or double after 3-5 days, or 50-100 events, whichever comes first.

From rules/budget.md as amended 2026-09-05:

  * Default duration: 2 days per ad set — the app owner's standing decision,
    replacing the 5 days every earlier record carried. Rs 300 x 2 = Rs 600 a
    test. Mirrored here for the same reason the daily default is: a flag default
    is enforcement, a paragraph is a hope somebody reads it.
  * It is SHORTER than the kill window above, deliberately. The end date makes
    the pause call now; the 3-5 day window governs the re-run decision instead.
  * The push commands stamp the ad squad's start at CREATION, not at enabling,
    and everything is created PAUSED. At 2 days a one-day gap between push and
    enable costs half the test, and nothing warns about it.

`below_floor` and `floor_note` keep their names — every call site is a warning,
and the warning is still true. What changed is what the number means: it now
marks where a read stops being trustworthy, not where a proposal stops being
acceptable.
"""
from __future__ import annotations

DEFAULT_DAILY_INR = 300.0
DEFAULT_DURATION_DAYS = 2

MIN_VIABLE_DAILY_INR = 800.0
MAX_VIABLE_DAILY_INR = 1200.0

KILL_WINDOW_DAYS_MIN = 3
KILL_WINDOW_DAYS_MAX = 5


def below_floor(daily_inr: float | None) -> bool:
    """True when a read at this spend is directional rather than conclusive."""
    return daily_inr is not None and float(daily_inr) < MIN_VIABLE_DAILY_INR


def floor_note(daily_inr: float) -> str:
    return (
        f"Rs {daily_inr:.0f}/day is below the Rs {MIN_VIABLE_DAILY_INR:.0f}-"
        f"{MAX_VIABLE_DAILY_INR:.0f} full-experiment threshold (rules/budget.md, as "
        "amended 2026-08-28: Rs 300 is the accepted default). The delivery algorithm "
        "may never exit its learning phase at this level, so expect a directional "
        "read — `inconclusive` is the normal audit verdict here, and raising this one "
        "ad set into the threshold band is the fix when its answer must be trusted."
    )
