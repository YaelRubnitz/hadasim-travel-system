"""AI execution scheduler and debounce logic."""
import threading
from datetime import datetime, timedelta, timezone

# Cooldown duration before AI can be called again for the same class
DEFAULT_COOLDOWN_MINUTES = 10

class AIScheduler:
    """
    Decides WHEN the AI layer should be executed.
    Prevents spamming the AI provider during high-frequency events.
    Thread-safe in-memory cache for development/MVP.
    """
    def __init__(self, cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES):
        self.cooldown_minutes = cooldown_minutes
        self._last_run_cache: dict[str, datetime] = {}
        self._lock = threading.Lock()

    def should_run_ai(
        self, 
        class_name: str, 
        force_event: bool = False,
        current_time: datetime | None = None
    ) -> bool:
        """
        Returns True if the AI should generate a summary now.
        Updates the internal cache if returning True.
        
        Rules:
        1. If force_event is True, always return True (and update cooldown).
        2. If class has never had AI run, return True.
        3. If time since last run >= cooldown_minutes, return True.
        """
        now = current_time or datetime.now(timezone.utc)
        
        with self._lock:
            last_run = self._last_run_cache.get(class_name)
            
            # Forced event (e.g. state transition or manual trigger)
            if force_event:
                self._last_run_cache[class_name] = now
                return True
                
            # First time
            if last_run is None:
                self._last_run_cache[class_name] = now
                return True
                
            # Time-based batching (cooldown expired)
            elapsed = now - last_run
            if elapsed >= timedelta(minutes=self.cooldown_minutes):
                self._last_run_cache[class_name] = now
                return True
                
            # Still in cooldown
            return False
