"""Visualization service module.

Orchestrates the visualization generation pipeline.
"""

from typing import Any
from app.graph import Graph as RepositoryGraph
from app.visualization.pipeline import VisualizationPipeline


class VisualizationService:
    """Service layer orchestrating the visualization pipeline."""

    def __init__(self, pipeline: VisualizationPipeline) -> None:
        """Initializes VisualizationService with a visualization pipeline.

        Args:
            pipeline: VisualizationPipeline instance.
        """
        self.pipeline = pipeline

    def generate_visualization(self, graph: RepositoryGraph) -> dict[str, Any]:
        """Orchestrates visualization generation by invoking the pipeline.

        Args:
            graph: RepositoryGraph instance.

        Returns:
            Serialized visualization dictionary.
        """
        return self.pipeline.generate(graph)
