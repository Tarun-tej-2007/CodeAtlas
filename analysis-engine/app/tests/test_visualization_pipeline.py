"""Unit test suite for VisualizationPipeline and visualization pipeline orchestrator."""

import unittest
from unittest.mock import MagicMock
from pydantic import ValidationError

from app.graph import Graph as RepositoryGraph
from app.graph import GraphMetadata
from app.visualization import (
    TransformationStageError,
    LayoutStageError,
    SerializationStageError,
    VisualizationGraph,
    VisualizationPipeline,
    VisualizationPipelineConfig,
)
from app.visualization.exceptions import TransformationError, SerializationError
from app.visualization.layouts.exceptions import LayoutEngineError


class TestVisualizationPipeline(unittest.TestCase):
    """Tests for VisualizationPipeline stages, dependency injection, and error propagation."""

    def setUp(self) -> None:
        self.mock_transformer = MagicMock()
        self.mock_layout_engine = MagicMock()
        self.mock_serializer = MagicMock()

        self.pipeline = VisualizationPipeline(
            transformer=self.mock_transformer,
            layout_engine=self.mock_layout_engine,
            serializer=self.mock_serializer,
        )

        self.repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="TestProject"))
        self.viz_graph = MagicMock(spec=VisualizationGraph)
        self.positioned_graph = MagicMock(spec=VisualizationGraph)
        self.serialized_dict = {"nodes": [], "edges": [], "metadata": {}}

    def test_pipeline_config_immutability(self) -> None:
        config = VisualizationPipelineConfig()
        # Ensure it works and fields are read-only
        self.assertEqual(config.rendering_options, {})
        with self.assertRaises(ValidationError if hasattr(config, "__pydantic_validator__") else Exception):
            config.layout_type = "invalid"  # type: ignore

    def test_successful_pipeline_execution_flow(self) -> None:
        # Arrange mock responses
        self.mock_transformer.transform.return_value = self.viz_graph
        self.mock_layout_engine.layout.return_value = self.positioned_graph
        self.mock_serializer.to_dict.return_value = self.serialized_dict

        # Act
        result = self.pipeline.generate(self.repo_graph)

        # Assert
        self.assertEqual(result, self.serialized_dict)

        # Verify execution order and dependency usage
        self.mock_transformer.transform.assert_called_once_with(self.repo_graph)
        self.mock_layout_engine.layout.assert_called_once_with(self.viz_graph)
        self.mock_serializer.to_dict.assert_called_once_with(self.positioned_graph)

    def test_null_graph_raises_transformation_stage_error(self) -> None:
        with self.assertRaises(TransformationStageError):
            self.pipeline.generate(None)  # type: ignore

    def test_transformer_failure_propagates_transformation_stage_error(self) -> None:
        # Arrange mock to raise error
        self.mock_transformer.transform.side_effect = TransformationError("Transformer failed!")

        # Act & Assert
        with self.assertRaises(TransformationStageError) as context:
            self.pipeline.generate(self.repo_graph)

        self.assertIn("Transformation stage failed", str(context.exception))
        # Ensure downstream components were not called
        self.mock_layout_engine.layout.assert_not_called()
        self.mock_serializer.to_dict.assert_not_called()

    def test_layout_engine_failure_propagates_layout_stage_error(self) -> None:
        # Arrange
        self.mock_transformer.transform.return_value = self.viz_graph
        self.mock_layout_engine.layout.side_effect = LayoutEngineError("Layout failed!")

        # Act & Assert
        with self.assertRaises(LayoutStageError) as context:
            self.pipeline.generate(self.repo_graph)

        self.assertIn("Layout stage failed", str(context.exception))
        self.mock_serializer.to_dict.assert_not_called()

    def test_serializer_failure_propagates_serialization_stage_error(self) -> None:
        # Arrange
        self.mock_transformer.transform.return_value = self.viz_graph
        self.mock_layout_engine.layout.return_value = self.positioned_graph
        self.mock_serializer.to_dict.side_effect = SerializationError("Serializer failed!")

        # Act & Assert
        with self.assertRaises(SerializationStageError) as context:
            self.pipeline.generate(self.repo_graph)

        self.assertIn("Serialization stage failed", str(context.exception))

    def test_unexpected_errors_are_wrapped_and_propagated(self) -> None:
        # Test unexpected exception in transformer
        self.mock_transformer.transform.side_effect = RuntimeError("Panic!")
        with self.assertRaises(TransformationStageError):
            self.pipeline.generate(self.repo_graph)


if __name__ == "__main__":
    unittest.main()
