import requests
from logging import getLogger

logger = getLogger(__name__)


class BudaAPIError(Exception):
    """Custom exception for Buda API errors."""

    pass


def get_markets() -> list[str]:
    """Fetches the list of markets from Buda API."""
    response = requests.get("https://www.buda.com/api/v2/markets")
    if response.status_code != 200:
        raise BudaAPIError(f"Error fetching markets: {response.status_code}")

    return [market["id"] for market in response.json()["markets"]]


def get_market_exchange_rate(market: str) -> float:
    """Fetches the exchange rate for a specific market."""
    if market not in get_markets():
        raise ValueError(f"Market {market} is not available.")

    response = requests.get(f"https://www.buda.com/api/v2/markets/{market}/ticker")
    if response.status_code != 200:
        raise BudaAPIError(
            f"Error fetching exchange rate for {market}: {response.status_code}"
        )

    raw_price: str = response.json()["ticker"]["last_price"][0]
    try:
        return float(raw_price)
    except BudaAPIError:
        raise BudaAPIError(
            f"Invalid price format for market {market}: {raw_price} from Buda API"
        )


def value_from_portfolio(portfolio: dict, fiat_currency: str) -> float:
    """Calculates the total value of the portfolio in the specified fiat currency."""
    all_markets = get_markets()
    total_value = 0.0

    for coin, amount in portfolio.items():
        market = f"{coin}-{fiat_currency}"
        if market in all_markets:
            coin_rate = get_market_exchange_rate(market)
            total_value += amount * coin_rate
            logger.debug(
                f"Value of {amount} {coin} in {fiat_currency}: {amount * coin_rate}"
            )
        else:
            logger.warning(f"Market {market} is not available.")
            raise ValueError(
                f"Market {market} is not available in the current portfolio."
            )
    logger.info(f"Total portfolio value in {fiat_currency}: {total_value}")
    return total_value
