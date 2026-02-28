from pydantic import BaseModel, Field  # type: ignore
from typing import Optional, List
from datetime import datetime


# ─── User Schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    monthly_income: Optional[float] = Field(None, ge=0)


class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    age: Optional[int]
    monthly_income: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Profile Schemas ────────────────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    user_id: int
    risk_profile: str  # Conservador | Moderado | Agresivo
    test_answers: Optional[str] = None  # JSON string


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    risk_profile: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ───────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    profile: str = "Moderado"


# ─── Calculator Schemas ─────────────────────────────────────────────────────────

class CalculatorRequest(BaseModel):
    ticker: str
    amount: float = Field(..., ge=10, description="Minimum investment $10")
    months: int = Field(..., ge=1, le=48, description="Investment term 1–48 months")


class MonthlyProjection(BaseModel):
    month: int
    value: float
    gain: float
    gain_pct: float


class CalculatorResponse(BaseModel):
    ticker: str
    asset_name: str
    initial_amount: float
    final_value: float
    total_gain: float
    total_gain_pct: float
    annualized_return_pct: float
    avg_monthly_return_pct: float
    monthly_breakdown: List[MonthlyProjection]
    data_period: str
    disclaimer: str


# ─── Risk Test Schemas ──────────────────────────────────────────────────────────

class RiskTestEvaluateRequest(BaseModel):
    answers: List[str]  # 5 answers to the risk questions
    user_name: Optional[str] = None


class RiskTestEvaluateResponse(BaseModel):
    profile: str           # Conservador | Moderado | Agresivo
    explanation: str
    recommendations: str
