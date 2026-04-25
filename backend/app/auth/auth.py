from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlmodel import Session, select

from app.database.db import get_session
from app.models.teacher import Teacher
from app.schemas.teacher_schemas import TeacherLogin

router = APIRouter()

@router.post("/login")
def login(
    teacher_id: int,
    response: Response,
    session: Session = Depends(get_session)
):
    teacher = session.get(Teacher, teacher_id)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    response.set_cookie(
        key="teacher_id",
        value=str(teacher.id),
        httponly=True
    )

    return {"message": "login successful"}


def get_current_teacher(
    request: Request,
    session: Session = Depends(get_session)
):
    teacher_id = request.cookies.get("teacher_id")

    if not teacher_id:
        raise HTTPException(status_code=401)

    teacher = session.get(Teacher, int(teacher_id))

    if not teacher:
        raise HTTPException(status_code=401)

    return teacher

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("teacher_id")
    return {"message": "logged out"}