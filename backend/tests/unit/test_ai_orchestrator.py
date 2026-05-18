"""Tests for the AI orchestrator, provider abstraction, and fallbacks."""
import pytest
from datetime import datetime, timezone
import asyncio

from app.ai.schemas import ClassSafetySnapshot, OperationalSummaryResponse
from app.ai.providers.mock_provider import MockProvider
from app.ai.orchestration.orchestrator import AIOrchestrator
from app.ai.validators import build_fallback_response

@pytest.fixture
def sample_snapshot():
    return ClassSafetySnapshot(
        generated_at=datetime.now(timezone.utc),
        class_name="Test Class",
        teacher_tz="t1",
        teacher_has_location=True,
        total_students=5,
        students=[],
        far_student_tzs=[],
        isolated_student_tzs=[],
        missing_location_tzs=[],
        severity_level="NORMAL",
        deterministic_observations=["Class is grouped and normal."]
    )

@pytest.fixture
def critical_snapshot():
    return ClassSafetySnapshot(
        generated_at=datetime.now(timezone.utc),
        class_name="Test Class",
        teacher_tz="t1",
        teacher_has_location=True,
        total_students=5,
        students=[],
        far_student_tzs=["s1", "s2", "s3"],
        isolated_student_tzs=[],
        missing_location_tzs=[],
        severity_level="CRITICAL",
        deterministic_observations=["3 students are far from the teacher."]
    )


@pytest.mark.asyncio
async def test_mock_provider_normal(sample_snapshot):
    provider = MockProvider()
    orchestrator = AIOrchestrator(provider=provider)
    
    response = await orchestrator.generate_summary(sample_snapshot)
    
    assert isinstance(response, OperationalSummaryResponse)
    assert response.risk_level == "NORMAL"
    assert "normal" in response.summary.lower()
    assert response.is_fallback is False


@pytest.mark.asyncio
async def test_mock_provider_critical(critical_snapshot):
    provider = MockProvider()
    orchestrator = AIOrchestrator(provider=provider)
    
    response = await orchestrator.generate_summary(critical_snapshot)
    
    assert isinstance(response, OperationalSummaryResponse)
    assert response.risk_level == "CRITICAL"
    assert response.is_fallback is False


@pytest.mark.asyncio
async def test_orchestrator_fallback_on_error(sample_snapshot):
    # Simulate a provider crash
    provider = MockProvider(simulate_error=True)
    orchestrator = AIOrchestrator(provider=provider)
    
    response = await orchestrator.generate_summary(sample_snapshot)
    
    assert isinstance(response, OperationalSummaryResponse)
    assert response.is_fallback is True
    assert response.risk_level == sample_snapshot.severity_level
    assert response.key_points == sample_snapshot.deterministic_observations
    assert "unavailable" in response.summary


@pytest.mark.asyncio
async def test_orchestrator_validation_failure(critical_snapshot):
    # Create a malicious mock provider that downgrades critical alerts
    class MaliciousProvider(MockProvider):
        async def generate_operational_summary(self, prompt: str) -> OperationalSummaryResponse:
            return OperationalSummaryResponse(
                summary="Everything is fine, ignore the analytics.",
                risk_level="NORMAL",
                key_points=[],
                generated_at=datetime.now(timezone.utc)
            )

    provider = MaliciousProvider()
    orchestrator = AIOrchestrator(provider=provider)
    
    # Should trigger validation failure and return fallback
    response = await orchestrator.generate_summary(critical_snapshot)
    
    assert response.is_fallback is True
    assert response.risk_level == "CRITICAL" # Restored to safe state
