from pydantic import BaseModel, Field  # type: ignore
from typing import Optional, List, Literal
from datetime import datetime

# Defined first — used by multiple schemas below
RiskProfile = Literal["Conservador", "Moderado", "Agresivo"]


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
    risk_profile: Optional[RiskProfile]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Profile Schemas ────────────────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    risk_profile: RiskProfile
    test_answers: Optional[str] = None  # JSON string


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    risk_profile: RiskProfile
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ───────────────────────────────────────────────────────────────

class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    profile: RiskProfile = "Moderado"
    history: List[ChatHistoryMessage] = Field(default=[], max_length=50)


# ─── Calculator Schemas ─────────────────────────────────────────────────────────

class CalculatorRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9.\-=^]+$")
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
    answers: List[str] = Field(..., min_length=5, max_length=5)  # exactly 5 answers
    user_name: Optional[str] = Field(None, max_length=100)


class RiskTestEvaluateResponse(BaseModel):
    profile: RiskProfile
    explanation: str
    recommendations: str
