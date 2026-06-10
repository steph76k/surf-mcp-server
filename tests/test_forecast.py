import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from forecast import get_forecast
from spots import get_spot


class ForecastTest(unittest.TestCase):
    def test_open_meteo_forecast_shape(self):
        forecast = get_forecast(get_spot("lakey_peak"))

        self.assertEqual(forecast["provider"], "open_meteo")
        self.assertEqual(forecast["spot_id"], "lakey_peak")
        self.assertIn("wave_height_ft", forecast)
        self.assertIn("period_s", forecast)
        self.assertIn("wind_kts", forecast)


if __name__ == "__main__":
    unittest.main()
