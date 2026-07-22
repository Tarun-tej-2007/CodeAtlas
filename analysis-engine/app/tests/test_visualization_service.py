"""Unit test suite for VisualizationService and layout integration."""

import unittest
from unittest.mock import MagicMock

from app.graph import Graph as RepositoryGraph
from app.graph import GraphMetadata
from app.services.visualization import VisualizationService
from app.visualization.pipeline import (
    VisualizationPipeline,
    TransformationStageError,
)


class TestVisualizationService(unittest.TestCase):
    """Tests for the VisualizationService layer."""

    def test_successful_visualization_generation(self) -> None:
        mock_pipeline = MagicMock(spec=VisualizationPipeline)
        expected_output = {"nodes": [], "edges": [], "metadata": {}}
        mock_pipeline.generate.return_value = expected_output

        service = VisualizationService(mock_pipeline)
        graph = RepositoryGraph(metadata=GraphMetadata(project_name="TestProject"))

        result = service.generate_visualization(graph)

        self.assertEqual(result, expected_output)
        mock_pipeline.generate.assert_called_once_with(graph)

    def test_pipeline_exception_propagation(self) -> None:
        mock_pipeline = MagicMock(spec=VisualizationPipeline)
        mock_pipeline.generate.side_effect = TransformationStageError("Transform error")

        service = VisualizationService(mock_pipeline)
        graph = RepositoryGraph(metadata=GraphMetadata(project_name="TestProject"))

        with self.assertRaises(TransformationStageError):
            service.generate_visualization(graph)

    def test_dependency_injection_wiring(self) -> None:
        mock_pipeline = MagicMock(spec=VisualizationPipeline)
        service = VisualizationService(pipeline=mock_pipeline)
        self.assertEqual(service.pipeline, mock_pipeline)


if __name__ == "__main__":
    unittest.main()
