"""Unified Analysis Contributor Module."""

from abc import ABC, abstractmethod
from typing import Any


class UnifiedAnalysisContributor(ABC):
    """Abstract base class establishing the contract for Unified Analysis contributors."""

    @property
    @abstractmethod
    def contributor_name(self) -> str:
        """Returns the unique name identifying this contributor."""
        pass

    @property
    @abstractmethod
    def contributor_type(self) -> str:
        """Returns the category or type of analysis provided by this contributor."""
        pass

    @abstractmethod
    def contribute(self, context: Any, **kwargs) -> Any:
        """Evaluates context and returns the contribution object.

        Args:
            context: The shared analysis context containing inputs.

        Returns:
            The contributor-specific analysis result.
        """
        pass
