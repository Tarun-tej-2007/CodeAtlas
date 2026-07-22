"""Unit test suite for GraphDiffEngine and graph comparison change models."""

import unittest
from pathlib import Path

from app.graph import Graph, GraphEdge, GraphMetadata, GraphNode
from app.graph.enums import EdgeType, NodeType
from app.graph.diff import (
    GraphDiffEngine,
    GraphDiff,
    GraphDiffError,
    InvalidGraphComparison,
)


class TestGraphDiffEngine(unittest.TestCase):
    """Tests for GraphDiffEngine comparing two RepositoryGraph states and generating a GraphDiff."""

    def test_empty_graphs_diff(self) -> None:
        g1 = Graph(metadata=GraphMetadata(project_name="P1"))
        g2 = Graph(metadata=GraphMetadata(project_name="P1"))

        diff = GraphDiffEngine.diff(g1, g2)
        self.assertIsInstance(diff, GraphDiff)
        self.assertEqual(len(diff.nodes_added), 0)
        self.assertEqual(len(diff.nodes_removed), 0)
        self.assertEqual(len(diff.nodes_updated), 0)
        self.assertEqual(len(diff.edges_added), 0)
        self.assertEqual(len(diff.edges_removed), 0)
        self.assertEqual(len(diff.edges_updated), 0)

    def test_identical_graphs_diff(self) -> None:
        g1 = Graph(metadata=GraphMetadata(project_name="P1"))
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        e1 = GraphEdge(id="e1", source="n1", target="n1", type=EdgeType.CALLS)
        g1.add_node(n1)
        g1.add_edge(e1)

        g2 = Graph(metadata=GraphMetadata(project_name="P1"))
        g2.add_node(n1)
        g2.add_edge(e1)

        diff = GraphDiffEngine.diff(g1, g2)
        self.assertEqual(len(diff.nodes_added), 0)
        self.assertEqual(len(diff.nodes_removed), 0)
        self.assertEqual(len(diff.nodes_updated), 0)
        self.assertEqual(len(diff.edges_added), 0)
        self.assertEqual(len(diff.edges_removed), 0)
        self.assertEqual(len(diff.edges_updated), 0)

    def test_node_addition_removal_and_update(self) -> None:
        g1 = Graph(metadata=GraphMetadata(project_name="P1"))
        # Nodes: n1 (to be removed), n2 (to be updated)
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        n2_old = GraphNode(id="n2", type=NodeType.FUNCTION, name="saveUser", line=10)
        g1.add_node(n1)
        g1.add_node(n2_old)

        g2 = Graph(metadata=GraphMetadata(project_name="P1"))
        # Nodes: n2 (updated), n3 (added)
        n2_new = GraphNode(id="n2", type=NodeType.FUNCTION, name="saveUser", line=22) # Updated line
        n3 = GraphNode(id="n3", type=NodeType.VARIABLE, name="db")
        g2.add_node(n2_new)
        g2.add_node(n3)

        diff = GraphDiffEngine.diff(g1, g2)

        # Nodes added: n3
        self.assertEqual(len(diff.nodes_added), 1)
        self.assertEqual(diff.nodes_added[0].id, "n3")
        self.assertEqual(diff.nodes_added[0].node, n3)

        # Nodes removed: n1
        self.assertEqual(len(diff.nodes_removed), 1)
        self.assertEqual(diff.nodes_removed[0].id, "n1")
        self.assertEqual(diff.nodes_removed[0].node, n1)

        # Nodes updated: n2
        self.assertEqual(len(diff.nodes_updated), 1)
        self.assertEqual(diff.nodes_updated[0].id, "n2")
        self.assertEqual(diff.nodes_updated[0].old_node, n2_old)
        self.assertEqual(diff.nodes_updated[0].new_node, n2_new)

    def test_edge_addition_removal_and_update(self) -> None:
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="N1")
        n2 = GraphNode(id="n2", type=NodeType.CLASS, name="N2")
        n3 = GraphNode(id="n3", type=NodeType.CLASS, name="N3")

        g1 = Graph(metadata=GraphMetadata(project_name="P1"))
        g1.add_node(n1)
        g1.add_node(n2)
        g1.add_node(n3)
        e1 = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.CONTAINS)
        e2_old = GraphEdge(id="e2", source="n2", target="n3", type=EdgeType.CALLS, metadata={"weight": 1})
        g1.add_edge(e1)
        g1.add_edge(e2_old)

        g2 = Graph(metadata=GraphMetadata(project_name="P1"))
        g2.add_node(n1)
        g2.add_node(n2)
        g2.add_node(n3)
        e2_new = GraphEdge(id="e2", source="n2", target="n3", type=EdgeType.CALLS, metadata={"weight": 5}) # Updated metadata
        e3 = GraphEdge(id="e3", source="n1", target="n3", type=EdgeType.CONTAINS)
        g2.add_edge(e2_new)
        g2.add_edge(e3)

        diff = GraphDiffEngine.diff(g1, g2)

        # Edges added: e3
        self.assertEqual(len(diff.edges_added), 1)
        self.assertEqual(diff.edges_added[0].id, "e3")

        # Edges removed: e1
        self.assertEqual(len(diff.edges_removed), 1)
        self.assertEqual(diff.edges_removed[0].id, "e1")

        # Edges updated: e2
        self.assertEqual(len(diff.edges_updated), 1)
        self.assertEqual(diff.edges_updated[0].id, "e2")
        self.assertEqual(diff.edges_updated[0].old_edge, e2_old)
        self.assertEqual(diff.edges_updated[0].new_edge, e2_new)

    def test_deterministic_sorting(self) -> None:
        g1 = Graph(metadata=GraphMetadata(project_name="P1"))
        g2 = Graph(metadata=GraphMetadata(project_name="P1"))

        # Add nodes out of order
        g2.add_node(GraphNode(id="z_node", type=NodeType.CLASS, name="Z"))
        g2.add_node(GraphNode(id="a_node", type=NodeType.CLASS, name="A"))
        g2.add_node(GraphNode(id="m_node", type=NodeType.CLASS, name="M"))

        diff = GraphDiffEngine.diff(g1, g2)

        # Must be sorted alphabetically: a_node, m_node, z_node
        self.assertEqual(diff.nodes_added[0].id, "a_node")
        self.assertEqual(diff.nodes_added[1].id, "m_node")
        self.assertEqual(diff.nodes_added[2].id, "z_node")

    def test_graph_immutability(self) -> None:
        g1 = Graph(metadata=GraphMetadata(project_name="P1"))
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        g1.add_node(n1)

        g2 = Graph(metadata=GraphMetadata(project_name="P1"))

        # Run diff
        diff = GraphDiffEngine.diff(g1, g2)

        # Inputs must remain completely unchanged
        self.assertEqual(len(g1.nodes), 1)
        self.assertEqual(len(g2.nodes), 0)

    def test_malformed_graph_inputs(self) -> None:
        with self.assertRaises(InvalidGraphComparison):
            GraphDiffEngine.diff(None, Graph(metadata=GraphMetadata(project_name="P1")))  # type: ignore

        with self.assertRaises(InvalidGraphComparison):
            GraphDiffEngine.diff(Graph(metadata=GraphMetadata(project_name="P1")), "invalid")  # type: ignore


if __name__ == "__main__":
    unittest.main()
