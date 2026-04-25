from sqlmodel import SQLModel, Field
from typing import Optional


class Teacher(SQLModel, table=True):
    __tablename__ = "teachers"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    tz: str

    class_name: str