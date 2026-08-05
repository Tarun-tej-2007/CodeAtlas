"""Report Generator Registry Module."""

import threading
from typing import Dict, Tuple

from app.reporting.exceptions import ReportGenerationError
from app.reporting.generator import ReportGenerator


class ReportGeneratorRegistry:
    """Thread-safe, insertion-order preserving registry for managing ReportGenerators."""

    def __init__(self) -> None:
        """Initializes the registry with a thread lock and empty generator storage."""
        self._lock = threading.Lock()
        self._generators: Dict[str, ReportGenerator] = {}

    def register(self, name: str, generator: ReportGenerator) -> None:
        """Registers a new ReportGenerator under a unique name.

        Raises ReportGenerationError on duplicate or invalid registrations.
        """
        if not name or not name.strip():
            raise ReportGenerationError("Generator name must not be empty or whitespace-only.")
        if generator is None:
            raise ReportGenerationError("Cannot register None generator.")
        if not isinstance(generator, ReportGenerator):
            raise ReportGenerationError("Registered object must inherit from ReportGenerator.")

        with self._lock:
            if name in self._generators:
                raise ReportGenerationError(f"Generator '{name}' is already registered.")
            self._generators[name] = generator

    def unregister(self, name: str) -> None:
        """Removes a registered generator by name.

        Raises ReportGenerationError if not found.
        """
        if not name or not name.strip():
            raise ReportGenerationError("Generator name must not be empty or whitespace-only.")

        with self._lock:
            if name not in self._generators:
                raise ReportGenerationError(f"Generator '{name}' is not registered.")
            del self._generators[name]

    def get(self, name: str) -> ReportGenerator:
        """Retrieves a registered generator by name.

        Raises ReportGenerationError if not found.
        """
        if not name or not name.strip():
            raise ReportGenerationError("Generator name must not be empty or whitespace-only.")

        with self._lock:
            generator = self._generators.get(name)
            if generator is None:
                raise ReportGenerationError(f"Generator '{name}' is not registered.")
            return generator

    def contains(self, name: str) -> bool:
        """Checks if a generator is registered under the given name."""
        if not name or not name.strip():
            return False

        with self._lock:
            return name in self._generators

    def list_generators(self) -> Tuple[ReportGenerator, ...]:
        """Returns all registered generators, preserving their deterministic insertion order."""
        with self._lock:
            return tuple(self._generators.values())

    def clear(self) -> None:
        """Clears all generators from the registry."""
        with self._lock:
            self._generators.clear()

    def __len__(self) -> int:
        """Returns the number of registered generators."""
        with self._lock:
            return len(self._generators)
