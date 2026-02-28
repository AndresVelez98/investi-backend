"""
main.py — FastAPI application for Investi AI Backend
Endpoints: Chat, Market Data, Financial Calculator, Risk Test, User Management
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
from market_data import get_market_data, get_top_assets, _get_yfinance_data  # type: ignore
from ai_advisor import get_unified_analysis, extract_ticker_from_message, evaluate_risk_profile, get_risk_question  # type: ignore
from calculator import calculate_projection
from router_auth import router as auth_router  # type: ignore

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Investi AI Backend", version="2.0.0")
app.include_router(auth_router)

# ─── CORS ───────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ─────────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database ready.")


# ─── Health Check ────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"status": "Investi AI Backend is Running", "version": "2.0.0"}


# ─── Chat Endpoint ────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    ticker = extract_ticker_from_message(request.message)
    market_data = get_market_data(ticker) if ticker != "UNKNOWN" else None
    if market_data and "error" in market_data:
        market_data = None

    ai_reply = get_unified_analysis(
        user_message=request.message,
        user_profile=request.profile,
        market_data=market_data
    )

    return {
        "reply": ai_reply,
        "market_data": market_data,
        "detected_ticker": ticker,
    }


# ─── Market Data Endpoints ────────────────────────────────────────────────────────

@app.get("/api/market/top")
def market_top_assets():
    """Returns current prices for curated list of top assets (dashboard use)."""
    assets = get_top_assets()
    return {"assets": assets}


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
