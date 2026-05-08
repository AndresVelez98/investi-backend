"""
router_auth.py — Register & Login endpoints for Investi
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from database import get_db
from models import User
from auth import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import RiskProfile  # type: ignore
from core.limiter import limiter  # type: ignore

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ─── Schemas locales ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    age: Optional[int] = Field(None, ge=18, le=100)
    monthly_income: Optional[float] = Field(None, ge=0)
    risk_profile: Optional[RiskProfile] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str
    risk_profile: Optional[RiskProfile] = None

# ─── Register ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    """Creates a new user with hashed password and returns a JWT token."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Este email ya está registrado")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        age=data.age,
        monthly_income=data.monthly_income,
        risk_profile=data.risk_profile,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "name": user.name, "risk_profile": user.risk_profile}

# ─── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates user and returns a JWT token."""
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not user.password_hash or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "name": user.name, "risk_profile": user.risk_profile}
