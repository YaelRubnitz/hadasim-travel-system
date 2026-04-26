from fastapi import APIRouter, Depends, HTTPException
from backend.app.schemas.student_schema import StudentRead
from sqlmodel import Session

from app.database.db import get_session
from app.services.students_service import (
    create_student_service,
    get_all_students,
    get_student_by_tz,
    get_students_by_class
)
from app.auth.auth import get_current_teacher

router = APIRouter()


@router.get("/", response_model=list[StudentRead])
def read_students(
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    return get_all_students(session)


@router.get("/my-class", response_model=list[StudentRead])
def read_my_class_students(
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    return get_students_by_class(session, teacher.class_name)


@router.get("/{tz}", response_model=StudentRead)
def read_student(
    tz: str,
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    student = get_student_by_tz(session, tz)
    if not student:
        raise HTTPException(status_code=404)
    return student


@router.post("/", response_model=StudentRead)
def create_student(student: dict, session: Session = Depends(get_session), teacher = Depends(get_current_teacher)):
    return create_student_service(session, student)