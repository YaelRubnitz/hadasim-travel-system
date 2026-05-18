import os
from sqlmodel import create_engine, SQLModel, Session, select
from app.models.teacher import Teacher

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Yr214980260@localhost:5432/travel_db")
engine = create_engine(DATABASE_URL, echo=True)
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/travel_db")
# engine = create_engine(DATABASE_URL)

def seed_admin():
    with Session(engine) as session:
        existing = session.exec(select(Teacher)).first()

        if not existing:
            admin = Teacher(
                first_name="Admin",
                last_name="Admin",
                tz="12345678",
                class_name="AdminClass"
            )
            session.add(admin)
            session.commit()

def init_db():
   # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    seed_admin()

def get_session():
    with Session(engine) as session:
        yield session