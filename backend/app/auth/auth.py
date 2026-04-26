from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlmodel import Session, select
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database.db import get_session
from app.models.teacher import Teacher

# move to env 
SECRET_KEY = "hadasim_secret_key_2026"
ALGORITHM = "HS256"

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



@router.post("/login")
def login(
    teacher_id_input: str,
    response: Response,
    session: Session = Depends(get_session)
):
    statement = select(Teacher).where(Teacher.tz == teacher_id_input)
    teacher = session.exec(statement).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    token = create_access_token({"sub": str(teacher.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False 
    )
    return {"message": "Success"}

def get_current_teacher(request: Request, session: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        teacher_id: str = payload.get("sub")
        if teacher_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    teacher = session.get(Teacher, int(teacher_id))
    if not teacher:
        raise HTTPException(status_code=401)
    
    return teacher

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}