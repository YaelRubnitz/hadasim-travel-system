from sqlmodel import Session, select, desc, func, and_
from app.models.location import LocationUpdate
from app.services.students_service import get_student_by_tz 
from fastapi import HTTPException, HTTPException
from datetime import datetime, timedelta
from app.models.student import Student

last_cleanup_time = datetime.utcnow()

def cleanup_old_locations(session: Session, hours: int = 24):
    global last_cleanup_time
    
    if datetime.utcnow() - last_cleanup_time < timedelta(hours=1):
        return
    try:
        threshold = datetime.utcnow() - timedelta(hours=hours)
        statement = delete(LocationUpdate).where(LocationUpdate.timestamp < threshold)
        session.exec(statement)
        session.commit()
        
        last_cleanup_time = datetime.utcnow()
        print(f"Cleanup performed at {last_cleanup_time}")
    except Exception as e:
        print(f"Cleanup failed: {e}")

def dmms_to_decimal(degrees: str, minutes: str, seconds: str) -> float:
    return float(degrees) + float(minutes) / 60 + float(seconds) / 3600

def create_location_service(session: Session, data: dict):
    get_student_by_tz(session, data.get("ID")) 

    try:
        lat_d = data["Coordinates"]["Latitude"]
        lon_d = data["Coordinates"]["Longitude"]

        latitude = dmms_to_decimal(lat_d["Degrees"], lat_d["Minutes"], lat_d["Seconds"])
        longitude = dmms_to_decimal(lon_d["Degrees"], lon_d["Minutes"], lon_d["Seconds"])

        location = LocationUpdate(
            student_tz=data["ID"],
            latitude=latitude,
            longitude=longitude,
            timestamp=data.get("Time")
        )
        session.add(location)
        session.commit()
        session.refresh(location)
        return location
    except KeyError as e:
        raise HTTPException(status_code=400, detail="Invalid coordinates format")
    
def get_last_location_service(session: Session, student_tz: str):
    get_student_by_tz(session, student_tz) 

    statement = select(LocationUpdate).where(LocationUpdate.student_tz == student_tz).order_by(desc(LocationUpdate.timestamp))
    location = session.exec(statement).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

def get_student_path_service(session: Session, student_tz: str):
    get_student_by_tz(session, student_tz) 

    statement = select(LocationUpdate).where(LocationUpdate.student_tz == student_tz).order_by(LocationUpdate.timestamp).limit(20)
    locations = session.exec(statement).all()
    return locations


def get_all_class_locations_service(session: Session, class_name: str):
    student_statement = select(Student.tz).where(Student.class_name == class_name)
    class_student_tzs = session.exec(student_statement).all()

    if not class_student_tzs:
        return []

    last_locations = []

    for tz in class_student_tzs:
        location_statement = (
            select(LocationUpdate)
            .where(LocationUpdate.student_tz == tz)
            .order_by(desc(LocationUpdate.timestamp)) # מיון מהחדש לישן
            .limit(1)
        )
        result = session.exec(location_statement).first()
        if result:
            last_locations.append(result)

    return last_locations