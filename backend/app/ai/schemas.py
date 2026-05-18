"""Pure data structures for the AI layer and Safety Snapshot."""
from datetime import datetime
from pydantic import BaseModel, Field


class StudentSnapshot(BaseModel):
    student_tz: str
    has_location: bool
    distance_to_teacher_km: float | None
    is_far: bool
    is_isolated: bool
    anomalies: list[str] = Field(default_factory=list)


class ClassSafetySnapshot(BaseModel):
    schema_version: str = "1.0"
    generated_at: datetime
    class_name: str
    teacher_tz: str | None
    teacher_has_location: bool
    total_students: int
    students: list[StudentSnapshot]
    far_student_tzs: list[str]
    isolated_student_tzs: list[str]
    missing_location_tzs: list[str]
    severity_level: str
    deterministic_observations: list[str]


class OperationalSummaryResponse(BaseModel):
    summary: str
    risk_level: str
    key_points: list[str]
    generated_at: datetime
    source_schema_version: str = "1.0"
    is_fallback: bool = False

