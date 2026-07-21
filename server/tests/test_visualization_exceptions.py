"""Unit test suite for visualization exception hierarchy."""

import unittest
import pytest
from app.visualization import (
    InvalidVisualizationGraph,
    LayoutError,
    SerializationError,
    TransformationError,
    VisualizationError,
    VisualizationValidationError,
)


class TestVisualizationExceptions(unittest.TestCase):
    """Tests for visualization exception inheritance hierarchy, message preservation, and handling."""

    def test_exception_inheritance_hierarchy(self) -> None:
        self.assertTrue(issubclass(VisualizationError, Exception))
        self.assertTrue(issubclass(InvalidVisualizationGraph, VisualizationError))
        self.assertTrue(issubclass(TransformationError, VisualizationError))
        self.assertTrue(issubclass(SerializationError, VisualizationError))
        self.assertTrue(issubclass(LayoutError, VisualizationError))
        self.assertTrue(issubclass(VisualizationValidationError, VisualizationError))

    def test_exception_raising_and_message_preservation(self) -> None:
        msg = "Structurally invalid visualization graph: duplicate node ID 'node_1'"
        with pytest.raises(InvalidVisualizationGraph) as exc_info:
            raise InvalidVisualizationGraph(msg)
        self.assertEqual(str(exc_info.value), msg)

        msg_trans = "Transformation from RepositoryGraph failed"
        with pytest.raises(TransformationError) as exc_info:
            raise TransformationError(msg_trans)
        self.assertEqual(str(exc_info.value), msg_trans)

        msg_ser = "Failed to serialize visualization model"
        with pytest.raises(SerializationError) as exc_info:
            raise SerializationError(msg_ser)
        self.assertEqual(str(exc_info.value), msg_ser)

        msg_layout = "Layout computation failed for force_directed strategy"
        with pytest.raises(LayoutError) as exc_info:
            raise LayoutError(msg_layout)
        self.assertEqual(str(exc_info.value), msg_layout)

        msg_val = "Visualization validation failed"
        with pytest.raises(VisualizationValidationError) as exc_info:
            raise VisualizationValidationError(msg_val)
        self.assertEqual(str(exc_info.value), msg_val)

    def test_catching_subclasses_with_base_exception(self) -> None:
        try:
            raise InvalidVisualizationGraph("Test exception")
        except VisualizationError as err:
            self.assertEqual(str(err), "Test exception")
        else:
            self.fail("VisualizationError was not caught")


if __name__ == "__main__":
    unittest.main()
