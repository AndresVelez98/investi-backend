"""
market_data.py — Real-time market data using yfinance (reliable, no scraping)
"""
import yfinance as yf
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Curated list of top assets for the dashboard
TOP_ASSETS = [
    {"ticker": "AAPL",    "name": "Apple",         "category": "Acciones"},
    {"ticker": "TSLA",    "name": "Tesla",          "category": "Acciones"},
    {"ticker": "GOOGL",   "name": "Google",         "category": "Acciones"},
    {"ticker": "MSFT",    "name": "Microsoft",      "category": "Acciones"},
    {"ticker": "NVDA",    "name": "NVIDIA",         "category": "Acciones"},
    {"ticker": "AMZN",    "name": "Amazon",         "category": "Acciones"},
    {"ticker": "BTC-USD", "name": "Bitcoin",        "category": "Cripto"},
    {"ticker": "ETH-USD", "name": "Ethereum",       "category": "Cripto"},
    {"ticker": "SPY",     "name": "S&P 500 ETF",    "category": "ETFs"},
]

# Keyword → Ticker mapping for natural language extraction
KEYWORD_TO_TICKER = {
    # Companies
    "apple": "AAPL", "aapl": "AAPL",
    "tesla": "TSLA", "tsla": "TSLA",
    "google": "GOOGL", "alphabet": "GOOGL", "googl": "GOOGL",
    "microsoft": "MSFT", "msft": "MSFT",
    "amazon": "AMZN", "amzn": "AMZN",
    "nvidia": "NVDA", "nvda": "NVDA",
    "meta": "META", "facebook": "META",
    "netflix": "NFLX", "nflx": "NFLX",
    "uber": "UBER",
    "airbnb": "ABNB",
    "disney": "DIS",
    "samsung": "005930.KS",
    # Crypto
    "bitcoin": "BTC-USD", "btc": "BTC-USD",
    "ethereum": "ETH-USD", "eth": "ETH-USD",
    "solana": "SOL-USD", "sol": "SOL-USD",
    "cardano": "ADA-USD", "ada": "ADA-USD",
    "dogecoin": "DOGE-USD", "doge": "DOGE-USD",
    "ripple": "XRP-USD", "xrp": "XRP-USD",
    # ETFs / Indices
    "sp500": "SPY", "spy": "SPY", "s&p": "SPY",
    "nasdaq": "QQQ", "qqq": "QQQ",
    "oro": "GLD", "gold": "GLD", "gld": "GLD",
}


def get_market_data(query: str) -> dict:
    """
    Get market data for a query string (ticker or company name).
    Uses keyword mapping first, then direct yfinance lookup.
    """
    if not query or query == "UNKNOWN":
        return {"error": "No se identificó un activo válido en tu mensaje"}

    # Resolve ticker from keyword map or use query directly
    ticker = KEYWORD_TO_TICKER.get(query.lower(), query.upper())
    logger.info(f"Fetching market data: query='{query}' → ticker='{ticker}'")

    return _get_yfinance_data(ticker)


def get_top_assets() -> list:
    """
    Returns current prices for the curated list of top assets.
    Uses yfinance batch download for efficiency.
    """
    results = []
    tickers_list = [a["ticker"] for a in TOP_ASSETS]

    try:
        # Batch download last 2 days of data
        data = yf.download(tickers_list, period="2d", progress=False, group_by="ticker")

        for asset in TOP_ASSETS:
            ticker = asset["ticker"]
            try:
                if len(tickers_list) > 1:
                    ticker_data = data[ticker]["Close"]
                else:
                    ticker_data = data["Close"]

                ticker_data = ticker_data.dropna()
                if len(ticker_data) < 1:
                    continue

                price = float(ticker_data.iloc[-1])
                prev_price = float(ticker_data.iloc[-2]) if len(ticker_data) >= 2 else price
                change = price - prev_price
                change_pct = (change / prev_price) * 100 if prev_price != 0 else 0

                results.append({
                    "ticker": ticker,
                    "name": asset["name"],
                    "category": asset["category"],
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "currency": "USD",
                })
            except Exception as e:
                logger.warning(f"Could not get price for {ticker}: {e}")
                continue

    except Exception as e:
        logger.error(f"Batch download failed: {e}")
        # Fallback: individual requests
        for asset in TOP_ASSETS:
            item = _get_yfinance_data(asset["ticker"])
            if item and "error" not in item:
                item["category"] = asset["category"]
                results.append(item)

    return results


def _get_yfinance_data(ticker_symbol: str) -> dict:
    """
    Fetch data for a single ticker using yfinance.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="2d")

        if hist.empty:
            return {"error": f"No se encontraron datos para '{ticker_symbol}'"}

        hist = hist.dropna(subset=["Close"])
        if len(hist) < 1:
            return {"error": f"No hay datos de cierre para '{ticker_symbol}'"}

        price = float(hist["Close"].iloc[-1])
        prev_price = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
        change = price - prev_price
        change_pct = (change / prev_price) * 100 if prev_price != 0 else 0

        # Try to get a friendly name from info
        try:
            info = ticker.info
            name = info.get("longName") or info.get("shortName") or ticker_symbol.upper()
        except Exception:
            name = ticker_symbol.upper()

        return {
            "source": "yfinance",
            "ticker": ticker_symbol.upper(),
            "name": name,
            "price": f"{price:,.2f}",
            "change": f"{change:+.2f}",
            "change_percent": f"{change_pct:+.2f}%",
            "currency": "USD",
        }

    except Exception as e:
        logger.error(f"yfinance error for {ticker_symbol}: {e}")
        return {"error": f"No se pudo obtener datos para '{ticker_symbol}'"}
