"""In-memory cache for AI responses."""
import threading
from datetime import datetime
from app.ai.schemas import OperationalSummaryResponse

class AICache:
    """
    Thread-safe in-memory cache to store the last generated AI summary per class.
    """
    def __init__(self):
        self._cache: dict[str, OperationalSummaryResponse] = {}
        self._lock = threading.Lock()

    def get(self, class_name: str) -> OperationalSummaryResponse | None:
        with self._lock:
            return self._cache.get(class_name)

    def set(self, class_name: str, response: OperationalSummaryResponse) -> None:
        with self._lock:
            self._cache[class_name] = response

# Global instance for MVP
ai_response_cache = AICache()
