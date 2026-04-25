from sqlmodel import Session, select
from app.models.student import Student


def get_all_students(session: Session):
    return session.exec(select(Student)).all()


def get_student_by_id(session: Session, student_id: int):
    return session.get(Student, student_id)


def get_students_by_class(session: Session, class_name: str):
    statement = select(Student).where(Student.class_name == class_name)
    return session.exec(statement).all()

def create_student_service(session: Session, data: dict):
    student = Student(**data)

    session.add(student)
    session.commit()
    session.refresh(student)

    return student