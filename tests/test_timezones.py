import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from forecast import to_local_time
import forecast


class TimezoneTest(unittest.TestCase):

    def test_to_local_time_converts_zulu_time_to_spot_time(self):

        times = to_local_time(
            "2026-06-12T03:00:00Z",
            "Asia/Makassar"
        )

        self.assertEqual(
            times["time_utc"],
            "2026-06-12T03:00:00+00:00"
        )

        self.assertEqual(
            times["time_local"],
            "2026-06-12T11:00:00+08:00"
        )

        self.assertEqual(
            times["local_hour"],
            "11:00"
        )

    def test_lookup_conditions_returns_local_times(self):

        original_lookup_forecast = forecast.lookup_forecast
        original_lookup_tides = forecast.lookup_tides

        try:
            forecast.lookup_forecast = lambda spot_id, provider: [
                {
                    "time": "2026-06-12T03:00:00Z",
                    "wave_height_ft": 4.2,
                    "wave_period_s": 12.0,
                    "swell_direction": "SW",
                    "swell_direction_deg": 225
                }
            ]

            forecast.lookup_tides = lambda spot_id: {
                "timezone": "Asia/Makassar",
                "datum": "LAT",
                "heights": [
                    {
                        "time": "2026-06-12T11:00:00+08:00",
                        "tide_height_ft": 2.1,
                        "tide_state": "mid"
                    }
                ],
                "extremes": [
                    {
                        "time": "2026-06-12T07:02:00+08:00",
                        "type": "high",
                        "height_ft": 5.0
                    }
                ]
            }

            conditions = forecast.lookup_conditions(
                "lakey_peak"
            )

        finally:
            forecast.lookup_forecast = original_lookup_forecast
            forecast.lookup_tides = original_lookup_tides

        forecast_item = conditions["forecast_conditions"][0]
        tide_extreme = conditions["tide_extremes"][0]

        self.assertEqual(
            conditions["timezone"],
            "Asia/Makassar"
        )

        self.assertEqual(
            forecast_item["time_utc"],
            "2026-06-12T03:00:00+00:00"
        )

        self.assertEqual(
            forecast_item["time_local"],
            "2026-06-12T11:00:00+08:00"
        )

        self.assertEqual(
            forecast_item["local_hour"],
            "11:00"
        )

        self.assertNotIn(
            "time",
            forecast_item
        )

        self.assertEqual(
            tide_extreme["time_utc"],
            "2026-06-11T23:02:00+00:00"
        )

        self.assertEqual(
            tide_extreme["time_local"],
            "2026-06-12T07:02:00+08:00"
        )


if __name__ == "__main__":
    unittest.main()
