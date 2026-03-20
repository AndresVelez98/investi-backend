"""
schemas_education.py — Pydantic schemas for the financial education system
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Module Schemas ────────────────────────────────────────────────────────────

class ModuleResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    icon: str
    order: int
    total_lessons: int = 0
    completed_lessons: int = 0        # se calcula dinámicamente por usuario
    progress_pct: float = 0.0         # porcentaje completado

    class Config:
        from_attributes = True


# ─── Lesson Schemas ────────────────────────────────────────────────────────────

class LessonSummaryResponse(BaseModel):
    """Vista resumida para listados"""
    id: int
    slug: str
    title: str
    summary: str
    difficulty: int
    xp_reward: int
    order: int
    is_completed: bool = False
    quiz_score: Optional[float] = None

    class Config:
        from_attributes = True


class QuizQuestionResponse(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: Optional[str] = None
    order: int
    # NO incluimos correct_option aquí — eso se valida en backend

    class Config:
        from_attributes = True


class LessonDetailResponse(BaseModel):
    """Vista completa de una lección"""
    id: int
    slug: str
    title: str
    summary: str
    content: str                      # markdown completo
    fun_fact: Optional[str] = None
    difficulty: int
    xp_reward: int
    module_title: str = ""
    quiz_questions: List[QuizQuestionResponse] = []
    is_completed: bool = False
    quiz_score: Optional[float] = None

    class Config:
        from_attributes = True


# ─── Quiz Submission ───────────────────────────────────────────────────────────

class QuizAnswer(BaseModel):
    question_id: int
    selected_option: str = Field(..., pattern="^[abcdABCD]$")


class QuizSubmitRequest(BaseModel):
    answers: List[QuizAnswer]


class QuizResultResponse(BaseModel):
    lesson_id: int
    score: float                      # porcentaje 0-100
    correct_count: int
    total_questions: int
    xp_earned: int
    passed: bool                      # >= 70% para pasar
    results: List[dict]               # detalle por pregunta
    new_achievements: List[dict] = [] # logros desbloqueados


# ─── Progress & Stats ──────────────────────────────────────────────────────────

class UserStatsResponse(BaseModel):
    total_xp: int
    lessons_completed: int
    modules_completed: int
    quiz_avg_score: float
    current_streak: int               # días consecutivos
    achievements: List[dict]


class AchievementResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    icon: str
    xp_bonus: int
    unlocked_at: Optional[datetime] = None
    is_unlocked: bool = False

    class Config:
        from_attributes = True
