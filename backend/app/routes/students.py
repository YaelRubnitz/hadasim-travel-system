from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database.db import get_session
from app.services.students_service import (
    create_student_service,
    get_all_students,
    get_student_by_id,
    get_students_by_class
)
from app.auth.auth import get_current_teacher

router = APIRouter()


@router.get("/")
def read_students(
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    return get_all_students(session)


@router.get("/{student_id}")
def read_student(
    student_id: int,
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    student = get_student_by_id(session, student_id)
    if not student:
        raise HTTPException(status_code=404)
    return student


@router.get("/my-class")
def read_my_class_students(
    session: Session = Depends(get_session),
    teacher = Depends(get_current_teacher)
):
    return get_students_by_class(session, teacher.class_name)


@router.post("/")
def create_student(student: dict, session: Session = Depends(get_session)):
    return create_student_service(session, student)