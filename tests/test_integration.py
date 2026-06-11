import sys
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spots import get_spot
from forecast import lookup_tides, lookup_conditions


class IntegrationTest(unittest.TestCase):

    def test_get_spot_lakey_peak(self):

        spot = get_spot("lakey_peak")

        self.assertEqual(
            spot["spot_id"],
            "lakey_peak"
        )

    @unittest.skipIf(
        "WORLDTIDES_API_KEY" not in os.environ,
        "WORLDTIDES_API_KEY not configured"
    )
    def test_lookup_tides(self):

        try:
            tides = lookup_tides("lakey_peak")
        except Exception as e:
            self.skipTest(f"WorldTides unavailable: {e}")

        self.assertIn(
            "heights",
            tides
        )

        self.assertIn(
            "extremes",
            tides
        )

        self.assertIn(
            "timezone",
            tides
        )

        self.assertGreater(
            len(tides["heights"]),
            0
        )

    @unittest.skipIf(
        "WORLDTIDES_API_KEY" not in os.environ,
        "WORLDTIDES_API_KEY not configured"
    )
    def test_lookup_conditions(self):

        try:
            conditions = lookup_conditions("lakey_peak")
        except Exception as e:
            self.skipTest(f"WorldTides unavailable: {e}")

        self.assertIn(
            "spot",
            conditions
        )

        self.assertIn(
            "forecast_conditions",
            conditions
        )

        self.assertIn(
            "tide_extremes",
            conditions
        )

        self.assertGreater(
            len(
                conditions["forecast_conditions"]
            ),
            0
        )


if __name__ == "__main__":
    unittest.main()