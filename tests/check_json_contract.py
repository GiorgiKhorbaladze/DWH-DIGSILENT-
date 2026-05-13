from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "html" / "PowerSim_v4.html"


def _html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def _extract_state_assets(html: str) -> list[dict]:
    marker = "assets: ["
    start = html.index(marker) + len("assets: ")
    depth = 0
    end = start
    for end, char in enumerate(html[start:], start=start):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                end += 1
                break
    js_array = html[start:end]
    jsonish = re.sub(r"(\{|,|\s)([a-zA-Z_][a-zA-Z0-9_]*):", r'\1"\2":', js_array)
    jsonish = jsonish.replace("'", '"')
    jsonish = re.sub(r",\s*([\]}])", r"\1", jsonish)
    return json.loads(jsonish)


def test_profile_column_is_localized() -> None:
    html = _html()
    assert "პროფილი" in html
    assert "Profile" in html
    assert '<th data-i18n="profile">' in html


def test_only_required_asset_types_are_bindable() -> None:
    html = _html()
    assert 'new Set(["wind", "solar", "hydro_ror"])' in html
    for asset_type in ["hydro_reg", "thermal", "bess", "import"]:
        assert asset_type in html
    assert "notUsed" in html
    assert "არ გამოიყენება" in html
    assert "Not used" in html


def test_supported_profile_types_are_listed() -> None:
    html = _html()
    for profile_type in [
        "wind_generation_profile",
        "solar_generation_profile",
        "hydro_ror_availability_profile",
        "hydro_ror_inflow_profile",
    ]:
        assert profile_type in html


def test_registry_uses_reconciled_asset_ids_and_powersim_types() -> None:
    html = _html()
    assets = _extract_state_assets(html)
    bindable = {"wind", "solar", "hydro_ror"}
    non_bindable = {"hydro_reg", "thermal", "bess", "import"}
    assert {asset["powersim_type"] for asset in assets} == bindable | non_bindable
    assert all("asset_id" in asset for asset in assets)
    assert all("name" not in asset for asset in assets)
    assert all("profile_id" not in asset for asset in assets)


def test_latest_registry_total_is_displayed() -> None:
    html = _html()
    assets = _extract_state_assets(html)
    assert "REGISTRY_TOTAL_REFERENCE_MW = 4770.194" in html
    assert "installedCapacityTotal" in html
    assert round(sum(asset["installed_capacity_mw"] for asset in assets), 3) == 4770.194


def test_export_omits_profile_id_for_non_bindable_or_default_assets() -> None:
    html = _html()
    assert "assetType(exported)" in html
    assert "delete exported.profile_id" in html


def test_import_restores_selected_profile_and_keeps_old_json_compatible() -> None:
    html = _html()
    assert "normalizeImportedAsset" in html
    assert "parsed.assets.map(normalizeImportedAsset)" in html
    assert "normalizeRegistryAsset" in html
    assert "!normalized.profile_id" in html


def test_validation_rules_are_present() -> None:
    html = _html()
    assert "missingProfile" in html
    assert "shortProfile" in html
    assert "incompatibleProfile" in html
    assert "!isProfileBindableAsset(type)" in html


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("JSON contract checks passed")
