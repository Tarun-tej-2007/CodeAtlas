"""Visualization profiler module.

Measures execution duration metrics for pipeline stages.
"""

import time


class VisualizationProfiler:
    """Helper class to measure timing details for pipeline executions."""

    def __init__(self, enabled: bool = True) -> None:
        """Initializes VisualizationProfiler.

        Args:
            enabled: If False, measurements are skipped to minimize overhead.
        """
        self.enabled = enabled
        self._timings: dict[str, float] = {}

    def start(self, stage: str) -> None:
        """Starts timing a specific stage."""
        if self.enabled:
            self._timings[f"{stage}_start"] = time.perf_counter()

    def stop(self, stage: str) -> float:
        """Stops timing a specific stage and returns duration in milliseconds."""
        if not self.enabled:
            return 0.0

        start_key = f"{stage}_start"
        if start_key in self._timings:
            duration = (time.perf_counter() - self._timings[start_key]) * 1000.0
            self._timings[f"{stage}_duration"] = duration
            return round(duration, 3)
        return 0.0

    def get_duration(self, stage: str) -> float:
        """Returns computed duration in milliseconds for the specified stage."""
        return round(self._timings.get(f"{stage}_duration", 0.0), 3)
