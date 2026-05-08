"""
main.py — FastAPI application entry point for Investi AI Backend
"""
import logging
import os

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore
from slowapi.util import get_remote_address  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore
from dotenv import load_dotenv  # type: ignore

from database import get_db, init_db  # type: ignore
from router_auth import router as auth_router  # type: ignore
from router_education import router as education_router  # type: ignore
from routers.chat import router as chat_router  # type: ignore
from routers.market import router as market_router  # type: ignore
from routers.calculator import router as calculator_router  # type: ignore
from routers.risk import router as risk_router  # type: ignore
from routers.users import router as users_router  # type: ignore

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Investi AI Backend", version="4.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(education_router)
app.include_router(chat_router)
app.include_router(market_router)
app.include_router(calculator_router)
app.include_router(risk_router)
app.include_router(users_router)

# ─── CORS ────────────────────────────────────────────────────────────────────

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

# ─── Startup ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database...")
    init_db()

    from models_education import EducationModule  # type: ignore
    db = next(get_db())
    try:
        module_count = db.query(EducationModule).count()
        if module_count == 0:
            logger.info("Seeding education data...")
            from seed_lessons import seed_education_data  # type: ignore
            seed_education_data(db)
            logger.info("Education data seeded successfully!")
        else:
            logger.info(f"Education data already exists ({module_count} modules).")
    finally:
        db.close()

    logger.info("Database ready.")


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"status": "Investi AI Backend is Running", "version": "4.0.0"}
