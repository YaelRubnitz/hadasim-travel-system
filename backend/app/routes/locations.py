from fastapi import APIRouter, Depends, BackgroundTasks
from app.database.db import get_session
from app.schemas.location_schema import LocationRead
from app.services.locations_service import create_location_service, get_far_students_service, get_last_location_service, get_student_path_service, cleanup_old_locations, get_all_class_locations_service
from app.models.teacher import Teacher
from sqlmodel import Session
from app.auth.auth import get_current_teacher

router = APIRouter()


@router.post("/update" ,response_model = LocationRead)
def update_location(location: dict ,background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    result = create_location_service(session, location)
    background_tasks.add_task(cleanup_old_locations, session)
    return result

@router.get("/{student_tz}/last-location", response_model = LocationRead)
def get_last_location(student_tz: str, session: Session = Depends(get_session), teacher = Depends(get_current_teacher)):
    return get_last_location_service(session, student_tz)

@router.get("/{student_tz}/path",response_model=list[LocationRead])
def get_student_path(student_tz: str, session: Session = Depends(get_session), teacher = Depends(get_current_teacher)):
    return get_student_path_service(session, student_tz)


@router.get("/class-last-locations", response_model=list[LocationRead])
def get_class_locations(
    session: Session = Depends(get_session), 
    teacher = Depends(get_current_teacher)
):
    return get_all_class_locations_service(session, teacher.class_name)

@router.get("/far-students")
def get_far_students(
    session: Session = Depends(get_session), 
    teacher = Depends(get_current_teacher)
):
  
    return get_far_students_service(session, teacher)   