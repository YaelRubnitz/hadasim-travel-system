"""Constructs a deterministic safety snapshot from pure analytics."""
from datetime import datetime, timezone
from app.ai.schemas import ClassSafetySnapshot, StudentSnapshot
from app.locations.analytics.proximity import ClassProximitySnapshot

def determine_severity(far_count: int, isolated_count: int, missing_count: int) -> str:
    """Returns a deterministic severity level based on counts."""
    if isolated_count > 0 or far_count > 2:
        return "CRITICAL"
    if far_count > 0 or missing_count > 0:
        return "WARNING"
    return "NORMAL"

def build_class_safety_snapshot(
    proximity_snapshot: ClassProximitySnapshot,
    teacher_tz: str | None,
    all_student_tzs: list[str],
    students_with_location: set[str],
    student_anomalies: dict[str, list[str]] | None = None
) -> ClassSafetySnapshot:
    """
    Builds a pure factual snapshot of the class state.
    This acts as the deterministic bridge between analytics and the AI layer.
    """
    student_anomalies = student_anomalies or {}
    
    far_tzs = proximity_snapshot.far_from_teacher
    isolated_tzs = [iso.student_tz for iso in proximity_snapshot.isolated]
    missing_tzs = [tz for tz in all_student_tzs if tz not in students_with_location]
    
    students = []
    for tz in all_student_tzs:
        is_far = tz in far_tzs
        is_isolated = tz in isolated_tzs
        has_location = tz in students_with_location
        dist_km = proximity_snapshot.student_distances_to_teacher_km.get(tz)
        anomalies = student_anomalies.get(tz, [])
        
        students.append(
            StudentSnapshot(
                student_tz=tz,
                has_location=has_location,
                distance_to_teacher_km=dist_km,
                is_far=is_far,
                is_isolated=is_isolated,
                anomalies=anomalies
            )
        )
    
    severity = determine_severity(
        far_count=len(far_tzs),
        isolated_count=len(isolated_tzs),
        missing_count=len(missing_tzs)
    )
    
    observations = []
    if len(far_tzs) > 0:
        observations.append(f"{len(far_tzs)} students are far from the teacher.")
    if len(isolated_tzs) > 0:
        observations.append(f"{len(isolated_tzs)} students are isolated.")
    if len(missing_tzs) > 0:
        observations.append(f"{len(missing_tzs)} students have no location data.")
    if severity == "NORMAL":
        observations.append("Class is grouped and normal.")
    
    return ClassSafetySnapshot(
        generated_at=datetime.now(timezone.utc),
        class_name=proximity_snapshot.class_name,
        teacher_tz=teacher_tz,
        teacher_has_location=proximity_snapshot.teacher_point is not None,
        total_students=len(all_student_tzs),
        students=students,
        far_student_tzs=far_tzs,
        isolated_student_tzs=isolated_tzs,
        missing_location_tzs=missing_tzs,
        severity_level=severity,
        deterministic_observations=observations
    )
