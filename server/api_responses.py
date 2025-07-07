from typing import Literal, TypedDict, Any
from fastapi.responses import JSONResponse
from fastapi import status

HttpCode = Literal[200, 400, 405, 500]


class SuccessBody(TypedDict):
    total_portfolio_value: float
    currency: str
    message: str


class ErrorBody(TypedDict, total=False):
    total_portfolio_value: None
    currency: None
    message: str
    error: str


def _response(body: dict[str, Any], code: HttpCode) -> JSONResponse:
    return JSONResponse(content=body, status_code=code)


def response_wrong_method() -> JSONResponse:
    return _response(
        {
            "total_portfolio_value": None,
            "currency": None,
            "message": "Please send a POST request with your portfolio data.",
        },
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def response_invalid_request() -> JSONResponse:
    return _response(
        {
            "total_portfolio_value": None,
            "currency": None,
            "error": "Invalid request data. Please provide 'portfolio' and 'fiat_currency'.",
        },
        status.HTTP_400_BAD_REQUEST,
    )


def response_success(value: float, currency: str) -> JSONResponse:
    return _response(
        {"total_portfolio_value": value, "currency": currency, "message": ""},
        status.HTTP_200_OK,
    )


def response_value_error(err: ValueError) -> JSONResponse:
    return _response(
        {
            "total_portfolio_value": None,
            "currency": None,
            "message": str(err),
        },
        status.HTTP_400_BAD_REQUEST,
    )


def response_buda_api_error(err: Exception) -> JSONResponse:
    return _response(
        {
            "total_portfolio_value": None,
            "currency": None,
            "message": f"Error fetching data from Buda API: {err}",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )