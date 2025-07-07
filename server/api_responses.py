from flask import jsonify, Response
from .utils import BudaAPIError
from typing import Literal

type FlaskResponse = tuple[Response, Literal[200, 400, 405, 500]]


def response_wrong_method() -> FlaskResponse:
    return (
        jsonify(
            {
                "total_portfolio_value": None,
                "currency": None,
                "message": "Please send a POST request with your portfolio data.",
            }
        ),
        405,
    )


def response_invalid_request() -> FlaskResponse:
    return (
        jsonify(
            {
                "total_portfolio_value": None,
                "currency": None,
                "error": "Invalid request data. Please provide 'portfolio' and 'fiat_currency'.",
            }
        ),
        400,
    )


def response_success(value, currency) -> FlaskResponse:
    return (
        jsonify({"total_portfolio_value": value, "currency": currency, "message": ""}),
        200,
    )


def response_value_error(e: ValueError) -> FlaskResponse:
    return (
        jsonify({"total_portfolio_value": None, "currency": None, "message": str(e)}),
        400,
    )


def response_buda_api_error(e: BudaAPIError) -> FlaskResponse:
    return (
        jsonify(
            {
                "total_portfolio_value": None,
                "currency": None,
                "message": f"Error fetching data from Buda API: {str(e)}",
            }
        ),
        500,
    )
