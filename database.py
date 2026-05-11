from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import unquote
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_raw = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'investi.db')}")

if _raw.startswith("postgres://"):
    _raw = _raw.replace("postgres://", "postgresql://", 1)

if _raw.startswith("postgresql://"):
    # urlparse breaks on passwords that contain [ or ] (treats them as IPv6).
    # Parse manually: split on the last @ to separate credentials from host info.
    body = _raw[len("postgresql://"):]
    at = body.rfind("@")
    credentials, hostinfo = body[:at], body[at + 1:]
    colon = credentials.index(":")
    _user = credentials[:colon]
    _password = unquote(credentials[colon + 1:])  # decode %2B → + etc.
    # hostinfo is "host:port/dbname"
    host_port, _dbname = hostinfo.rsplit("/", 1)
    _host, _port = host_port.rsplit(":", 1)
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg2",
        username=_user,
        password=_password,
        host=_host,
        port=int(_port),
        database=_dbname,
    )
    connect_args = {}
else:
    DATABASE_URL = _raw
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency injector for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables on startup."""
    from models import User, Profile  # noqa: F401
    from models_education import (  # noqa: F401
        EducationModule, Lesson, QuizQuestion,
        UserLessonProgress, Achievement, UserAchievement,
    )
    Base.metadata.create_all(bind=engine)
    