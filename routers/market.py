"""
routers/market.py — Market data and TRM endpoints
"""
import logging
import yfinance as yf  # type: ignore
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter  # type: ignore
from slowapi.util import get_remote_address  # type: ignore

from market_data import get_market_data, get_top_assets, _get_yfinance_data, get_sparkline_data, get_asset_detail  # type: ignore
from core.cache import ttl_cache  # type: ignore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Market"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/api/trm")
@limiter.limit("30/minute")
def get_trm(request: Request):
    """Returns current USD/COP exchange rate (TRM) via yfinance."""
    return _get_trm_cached()


@ttl_cache(ttl=300)
def _get_trm_cached():
    try:
        ticker = yf.Ticker("USDCOP=X")
        rate = ticker.fast_info.last_price
        if rate and rate > 1000:
            return {"trm": round(rate, 0), "source": "yfinance"}
    except Exception as e:
        logger.warning(f"TRM fetch failed: {e}")
    return {"trm": 3588, "source": "fallback"}


@router.get("/api/market/top")
@limiter.limit("30/minute")
def market_top_assets(request: Request):
    """Returns current prices for curated list of top assets."""
    return {"assets": _get_top_assets_cached()}


@ttl_cache(ttl=60)
def _get_top_assets_cached():
    return get_top_assets()


@router.get("/api/market/search")
@limiter.limit("30/minute")
def market_search(request: Request, q: str = ""):
    """Search any ticker or keyword. Returns live price data."""
    if not q or len(q.strip()) < 1:
        return {"results": []}
    data = get_market_data(q.strip())
    if "error" in data:
        return {"results": []}
    return {"results": [data]}


@router.get("/api/market/{ticker}/sparkline")
@limiter.limit("30/minute")
def market_sparkline(request: Request, ticker: str):
    """Returns last 7 days of close prices for sparkline rendering."""
    return get_sparkline_data(ticker.upper())


@router.get("/api/market/{ticker}/detail")
@limiter.limit("30/minute")
def market_detail(request: Request, ticker: str):
    """Returns OHLCV, market cap, prev close and 7-day chart for a single asset."""
    data = get_asset_detail(ticker.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@router.get("/api/market/{ticker}")
@limiter.limit("30/minute")
def market_single_asset(request: Request, ticker: str):
    """Returns real-time data for a single ticker."""
    data = _get_yfinance_data(ticker.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
