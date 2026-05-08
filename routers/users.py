"""
routers/users.py — Authenticated user & profile management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db  # type: ignore
from models import User, Profile  # type: ignore
from schemas import ProfileCreate, ProfileResponse, UserResponse  # type: ignore
from auth import get_current_user  # type: ignore

router = APIRouter(tags=["Users"])


@router.get("/api/users/me", response_model=UserResponse)
def get_me_user(current_user: User = Depends(get_current_user)):
    """Returns the current authenticated user."""
    return current_user


@router.post("/api/profiles", response_model=ProfileResponse, status_code=201)
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Saves the authenticated user's risk profile result."""
    # Always use the token's user_id — never trust the body's user_id
    db_profile = Profile(
        user_id=current_user.id,
        risk_profile=profile_data.risk_profile,
        test_answers=profile_data.test_answers,
    )
    db.add(db_profile)

    # Denormalize onto User for quick access
    current_user.risk_profile = profile_data.risk_profile
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/api/profiles/me", response_model=ProfileResponse)
def get_latest_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets the latest risk profile for the authenticated user."""
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .order_by(Profile.created_at.desc())
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile
