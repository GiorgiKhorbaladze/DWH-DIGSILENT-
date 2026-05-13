from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "schema", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from powersim_schema import SCHEMA_VERSION, validate_input  # noqa: E402

HTML_PATH = ROOT / "html" / "PowerSim_v4.html"


def _base_input() -> dict:
    return {
        "metadata": {"schema_version": SCHEMA_VERSION, "model_version": "PowerSim v4.0"},
        "assets": [{"id": "enguri_hpp", "name": "Enguri HPP", "pmax_mw": 1300}],
        "study_horizon": {"start": "2026-01-01T00:00:00", "end": "2026-12-31T23:00:00"},
    }


def test_old_json_without_maintenance_still_loads() -> None:
    ok, errors, _warnings = validate_input(_base_input())
    assert ok, errors


def test_json_with_maintenance_events_validates_and_round_trips() -> None:
    data = _base_input()
    data["maintenance"] = [
        {
            "asset_id": "enguri_hpp",
            "start": "2026-04-01T00:00:00",
            "end": "2026-04-10T23:00:00",
            "event_type": "planned_maintenance",
            "available_capacity_mw": 900,
            "availability_factor": None,
            "note": "Unit maintenance",
        }
    ]

    encoded = json.dumps(data)
    decoded = json.loads(encoded)
    ok, errors, _warnings = validate_input(decoded)

    assert ok, errors
    assert decoded["maintenance"][0]["asset_id"] == "enguri_hpp"


def test_maintenance_validation_catches_required_errors_and_warnings() -> None:
    data = _base_input()
    data["maintenance"] = [
        {
            "asset_id": "enguri_hpp",
            "start": "2026-05-02T00:00:00",
            "end": "2026-05-01T00:00:00",
            "event_type": "planned_maintenance",
            "available_capacity_mw": 0,
        },
        {
            "asset_id": "missing_station",
            "start": "2026-06-01T00:00:00",
            "end": "2026-06-02T00:00:00",
            "event_type": "partial_derating",
            "available_capacity_mw": 1400,
        },
        {
            "asset_id": "enguri_hpp",
            "start": "2026-07-01T00:00:00",
            "end": "2026-07-05T00:00:00",
            "event_type": "partial_derating",
            "available_capacity_mw": 1200,
        },
        {
            "asset_id": "enguri_hpp",
            "start": "2026-07-04T00:00:00",
            "end": "2026-07-06T00:00:00",
            "event_type": "forced_outage",
            "availability_factor": 0,
        },
    ]

    ok, errors, warnings = validate_input(data)

    assert not ok
    assert any("start must be before end" in err for err in errors)
    assert any("does not match any asset" in err for err in errors)
    assert any("overlaps" in warn for warn in warnings)


def test_available_capacity_cannot_exceed_asset_pmax() -> None:
    data = _base_input()
    data["maintenance"] = [
        {
            "asset_id": "enguri_hpp",
            "start": "2026-04-01T00:00:00",
            "end": "2026-04-02T00:00:00",
            "event_type": "partial_derating",
            "available_capacity_mw": 1301,
        }
    ]

    ok, errors, _warnings = validate_input(data)

    assert not ok
    assert any("exceeds asset pmax" in err for err in errors)


def test_html_exports_maintenance_contract_surface() -> None:
    text = HTML_PATH.read_text(encoding="utf-8")

    assert "const SCHEMA_VERSION = '1.4'" in text
    assert re.search(r"maintenance\s*:\s*STATE\.maintenance", text)
    assert "function importInputJSON" in text
    assert "validateMaintenance" in text
    assert "გეგმური რემონტი" in text
    assert "ავარიული გათიშვა" in text
    assert "ნაწილობრივი შეზღუდვა" in text


if __name__ == "__main__":
    raise SystemExit(0 if not __import__("pytest").main([__file__]) else 1)
