"""Service layer for AI operations, integrating deterministic analytics with AI orchestration."""

from sqlmodel import Session
from fastapi import HTTPException
from sqlmodel import select

from app.models.student import Student
from app.locations.series import fetch_class_tracks, fetch_track
from app.locations.analytics.proximity import build_class_proximity_snapshot
from app.ai.snapshot_builder import build_class_safety_snapshot
from app.ai.scheduler.scheduler import AIScheduler
from app.ai.orchestration.orchestrator import AIOrchestrator
from app.ai.providers.mock_provider import MockProvider
from app.ai.cache.cache import ai_response_cache
from app.ai.schemas import OperationalSummaryResponse
from app.ai.validators import build_fallback_response

# Global instances for the MVP
ai_scheduler = AIScheduler(cooldown_minutes=10)
# We inject the MockProvider here. In the future, this could be configured via env vars.
ai_orchestrator = AIOrchestrator(provider=MockProvider())


async def get_class_ai_summary_service(
    session: Session, 
    class_name: str, 
    teacher_tz: str | None = None, 
    force: bool = False
) -> OperationalSummaryResponse:
    """
    End-to-end integration:
    1. Fetch deterministic location data
    2. Build safety snapshot
    3. Check scheduler
    4. Call AI or return cached/fallback
    """
    
    # 1. Fetch all students in the class to know who is missing
    student_tzs = session.exec(
        select(Student.tz).where(Student.class_name == class_name)
    ).all()
    
    if not student_tzs:
        raise HTTPException(status_code=404, detail=f"No students found for class {class_name}")

    # 2. Fetch latest points (limit_per_student=1 is sufficient for proximity snapshot)
    student_tracks = fetch_class_tracks(session, class_name, limit_per_student=1)
    
    student_points = {}
    for tz, track in student_tracks.items():
        if track.points:
            student_points[tz] = track.points[-1]

    teacher_point = None
    if teacher_tz:
        teacher_track = fetch_track(session, teacher_tz, limit=1)
        if teacher_track.points:
            teacher_point = teacher_track.points[-1]

    # 3. Build deterministic proximity snapshot
    proximity_snapshot = build_class_proximity_snapshot(
        class_name=class_name,
        student_points=student_points,
        teacher_point=teacher_point
    )

    # 4. Build safety snapshot for AI
    safety_snapshot = build_class_safety_snapshot(
        proximity_snapshot=proximity_snapshot,
        teacher_tz=teacher_tz,
        all_student_tzs=list(student_tzs),
        students_with_location=set(student_points.keys())
    )

    # 5. Check scheduler
    if ai_scheduler.should_run_ai(class_name, force_event=force):
        # Run AI Orchestrator
        ai_response = await ai_orchestrator.generate_summary(safety_snapshot)
        
        # Cache the result
        ai_response_cache.set(class_name, ai_response)
        return ai_response
    else:
        # Return cached response, or fallback if nothing is cached yet
        cached_response = ai_response_cache.get(class_name)
        if cached_response:
            return cached_response
            
        return build_fallback_response(safety_snapshot)
