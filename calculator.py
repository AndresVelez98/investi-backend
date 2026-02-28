"""
calculator.py — Financial projection calculator using yfinance historical data
"""
import yfinance as yf
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Friendly name mapping
ASSET_NAMES = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla Inc.",
    "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon.com Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.",
    "META": "Meta Platforms",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq 100 ETF",
    "GLD": "Gold ETF",
}


def calculate_projection(ticker: str, amount: float, months: int) -> dict:
    """
    Calculate projected return based on historical average monthly returns.

    Args:
        ticker: Stock/crypto ticker symbol (e.g. 'AAPL', 'BTC-USD')
        amount: Initial investment amount (min $10)
        months: Investment term in months (1–48)

    Returns:
        dict with projection or error key
    """
    ticker = ticker.upper().strip()

    try:
        stock = yf.Ticker(ticker)
        # Get 2 years of history to compute average returns
        hist = stock.history(period="2y")

        if hist.empty or len(hist) < 20:
            return {"error": f"No hay datos históricos suficientes para {ticker}"}

        # Calculate monthly returns from daily close prices
        hist.index = pd.to_datetime(hist.index)
        monthly_prices = hist["Close"].resample("ME").last()

        if len(monthly_prices) < 2:
            return {"error": f"Datos insuficientes para calcular retorno mensual de {ticker}"}

        monthly_returns = monthly_prices.pct_change().dropna()
        avg_monthly_return = float(monthly_returns.mean())
        data_period = f"{monthly_prices.index[0].strftime('%b %Y')} – {monthly_prices.index[-1].strftime('%b %Y')}"

        # Project forward month by month
        monthly_breakdown = []
        current_value = amount

        for m in range(1, months + 1):
            current_value = current_value * (1 + avg_monthly_return)
            gain = current_value - amount
            gain_pct = (gain / amount) * 100
            monthly_breakdown.append({
                "month": m,
                "value": round(current_value, 2),
                "gain": round(gain, 2),
                "gain_pct": round(gain_pct, 2),
            })

        final_value = monthly_breakdown[-1]["value"]
        total_gain = final_value - amount
        total_gain_pct = (total_gain / amount) * 100

        # Annualized return
        years = months / 12
        annualized_return = ((final_value / amount) ** (1 / years) - 1) * 100 if years > 0 else 0

        asset_name = ASSET_NAMES.get(ticker, ticker)

        return {
            "ticker": ticker,
            "asset_name": asset_name,
            "initial_amount": round(amount, 2),
            "final_value": round(final_value, 2),
            "total_gain": round(total_gain, 2),
            "total_gain_pct": round(total_gain_pct, 2),
            "annualized_return_pct": round(annualized_return, 2),
            "avg_monthly_return_pct": round(avg_monthly_return * 100, 4),
            "monthly_breakdown": monthly_breakdown,
            "data_period": data_period,
            "disclaimer": "Este cálculo es estimativo, basado en rendimientos históricos promedio. El rendimiento pasado no garantiza resultados futuros. No constituye asesoría financiera oficial."
        }

    except Exception as e:
        logger.error(f"Calculator error for {ticker}: {e}")
        return {"error": f"No se pudo calcular la proyección para {ticker}: {str(e)}"}
