"""Orchestrates the AI pipeline for operational summaries."""
import logging
from app.ai.schemas import ClassSafetySnapshot, OperationalSummaryResponse
from app.ai.prompt_builder import build_operational_summary_prompt
from app.ai.providers.base import AIProvider
from app.ai.validators import validate_ai_summary, build_fallback_response

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Single entry point for the AI presentation layer.
    Manages the pipeline: snapshot -> prompt -> provider -> validation -> output.
    """
    
    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def generate_summary(self, snapshot: ClassSafetySnapshot) -> OperationalSummaryResponse:
        """
        Orchestrates the generation of an operational summary.
        Guarantees a safe fallback response if anything fails.
        """
        prompt = build_operational_summary_prompt(snapshot)
        
        try:
            # The AI is purely presentational, not safety-critical.
            # We catch all exceptions to prevent breaking the main application.
            response = await self.provider.generate_operational_summary(prompt)
            
            if validate_ai_summary(snapshot, response):
                return response
            else:
                logger.warning("AI output failed validation. Falling back to deterministic summary.")
                return build_fallback_response(snapshot)
                
        except Exception as e:
            logger.error(f"AI provider failed: {e}. Falling back to deterministic summary.")
            return build_fallback_response(snapshot)
