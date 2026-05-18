import pytest
from datetime import datetime, timedelta, timezone
from app.ai.scheduler.scheduler import AIScheduler

def test_scheduler_first_run():
    scheduler = AIScheduler(cooldown_minutes=10)
    now = datetime.now(timezone.utc)
    
    # Should run on first check
    assert scheduler.should_run_ai("Class A", current_time=now) is True

def test_scheduler_cooldown_enforced():
    scheduler = AIScheduler(cooldown_minutes=10)
    now = datetime.now(timezone.utc)
    
    # First run
    assert scheduler.should_run_ai("Class A", current_time=now) is True
    
    # Immediately after -> should be false
    assert scheduler.should_run_ai("Class A", current_time=now) is False
    
    # 5 minutes later -> should be false
    five_mins_later = now + timedelta(minutes=5)
    assert scheduler.should_run_ai("Class A", current_time=five_mins_later) is False

def test_scheduler_cooldown_expired():
    scheduler = AIScheduler(cooldown_minutes=10)
    now = datetime.now(timezone.utc)
    
    # First run
    scheduler.should_run_ai("Class A", current_time=now)
    
    # 11 minutes later -> should be true
    eleven_mins_later = now + timedelta(minutes=11)
    assert scheduler.should_run_ai("Class A", current_time=eleven_mins_later) is True

def test_scheduler_forced_event():
    scheduler = AIScheduler(cooldown_minutes=10)
    now = datetime.now(timezone.utc)
    
    # First run
    scheduler.should_run_ai("Class A", current_time=now)
    
    # 2 minutes later but forced
    two_mins_later = now + timedelta(minutes=2)
    assert scheduler.should_run_ai("Class A", force_event=True, current_time=two_mins_later) is True
    
    # Immediate normal check after forced run should fail (cooldown reset)
    assert scheduler.should_run_ai("Class A", current_time=two_mins_later) is False

def test_scheduler_independent_classes():
    scheduler = AIScheduler(cooldown_minutes=10)
    now = datetime.now(timezone.utc)
    
    # Run Class A
    assert scheduler.should_run_ai("Class A", current_time=now) is True
    
    # Class B should still run independently
    assert scheduler.should_run_ai("Class B", current_time=now) is True
    
    # Class A is still cooling down
    assert scheduler.should_run_ai("Class A", current_time=now) is False
