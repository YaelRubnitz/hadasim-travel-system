from fastapi import APIRouter, Depends, HTTPException
from backend.app.database.db import get_session
from backend.app.schemas.location_schema import LocationRead
from backend.app.services.locations_service import create_location_service, get_last_location_service, get_student_path_service
from sqlmodel import Session
from app.auth.auth import get_current_teacher

router = APIRouter()


@router.post("/update" ,response_model = LocationRead)
def update_location(location: dict, session: Session = Depends(get_session)):
    result = create_location_service(session, location)
    return result

@router.get("/{student_tz}/last-location", response_model = LocationRead)
def get_last_location(student_tz: str, session: Session = Depends(get_session), teacher = Depends(get_current_teacher)):
    return get_last_location_service(session, student_tz)

@router.get("/{student_tz}/path",response_model=list[LocationRead])
def get_student_path(student_tz: str, session: Session = Depends(get_session), teacher = Depends(get_current_teacher)):
    return get_student_path_service(session, student_tz)
