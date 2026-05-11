"""
models_education.py — Modelos para el sistema de educación financiera gamificada
Módulos → Lecciones → Quizzes → Progreso del usuario → Logros (badges)
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, SmallInteger, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base
from core.utils import utcnow as _now  # type: ignore


# ─── Módulos (categorías principales) ─────────────────────────────────────────

class EducationModule(Base):
    """
    Un módulo agrupa lecciones por tema.
    Ejemplo: "Ahorro Inteligente", "Inversión Básica"
    """
    __tablename__ = "education_modules"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)  # "ahorro-inteligente"
    title = Column(String(200), nullable=False)                          # "Ahorro Inteligente"
    description = Column(Text, nullable=False)
    icon = Column(String(10), default="📘")                              # emoji para el frontend
    order = Column(SmallInteger, nullable=False, default=0)              # orden pedagógico
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)

    lessons = relationship("Lesson", back_populates="module", order_by="Lesson.order")


# ─── Lecciones ─────────────────────────────────────────────────────────────────

class Lesson(Base):
    """
    Una lección individual dentro de un módulo.
    Tiene contenido educativo + quiz de validación.
    """
    __tablename__ = "education_lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("education_modules.id"), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(String(500), nullable=False)          # resumen corto para cards
    content = Column(Text, nullable=False)                  # contenido completo (markdown)
    fun_fact = Column(Text, nullable=True)                  # dato curioso para engagement
    difficulty = Column(SmallInteger, default=1)            # 1=básico, 2=intermedio, 3=avanzado
    xp_reward = Column(Integer, default=50)                 # puntos de experiencia
    order = Column(SmallInteger, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)

    module = relationship("EducationModule", back_populates="lessons")
    quiz_questions = relationship("QuizQuestion", back_populates="lesson", order_by="QuizQuestion.order")


# ─── Preguntas del Quiz ────────────────────────────────────────────────────────

class QuizQuestion(Base):
    """
    Pregunta de opción múltiple vinculada a una lección.
    Cada lección tiene ~3 preguntas para validar comprensión.
    """
    __tablename__ = "education_quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("education_lessons.id"), nullable=False)
    question = Column(Text, nullable=False)
    option_a = Column(String(300), nullable=False)
    option_b = Column(String(300), nullable=False)
    option_c = Column(String(300), nullable=False)
    option_d = Column(String(300), nullable=True)           # opcional, puede ser 3 o 4 opciones
    correct_option = Column(String(1), nullable=False)      # "a", "b", "c" o "d"
    explanation = Column(Text, nullable=False)               # por qué esa es la correcta
    order = Column(SmallInteger, default=0)

    lesson = relationship("Lesson", back_populates="quiz_questions")


# ─── Progreso del Usuario ──────────────────────────────────────────────────────

class UserLessonProgress(Base):
    """
    Registra el progreso de cada usuario en cada lección.
    """
    __tablename__ = "education_user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("education_lessons.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    quiz_score = Column(Float, nullable=True)               # porcentaje 0-100
    quiz_attempts = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), default=_now)

    user = relationship("User")
    lesson = relationship("Lesson")


# ─── Logros (Badges / Achievements) ───────────────────────────────────────────

class Achievement(Base):
    """
    Definición de logros desbloqueables.
    """
    __tablename__ = "education_achievements"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), default="🏆")
    xp_bonus = Column(Integer, default=100)
    condition_type = Column(String(50), nullable=False)     # "lessons_completed", "module_completed", "streak", "perfect_quiz"
    condition_value = Column(Integer, nullable=False)        # ej: 5 lecciones, 1 módulo, 3 días seguidos
    created_at = Column(DateTime(timezone=True), default=_now)


class UserAchievement(Base):
    """
    Logros desbloqueados por cada usuario.
    """
    __tablename__ = "education_user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("education_achievements.id"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), default=_now)

    user = relationship("User")
    achievement = relationship("Achievement")
