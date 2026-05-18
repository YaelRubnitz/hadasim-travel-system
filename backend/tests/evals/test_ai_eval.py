"""
Evaluation tests for the AI layer.
These tests validate the factual consistency and prompt constraints of the AI orchestration,
ensuring it meets evaluation criteria without requiring actual LLM network calls yet.
"""

import pytest
from datetime import datetime, timezone
from app.ai.schemas import ClassSafetySnapshot, OperationalSummaryResponse
from app.ai.validators import validate_ai_summary

@pytest.fixture
def test_snapshot():
    return ClassSafetySnapshot(
        generated_at=datetime.now(timezone.utc),
        class_name="Eval Class",
        teacher_tz="t1",
        teacher_has_location=True,
        total_students=4,
        students=[],
        far_student_tzs=["s1", "s2"],
        isolated_student_tzs=["s3"],
        missing_location_tzs=[],
        severity_level="CRITICAL",
        deterministic_observations=["3 students are far or isolated."]
    )

def test_eval_factual_consistency(test_snapshot):
    """
    Eval: AI output must not downgrade critical deterministic alerts.
    """
    # A valid summary correctly matching the severity
    valid_response = OperationalSummaryResponse(
        summary="Critical: students isolated and far.",
        risk_level="CRITICAL",
        key_points=[],
        generated_at=datetime.now(timezone.utc)
    )
    assert validate_ai_summary(test_snapshot, valid_response) is True

def test_eval_hallucination_prevention(test_snapshot):
    """
    Eval: AI output must not contradict deterministic facts by lowering risk level.
    """
    # An invalid summary that hallucinates a normal state when it's critical
    invalid_response = OperationalSummaryResponse(
        summary="Everything is fine.",
        risk_level="NORMAL",
        key_points=[],
        generated_at=datetime.now(timezone.utc)
    )
    assert validate_ai_summary(test_snapshot, invalid_response) is False

def test_eval_empty_response(test_snapshot):
    """
    Eval: AI output must not be completely empty.
    """
    empty_response = OperationalSummaryResponse(
        summary="",
        risk_level="CRITICAL",
        key_points=[],
        generated_at=datetime.now(timezone.utc)
    )
    assert validate_ai_summary(test_snapshot, empty_response) is False
