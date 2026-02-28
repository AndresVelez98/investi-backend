from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from database import Base  # type: ignore
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=True)
    age = Column(Integer, nullable=True)
    monthly_income = Column(Float, nullable=True)
    password_hash = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profiles = relationship("Profile", back_populates="owner")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_profile = Column(String(20), nullable=False)  # Conservador | Moderado | Agresivo
    test_answers = Column(Text, nullable=True)         # JSON string of Q&A pairs
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="profiles")
