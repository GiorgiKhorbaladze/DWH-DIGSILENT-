from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


HOURS_PER_YEAR = 8760


MaintWindow = Mapping[str, Any]


def _maint_factor(asset: Mapping[str, Any], t_local: int, offset_h: int = 0) -> float:
    """Return maintenance availability factor for a local horizon period.

    ``maint_windows`` entries use global hour indices with inclusive
    ``start_hour`` and exclusive ``end_hour`` bounds. ``offset_h`` aligns a
    rolling-horizon local period to that global hour clock.
    """
    windows = asset.get("maint_windows", [])
    if not windows:
        return 1.0

    global_hour = int(offset_h) + int(t_local)
    factor = 1.0
    for window in windows:
        start_hour = _required_int(window, "start_hour")
        end_hour = _required_int(window, "end_hour")
        availability_factor = float(window.get("availability_factor", 1.0))

        if end_hour < start_hour:
            raise ValueError("maint_windows end_hour must be >= start_hour")
        if not 0.0 <= availability_factor <= 1.0:
            raise ValueError("maint_windows availability_factor must be in [0, 1]")

        if start_hour <= global_hour < end_hour:
            factor = min(factor, availability_factor)

    return factor


def get_pmax_t(
    asset: Mapping[str, Any],
    t_local: int,
    profiles: Mapping[str, Sequence[float]],
    offset_h: int = 0,
) -> float:
    """Effective Pmax at a local rolling-horizon period.

    Maintenance is applied to thermal, hydro, import, wind, and solar assets.
    Wind/solar and run-of-river hydro combine their capacity factor with the
    maintenance factor.
    """
    atype = asset.get("type")
    maint = _maint_factor(asset, t_local, offset_h=offset_h)

    if atype in ("wind", "solar"):
        prof_key = asset.get("availability_profile")
        cf = profiles.get(prof_key, [1.0] * (t_local + 1))[t_local] if prof_key else 1.0
        return float(asset.get("pmax_installed", asset.get("pmax", 0))) * _clamp01(cf) * maint

    if atype == "hydro_ror":
        prof_key = asset.get("availability_profile")
        default_cf = asset.get("cf", 0.65)
        cf = profiles.get(prof_key, [default_cf] * (t_local + 1))[t_local] if prof_key else default_cf
        return float(asset.get("pmax", 0)) * _clamp01(cf) * maint

    if atype == "import":
        prof_key = asset.get("pmax_profile")
        if prof_key and isinstance(profiles.get(prof_key), list):
            return float(profiles[prof_key][t_local]) * maint
        return float(asset.get("pmax_profile", asset.get("pmax", 0))) * maint

    if atype in ("thermal", "hydro_reg"):
        return float(asset.get("pmax", 0)) * maint

    return float(asset.get("pmax", 0))


def _clamp01(value: Any) -> float:
    return max(0.0, min(1.0, float(value)))


def _required_int(window: MaintWindow, key: str) -> int:
    if key not in window:
        raise ValueError(f"maint_windows entries require {key}")
    return int(window[key])
