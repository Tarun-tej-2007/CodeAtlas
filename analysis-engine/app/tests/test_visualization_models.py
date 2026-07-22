"""Unit test suite for visualization domain models and VisualizationGraph aggregate root."""

import unittest
from pydantic import ValidationError

from app.visualization import (
    EdgeKind,
    EdgeStyle,
    GroupKind,
    GroupStyle,
    LayoutKind,
    NodeKind,
    NodeStyle,
    Position,
    VisualizationEdge,
    VisualizationGraph,
    VisualizationGroup,
    VisualizationMetadata,
    VisualizationNode,
)


class TestVisualizationModels(unittest.TestCase):
    """Tests for Position, VisualizationNode, Edge, Group, Metadata, and VisualizationGraph aggregate root."""

    def test_position_construction_and_equality(self) -> None:
        pos1 = Position(x=10.5, y=20.0)
        pos2 = Position(x=10.5, y=20.0)
        pos3 = Position(x=0.0, y=0.0)

        self.assertEqual(pos1.x, 10.5)
        self.assertEqual(pos1.y, 20.0)
        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)

    def test_visualization_node_construction_and_defaults(self) -> None:
        node = VisualizationNode(
            id="v_node_1",
            label="UserService",
            kind=NodeKind.CLASS,
        )

        self.assertEqual(node.id, "v_node_1")
        self.assertEqual(node.label, "UserService")
        self.assertEqual(node.kind, NodeKind.CLASS)
        self.assertIsNone(node.position)
        self.assertEqual(node.style.shape, "default")
        self.assertEqual(node.metadata, {})

        pos = Position(x=100.0, y=200.0)
        custom_style = NodeStyle(shape="box", color="#ff0000")
        custom_node = VisualizationNode(
            id="v_node_2",
            label="main()",
            kind=NodeKind.FUNCTION,
            position=pos,
            style=custom_style,
            metadata={"visibility": "public"},
        )
        self.assertEqual(custom_node.position, pos)
        self.assertEqual(custom_node.style.shape, "box")
        self.assertEqual(custom_node.metadata["visibility"], "public")

    def test_visualization_edge_construction_and_defaults(self) -> None:
        edge = VisualizationEdge(
            id="v_edge_1",
            source="v_node_1",
            target="v_node_2",
            kind=EdgeKind.CALL,
        )

        self.assertEqual(edge.id, "v_edge_1")
        self.assertEqual(edge.source, "v_node_1")
        self.assertEqual(edge.target, "v_node_2")
        self.assertEqual(edge.kind, EdgeKind.CALL)
        self.assertEqual(edge.style.style, "solid")
        self.assertTrue(edge.style.arrow)

    def test_visualization_group_construction_and_tuple_immutability(self) -> None:
        group = VisualizationGroup(
            id="v_group_1",
            label="AppModule",
            kind=GroupKind.MODULE,
            members=("v_node_1", "v_node_2"),
        )

        self.assertEqual(group.id, "v_group_1")
        self.assertEqual(group.members, ("v_node_1", "v_node_2"))
        self.assertIsInstance(group.members, tuple)

    def test_visualization_metadata_defaults_and_validation(self) -> None:
        default_meta = VisualizationMetadata()
        self.assertEqual(default_meta.node_count, 0)
        self.assertEqual(default_meta.edge_count, 0)
        self.assertEqual(default_meta.group_count, 0)
        self.assertEqual(default_meta.layout, LayoutKind.NONE)
        self.assertEqual(default_meta.graph_version, "1.0")

        with self.assertRaises(ValidationError):
            VisualizationMetadata(node_count=-1)

        with self.assertRaises(ValidationError):
            VisualizationMetadata(edge_count=-5)

        with self.assertRaises(ValidationError):
            VisualizationMetadata(group_count=-2)

    def test_empty_visualization_graph(self) -> None:
        empty_graph = VisualizationGraph()
        self.assertEqual(empty_graph.nodes, ())
        self.assertEqual(empty_graph.edges, ())
        self.assertEqual(empty_graph.groups, ())
        self.assertEqual(empty_graph.metadata.node_count, 0)

    def test_fully_populated_visualization_graph(self) -> None:
        node1 = VisualizationNode(id="n1", label="mod.js", kind=NodeKind.MODULE)
        node2 = VisualizationNode(id="n2", label="main", kind=NodeKind.FUNCTION)

        edge = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)
        group = VisualizationGroup(id="g1", label="Root", kind=GroupKind.DIRECTORY, members=("n1", "n2"))

        meta = VisualizationMetadata(node_count=2, edge_count=1, group_count=1, layout=LayoutKind.HIERARCHICAL)

        graph = VisualizationGraph(
            nodes=(node1, node2),
            edges=(edge,),
            groups=(group,),
            metadata=meta,
        )

        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(len(graph.groups), 1)
        self.assertEqual(graph.metadata.layout, LayoutKind.HIERARCHICAL)

    def test_model_immutability(self) -> None:
        node = VisualizationNode(id="n1", label="test", kind=NodeKind.VARIABLE)
        edge = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CALL)
        graph = VisualizationGraph(nodes=(node,))

        with self.assertRaises(ValidationError):
            node.label = "modified"  # type: ignore

        with self.assertRaises(ValidationError):
            edge.kind = EdgeKind.IMPORT  # type: ignore

        with self.assertRaises(ValidationError):
            graph.nodes = ()  # type: ignore

    def test_nested_model_dump_serialization(self) -> None:
        node = VisualizationNode(
            id="n1",
            label="UserService",
            kind=NodeKind.CLASS,
            position=Position(x=10.0, y=20.0),
            style=NodeStyle(shape="box", color="#ff0000"),
        )

        graph = VisualizationGraph(
            nodes=(node,),
            metadata=VisualizationMetadata(node_count=1),
        )

        dump = graph.model_dump()
        self.assertIsInstance(dump, dict)
        self.assertEqual(dump["nodes"][0]["position"]["x"], 10.0)
        self.assertEqual(dump["nodes"][0]["style"]["shape"], "box")
        self.assertEqual(dump["metadata"]["node_count"], 1)


if __name__ == "__main__":
    unittest.main()
