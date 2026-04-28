from fastapi import FastAPI

from app.database.db import init_db
from app.routes import students, teachers, locations
from app.auth.auth import router as auth_router


from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="School Trip System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)



@app.on_event("startup")
def on_startup():
    init_db()


# Auth endpoints
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Students endpoints
app.include_router(students.router, prefix="/students", tags=["Students"])

# Teachers endpoints
app.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])

# Locations endpoints
app.include_router(locations.router, prefix="/locations", tags=["Locations"])