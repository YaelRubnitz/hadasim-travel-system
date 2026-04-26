from pydantic import BaseModel
from datetime import datetime

class LocationRead(BaseModel):
    student_tz: str
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        from_attributes = True