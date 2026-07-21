"""Unit test suite for graph domain models, Graph container, indexing, and immutability."""

from pathlib import Path
import unittest

from app.graph import (
    EdgeType,
    Graph,
    GraphEdge,
    GraphError,
    GraphMetadata,
    GraphNode,
    NodeType,
)


class TestGraphFoundation(unittest.TestCase):
    """Tests for GraphNode, GraphEdge, GraphMetadata, and Graph container indexing."""

    def test_node_and_edge_creation(self) -> None:
        node1 = GraphNode(
            id="node_1",
            type=NodeType.FUNCTION,
            name="calculate",
            path=Path("/repo/math.js"),
            line=10,
            metadata={"visibility": "public"},
        )
        node2 = GraphNode(
            id="node_2",
            type=NodeType.FUNCTION,
            name="add",
            path=Path("/repo/math.js"),
            line=20,
        )

        edge = GraphEdge(
            id="edge_1_2",
            source="node_1",
            target="node_2",
            type=EdgeType.CALLS,
            metadata={"weight": 1},
        )

        self.assertEqual(node1.id, "node_1")
        self.assertEqual(node1.type, NodeType.FUNCTION)
        self.assertEqual(edge.source, "node_1")
        self.assertEqual(edge.target, "node_2")

    def test_graph_node_and_edge_insertion(self) -> None:
        graph = Graph(metadata=GraphMetadata(project_name="TestRepo"))
        node1 = GraphNode(id="n1", type=NodeType.MODULE, name="main")
        node2 = GraphNode(id="n2", type=NodeType.FUNCTION, name="run")

        graph.add_node(node1)
        graph.add_node(node2)

        edge = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.DECLARES)
        graph.add_edge(edge)

        self.assertEqual(graph.node_count(), 2)
        self.assertEqual(graph.edge_count(), 1)
        self.assertEqual(graph.get_node("n1"), node1)
        self.assertEqual(graph.get_edge("e1"), edge)

    def test_duplicate_node_rejection(self) -> None:
        graph = Graph()
        node = GraphNode(id="n1", type=NodeType.MODULE, name="mod")
        graph.add_node(node)

        with self.assertRaises(GraphError):
            graph.add_node(node)

    def test_duplicate_edge_rejection(self) -> None:
        graph = Graph()
        graph.add_node(GraphNode(id="n1", type=NodeType.MODULE, name="m1"))
        graph.add_node(GraphNode(id="n2", type=NodeType.MODULE, name="m2"))

        edge = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.IMPORTS)
        graph.add_edge(edge)

        with self.assertRaises(GraphError):
            graph.add_edge(edge)

    def test_missing_source_or_target_node_edge_rejection(self) -> None:
        graph = Graph()
        graph.add_node(GraphNode(id="n1", type=NodeType.MODULE, name="m1"))

        # Missing target node n2
        edge = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.CALLS)
        with self.assertRaises(GraphError):
            graph.add_edge(edge)

    def test_edge_query_filtering(self) -> None:
        graph = Graph()
        graph.add_node(GraphNode(id="n1", type=NodeType.MODULE, name="m1"))
        graph.add_node(GraphNode(id="n2", type=NodeType.FUNCTION, name="f1"))
        graph.add_node(GraphNode(id="n3", type=NodeType.FUNCTION, name="f2"))

        e1 = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.DECLARES)
        e2 = GraphEdge(id="e2", source="n1", target="n3", type=EdgeType.DECLARES)
        e3 = GraphEdge(id="e3", source="n2", target="n3", type=EdgeType.CALLS)

        graph.add_edge(e1)
        graph.add_edge(e2)
        graph.add_edge(e3)

        # Filter by source_id
        out_n1 = graph.get_edges(source_id="n1")
        self.assertEqual(len(out_n1), 2)
        self.assertIn(e1, out_n1)
        self.assertIn(e2, out_n1)

        # Filter by edge_type
        call_edges = graph.get_edges(edge_type=EdgeType.CALLS)
        self.assertEqual(len(call_edges), 1)
        self.assertEqual(call_edges[0], e3)

    def test_deterministic_insertion_ordering(self) -> None:
        graph = Graph()
        nodes = [GraphNode(id=f"n_{i}", type=NodeType.VARIABLE, name=f"var_{i}") for i in range(10)]
        for n in nodes:
            graph.add_node(n)

        self.assertEqual([n.id for n in graph.nodes], [f"n_{i}" for i in range(10)])

    def test_models_immutability(self) -> None:
        node = GraphNode(id="n1", type=NodeType.CLASS, name="User")

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            node.name = "Modified"


if __name__ == "__main__":
    unittest.main()
