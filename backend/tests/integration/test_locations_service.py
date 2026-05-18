"""
Characterization tests for locations_service (current behavior, SQLite).

Note: SQLite requires ``datetime`` objects for ``timestamp`` columns. Production
may receive ISO strings via JSON on PostgreSQL; ordering tests pass ``datetime``
directly to exercise service logic without changing production code.
"""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.teacher import Teacher
from app.services.locations_service import (
    create_location_service,
    get_all_class_locations_service,
    get_far_students_service,
    get_last_location_service,
    get_student_path_service,
)
from tests.conftest import (
    BEER_SHEVA_LAT,
    BEER_SHEVA_LON,
    JERUSALEM_LAT,
    JERUSALEM_LON,
    dms_payload,
)


class TestCreateLocationService:
    def test_inserts_student_location(self, session: Session, student_near):
        data = dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON)
        row = create_location_service(session, data)
        assert row.student_tz == student_near.tz
        assert row.latitude == pytest.approx(31 + 46 / 60 + 20 / 3600, rel=1e-6)
        assert row.longitude == pytest.approx(35 + 13 / 60 + 5 / 3600, rel=1e-6)

    def test_accepts_teacher_tz(self, session: Session, teacher: Teacher):
        data = dms_payload(teacher.tz, JERUSALEM_LAT, JERUSALEM_LON)
        row = create_location_service(session, data)
        assert row.student_tz == teacher.tz

    def test_unknown_tz_404_message(self, session: Session):
        data = dms_payload("99999999", JERUSALEM_LAT, JERUSALEM_LON)
        with pytest.raises(HTTPException) as exc:
            create_location_service(session, data)
        assert exc.value.status_code == 404
        assert "not registered as Student or Teacher" in exc.value.detail

    def test_invalid_coordinates_400(self, session: Session, student_near):
        with pytest.raises(HTTPException) as exc:
            create_location_service(session, {"ID": student_near.tz, "Coordinates": {}})
        assert exc.value.status_code == 400
        assert exc.value.detail == "Invalid coordinates format"


class TestGetLastLocationService:
    def test_returns_latest_by_timestamp(self, session: Session, student_near):
        older = dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON)
        older["Time"] = datetime(2026, 5, 17, 9, 0, 0, tzinfo=timezone.utc)
        newer = dms_payload(student_near.tz, BEER_SHEVA_LAT, BEER_SHEVA_LON)
        newer["Time"] = datetime(2026, 5, 17, 11, 0, 0, tzinfo=timezone.utc)
        create_location_service(session, older)
        create_location_service(session, newer)
        last = get_last_location_service(session, student_near.tz)
        assert last.latitude == pytest.approx(31 + 15 / 60 + 10 / 3600, rel=1e-6)

    def test_unknown_user_message(self, session: Session):
        with pytest.raises(HTTPException) as exc:
            get_last_location_service(session, "99999999")
        assert exc.value.status_code == 404
        assert exc.value.detail == "User not found in Students or Teachers"

    def test_no_location_rows_message(self, session: Session, student_near):
        with pytest.raises(HTTPException) as exc:
            get_last_location_service(session, student_near.tz)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Location not found for this user"


class TestGetStudentPathService:
    def test_returns_at_most_twenty_ordered_points(self, session: Session, student_near):
        base_time = datetime(2026, 5, 17, 0, 0, 0, tzinfo=timezone.utc)
        for i in range(25):
            data = dms_payload(student_near.tz, (31, 0, i), JERUSALEM_LON)
            data["Time"] = base_time + timedelta(hours=i)
            create_location_service(session, data)
        path = get_student_path_service(session, student_near.tz)
        assert len(path) == 20
        timestamps = [p.timestamp for p in path]
        assert timestamps == sorted(timestamps)

    def test_requires_registered_student(self, session: Session, teacher: Teacher):
        with pytest.raises(HTTPException) as exc:
            get_student_path_service(session, teacher.tz)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Student not found"


class TestGetAllClassLocationsService:
    def test_returns_only_class_students_with_locations(
        self, session: Session, student_near, student_far, student_other_class, teacher
    ):
        create_location_service(session, dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON))
        create_location_service(session, dms_payload(student_far.tz, BEER_SHEVA_LAT, BEER_SHEVA_LON))
        create_location_service(
            session, dms_payload(student_other_class.tz, JERUSALEM_LAT, JERUSALEM_LON)
        )
        rows = get_all_class_locations_service(session, "ClassA")
        tzs = {r.student_tz for r in rows}
        assert student_near.tz in tzs
        assert student_far.tz in tzs
        assert student_other_class.tz not in tzs

    def test_empty_class_returns_empty_list(self, session: Session):
        assert get_all_class_locations_service(session, "EmptyClass") == []


class TestGetFarStudentsService:
    def test_returns_far_classmate_with_expected_shape(
        self, session: Session, teacher, student_near, student_far
    ):
        create_location_service(session, dms_payload(teacher.tz, JERUSALEM_LAT, JERUSALEM_LON))
        create_location_service(session, dms_payload(student_near.tz, JERUSALEM_LAT, JERUSALEM_LON))
        create_location_service(session, dms_payload(student_far.tz, BEER_SHEVA_LAT, BEER_SHEVA_LON))

        result = get_far_students_service(session, teacher)
        assert len(result) == 1
        entry = result[0]
        assert set(entry.keys()) == {
            "student_tz",
            "first_name",
            "last_name",
            "distance",
            "latitude",
            "longitude",
            "timestamp",
        }
        assert entry["student_tz"] == student_far.tz
        assert entry["first_name"] == "Far"
        assert entry["distance"] > 3.0

    def test_no_teacher_location_returns_empty_list(
        self, session: Session, teacher, student_far
    ):
        create_location_service(session, dms_payload(student_far.tz, BEER_SHEVA_LAT, BEER_SHEVA_LON))
        assert get_far_students_service(session, teacher) == []
