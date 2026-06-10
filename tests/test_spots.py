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
                json.loads(path.read_text())

    def test_spots_use_searchable_location_and_level_schema(self):
        for spot in get_all_spots():
            with self.subTest(spot=spot["spot_id"]):
                self.assertIsInstance(spot["country"], str)
                self.assertIsInstance(spot["island"], str)
                self.assertIsInstance(spot["region"], str)
                self.assertIsInstance(spot["surfer_level"], list)
                self.assertTrue(spot["surfer_level"])

    def test_get_spot_loads_by_id(self):
        spot = get_spot("lakey_peak")
        self.assertEqual(spot["spot_id"], "lakey_peak")


if __name__ == "__main__":
    unittest.main()
