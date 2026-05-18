import pytest
from sqlmodel import Session
from datetime import datetime, timezone
import math

from app.models.location import LocationUpdate
from app.models.student import Student
from app.models.teacher import Teacher
from app.services.locations_service import get_far_students_service

UTC = timezone.utc

def _create_student(session: Session, tz: str, class_name: str, first_name="S", last_name="L") -> Student:
    student = Student(tz=tz, class_name=class_name, first_name=first_name, last_name=last_name)
    session.add(student)
    session.commit()
    return student

def _create_teacher(session: Session, tz: str, class_name: str) -> Teacher:
    teacher = Teacher(tz=tz, class_name=class_name, first_name="T", last_name="T")
    session.add(teacher)
    session.commit()
    return teacher

def _insert_location(session: Session, tz: str, lat: float, lon: float):
    loc = LocationUpdate(
        student_tz=tz,
        latitude=lat,
        longitude=lon,
        timestamp=datetime.now(UTC)
    )
    session.add(loc)
    session.commit()

class TestLocationProximityIntegration:

    def test_teacher_with_no_students(self, session: Session):
        teacher = _create_teacher(session, "t1", "ClassEmpty")
        _insert_location(session, teacher.tz, 31.0, 35.0)

        far_students = get_far_students_service(session, teacher)
        assert far_students == []

    def test_teacher_has_no_location_at_all(self, session: Session):
        teacher = _create_teacher(session, "t2", "ClassNoLoc")
        student = _create_student(session, "s2", "ClassNoLoc")
        _insert_location(session, student.tz, 31.0, 35.0)

        # Teacher has no location update
        far_students = get_far_students_service(session, teacher)
        assert far_students == []

    def test_students_only_close_to_teacher(self, session: Session):
        teacher = _create_teacher(session, "t3", "ClassClose")
        s1 = _create_student(session, "s3_1", "ClassClose")
        s2 = _create_student(session, "s3_2", "ClassClose")

        lat, lon = 31.0, 35.0
        _insert_location(session, teacher.tz, lat, lon)
        # Students very close (within 0.01 degrees ~ 1km)
        _insert_location(session, s1.tz, lat + 0.005, lon)
        _insert_location(session, s2.tz, lat, lon + 0.005)

        far_students = get_far_students_service(session, teacher)
        assert far_students == []

    def test_students_only_far_from_teacher(self, session: Session):
        teacher = _create_teacher(session, "t4", "ClassFar")
        s1 = _create_student(session, "s4_1", "ClassFar")
        s2 = _create_student(session, "s4_2", "ClassFar")

        lat, lon = 31.0, 35.0
        _insert_location(session, teacher.tz, lat, lon)
        # Students clearly > 3 km away (0.1 degrees is > 10km)
        _insert_location(session, s1.tz, lat + 0.1, lon)
        _insert_location(session, s2.tz, lat, lon + 0.1)

        far_students = get_far_students_service(session, teacher)
        assert len(far_students) == 2
        far_tzs = {s["student_tz"] for s in far_students}
        assert far_tzs == {s1.tz, s2.tz}

    def test_mixed_scenario(self, session: Session):
        teacher = _create_teacher(session, "t5", "ClassMixed")
        s_close1 = _create_student(session, "s5_c1", "ClassMixed")
        s_close2 = _create_student(session, "s5_c2", "ClassMixed")
        s_far1 = _create_student(session, "s5_f1", "ClassMixed")
        s_far2 = _create_student(session, "s5_f2", "ClassMixed")

        lat, lon = 31.0, 35.0
        _insert_location(session, teacher.tz, lat, lon)

        # Close students
        _insert_location(session, s_close1.tz, lat + 0.005, lon)
        _insert_location(session, s_close2.tz, lat - 0.005, lon)

        # Far students
        _insert_location(session, s_far1.tz, lat + 0.1, lon)
        _insert_location(session, s_far2.tz, lat - 0.1, lon)

        far_students = get_far_students_service(session, teacher)
        assert len(far_students) == 2
        far_tzs = {s["student_tz"] for s in far_students}
        assert far_tzs == {s_far1.tz, s_far2.tz}

    def test_missing_student_location(self, session: Session):
        teacher = _create_teacher(session, "t6", "ClassMissLoc")
        s_loc = _create_student(session, "s6_loc", "ClassMissLoc")
        s_no_loc = _create_student(session, "s6_noloc", "ClassMissLoc")
        s_far_loc = _create_student(session, "s6_farloc", "ClassMissLoc")

        lat, lon = 31.0, 35.0
        _insert_location(session, teacher.tz, lat, lon)
        _insert_location(session, s_loc.tz, lat + 0.005, lon)
        _insert_location(session, s_far_loc.tz, lat + 0.1, lon)
        # s_no_loc gets no location

        far_students = get_far_students_service(session, teacher)
        assert len(far_students) == 1
        assert far_students[0]["student_tz"] == s_far_loc.tz

    def test_edge_case_exactly_on_boundary(self, session: Session):
        teacher = _create_teacher(session, "t7", "ClassEdge")
        s_exactly_3km = _create_student(session, "s7_exact", "ClassEdge")
        s_just_over_3km = _create_student(session, "s7_over", "ClassEdge")

        lat, lon = 31.0, 35.0
        _insert_location(session, teacher.tz, lat, lon)

        # 3.0 km offset in latitude = 3.0 / 6371.0 radians
        # To avoid floating point issues where dist becomes slightly > 3.0,
        # we'll use 2.99 km for the "close" boundary test.
        offset_2_99km_deg = math.degrees(2.99 / 6371.0)
        _insert_location(session, s_exactly_3km.tz, lat + offset_2_99km_deg, lon)
        
        offset_3_01km_deg = math.degrees(3.01 / 6371.0)
        _insert_location(session, s_just_over_3km.tz, lat + offset_3_01km_deg, lon)

        far_students = get_far_students_service(session, teacher)
        assert len(far_students) == 1
        assert far_students[0]["student_tz"] == s_just_over_3km.tz

    def test_stability_no_crash(self, session: Session):
        # Random mix of missing locations, close, and far students.
        teacher = _create_teacher(session, "t8", "ClassStability")
        students = [_create_student(session, f"s8_{i}", "ClassStability") for i in range(10)]

        lat, lon = 31.0, 35.0
        _insert_location(session, teacher.tz, lat, lon)

        for i, student in enumerate(students):
            if i % 3 == 0:
                pass # missing location
            elif i % 3 == 1:
                _insert_location(session, student.tz, lat + 0.001, lon) # close
            else:
                _insert_location(session, student.tz, lat + 0.5, lon) # far

        far_students = get_far_students_service(session, teacher)
        
        # Should be safe, return valid list
        assert isinstance(far_students, list)
        
        # There are 10 students: indices 2, 5, 8 are far (3 students)
        assert len(far_students) == 3
        far_tzs = {s["student_tz"] for s in far_students}
        assert far_tzs == {students[2].tz, students[5].tz, students[8].tz}
