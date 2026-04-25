from pydantic import BaseModel

class StudentRead(BaseModel):
    id_number: str
    first_name: str
    last_name: str
    class_name: str