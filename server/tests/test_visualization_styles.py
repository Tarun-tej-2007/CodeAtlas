"""Unit test suite for visualization presentation style models."""

import unittest
from pydantic import ValidationError
from app.visualization import EdgeStyle, GroupStyle, NodeStyle


class TestVisualizationStyles(unittest.TestCase):
    """Tests for NodeStyle, EdgeStyle, and GroupStyle presentation hint models."""

    def test_node_style_defaults_and_custom(self) -> None:
        default_style = NodeStyle()
        self.assertEqual(default_style.shape, "default")
        self.assertIsNone(default_style.icon)
        self.assertIsNone(default_style.color)
        self.assertIsNone(default_style.border_color)
        self.assertEqual(default_style.border_width, 1.0)

        custom_style = NodeStyle(
            shape="box",
            icon="class-icon",
            color="#ffffff",
            border_color="#000000",
            border_width=2.5,
        )
        self.assertEqual(custom_style.shape, "box")
        self.assertEqual(custom_style.icon, "class-icon")
        self.assertEqual(custom_style.color, "#ffffff")
        self.assertEqual(custom_style.border_color, "#000000")
        self.assertEqual(custom_style.border_width, 2.5)

    def test_edge_style_defaults_and_custom(self) -> None:
        default_style = EdgeStyle()
        self.assertEqual(default_style.width, 1.0)
        self.assertEqual(default_style.style, "solid")
        self.assertTrue(default_style.arrow)
        self.assertIsNone(default_style.color)

        custom_style = EdgeStyle(
            width=3.0,
            style="dashed",
            arrow=False,
            color="#ff0000",
        )
        self.assertEqual(custom_style.width, 3.0)
        self.assertEqual(custom_style.style, "dashed")
        self.assertFalse(custom_style.arrow)
        self.assertEqual(custom_style.color, "#ff0000")

    def test_group_style_defaults_and_custom(self) -> None:
        default_style = GroupStyle()
        self.assertIsNone(default_style.background_color)
        self.assertIsNone(default_style.border_color)
        self.assertEqual(default_style.border_width, 1.0)
        self.assertFalse(default_style.collapsed)

        custom_style = GroupStyle(
            background_color="#f0f0f0",
            border_color="#cccccc",
            border_width=1.5,
            collapsed=True,
        )
        self.assertEqual(custom_style.background_color, "#f0f0f0")
        self.assertEqual(custom_style.border_color, "#cccccc")
        self.assertEqual(custom_style.border_width, 1.5)
        self.assertTrue(custom_style.collapsed)

    def test_style_models_immutability(self) -> None:
        node_style = NodeStyle()
        edge_style = EdgeStyle()
        group_style = GroupStyle()

        with self.assertRaises(ValidationError):
            node_style.shape = "circle"  # type: ignore

        with self.assertRaises(ValidationError):
            edge_style.width = 2.0  # type: ignore

        with self.assertRaises(ValidationError):
            group_style.collapsed = True  # type: ignore

    def test_invalid_width_validation_failures(self) -> None:
        with self.assertRaises(ValidationError):
            NodeStyle(border_width=0.0)

        with self.assertRaises(ValidationError):
            NodeStyle(border_width=-1.0)

        with self.assertRaises(ValidationError):
            EdgeStyle(width=0.0)

        with self.assertRaises(ValidationError):
            GroupStyle(border_width=0.0)

    def test_style_equality_semantics(self) -> None:
        n1 = NodeStyle(shape="box", border_width=2.0)
        n2 = NodeStyle(shape="box", border_width=2.0)
        n3 = NodeStyle(shape="circle", border_width=2.0)

        self.assertEqual(n1, n2)
        self.assertNotEqual(n1, n3)

    def test_style_model_dump_serialization(self) -> None:
        node_style = NodeStyle(shape="hexagon", border_width=2.0)
        data = node_style.model_dump()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["shape"], "hexagon")
        self.assertEqual(data["border_width"], 2.0)


if __name__ == "__main__":
    unittest.main()
