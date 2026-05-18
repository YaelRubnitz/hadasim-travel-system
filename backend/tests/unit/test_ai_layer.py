"""Tests for the AI architecture layer (snapshot and prompt generation)."""
from datetime import datetime, timezone
import pytest

from app.ai.schemas import ClassSafetySnapshot, StudentSnapshot
from app.ai.snapshot_builder import build_class_safety_snapshot, determine_severity
from app.ai.prompt_builder import build_operational_summary_prompt
from app.ai.validators import validate_ai_summary
from app.locations.analytics.proximity import ClassProximitySnapshot
from app.locations.types import TrackPoint

def test_determine_severity():
    assert determine_severity(far_count=0, isolated_count=0, missing_count=0) == "NORMAL"
    assert determine_severity(far_count=1, isolated_count=0, missing_count=0) == "WARNING"
    assert determine_severity(far_count=0, isolated_count=0, missing_count=1) == "WARNING"
    assert determine_severity(far_count=3, isolated_count=0, missing_count=0) == "CRITICAL"
    assert determine_severity(far_count=0, isolated_count=1, missing_count=0) == "CRITICAL"


def test_build_class_safety_snapshot():
    proximity = ClassProximitySnapshot(
        class_name="Class A",
        recorded_at=datetime.now(timezone.utc),
        centroid=None,
        teacher_point=TrackPoint(
            id=1,
            student_tz="teacher",
            latitude=31.0,
            longitude=35.0,
            recorded_at=datetime.now(timezone.utc),
        ),
        student_distances_to_teacher_km={"student_1": 1.0, "student_2": 4.0},
        student_distances_to_centroid_m={},
        far_from_teacher=["student_2"],
        isolated=[],
    )
    
    all_student_tzs = ["student_1", "student_2", "student_3"]
    students_with_location = {"student_1", "student_2"}
    
    snapshot = build_class_safety_snapshot(
        proximity_snapshot=proximity,
        teacher_tz="teacher",
        all_student_tzs=all_student_tzs,
        students_with_location=students_with_location,
        student_anomalies={"student_1": ["jump"]}
    )
    
    assert snapshot.schema_version == "1.0"
    assert snapshot.class_name == "Class A"
    assert snapshot.teacher_has_location is True
    assert snapshot.total_students == 3
    assert snapshot.far_student_tzs == ["student_2"]
    assert snapshot.missing_location_tzs == ["student_3"]
    assert snapshot.severity_level == "WARNING"
    
    # Check student 1
    s1 = next(s for s in snapshot.students if s.student_tz == "student_1")
    assert s1.has_location is True
    assert s1.distance_to_teacher_km == 1.0
    assert s1.is_far is False
    assert s1.anomalies == ["jump"]
    
    # Check student 3
    s3 = next(s for s in snapshot.students if s.student_tz == "student_3")
    assert s3.has_location is False
    assert s3.distance_to_teacher_km is None


def test_build_operational_summary_prompt():
    proximity = ClassProximitySnapshot(
        class_name="Class B",
        recorded_at=datetime.now(timezone.utc),
        centroid=None,
        teacher_point=None,
        student_distances_to_teacher_km={},
        student_distances_to_centroid_m={},
        far_from_teacher=[],
        isolated=[],
    )
    snapshot = build_class_safety_snapshot(
        proximity_snapshot=proximity,
        teacher_tz="teacher2",
        all_student_tzs=["s1"],
        students_with_location={"s1"}
    )
    
    prompt = build_operational_summary_prompt(snapshot)
    
    assert "operational safety AI assistant" in prompt
    assert "RULES:" in prompt
    assert "DO NOT calculate distances" in prompt
    assert snapshot.model_dump_json(indent=2) in prompt


def test_validate_ai_summary():
    # Placeholder test for the validator architecture
    assert validate_ai_summary(None, "Everything is fine") is True
