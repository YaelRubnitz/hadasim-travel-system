import os
from sqlmodel import create_engine, SQLModel, Session

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Yr214980260@localhost:5432/travel_db")
# engine = create_engine(DATABASE_URL, echo=True)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret_pass@localhost:5432/travel_db")
engine = create_engine(DATABASE_URL)

def init_db():
   # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session