"""In-memory time-series buffer for recent telemetry history."""

from collections import deque
from typing import Dict, List
import time


class FlightRecorder:
    """Stores recent telemetry samples by key with a rolling time window."""

    def __init__(self, history_seconds: int = 60) -> None:
        self.history_seconds = history_seconds
        self.buffers: Dict[str, deque] = {}

    def log(self, key: str, value: float) -> None:
        """Append a value for a key, ignoring missing/invalid inputs."""
        if value is None:
            return
        try:
            num = float(value)
        except (TypeError, ValueError):
            return

        if key not in self.buffers:
            self.buffers[key] = deque(maxlen=self.history_seconds * 2)

        self.buffers[key].append((time.time(), num))

    def get_history(self, key: str) -> List[float]:
        """Return recent values for a key within the history window."""
        if key not in self.buffers:
            return []

        cutoff = time.time() - self.history_seconds
        return [val for ts, val in self.buffers[key] if ts >= cutoff]


recorder = FlightRecorder(history_seconds=300)
