"""Unit tests for DependencyGraphQuery module."""

import unittest

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.query import DependencyGraphQuery


class TestDependencyGraphQuery(unittest.TestCase):
    """Tests lookup, neighbour, shortest path, and reachability query APIs."""

    def setUp(self) -> None:
        self.query = DependencyGraphQuery()
        self.node_a = GraphNode(id="node-a", name="A", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="node-b", name="B", type=DependencyNodeType.MODULE)
        self.node_c = GraphNode(id="node-c", name="C", type=DependencyNodeType.MODULE)
        self.node_d = GraphNode(id="node-d", name="D", type=DependencyNodeType.MODULE)

        # Graph setup: A -> B -> C, and disconnected D
        self.edge_ab = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        self.edge_bc = GraphEdge(source_id="node-b", target_id="node-c", type=DependencyEdgeType.USAGE)

        self.graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c, self.node_d],
            edges=[self.edge_ab, self.edge_bc]
        )

    def test_node_lookups(self) -> None:
        self.assertTrue(self.query.has_node(self.graph, "node-a"))
        self.assertFalse(self.query.has_node(self.graph, "ghost-node"))
        self.assertEqual(self.query.get_node(self.graph, "node-a"), self.node_a)
        self.assertIsNone(self.query.get_node(self.graph, "ghost-node"))

    def test_edge_lookups(self) -> None:
        out_a = self.query.get_outgoing_edges(self.graph, "node-a")
        self.assertEqual(len(out_a), 1)
        self.assertEqual(out_a[0], self.edge_ab)

        in_b = self.query.get_incoming_edges(self.graph, "node-b")
        self.assertEqual(len(in_b), 1)
        self.assertEqual(in_b[0], self.edge_ab)

    def test_neighbour_retrieval(self) -> None:
        # A's neighbours is [B]
        neighbours_a = self.query.get_neighbours(self.graph, "node-a")
        self.assertEqual(neighbours_a, [self.node_b])

        # D has no neighbours
        neighbours_d = self.query.get_neighbours(self.graph, "node-d")
        self.assertEqual(neighbours_d, [])

    def test_reachable_node_computation(self) -> None:
        # Reachable from A: [A, B, C]
        reach_a = self.query.get_reachable_nodes(self.graph, "node-a")
        self.assertEqual(reach_a, ["node-a", "node-b", "node-c"])

        # Reachable from D: [D]
        reach_d = self.query.get_reachable_nodes(self.graph, "node-d")
        self.assertEqual(reach_d, ["node-d"])

    def test_shortest_path_unweighted(self) -> None:
        # Shortest path A -> C: [A, B, C]
        path = self.query.shortest_path(self.graph, "node-a", "node-c")
        self.assertEqual(path, ["node-a", "node-b", "node-c"])

        # No path A -> D
        path_none = self.query.shortest_path(self.graph, "node-a", "node-d")
        self.assertIsNone(path_none)

        # Same node path: A -> A
        path_self = self.query.shortest_path(self.graph, "node-a", "node-a")
        self.assertEqual(path_self, ["node-a"])

    def test_empty_graph(self) -> None:
        empty = DependencyGraph(nodes=[], edges=[])
        self.assertFalse(self.query.has_node(empty, "node-a"))
        self.assertEqual(self.query.get_neighbours(empty, "node-a"), [])
        self.assertEqual(self.query.get_reachable_nodes(empty, "node-a"), [])
        self.assertIsNone(self.query.shortest_path(empty, "node-a", "node-b"))


if __name__ == "__main__":
    unittest.main()
