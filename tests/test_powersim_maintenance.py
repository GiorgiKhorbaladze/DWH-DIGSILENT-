from __future__ import annotations

import unittest

from solver.powersim_solver import _maint_factor, get_pmax_t


class MaintenanceScheduleTests(unittest.TestCase):
    def test_no_maintenance_leaves_pmax_unchanged(self) -> None:
        asset = {"type": "thermal", "pmax": 100.0}

        self.assertEqual(get_pmax_t(asset, 5, {}), 100.0)
        self.assertEqual(_maint_factor(asset, 5), 1.0)

    def test_full_outage_sets_pmax_to_zero_inside_window(self) -> None:
        asset = {
            "type": "hydro_reg",
            "pmax": 80.0,
            "maint_windows": [
                {"start_hour": 100, "end_hour": 120, "availability_factor": 0.0}
            ],
        }

        self.assertEqual(get_pmax_t(asset, 100, {}), 0.0)
        self.assertEqual(get_pmax_t(asset, 119, {}), 0.0)
        self.assertEqual(get_pmax_t(asset, 120, {}), 80.0)

    def test_partial_derating_multiplies_pmax_by_factor(self) -> None:
        asset = {
            "type": "import",
            "pmax_profile": "import_cap",
            "maint_windows": [
                {"start_hour": 10, "end_hour": 12, "availability_factor": 0.4}
            ],
        }

        self.assertEqual(get_pmax_t(asset, 10, {"import_cap": [50.0] * 24}), 20.0)

    def test_rolling_horizon_offset_uses_global_hour(self) -> None:
        asset = {
            "type": "thermal",
            "pmax": 30.0,
            "maint_windows": [
                {"start_hour": 100, "end_hour": 120, "availability_factor": 0.0}
            ],
        }

        self.assertEqual(get_pmax_t(asset, 3, {}, offset_h=96), 30.0)
        self.assertEqual(get_pmax_t(asset, 4, {}, offset_h=96), 0.0)

    def test_wind_and_solar_cf_combine_with_maintenance_factor(self) -> None:
        maint_windows = [
            {"start_hour": 7, "end_hour": 8, "availability_factor": 0.5}
        ]
        wind = {
            "type": "wind",
            "pmax_installed": 100.0,
            "availability_profile": "wind_cf",
            "maint_windows": maint_windows,
        }
        solar = {
            "type": "solar",
            "pmax_installed": 40.0,
            "availability_profile": "solar_cf",
            "maint_windows": maint_windows,
        }

        self.assertEqual(get_pmax_t(wind, 0, {"wind_cf": [0.2]}, offset_h=7), 10.0)
        self.assertEqual(get_pmax_t(solar, 0, {"solar_cf": [0.75]}, offset_h=7), 15.0)


if __name__ == "__main__":
    unittest.main()
