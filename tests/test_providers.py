import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from providers.http import DEFAULT_HEADERS, DEFAULT_TIMEOUT, get_json
from providers.open_meteo import get_marine_forecast


class ProvidersTest(unittest.TestCase):

    @patch("providers.http.requests.get")
    def test_get_json_uses_short_timeout_and_headers(self, mock_get):

        response = Mock()
        response.json.return_value = {"ok": True}
        mock_get.return_value = response

        result = get_json(
            "https://example.test/api",
            params={"foo": "bar"}
        )

        self.assertEqual(
            result,
            {"ok": True}
        )

        mock_get.assert_called_once_with(
            "https://example.test/api",
            params={"foo": "bar"},
            headers=DEFAULT_HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )

        response.raise_for_status.assert_called_once()

    @patch("providers.open_meteo.get_json")
    def test_open_meteo_provider_uses_shared_http_helper(self, mock_get_json):

        mock_get_json.return_value = {"hourly": {}}

        result = get_marine_forecast(
            -8.810277778,
            118.3825
        )

        self.assertEqual(
            result,
            {"hourly": {}}
        )

        called_url = mock_get_json.call_args.args[0]

        self.assertIn(
            "marine-api.open-meteo.com",
            called_url
        )

        self.assertIn(
            "timezone=auto",
            called_url
        )


if __name__ == "__main__":
    unittest.main()
