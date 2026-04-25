from pydantic import BaseModel

class TeacherRead(BaseModel):
    id_number: str
    first_name: str
    last_name: str
    class_name: str

class TeacherLogin(BaseModel):
    teacher_id: str