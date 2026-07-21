"""Unit test suite for GraphSerializer serialization and deserialization."""

from pathlib import Path
import unittest

from app.graph import (
    EdgeType,
    Graph,
    GraphEdge,
    GraphMetadata,
    GraphNode,
    NodeType,
)
from app.graph.serialization import (
    GraphSerializationError,
    GraphSerializer,
    SerializedGraph,
)


class TestGraphSerializer(unittest.TestCase):
    """Tests for GraphSerializer to_dict, to_json, from_dict, and from_json methods."""

    def setUp(self) -> None:
        self.graph = Graph(metadata=GraphMetadata(project_name="SerializationTestRepo"))

        self.n1 = GraphNode(id="n1", type=NodeType.PROJECT, name="Project")
        self.n2 = GraphNode(id="n2", type=NodeType.FILE, name="app.js", path=Path("/repo/app.js"))
        self.n3 = GraphNode(id="n3", type=NodeType.FUNCTION, name="main", path=Path("/repo/app.js"), line=10)

        self.graph.add_node(self.n1)
        self.graph.add_node(self.n2)
        self.graph.add_node(self.n3)

        self.e1 = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.CONTAINS)
        self.e2 = GraphEdge(id="e2", source="n2", target="n3", type=EdgeType.DECLARES)

        self.graph.add_edge(self.e1)
        self.graph.add_edge(self.e2)

    def test_graph_to_dict_and_from_dict(self) -> None:
        data = GraphSerializer.to_dict(self.graph)

        self.assertIsInstance(data, dict)
        self.assertIn("metadata", data)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertEqual(len(data["nodes"]), 3)
        self.assertEqual(len(data["edges"]), 2)

        reconstructed = GraphSerializer.from_dict(data)

        self.assertIsInstance(reconstructed, Graph)
        self.assertEqual(reconstructed.metadata.project_name, "SerializationTestRepo")
        self.assertEqual(reconstructed.node_count(), 3)
        self.assertEqual(reconstructed.edge_count(), 2)

        # Verify ordering preservation
        self.assertEqual([n.id for n in reconstructed.nodes], ["n1", "n2", "n3"])
        self.assertEqual([e.id for e in reconstructed.edges], ["e1", "e2"])

    def test_graph_to_json_and_from_json(self) -> None:
        json_str = GraphSerializer.to_json(self.graph)

        self.assertIsInstance(json_str, str)
        self.assertIn('"project_name": "SerializationTestRepo"', json_str)
        self.assertIn('"id": "n1"', json_str)

        reconstructed = GraphSerializer.from_json(json_str)

        self.assertEqual(reconstructed.metadata.project_name, "SerializationTestRepo")
        self.assertEqual(reconstructed.node_count(), 3)
        self.assertEqual(reconstructed.edge_count(), 2)

    def test_malformed_json_raises_serialization_error(self) -> None:
        with self.assertRaises(GraphSerializationError):
            GraphSerializer.from_json("invalid json string {")

    def test_missing_metadata_raises_serialization_error(self) -> None:
        invalid_data = {"nodes": [], "edges": []}
        with self.assertRaises(GraphSerializationError):
            GraphSerializer.from_dict(invalid_data)

    def test_duplicate_node_deserialization_rejection(self) -> None:
        data = GraphSerializer.to_dict(self.graph)
        # Duplicate node n1
        data["nodes"].append(data["nodes"][0])

        with self.assertRaises(GraphSerializationError):
            GraphSerializer.from_dict(data)

    def test_invalid_edge_reference_deserialization_rejection(self) -> None:
        data = GraphSerializer.to_dict(self.graph)
        # Edge pointing to non-existent target node n99
        data["edges"].append({
            "id": "e_bad",
            "source": "n1",
            "target": "n99",
            "type": "contains",
            "metadata": {}
        })

        with self.assertRaises(GraphSerializationError):
            GraphSerializer.from_dict(data)

    def test_empty_graph_serialization(self) -> None:
        empty_graph = Graph()
        json_str = GraphSerializer.to_json(empty_graph)
        reconstructed = GraphSerializer.from_json(json_str)

        self.assertEqual(reconstructed.node_count(), 0)
        self.assertEqual(reconstructed.edge_count(), 0)


if __name__ == "__main__":
    unittest.main()
