"""PowerSim JSON contract validation for maintenance handoff.

This module intentionally validates the browser/Python handoff only; solver
maintenance enforcement remains a separate, model-audited change.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

SCHEMA_VERSION = "1.4"
ACCEPTED_SCHEMA_PRIOR = {"1.0", "1.1", "1.2", "1.3"}
MAINTENANCE_EVENT_TYPES = {
    "planned_maintenance",
    "forced_outage",
    "partial_derating",
}


def validate_input(inp: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    metadata = inp.get("metadata") or {}
    schema_version = metadata.get("schema_version")
    if schema_version == SCHEMA_VERSION:
        pass
    elif schema_version in ACCEPTED_SCHEMA_PRIOR:
        warnings.append(
            f"schema_version '{schema_version}' accepted as legacy "
            f"(active schema is '{SCHEMA_VERSION}')"
        )
    else:
        errors.append(f"schema_version '{schema_version}' unsupported")

    assets = inp.get("assets") or []
    asset_by_id = {asset.get("id"): asset for asset in assets if asset.get("id")}
    if not assets:
        warnings.append("assets list is empty")

    maintenance = inp.get("maintenance", [])
    if maintenance is None:
        maintenance = []
    if not isinstance(maintenance, list):
        errors.append("maintenance must be a list when provided")
        maintenance = []

    _validate_maintenance_events(
        maintenance,
        asset_by_id=asset_by_id,
        horizon=inp.get("study_horizon") or {},
        errors=errors,
        warnings=warnings,
    )
    return not errors, errors, warnings


def validate_output(_out: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    return True, [], []


def _validate_maintenance_events(
    events: list[Any],
    *,
    asset_by_id: dict[str, dict[str, Any]],
    horizon: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    normalized: list[tuple[str, datetime, datetime, int]] = []
    horizon_start = _parse_datetime(horizon.get("start"))
    horizon_end = _parse_datetime(horizon.get("end"))

    for idx, event in enumerate(events):
        prefix = f"maintenance[{idx}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue

        asset_id = event.get("asset_id")
        if not asset_id:
            errors.append(f"{prefix}.asset_id is required")
        elif asset_id not in asset_by_id:
            errors.append(f"{prefix}.asset_id '{asset_id}' does not match any asset")

        event_type = event.get("event_type")
        if event_type not in MAINTENANCE_EVENT_TYPES:
            errors.append(f"{prefix}.event_type must be one of {sorted(MAINTENANCE_EVENT_TYPES)}")

        start = _parse_datetime(event.get("start"))
        end = _parse_datetime(event.get("end"))
        if start is None:
            errors.append(f"{prefix}.start must be an ISO datetime")
        if end is None:
            errors.append(f"{prefix}.end must be an ISO datetime")
        if start and end and start >= end:
            errors.append(f"{prefix}.start must be before end")

        available_capacity_mw = event.get("available_capacity_mw")
        availability_factor = event.get("availability_factor")
        if available_capacity_mw in ("", None):
            available_capacity_mw = None
        if availability_factor in ("", None):
            availability_factor = None

        asset = asset_by_id.get(asset_id)
        pmax = _asset_pmax(asset) if asset else None
        if available_capacity_mw is not None:
            if not _is_number(available_capacity_mw):
                errors.append(f"{prefix}.available_capacity_mw must be numeric")
            elif float(available_capacity_mw) < 0:
                errors.append(f"{prefix}.available_capacity_mw must be >= 0")
            elif pmax is not None and float(available_capacity_mw) > pmax:
                errors.append(f"{prefix}.available_capacity_mw exceeds asset pmax_mw ({pmax:g})")

        if availability_factor is not None:
            if not _is_number(availability_factor):
                errors.append(f"{prefix}.availability_factor must be numeric")
            elif not 0 <= float(availability_factor) <= 1:
                errors.append(f"{prefix}.availability_factor must be between 0 and 1")

        if event_type == "partial_derating" and available_capacity_mw is None and availability_factor is None:
            warnings.append(
                f"{prefix}: partial_derating should set available_capacity_mw or availability_factor"
            )

        if start and end:
            if horizon_start and end <= horizon_start or horizon_end and start >= horizon_end:
                warnings.append(f"{prefix}: event is outside selected horizon")
            if asset_id:
                normalized.append((str(asset_id), start, end, idx))

    normalized.sort(key=lambda item: (item[0], item[1], item[2]))
    for left, right in zip(normalized, normalized[1:]):
        if left[0] == right[0] and right[1] < left[2]:
            warnings.append(
                f"maintenance[{left[3]}] overlaps maintenance[{right[3]}] for asset '{left[0]}'"
            )


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _asset_pmax(asset: dict[str, Any] | None) -> float | None:
    if not asset:
        return None
    for key in ("pmax_mw", "pmax", "pmax_installed", "power_mw"):
        value = asset.get(key)
        if _is_number(value):
            return float(value)
    return None
