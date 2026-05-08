"""
routers/calculator.py — Financial calculator endpoint
"""
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter  # type: ignore
from slowapi.util import get_remote_address  # type: ignore

from schemas import CalculatorRequest  # type: ignore
from calculator import calculate_projection  # type: ignore
from core.cache import ttl_cache  # type: ignore

router = APIRouter(tags=["Calculator"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/api/calculate")
@limiter.limit("20/minute")
def calculate_endpoint(request: Request, body: CalculatorRequest):
    """Projects investment returns based on historical data."""
    result = _calculate_cached(body.ticker.upper(), body.amount, body.months)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result


@ttl_cache(ttl=3600)
def _calculate_cached(ticker: str, amount: float, months: int) -> dict:
    return calculate_projection(ticker=ticker, amount=amount, months=months)
