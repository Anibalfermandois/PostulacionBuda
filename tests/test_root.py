import unittest
from unittest.mock import patch
from server.main import app
from server.utils import BudaAPIError

import json


class TestPortfolioAPI(unittest.TestCase):

    def setUp(self):
        """Set up test client and common test data."""
        self.app = app
        self.client = self.app.test_client()

        # Common test data
        self.valid_portfolio = {
            "portfolio": {"BTC": 0.5, "ETH": 2.0, "USDT": 1000},
            "fiat_currency": "CLP",
        }

    @patch("server.utils.get_market_exchange_rate")
    @patch("server.utils.get_markets")
    def test_happy_path_successful_portfolio_calculation(
        self, mock_get_markets, mock_get_exchange_rate
    ):
        """Test 1: Happy path - successful portfolio value calculation."""
        # Mock external API responses
        mock_get_markets.return_value = ["BTC-CLP", "ETH-CLP", "USDT-CLP"]
        mock_get_exchange_rate.side_effect = lambda market: {
            "BTC-CLP": 1000,
            "ETH-CLP": 2000,
            "USDT-CLP": 3000,
        }[market]

        response = self.client.post(
            "/", data=json.dumps(self.valid_portfolio), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Expected: 1.5 * 50M + 10 * 2.5M = 75M + 25M = 100M CLP
        expected_value = 0.5 * 1000 + 2.0 * 2000 + 1000 * 3000
        self.assertEqual(data["total_portfolio_value"], expected_value)
        self.assertEqual(data["currency"], "CLP")

        # Verify external APIs were called correctly
        mock_get_markets.assert_called()
        self.assertEqual(
            mock_get_exchange_rate.call_count, len(self.valid_portfolio["portfolio"])
        )

    def test_no_body_request(self):
        """Test 2: Request with empty json should return 400."""
        response = self.client.post(
            "/", content_type="application/json", data=json.dumps({})
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)

        self.assertIsNone(data["total_portfolio_value"])
        self.assertIsNone(data["currency"])
        self.assertIn("Invalid request data", data["error"])

    def test_invalid_body_structure(self):
        """Test 3: Body with incorrect structure should return 400."""
        invalid_request = [
            {"portfolio": {"btc": 1.0}},  # Missing fiat_currency
            {"fiat_currency": "usd"},  # Missing portfolio
            {"wrong_field": "value"},  # Completely wrong structure
            {},  # Empty object
        ]

        response = self.client.post(
            "/", data=json.dumps(invalid_request), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Invalid request data", data["error"])

    @patch("server.utils.get_markets")
    def test_coin_market_not_found(self, mock_get_markets):
        """Test 4: Market not available should return 400 with error message."""
        # Mock markets without the requested coin-fiat pair
        mock_get_markets.return_value = ["BTC-CLP", "ETC-CLP"]  # No DOGE-USD market

        unavailable_market_portfolio = {
            "portfolio": {"doge": 1000.0},  # DOGE-USD market not available
            "fiat_currency": "USD",
        }

        response = self.client.post(
            "/",
            data=json.dumps(unavailable_market_portfolio),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)

        self.assertIsNone(data["total_portfolio_value"])
        self.assertIsNone(data["currency"])
        self.assertIsNotNone(data["message"])

    def test_get_method_not_allowed(self):
        """Test that GET method returns 405 Method Not Allowed."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 405)
        data = json.loads(response.data)
        self.assertIn("POST request", data["message"])

    @patch("server.utils.get_market_exchange_rate")
    @patch("server.utils.get_markets")
    def test_buda_api_error_handling(self, mock_get_markets, mock_get_exchange_rate):
        """Test handling of Buda API errors."""
        mock_get_markets.return_value = ["BTC-CLP"]
        mock_get_exchange_rate.side_effect = BudaAPIError("API connection failed")

        response = self.client.post(
            "/", data=json.dumps(self.valid_portfolio), content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)

        self.assertIsNone(data["total_portfolio_value"])
        self.assertIn("Error fetching data from Buda API", data["message"])


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
