"""Base interface for AI providers."""
from abc import ABC, abstractmethod
from app.ai.schemas import OperationalSummaryResponse

class AIProvider(ABC):
    """
    Abstract interface for AI generation providers (e.g., Mock, OpenAI, Anthropic).
    Decouples the business logic from specific vendor SDKs.
    """
    
    @abstractmethod
    async def generate_operational_summary(self, prompt: str) -> OperationalSummaryResponse:
        """
        Takes a highly structured prompt and returns a strictly typed 
        OperationalSummaryResponse. Must handle its own network errors
        and raise appropriate exceptions or return fallbacks.
        """
        pass
