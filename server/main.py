from flask import Flask, request
from .utils import value_from_portfolio, BudaAPIError
from .api_responses import (
    response_wrong_method,
    response_invalid_request,
    response_success,
    response_value_error,
    response_buda_api_error,
)
from logging import getLogger

logger = getLogger(__name__)
app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])  # type: ignore
def get_portfolio_value():
    if request.method == "GET":
        return response_wrong_method()
    if request.method == "POST":
        request_data = request.json
        if (
            not request_data
            or "portfolio" not in request_data
            or "fiat_currency" not in request_data
        ):
            return response_invalid_request()
        try:
            value = value_from_portfolio(
                request_data["portfolio"], request_data["fiat_currency"]
            )
            response = response_success(value, request_data["fiat_currency"])
            logger.info(response)
            return response
        except ValueError as e:
            return response_value_error(e)
        except BudaAPIError as e:
            return response_buda_api_error(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
