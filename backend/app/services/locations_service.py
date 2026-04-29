from sqlmodel import Session, select, desc, func, and_, delete
from app.models.location import LocationUpdate
from app.services.students_service import get_student_by_tz 
from app.services.teachers_service import get_teacher_by_tz
from fastapi import HTTPException, HTTPException
from datetime import datetime, timedelta
from app.models.student import Student
from app.models.teacher import Teacher
import math

last_cleanup_time = datetime.utcnow()
FAR = 3.0

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

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
    user_id = data.get("ID")
    try:
        get_student_by_tz(session, user_id)
    except HTTPException:
        try:
            get_teacher_by_tz(session, user_id)
        except HTTPException:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID {user_id} is not registered as Student or Teacher"
            )

    try:
        lat_d = data["Coordinates"]["Latitude"]
        lon_d = data["Coordinates"]["Longitude"]

        latitude = dmms_to_decimal(lat_d["Degrees"], lat_d["Minutes"], lat_d["Seconds"])
        longitude = dmms_to_decimal(lon_d["Degrees"], lon_d["Minutes"], lon_d["Seconds"])

        location = LocationUpdate(
            student_tz=user_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=data.get("Time")
        )
        
        session.add(location)
        session.commit()
        session.refresh(location)
        return location
        
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format")

def get_last_location_by_tz(session, tz):
    return session.exec(
        select(LocationUpdate)
        .where(LocationUpdate.student_tz == tz)
        .order_by(desc(LocationUpdate.timestamp))
    ).first()
     
    
def get_last_location_service(session: Session, tz: str):
    student = session.exec(select(Student).where(Student.tz == tz)).first()
    teacher = session.exec(select(Teacher).where(Teacher.tz == tz)).first()

    if not student and not teacher:
        raise HTTPException(status_code=404, detail="User not found in Students or Teachers")


    location = get_last_location_by_tz(session, tz)
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found for this user")
        
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
        result = get_last_location_by_tz(session, tz)
        if result:
            last_locations.append(result)

    return last_locations

def get_far_students_service(session: Session, teacher: Teacher):
    
    try:
        teacher_location = get_last_location_service(session, teacher.tz)
    except HTTPException:
        return []
    
    all_class_locations = get_all_class_locations_service(session, teacher.class_name)
    
    far_students = []
    
    for loc in all_class_locations:
        if loc.student_tz == teacher.tz:
            continue
            
        dist = calculate_distance(
            teacher_location.latitude, teacher_location.longitude,
            loc.latitude, loc.longitude
        )
                
        if dist > FAR:
            try:
                student = get_student_by_tz(session, loc.student_tz)
                far_students.append({
                    "student_tz": loc.student_tz,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "distance": round(dist, 2),
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                    "timestamp": loc.timestamp
                })
            except Exception as e:
                print(f"Error fetching student info for tz {loc.student_tz}: {e}")
    return far_students