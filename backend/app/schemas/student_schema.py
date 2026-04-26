from pydantic import BaseModel

class StudentRead(BaseModel):
    tz: str
    first_name: str
    last_name: str
    class_name: str

class Config:
        from_attributes = True    