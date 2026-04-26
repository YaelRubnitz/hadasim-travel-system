from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class LocationUpdate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_tz: str = Field(index=True) 
    latitude: float                     
    longitude: float                    
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)