import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spots import get_all_spots, get_spot


class SpotsTest(unittest.TestCase):

    def test_all_spot_files_are_valid_json(self):

        for path in (ROOT / "data").glob("*.json"):

            with self.subTest(path=path.name):

                with open(path) as f:
                    json.load(f)

    def test_get_spot_lakey_peak(self):

        spot = get_spot(
            "lakey_peak"
        )

        self.assertEqual(
            spot["spot_id"],
            "lakey_peak"
        )

        self.assertEqual(
            spot["name"],
            "Lakey Peak"
        )

    def test_spot_has_preferred_conditions(self):

        for spot in get_all_spots():

            with self.subTest(
                spot=spot["spot_id"]
            ):

                self.assertIn(
                    "preferred_conditions",
                    spot
                )

                self.assertIn(
                    "swell",
                    spot["preferred_conditions"]
                )

                self.assertIn(
                    "wind",
                    spot["preferred_conditions"]
                )

                self.assertIn(
                    "tide",
                    spot["preferred_conditions"]
                )

    def test_find_spots_lakey_region(self):

        spots = [
            spot
            for spot in get_all_spots()
            if spot["region"] == "Lakey"
        ]

        self.assertGreater(
            len(spots),
            0
        )

        ids = [
            spot["spot_id"]
            for spot in spots
        ]

        self.assertIn(
            "lakey_peak",
            ids
        )


if __name__ == "__main__":
    unittest.main()