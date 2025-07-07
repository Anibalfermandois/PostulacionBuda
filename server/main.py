from logging import basicConfig, INFO, getLogger
from fastapi import FastAPI, Body
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from .utils import value_from_portfolio, BudaAPIError
from .api_responses import (
    response_wrong_method,
    response_invalid_request,
    response_success,
    response_value_error,
    response_buda_api_error,
)

basicConfig(level=INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = getLogger(__name__)

app = FastAPI(title="Buda Portfolio API", version="1.0.0")


# ---------- Pydantic models ----------
class PortfolioRequest(BaseModel):
    portfolio: dict[str, float] = Field(..., description="Coin => amount mapping")
    fiat_currency: str = Field(..., min_length=2, max_length=5, description="Target fiat currency")


# ---------- Custom validation → keep 400 & custom body ----------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, __):
    return response_invalid_request()


# ---------- Endpoints ----------
@app.get("/", include_in_schema=False)
async def wrong_method():
    # Explicit 405 with old message-body
    return response_wrong_method()


@app.post("/", response_model=None)  # we already format body ourselves
async def get_portfolio_value(request_data: PortfolioRequest = Body(...)):
    try:
        value = value_from_portfolio(
            request_data.portfolio, request_data.fiat_currency
        )
        resp = response_success(value, request_data.fiat_currency)
        logger.info(resp.body.decode())
        return resp
    except ValueError as exc:
        return response_value_error(exc)
    except BudaAPIError as exc:
        return response_buda_api_error(exc)


# ---------- CLI ENTRY ----------
if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("server.main:app", host="0.0.0.0", port=5001, reload=False)