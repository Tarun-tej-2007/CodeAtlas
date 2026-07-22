"""Unit test suite for visualization exception hierarchy."""

import unittest
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
        try:
            raise InvalidVisualizationGraph(msg)
        except InvalidVisualizationGraph as err:
            self.assertEqual(str(err), msg)

        msg_trans = "Transformation from RepositoryGraph failed"
        try:
            raise TransformationError(msg_trans)
        except TransformationError as err:
            self.assertEqual(str(err), msg_trans)

        msg_ser = "Failed to serialize visualization model"
        try:
            raise SerializationError(msg_ser)
        except SerializationError as err:
            self.assertEqual(str(err), msg_ser)

        msg_layout = "Layout computation failed for force_directed strategy"
        try:
            raise LayoutError(msg_layout)
        except LayoutError as err:
            self.assertEqual(str(err), msg_layout)

        msg_val = "Visualization validation failed"
        try:
            raise VisualizationValidationError(msg_val)
        except VisualizationValidationError as err:
            self.assertEqual(str(err), msg_val)

    def test_catching_subclasses_with_base_exception(self) -> None:
        try:
            raise InvalidVisualizationGraph("Test exception")
        except VisualizationError as err:
            self.assertEqual(str(err), "Test exception")
        else:
            self.fail("VisualizationError was not caught")


if __name__ == "__main__":
    unittest.main()
