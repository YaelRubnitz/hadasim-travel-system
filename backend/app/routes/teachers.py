from fastapi import APIRouter, Depends, HTTPException
from app.schemas.teacher_schemas import TeacherRead
from sqlmodel import Session

from app.database.db import get_session
from app.services.teachers_service import (
    create_teacher_service,
    get_all_teachers,
    get_teacher_by_tz
)
from app.auth.auth import get_current_teacher

router = APIRouter()


@router.get("/", response_model=list[TeacherRead])
def read_teachers(
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    return get_all_teachers(session)


@router.get("/{tz}", response_model=TeacherRead)
def read_teacher(
    tz: str,
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    result = get_teacher_by_tz(session, tz)
    if not result:
        raise HTTPException(status_code=404)
    return result


#
@router.post("/", response_model=TeacherRead)
def create_teacher(teacher: dict, session: Session = Depends(get_session),current_user = Depends(get_current_teacher)):
    return create_teacher_service(session, teacher)