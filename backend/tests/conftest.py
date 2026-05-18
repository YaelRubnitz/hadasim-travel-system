"""
Shared pytest fixtures: in-memory SQLite, FastAPI TestClient, sample users.

Production code is not modified; tests patch db.engine before importing the app
so startup/init_db and requests use the same SQLite database.
"""
import os

# Must be set before app.database.db is first imported by the app package.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.models.location import LocationUpdate
from app.models.student import Student
from app.models.teacher import Teacher

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

import app.database.db as db

db.engine = TEST_ENGINE

from app.database.db import get_session
from app.main import app

# Jerusalem-area coordinates (match seed_data.py style)
JERUSALEM_LAT = (31, 46, 20)
JERUSALEM_LON = (35, 13, 5)
BEER_SHEVA_LAT = (31, 15, 10)
BEER_SHEVA_LON = (34, 53, 50)


def dms_payload(
    tz: str,
    lat: tuple[int, int, int],
    lon: tuple[int, int, int],
    time: str | None = None,
) -> dict:
    """Build POST /locations/update body (DMS contract used by devices and simulators)."""
    lat_d, lat_m, lat_s = lat
    lon_d, lon_m, lon_s = lon
    payload = {
        "ID": tz,
        "Coordinates": {
            "Latitude": {
                "Degrees": str(lat_d),
                "Minutes": str(lat_m),
                "Seconds": str(lat_s),
            },
            "Longitude": {
                "Degrees": str(lon_d),
                "Minutes": str(lon_m),
                "Seconds": str(lon_s),
            },
        },
    }
    if time is not None:
        payload["Time"] = time
    return payload


@pytest.fixture(autouse=True)
def reset_database():
    """Fresh schema per test for deterministic characterization."""
    SQLModel.metadata.drop_all(TEST_ENGINE)
    SQLModel.metadata.create_all(TEST_ENGINE)
    yield


@pytest.fixture
def session():
    with Session(TEST_ENGINE) as s:
        yield s


@pytest.fixture
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def teacher(session) -> Teacher:
    t = Teacher(
        first_name="Rina",
        last_name="Cohen",
        tz="90000001",
        class_name="ClassA",
    )
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


@pytest.fixture
def student_near(session) -> Student:
    s = Student(
        first_name="Near",
        last_name="Student",
        tz="81111111",
        class_name="ClassA",
    )
    session.add(s)
    session.commit()
    session.refresh(s)
    return s


@pytest.fixture
def student_far(session) -> Student:
    s = Student(
        first_name="Far",
        last_name="Student",
        tz="82222222",
        class_name="ClassA",
    )
    session.add(s)
    session.commit()
    session.refresh(s)
    return s


@pytest.fixture
def student_other_class(session) -> Student:
    s = Student(
        first_name="Other",
        last_name="Class",
        tz="83333333",
        class_name="ClassB",
    )
    session.add(s)
    session.commit()
    session.refresh(s)
    return s


@pytest.fixture
def authenticated_client(client, teacher):
    response = client.post(f"/auth/login?teacher_id_input={teacher.tz}")
    assert response.status_code == 200
    return client
