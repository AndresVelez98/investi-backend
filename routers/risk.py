"""
routers/risk.py — Risk test endpoints
"""
from fastapi import APIRouter, HTTPException

from schemas import RiskTestEvaluateRequest  # type: ignore
from ai_advisor import evaluate_risk_profile, get_risk_question  # type: ignore

router = APIRouter(tags=["Risk Test"])


@router.get("/api/risk-test/question/{number}")
def get_question(number: int):
    """Returns a risk test question by number (1–5)."""
    if not (1 <= number <= 5):
        raise HTTPException(status_code=400, detail="Question number must be between 1 and 5")
    question = get_risk_question(number - 1)
    return {"question_number": number, "total_questions": 5, "question": question}


@router.post("/api/risk-test/evaluate")
def evaluate_risk_test(request: RiskTestEvaluateRequest):
    """Evaluates 5 answers and returns the user's risk profile."""
    if len(request.answers) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Se necesitan 5 respuestas, se recibieron {len(request.answers)}"
        )
    return evaluate_risk_profile(request.answers, request.user_name)
