"""
routers/chat.py — Chat endpoint
"""
import re as _re
from fastapi import APIRouter, Request
from slowapi import Limiter  # type: ignore
from slowapi.util import get_remote_address  # type: ignore

from schemas import ChatRequest
from market_data import get_market_data  # type: ignore
from ai_advisor import get_unified_analysis, extract_ticker_from_message  # type: ignore

router = APIRouter(tags=["Chat"])
limiter = Limiter(key_func=get_remote_address)

TRM_FALLBACK = 3588


def _detect_amount(message: str) -> dict | None:
    """Detect investment amounts in user messages for the calculator widget."""
    patterns = [
        (_re.compile(r'\$\s*(\d{1,3}(?:[.\s]\d{3})*|\d+)\s*(?:USD|usd|dólares?)', _re.IGNORECASE), "usd"),
        (_re.compile(r'(\d{1,3}(?:[.\s]\d{3})*|\d+)\s*(?:pesos?|COP|cop)', _re.IGNORECASE), "cop"),
        (_re.compile(r'\$\s*(\d{1,3}(?:[.\s]\d{3})*|\d+)', _re.IGNORECASE), "ambiguous"),
    ]
    for pattern, kind in patterns:
        m = pattern.search(message)
        if m:
            raw = m.group(1).replace(".", "").replace(" ", "")
            try:
                amount = float(raw)
                if kind == "usd" or (kind == "ambiguous" and amount < 5000):
                    return {"amount_cop": int(amount * TRM_FALLBACK), "amount_usd": round(amount, 2)}
                else:
                    if amount < 500:
                        amount *= 1000
                    return {"amount_cop": int(amount), "amount_usd": round(amount / TRM_FALLBACK, 2)}
            except ValueError:
                pass
    return None


@router.post("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, body: ChatRequest):
    ticker = extract_ticker_from_message(body.message)
    market_data = get_market_data(ticker) if ticker != "UNKNOWN" else None
    if market_data and "error" in market_data:
        market_data = None

    history = [{"role": m.role, "content": m.content} for m in body.history]

    ai_reply = get_unified_analysis(
        user_message=body.message,
        user_profile=body.profile,
        market_data=market_data,
        history=history,
    )

    return {
        "reply": ai_reply,
        "market_data": market_data,
        "detected_ticker": ticker,
        "calculator_data": _detect_amount(body.message),
    }
