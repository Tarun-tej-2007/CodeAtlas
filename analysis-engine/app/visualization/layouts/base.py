"""Base graph layout engine interface module.

Defines the abstract BaseLayoutEngine interface for coordinate computation algorithms.
"""

from abc import ABC, abstractmethod
from app.visualization.models import VisualizationGraph


class BaseLayoutEngine(ABC):
    """Abstract base class interface for graph layout algorithms."""

    @abstractmethod
    def layout(self, graph: VisualizationGraph) -> VisualizationGraph:
        """Computes coordinate positions for all nodes in the visualization graph.

        Args:
            graph: Input VisualizationGraph container (must remain unmodified).

        Returns:
            A new VisualizationGraph instance populated with computed positions.

        Raises:
            LayoutEngineError: If layout computation fails.
        """
        pass
