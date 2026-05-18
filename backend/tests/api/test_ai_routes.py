import pytest
from httpx import AsyncClient
from app.main import app
from app.ai.cache.cache import ai_response_cache
from app.services.ai_service import ai_scheduler

@pytest.fixture(autouse=True)
def reset_ai_state():
    # Clear cache and scheduler state before each test
    ai_response_cache._cache.clear()
    ai_scheduler._last_run_cache.clear()

@pytest.mark.asyncio
async def test_get_ai_summary_success(client, teacher, student_near):
    # Authenticate
    client.cookies.set("access_token", "fake-jwt-token")
    
    # First call - should trigger AI and return NORMAL because student is near
    response = client.get(f"/ai/class/{teacher.class_name}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "NORMAL"
    assert data["is_fallback"] is False
    assert "summary" in data

@pytest.mark.asyncio
async def test_get_ai_summary_cooldown_and_cache(client, teacher, student_near):
    client.cookies.set("access_token", "fake-jwt-token")
    
    # 1. Initial call
    resp1 = client.get(f"/ai/class/{teacher.class_name}/summary")
    assert resp1.status_code == 200
    data1 = resp1.json()
    
    # 2. Second call immediately (should be blocked by scheduler and return cached)
    resp2 = client.get(f"/ai/class/{teacher.class_name}/summary")
    assert resp2.status_code == 200
    data2 = resp2.json()
    
    # The generated_at timestamp should be exactly the same since it's cached
    assert data1["generated_at"] == data2["generated_at"]

@pytest.mark.asyncio
async def test_force_ai_summary_bypasses_cooldown(client, teacher, student_near):
    client.cookies.set("access_token", "fake-jwt-token")
    
    # 1. Initial normal call
    resp1 = client.get(f"/ai/class/{teacher.class_name}/summary")
    assert resp1.status_code == 200
    data1 = resp1.json()
    
    # 2. Forced call immediately
    resp2 = client.post(f"/ai/class/{teacher.class_name}/summary/force")
    assert resp2.status_code == 200
    data2 = resp2.json()
    
    # The generated_at timestamp should be different since forced bypassed cooldown
    assert data1["generated_at"] != data2["generated_at"]

@pytest.mark.asyncio
async def test_ai_summary_no_students_fallback(client, teacher):
    # Teacher has no students created in the fixture yet
    client.cookies.set("access_token", "fake-jwt-token")
    
    response = client.get(f"/ai/class/{teacher.class_name}/summary")
    # Our ai service raises 404 if no students exist for the class
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ai_summary_provider_failure_fallback(client, teacher, student_near):
    from app.services.ai_service import ai_orchestrator
    
    # Temporarily force the mock provider to throw an error
    original_simulate = ai_orchestrator.provider.simulate_error
    ai_orchestrator.provider.simulate_error = True
    
    try:
        client.cookies.set("access_token", "fake-jwt-token")
        response = client.get(f"/ai/class/{teacher.class_name}/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["is_fallback"] is True
        assert "unavailable" in data["summary"].lower()
    finally:
        # Restore state
        ai_orchestrator.provider.simulate_error = original_simulate
