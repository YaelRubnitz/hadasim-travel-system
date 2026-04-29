from fastapi import HTTPException

from sqlmodel import Session, select
from app.models.teacher import Teacher

def get_teacher_by_tz(session: Session, tz: str):
    statement = select(Teacher).where(Teacher.tz == tz)
    teacher = session.exec(statement).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

def get_all_teachers(session: Session):
    return session.exec(select(Teacher)).all()


def get_teacher_by_tz(session: Session, tz: str):
    statement = select(Teacher).where(Teacher.tz == tz)
    teacher = session.exec(statement).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

def create_teacher_service(session: Session, data: dict):
    
    statement = select(Teacher).where(Teacher.tz == data.get("tz"))
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher with this TZ already exists")
    
    teacher = Teacher(**data)

    session.add(teacher)
    session.commit()
    session.refresh(teacher)

    return teacher