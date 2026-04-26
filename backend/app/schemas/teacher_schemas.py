from pydantic import BaseModel

class TeacherRead(BaseModel):
    tz: str
    first_name: str
    last_name: str
    class_name: str


class Config:
    from_attributes = True    

class TeacherLogin(BaseModel):
    teacher_id: str