"""Visualization pipeline orchestrator module.

Combines transformation, layout, and serialization stages into a single unified pipeline.
"""

from typing import Any
from app.graph import Graph
from app.visualization.exceptions import (
    TransformationError,
    SerializationError,
)
from app.visualization.layouts.exceptions import LayoutEngineError
from app.visualization.pipeline.exceptions import (
    LayoutStageError,
    SerializationStageError,
    TransformationStageError,
    VisualizationPipelineError,
)


class VisualizationPipeline:
    """Orchestrates transformation, layout placement, and serialization of a RepositoryGraph."""

    def __init__(
        self,
        transformer: Any,
        layout_engine: Any,
        serializer: Any,
    ) -> None:
        """Initializes VisualizationPipeline with injected dependencies.

        Args:
            transformer: Object satisfying the transform method (e.g. VisualizationTransformer).
            layout_engine: Object satisfying the layout method (e.g. BaseLayoutEngine).
            serializer: Object satisfying serialization to_dict / to_json (e.g. VisualizationSerializer).
        """
        self.transformer = transformer
        self.layout_engine = layout_engine
        self.serializer = serializer

    def generate(self, graph: Graph) -> dict[str, Any]:
        """Generates a fully positioned and serialized visualization from a RepositoryGraph.

        Args:
            graph: RepositoryGraph instance.

        Returns:
            Dictionary containing the serialized visualization graph.

        Raises:
            TransformationStageError: If transformation fails.
            LayoutStageError: If layout computation fails.
            SerializationStageError: If serialization fails.
            VisualizationPipelineError: For other general pipeline failures.
        """
        if graph is None:
            raise TransformationStageError("RepositoryGraph input cannot be None.")

        # 1. Transform Stage
        try:
            viz_graph = self.transformer.transform(graph)
        except TransformationError as err:
            raise TransformationStageError(f"Transformation stage failed: {err}") from err
        except Exception as err:
            raise TransformationStageError(f"Unexpected error in transformation stage: {err}") from err

        # 2. Layout Stage
        try:
            positioned_graph = self.layout_engine.layout(viz_graph)
        except LayoutEngineError as err:
            raise LayoutStageError(f"Layout stage failed: {err}") from err
        except Exception as err:
            raise LayoutStageError(f"Unexpected error in layout stage: {err}") from err

        # 3. Serialization Stage
        try:
            serialized_dict = self.serializer.to_dict(positioned_graph)
            return serialized_dict
        except SerializationError as err:
            raise SerializationStageError(f"Serialization stage failed: {err}") from err
        except Exception as err:
            raise SerializationStageError(f"Unexpected error in serialization stage: {err}") from err
