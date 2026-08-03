"""AI Context Builder Interface module.

Defines the abstract interface and pipeline contract for building structured
context packages for downstream LLMs.
"""

from abc import ABC, abstractmethod

from app.ai.models import AIContextResult


class AIContextBuilder(ABC):
    """Abstract base class establishing the contract for AI context compilers."""

    @abstractmethod
    def build_context(self, *args, **kwargs) -> AIContextResult:
        """Constructs the structured context representation of the codebase.

        Must yield an immutable AIContextResult payload populated with sections,
        symbols, or repository definitions.
        """
        pass
