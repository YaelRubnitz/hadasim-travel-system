from sqlmodel import Session, select, desc
from app.models.location import LocationUpdate
from app.services.students_service import get_student_by_tz 
from fastapi import HTTPException, HTTPException


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