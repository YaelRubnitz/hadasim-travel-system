"""Mock AI provider for testing and safe fallbacks."""
from datetime import datetime, timezone
import asyncio

from app.ai.providers.base import AIProvider
from app.ai.schemas import OperationalSummaryResponse

class MockProvider(AIProvider):
    """
    Deterministic mock provider that simulates an AI response based on keywords
    in the prompt. Ensures UI and orchestration can be tested without 
    external network calls or non-deterministic outputs.
    """
    
    def __init__(self, simulate_latency_s: float = 0.0, simulate_error: bool = False):
        self.simulate_latency_s = simulate_latency_s
        self.simulate_error = simulate_error

    async def generate_operational_summary(self, prompt: str) -> OperationalSummaryResponse:
        if self.simulate_latency_s > 0:
            await asyncio.sleep(self.simulate_latency_s)
            
        if self.simulate_error:
            raise RuntimeError("Simulated AI provider error")
            
        # Very naive deterministic simulation based on prompt content
        risk_level = "NORMAL"
        summary = "Class is grouped and normal."
        key_points = []
        
        if "CRITICAL" in prompt:
            risk_level = "CRITICAL"
            summary = "Critical alert: Students are isolated or significantly separated from the group."
            key_points.append("Immediate teacher intervention recommended.")
        elif "WARNING" in prompt:
            risk_level = "WARNING"
            summary = "Warning: Some students are far or missing location data."
            key_points.append("Monitor far students.")
            
        if "missing" in prompt.lower() and "location data" in prompt.lower():
            key_points.append("Some students lack location updates.")
            
        return OperationalSummaryResponse(
            summary=summary,
            risk_level=risk_level,
            key_points=key_points,
            generated_at=datetime.now(timezone.utc),
            source_schema_version="1.0"
        )
