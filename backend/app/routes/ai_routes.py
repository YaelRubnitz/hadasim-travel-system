from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.db import get_session
from app.auth.auth import get_current_teacher
from app.models.teacher import Teacher
from app.ai.schemas import OperationalSummaryResponse
from app.services.ai_service import get_class_ai_summary_service

router = APIRouter()

@router.get("/class/{class_id}/summary", response_model=OperationalSummaryResponse)
async def get_ai_summary(
    class_id: str,
    session: Session = Depends(get_session),
    teacher: Teacher = Depends(get_current_teacher)
):
    """
    Get the AI operational summary for a class.
    Subject to cooldowns and AI Scheduler logic.
    """
    # Using class_id as class_name based on current schema constraints
    return await get_class_ai_summary_service(
        session=session,
        class_name=class_id,
        teacher_tz=teacher.tz,
        force=False
    )

@router.post("/class/{class_id}/summary/force", response_model=OperationalSummaryResponse)
async def force_ai_summary(
    class_id: str,
    session: Session = Depends(get_session),
    teacher: Teacher = Depends(get_current_teacher)
):
    """
    Force execution of the AI operational summary, bypassing cooldowns.
    Useful for manual triggers or debugging.
    """
    return await get_class_ai_summary_service(
        session=session,
        class_name=class_id,
        teacher_tz=teacher.tz,
        force=True
    )
