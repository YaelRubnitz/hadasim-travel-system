"""Future hooks and guards for AI output validation."""
from datetime import datetime, timezone
from app.ai.schemas import ClassSafetySnapshot, OperationalSummaryResponse

def validate_ai_summary(snapshot: ClassSafetySnapshot, ai_output: OperationalSummaryResponse) -> bool:
    """
    Validates that the AI output does not contradict the deterministic snapshot.
    This acts as a guardrail against hallucinations.
    """
    # Basic validation: ensure critical severity wasn't downgraded
    if snapshot.severity_level == "CRITICAL" and ai_output.risk_level == "NORMAL":
        return False
        
    if not ai_output.summary:
        return False
        
    return True

def build_fallback_response(snapshot: ClassSafetySnapshot) -> OperationalSummaryResponse:
    """
    Provides a completely deterministic fallback response if the AI generation 
    fails, times out, or produces invalid output.
    """
    return OperationalSummaryResponse(
        summary="AI operational summary unavailable. Please refer to the raw metrics.",
        risk_level=snapshot.severity_level,
        key_points=snapshot.deterministic_observations,
        generated_at=datetime.now(timezone.utc),
        source_schema_version=snapshot.schema_version,
        is_fallback=True
    )

