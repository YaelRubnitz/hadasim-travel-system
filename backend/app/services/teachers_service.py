from sqlmodel import Session, select
from app.models.teacher import Teacher


def get_all_teachers(session: Session):
    return session.exec(select(Teacher)).all()


def get_teacher_by_id(session: Session, teacher_id: int):
    return session.get(Teacher, teacher_id)

def create_teacher_service(session: Session, data: dict):
    teacher = Teacher(**data)

    session.add(teacher)
    session.commit()
    session.refresh(teacher)

    return teacher