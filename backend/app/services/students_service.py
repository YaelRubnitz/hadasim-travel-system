from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.student import Student


def get_all_students(session: Session):
    return session.exec(select(Student)).all()


def get_student_by_tz(session: Session, tz: str):
    statement = select(Student).where(Student.tz == tz)
    student = session.exec(statement).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def get_students_by_class(session: Session, class_name: str):
    statement = select(Student).where(Student.class_name == class_name)
    return session.exec(statement).all()

def create_student_service(session: Session, data: dict):
    statement = select(Student).where(Student.tz == data.get("tz"))
    existing_student = session.exec(statement).first()
    
    if existing_student:
        raise HTTPException(status_code=400, detail="Student with this TZ already exists")
    
    student = Student(**data)

    session.add(student)
    session.commit()
    session.refresh(student)

    return student