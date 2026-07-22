"""Base graph builder interface module.

Defines abstract BaseGraphBuilder interface for graph construction strategies.
"""

from abc import ABC, abstractmethod
from typing import Any
from app.graph.graph import Graph


class BaseGraphBuilder(ABC):
    """Abstract base class interface for graph builder strategies."""

    @abstractmethod
    def build(self, context: Any) -> Graph:
        """Builds and returns a canonical Graph instance from the provided context.

        Args:
            context: Input context model or data structure.

        Returns:
            A populated Graph container.

        Raises:
            GraphBuilderError: If graph construction fails.
        """
        pass
