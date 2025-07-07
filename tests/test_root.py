import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from server.main import app
from server.utils import BudaAPIError

client = TestClient(app)


class TestPortfolioAPI(unittest.TestCase):
    def setUp(self):
        self.valid_portfolio = {
            "portfolio": {"BTC": 0.5, "ETH": 2.0, "USDT": 1000},
            "fiat_currency": "CLP",
        }

    # 1 — Happy path
    @patch("server.utils.get_market_exchange_rate")
    @patch("server.utils.get_markets")
    def test_happy_path(self, mock_markets, mock_rate):
        mock_markets.return_value = ["BTC-CLP", "ETH-CLP", "USDT-CLP"]
        mock_rate.side_effect = lambda m: {"BTC-CLP": 1000, "ETH-CLP": 2000, "USDT-CLP": 3000}[m]

        resp = client.post("/", json=self.valid_portfolio)
        self.assertEqual(resp.status_code, 200)

        expected_value = 0.5 * 1000 + 2.0 * 2000 + 1000 * 3000
        body = resp.json()
        self.assertEqual(body["total_portfolio_value"], expected_value)
        self.assertEqual(body["currency"], "CLP")

    # 2 — Empty body
    def test_no_body(self):
        resp = client.post("/", json={})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid request data", resp.json()["error"])

    # 3 — Wrong structure
    def test_invalid_structure(self):
        bad = {"foo": "bar"}
        resp = client.post("/", json=bad)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid request data", resp.json()["error"])

    # 4 — Market not found
    @patch("server.utils.get_markets")
    def test_market_not_found(self, mock_markets):
        mock_markets.return_value = ["BTC-CLP", "ETH-CLP"]
        body = {"portfolio": {"DOGE": 123}, "fiat_currency": "USD"}

        resp = client.post("/", json=body)
        self.assertEqual(resp.status_code, 400)
        self.assertIsNone(resp.json()["total_portfolio_value"])

    # 5 — Upstream error
    @patch("server.utils.get_market_exchange_rate", side_effect=BudaAPIError("API down"))
    @patch("server.utils.get_markets", return_value=["BTC-CLP"])
    def test_buda_api_error(self, *_):
        resp = client.post("/", json=self.valid_portfolio)
        self.assertEqual(resp.status_code, 500)
        self.assertIn("Error fetching data from Buda API", resp.json()["message"])

    # Extra — GET not allowed
    def test_get_not_allowed(self):
        resp = client.get("/")
        self.assertEqual(resp.status_code, 405)
        self.assertIn("POST request", resp.json()["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)