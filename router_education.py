"""
router_education.py — Endpoints para el sistema de educación financiera gamificada
Incluye: módulos, lecciones, quizzes, progreso, logros y estadísticas
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import User
from models_education import (
    EducationModule, Lesson, QuizQuestion,
    UserLessonProgress, Achievement, UserAchievement,
)
from schemas_education import (
    ModuleResponse, LessonSummaryResponse, LessonDetailResponse,
    QuizQuestionResponse, QuizSubmitRequest, QuizResultResponse,
    UserStatsResponse, AchievementResponse,
)
from auth import get_current_user

router = APIRouter(prefix="/api/education", tags=["Education"])


# ═══════════════════════════════════════════════════════════════════════════════
#  MÓDULOS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/modules", response_model=List[ModuleResponse])
def list_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista todos los módulos con el progreso del usuario.
    """
    modules = (
        db.query(EducationModule)
        .filter(EducationModule.is_active == True)
        .order_by(EducationModule.order)
        .all()
    )

    result = []
    for mod in modules:
        total_lessons = (
            db.query(func.count(Lesson.id))
            .filter(Lesson.module_id == mod.id, Lesson.is_active == True)
            .scalar()
        )
        completed_lessons = (
            db.query(func.count(UserLessonProgress.id))
            .join(Lesson, Lesson.id == UserLessonProgress.lesson_id)
            .filter(
                UserLessonProgress.user_id == current_user.id,
                Lesson.module_id == mod.id,
                UserLessonProgress.is_completed == True,
            )
            .scalar()
        )
        progress_pct = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0

        result.append(ModuleResponse(
            id=mod.id,
            slug=mod.slug,
            title=mod.title,
            description=mod.description,
            icon=mod.icon,
            order=mod.order,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            progress_pct=round(progress_pct, 1),
        ))

    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  LECCIONES
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/modules/{module_slug}/lessons", response_model=List[LessonSummaryResponse])
def list_lessons(
    module_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista las lecciones de un módulo con el estado de cada una para el usuario.
    """
    module = db.query(EducationModule).filter_by(slug=module_slug, is_active=True).first()
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    lessons = (
        db.query(Lesson)
        .filter(Lesson.module_id == module.id, Lesson.is_active == True)
        .order_by(Lesson.order)
        .all()
    )

    result = []
    for lesson in lessons:
        progress = (
            db.query(UserLessonProgress)
            .filter_by(user_id=current_user.id, lesson_id=lesson.id)
            .first()
        )
        result.append(LessonSummaryResponse(
            id=lesson.id,
            slug=lesson.slug,
            title=lesson.title,
            summary=lesson.summary,
            difficulty=lesson.difficulty,
            xp_reward=lesson.xp_reward,
            order=lesson.order,
            is_completed=progress.is_completed if progress else False,
            quiz_score=progress.quiz_score if progress else None,
        ))

    return result


@router.get("/lessons/{lesson_slug}", response_model=LessonDetailResponse)
def get_lesson(
    lesson_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene el detalle completo de una lección, incluyendo quiz (sin respuestas correctas).
    """
    lesson = db.query(Lesson).filter_by(slug=lesson_slug, is_active=True).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    module = db.query(EducationModule).filter_by(id=lesson.module_id).first()

    progress = (
        db.query(UserLessonProgress)
        .filter_by(user_id=current_user.id, lesson_id=lesson.id)
        .first()
    )

    # Registrar que el usuario empezó la lección
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    quiz_questions = (
        db.query(QuizQuestion)
        .filter_by(lesson_id=lesson.id)
        .order_by(QuizQuestion.order)
        .all()
    )

    return LessonDetailResponse(
        id=lesson.id,
        slug=lesson.slug,
        title=lesson.title,
        summary=lesson.summary,
        content=lesson.content,
        fun_fact=lesson.fun_fact,
        difficulty=lesson.difficulty,
        xp_reward=lesson.xp_reward,
        module_title=module.title if module else "",
        quiz_questions=[
            QuizQuestionResponse(
                id=q.id,
                question=q.question,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
                order=q.order,
            )
            for q in quiz_questions
        ],
        is_completed=progress.is_completed,
        quiz_score=progress.quiz_score,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  QUIZ
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/lessons/{lesson_slug}/quiz", response_model=QuizResultResponse)
def submit_quiz(
    lesson_slug: str,
    submission: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evalúa las respuestas del quiz de una lección.
    Retorna el resultado, XP ganado y logros desbloqueados.
    """
    lesson = db.query(Lesson).filter_by(slug=lesson_slug, is_active=True).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    # Obtener preguntas de la lección
    questions = (
        db.query(QuizQuestion)
        .filter_by(lesson_id=lesson.id)
        .all()
    )
    question_map = {q.id: q for q in questions}

    if len(submission.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Se esperaban {len(questions)} respuestas, se recibieron {len(submission.answers)}"
        )

    # Evaluar respuestas
    correct_count = 0
    results = []
    for answer in submission.answers:
        question = question_map.get(answer.question_id)
        if not question:
            raise HTTPException(status_code=400, detail=f"Pregunta {answer.question_id} no encontrada")

        is_correct = answer.selected_option.lower() == question.correct_option.lower()
        if is_correct:
            correct_count += 1

        results.append({
            "question_id": question.id,
            "question": question.question,
            "selected": answer.selected_option.lower(),
            "correct": question.correct_option,
            "is_correct": is_correct,
            "explanation": question.explanation,
        })

    # Calcular score
    score = (correct_count / len(questions)) * 100
    passed = score >= 70

    # Calcular XP
    xp_earned = 0
    if passed:
        xp_earned = lesson.xp_reward
        if score == 100:
            xp_earned = int(lesson.xp_reward * 1.5)  # bonus por perfecto

    # Actualizar progreso
    progress = (
        db.query(UserLessonProgress)
        .filter_by(user_id=current_user.id, lesson_id=lesson.id)
        .first()
    )
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
        )
        db.add(progress)

    progress.quiz_attempts += 1

    # Solo actualizar si es mejor score o primera vez que pasa
    if passed and (not progress.is_completed or score > (progress.quiz_score or 0)):
        progress.is_completed = True
        progress.quiz_score = score
        progress.xp_earned = xp_earned
        progress.completed_at = datetime.utcnow()

    db.commit()

    # Verificar logros nuevos
    new_achievements = _check_achievements(db, current_user.id, score)

    return QuizResultResponse(
        lesson_id=lesson.id,
        score=round(score, 1),
        correct_count=correct_count,
        total_questions=len(questions),
        xp_earned=xp_earned,
        passed=passed,
        results=results,
        new_achievements=new_achievements,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTADÍSTICAS DEL USUARIO
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna las estadísticas completas del usuario en educación.
    """
    # Total XP
    total_xp = (
        db.query(func.coalesce(func.sum(UserLessonProgress.xp_earned), 0))
        .filter_by(user_id=current_user.id)
        .scalar()
    )

    # Lecciones completadas
    lessons_completed = (
        db.query(func.count(UserLessonProgress.id))
        .filter_by(user_id=current_user.id, is_completed=True)
        .scalar()
    )

    # Módulos completados
    modules_completed = _count_completed_modules(db, current_user.id)

    # Promedio de quizzes
    avg_score = (
        db.query(func.avg(UserLessonProgress.quiz_score))
        .filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.quiz_score.isnot(None),
        )
        .scalar()
    ) or 0.0

    # Racha actual
    current_streak = _calculate_streak(db, current_user.id)

    # Logros
    user_achievements = (
        db.query(UserAchievement, Achievement)
        .join(Achievement, Achievement.id == UserAchievement.achievement_id)
        .filter(UserAchievement.user_id == current_user.id)
        .all()
    )
    achievements = [
        {
            "slug": ach.slug,
            "title": ach.title,
            "description": ach.description,
            "icon": ach.icon,
            "unlocked_at": ua.unlocked_at.isoformat(),
        }
        for ua, ach in user_achievements
    ]

    # Agregar XP de logros al total
    achievement_xp = (
        db.query(func.coalesce(func.sum(Achievement.xp_bonus), 0))
        .join(UserAchievement, UserAchievement.achievement_id == Achievement.id)
        .filter(UserAchievement.user_id == current_user.id)
        .scalar()
    )
    total_xp += achievement_xp

    return UserStatsResponse(
        total_xp=total_xp,
        lessons_completed=lessons_completed,
        modules_completed=modules_completed,
        quiz_avg_score=round(avg_score, 1),
        current_streak=current_streak,
        achievements=achievements,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGROS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/achievements", response_model=List[AchievementResponse])
def list_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista todos los logros disponibles y cuáles ha desbloqueado el usuario.
    """
    all_achievements = db.query(Achievement).all()
    user_unlocked = (
        db.query(UserAchievement.achievement_id, UserAchievement.unlocked_at)
        .filter_by(user_id=current_user.id)
        .all()
    )
    unlocked_map = {ua.achievement_id: ua.unlocked_at for ua in user_unlocked}

    return [
        AchievementResponse(
            id=ach.id,
            slug=ach.slug,
            title=ach.title,
            description=ach.description,
            icon=ach.icon,
            xp_bonus=ach.xp_bonus,
            is_unlocked=ach.id in unlocked_map,
            unlocked_at=unlocked_map.get(ach.id),
        )
        for ach in all_achievements
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def _check_achievements(db: Session, user_id: int, latest_score: float) -> list:
    """
    Verifica si el usuario desbloqueó nuevos logros después de completar un quiz.
    """
    new_achievements = []

    # Contar lecciones completadas
    lessons_completed = (
        db.query(func.count(UserLessonProgress.id))
        .filter_by(user_id=user_id, is_completed=True)
        .scalar()
    )

    # Contar módulos completados
    modules_completed = _count_completed_modules(db, user_id)

    # Calcular racha
    current_streak = _calculate_streak(db, user_id)

    # Verificar cada logro no desbloqueado
    all_achievements = db.query(Achievement).all()
    unlocked_ids = set(
        ua.achievement_id
        for ua in db.query(UserAchievement.achievement_id)
        .filter_by(user_id=user_id)
        .all()
    )

    for ach in all_achievements:
        if ach.id in unlocked_ids:
            continue

        unlocked = False
        if ach.condition_type == "lessons_completed" and lessons_completed >= ach.condition_value:
            unlocked = True
        elif ach.condition_type == "module_completed" and modules_completed >= ach.condition_value:
            unlocked = True
        elif ach.condition_type == "perfect_quiz" and latest_score == 100:
            unlocked = True
        elif ach.condition_type == "streak" and current_streak >= ach.condition_value:
            unlocked = True

        if unlocked:
            user_ach = UserAchievement(user_id=user_id, achievement_id=ach.id)
            db.add(user_ach)
            new_achievements.append({
                "slug": ach.slug,
                "title": ach.title,
                "description": ach.description,
                "icon": ach.icon,
                "xp_bonus": ach.xp_bonus,
            })

    if new_achievements:
        db.commit()

    return new_achievements


def _count_completed_modules(db: Session, user_id: int) -> int:
    """Cuenta cuántos módulos tiene completamente terminados el usuario."""
    modules = db.query(EducationModule).filter_by(is_active=True).all()
    completed = 0

    for mod in modules:
        total = (
            db.query(func.count(Lesson.id))
            .filter(Lesson.module_id == mod.id, Lesson.is_active == True)
            .scalar()
        )
        if total == 0:
            continue

        user_completed = (
            db.query(func.count(UserLessonProgress.id))
            .join(Lesson, Lesson.id == UserLessonProgress.lesson_id)
            .filter(
                UserLessonProgress.user_id == user_id,
                Lesson.module_id == mod.id,
                UserLessonProgress.is_completed == True,
            )
            .scalar()
        )
        if user_completed >= total:
            completed += 1

    return completed


def _calculate_streak(db: Session, user_id: int) -> int:
    """Calcula la racha actual de días consecutivos con lecciones completadas."""
    completions = (
        db.query(func.date(UserLessonProgress.completed_at))
        .filter(
            UserLessonProgress.user_id == user_id,
            UserLessonProgress.completed_at.isnot(None),
        )
        .distinct()
        .order_by(func.date(UserLessonProgress.completed_at).desc())
        .all()
    )

    if not completions:
        return 0

    dates = [row[0] for row in completions if row[0] is not None]
    if not dates:
        return 0

    today = datetime.utcnow().date()
    streak = 0

    # La racha debe incluir hoy o ayer para ser "actual"
    if dates[0] != today and dates[0] != today - timedelta(days=1):
        return 0

    for i, d in enumerate(dates):
        expected = today - timedelta(days=i)
        # Permitir que empiece desde ayer
        if i == 0 and d == today - timedelta(days=1):
            expected = today - timedelta(days=1)
            streak += 1
            continue
        if d == expected:
            streak += 1
        else:
            break

    return streak
