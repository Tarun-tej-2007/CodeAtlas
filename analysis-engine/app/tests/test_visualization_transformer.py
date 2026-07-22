"""Unit test suite for VisualizationTransformer and VisualizationSerializer."""

import unittest
from pydantic import ValidationError

from app.graph import Graph as RepositoryGraph
from app.graph import GraphEdge, GraphMetadata, GraphNode
from app.graph.enums import EdgeType, NodeType
from app.visualization import (
    EdgeKind,
    NodeKind,
    SerializationError,
    TransformationError,
    VisualizationGraph,
    VisualizationSerializer,
    VisualizationTransformer,
)


class TestVisualizationTransformer(unittest.TestCase):
    """Tests for VisualizationTransformer node/edge conversion, style applications, and serialization."""

    def setUp(self) -> None:
        self.transformer = VisualizationTransformer()

    def test_empty_graph_transformation(self) -> None:
        repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="EmptyProject"))
        viz_graph = self.transformer.transform(repo_graph)

        self.assertIsInstance(viz_graph, VisualizationGraph)
        self.assertEqual(len(viz_graph.nodes), 0)
        self.assertEqual(len(viz_graph.edges), 0)
        self.assertEqual(viz_graph.groups, ())
        self.assertEqual(viz_graph.metadata.node_count, 0)
        self.assertEqual(viz_graph.metadata.edge_count, 0)
        self.assertEqual(viz_graph.metadata.group_count, 0)

    def test_single_and_multiple_node_transformation(self) -> None:
        repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="NodeProject"))

        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        n2 = GraphNode(id="n2", type=NodeType.FUNCTION, name="saveUser")
        n3 = GraphNode(id="n3", type=NodeType.FILE, name="app.js")

        repo_graph.add_node(n1)
        repo_graph.add_node(n2)
        repo_graph.add_node(n3)

        viz_graph = self.transformer.transform(repo_graph)

        self.assertEqual(len(viz_graph.nodes), 3)

        # Check fields and mapping
        viz_n1 = [n for n in viz_graph.nodes if n.id == "n1"][0]
        self.assertEqual(viz_n1.label, "UserService")
        self.assertEqual(viz_n1.kind, NodeKind.CLASS)
        self.assertIsNone(viz_n1.position)
        self.assertEqual(viz_n1.style.shape, "default")

        viz_n2 = [n for n in viz_graph.nodes if n.id == "n2"][0]
        self.assertEqual(viz_n2.label, "saveUser")
        self.assertEqual(viz_n2.kind, NodeKind.FUNCTION)

        # FILE should map to UNKNOWN NodeKind
        viz_n3 = [n for n in viz_graph.nodes if n.id == "n3"][0]
        self.assertEqual(viz_n3.kind, NodeKind.UNKNOWN)

    def test_edge_transformation_and_defaults(self) -> None:
        repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="EdgeProject"))

        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        n2 = GraphNode(id="n2", type=NodeType.METHOD, name="save")
        repo_graph.add_node(n1)
        repo_graph.add_node(n2)

        edge = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.DECLARES)
        repo_graph.add_edge(edge)

        viz_graph = self.transformer.transform(repo_graph)

        self.assertEqual(len(viz_graph.edges), 1)
        viz_edge = viz_graph.edges[0]
        self.assertEqual(viz_edge.id, "e1")
        self.assertEqual(viz_edge.source, "n1")
        self.assertEqual(viz_edge.target, "n2")
        self.assertEqual(viz_edge.kind, EdgeKind.CONTAINS)  # DECLARES maps to CONTAINS
        self.assertEqual(viz_edge.style.width, 1.0)
        self.assertEqual(viz_edge.style.style, "solid")

    def test_transformation_output_immutability(self) -> None:
        repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="ImmutProject"))
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        repo_graph.add_node(n1)

        viz_graph = self.transformer.transform(repo_graph)

        with self.assertRaises(ValidationError):
            viz_graph.nodes[0].label = "new label"  # type: ignore

    def test_invalid_graph_input_raises_transformation_error(self) -> None:
        with self.assertRaises(TransformationError):
            self.transformer.transform(None)  # type: ignore

    def test_deterministic_output_for_identical_inputs(self) -> None:
        repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="DetProject"))
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="Service")
        repo_graph.add_node(n1)

        v1 = self.transformer.transform(repo_graph)
        v2 = self.transformer.transform(repo_graph)

        self.assertEqual(v1.model_dump(), v2.model_dump())

    def test_visualization_serialization_and_deserialization(self) -> None:
        repo_graph = RepositoryGraph(metadata=GraphMetadata(project_name="SerProject"))
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="Service")
        repo_graph.add_node(n1)

        viz_graph = self.transformer.transform(repo_graph)

        # Serialize to dict & JSON
        data = VisualizationSerializer.to_dict(viz_graph)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["metadata"]["node_count"], 1)

        json_str = VisualizationSerializer.to_json(viz_graph)
        self.assertIsInstance(json_str, str)
        self.assertIn('"node_count": 1', json_str)

        # Deserialize from dict & JSON
        reconstructed = VisualizationSerializer.from_dict(data)
        self.assertIsInstance(reconstructed, VisualizationGraph)
        self.assertEqual(reconstructed.metadata.node_count, 1)

        reconstructed_json = VisualizationSerializer.from_json(json_str)
        self.assertEqual(reconstructed_json.metadata.node_count, 1)

    def test_invalid_serialization_inputs_raise_errors(self) -> None:
        with self.assertRaises(SerializationError):
            VisualizationSerializer.to_dict(None)  # type: ignore

        with self.assertRaises(SerializationError):
            VisualizationSerializer.from_dict({"invalid": "keys"})

        with self.assertRaises(SerializationError):
            VisualizationSerializer.from_json("{malformed json")


if __name__ == "__main__":
    unittest.main()
