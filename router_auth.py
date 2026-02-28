"""
router_auth.py — Register & Login endpoints for Investi
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from database import get_db
from models import User
from auth import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ─── Schemas locales ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int | None = None
    monthly_income: float | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str

# ─── Register ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
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
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "name": user.name}

# ─── Login ────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates user and returns a JWT token."""
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not user.password_hash or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "name": user.name}
