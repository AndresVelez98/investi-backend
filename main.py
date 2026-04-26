"""
main.py — FastAPI application for Investi AI Backend
Endpoints: Chat, Market Data, Financial Calculator, Risk Test, User Management, Education
"""
from fastapi import FastAPI, HTTPException, Depends  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
import os
import json
import logging
from dotenv import load_dotenv  # type: ignore

from database import get_db, init_db  # type: ignore
from models import User, Profile  # type: ignore
from schemas import (  # type: ignore
    UserCreate, UserResponse,
    ProfileCreate, ProfileResponse,
    ChatRequest,
    CalculatorRequest, CalculatorResponse,
    RiskTestEvaluateRequest, RiskTestEvaluateResponse,
)
import re as _re

def _detect_amount(message: str) -> Optional[dict]:
    """Detect investment amounts in user messages for the calculator widget."""
    # Patterns: $100.000 COP, $25 USD, 200000 pesos, 100k
    patterns = [
        (r'\$\s*(\d{1,3}(?:[.\s]\d{3})*|\d+)\s*(?:USD|usd|dólares?)', "usd"),
        (r'(\d{1,3}(?:[.\s]\d{3})*|\d+)\s*(?:pesos?|COP|cop)', "cop"),
        (r'\$\s*(\d{1,3}(?:[.\s]\d{3})*|\d+)', "ambiguous"),
    ]
    for pattern, kind in patterns:
        m = _re.search(pattern, message, _re.IGNORECASE)
        if m:
            raw = m.group(1).replace(".", "").replace(" ", "")
            try:
                amount = float(raw)
                if kind == "usd" or (kind == "ambiguous" and amount < 5000):
                    return {"amount_cop": int(amount * 4200), "amount_usd": round(amount, 2)}
                else:
                    if amount < 500:
                        amount *= 1000  # treat as thousands
                    return {"amount_cop": int(amount), "amount_usd": round(amount / 4200, 2)}
            except ValueError:
                pass
    return None
from market_data import get_market_data, get_top_assets, _get_yfinance_data, get_sparkline_data, get_asset_detail  # type: ignore
from ai_advisor import get_unified_analysis, extract_ticker_from_message, evaluate_risk_profile, get_risk_question  # type: ignore
from calculator import calculate_projection
from router_auth import router as auth_router  # type: ignore
from router_education import router as education_router  # type: ignore

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Investi AI Backend", version="3.0.0")
app.include_router(auth_router)
app.include_router(education_router)

# ─── CORS ───────────────────────────────────────────────────────────────────────

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://investi-frontend-teal.vercel.app",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ─────────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database...")
    init_db()

    # Seed education data if tables are empty
    from models_education import EducationModule
    db = next(get_db())
    try:
        module_count = db.query(EducationModule).count()
        if module_count == 0:
            logger.info("Seeding education data...")
            from seed_lessons import seed_education_data
            seed_education_data(db)
            logger.info("Education data seeded successfully!")
        else:
            logger.info(f"Education data already exists ({module_count} modules).")
    finally:
        db.close()

    logger.info("Database ready.")


# ─── Health Check ────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"status": "Investi AI Backend is Running", "version": "3.0.0"}


# ─── Chat Endpoint ────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    ticker = extract_ticker_from_message(request.message)
    market_data = get_market_data(ticker) if ticker != "UNKNOWN" else None
    if market_data and "error" in market_data:
        market_data = None

    history = [{"role": m.role, "content": m.content} for m in request.history]

    ai_reply = get_unified_analysis(
        user_message=request.message,
        user_profile=request.profile,
        market_data=market_data,
        history=history,
    )

    calculator_data = _detect_amount(request.message)

    return {
        "reply": ai_reply,
        "market_data": market_data,
        "detected_ticker": ticker,
        "calculator_data": calculator_data,
    }


# ─── TRM Endpoint ────────────────────────────────────────────────────────────────

@app.get("/api/trm")
def get_trm():
    """Returns current USD/COP exchange rate (TRM) via yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker("USDCOP=X")
        rate = ticker.fast_info.last_price
        if rate and rate > 1000:
            return {"trm": round(rate, 0), "source": "yfinance"}
    except Exception as e:
        logger.warning(f"TRM fetch failed: {e}")
    return {"trm": 3588, "source": "fallback"}


# ─── Market Data Endpoints ────────────────────────────────────────────────────────

@app.get("/api/market/top")
def market_top_assets():
    """Returns current prices for curated list of top assets (dashboard + markets hub)."""
    assets = get_top_assets()
    return {"assets": assets}


@app.get("/api/market/search")
def market_search(q: str = ""):
    """Search any ticker or keyword. Returns live price data."""
    if not q or len(q.strip()) < 1:
        return {"results": []}
    data = get_market_data(q.strip())
    if "error" in data:
        return {"results": []}
    return {"results": [data]}


@app.get("/api/market/{ticker}/sparkline")
def market_sparkline(ticker: str):
    """Returns last 7 days of close prices for sparkline rendering."""
    return get_sparkline_data(ticker.upper())


@app.get("/api/market/{ticker}/detail")
def market_detail(ticker: str):
    """Returns OHLCV, market cap, prev close and 7-day chart for a single asset."""
    data = get_asset_detail(ticker.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/api/market/{ticker}")
def market_single_asset(ticker: str):
    """Returns real-time data for a single ticker."""
    data = _get_yfinance_data(ticker.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


# ─── Financial Calculator ─────────────────────────────────────────────────────────

@app.post("/api/calculate")
def calculate_endpoint(request: CalculatorRequest):
    """Projects investment returns based on historical data."""
    result = calculate_projection(
        ticker=request.ticker,
        amount=request.amount,
        months=request.months,
    )
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result


# ─── Risk Test Endpoints ──────────────────────────────────────────────────────────

@app.get("/api/risk-test/question/{number}")
def get_question(number: int):
    """Returns a risk test question by number (1–5)."""
    if not (1 <= number <= 5):
        raise HTTPException(status_code=400, detail="Question number must be between 1 and 5")
    question = get_risk_question(number - 1)
    return {"question_number": number, "total_questions": 5, "question": question}


@app.post("/api/risk-test/evaluate")
def evaluate_risk_test(request: RiskTestEvaluateRequest):
    """Evaluates 5 answers and returns the user's risk profile."""
    if len(request.answers) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Se necesitan 5 respuestas, se recibieron {len(request.answers)}"
        )
    result = evaluate_risk_profile(request.answers, request.user_name)
    return result


# ─── User Management ──────────────────────────────────────────────────────────────

@app.post("/api/users", response_model=UserResponse, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user record."""
    if user_data.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Este email ya está registrado")

    db_user = User(
        name=user_data.name,
        email=user_data.email,
        age=user_data.age,
        monthly_income=user_data.monthly_income,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Gets a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ─── Profile Management ───────────────────────────────────────────────────────────

@app.post("/api/profiles", response_model=ProfileResponse, status_code=201)
def create_profile(profile_data: ProfileCreate, db: Session = Depends(get_db)):
    """Saves a user's risk profile result."""
    user = db.query(User).filter(User.id == profile_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_profile = Profile(
        user_id=profile_data.user_id,
        risk_profile=profile_data.risk_profile,
        test_answers=profile_data.test_answers,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@app.get("/api/profiles/{user_id}", response_model=ProfileResponse)
def get_latest_profile(user_id: int, db: Session = Depends(get_db)):
    """Gets the latest risk profile for a user."""
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user_id)
        .order_by(Profile.created_at.desc())
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile
