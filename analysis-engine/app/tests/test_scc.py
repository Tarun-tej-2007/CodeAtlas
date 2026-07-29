"""Unit tests for SCCEngine module."""

import unittest

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.scc import SCCEngine


class TestSCCEngine(unittest.TestCase):
    """Tests strongly connected components (SCC) extraction and sorting determinism."""

    def setUp(self) -> None:
        self.engine = SCCEngine()
        self.node_a = GraphNode(id="node-a", name="A", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="node-b", name="B", type=DependencyNodeType.MODULE)
        self.node_c = GraphNode(id="node-c", name="C", type=DependencyNodeType.MODULE)
        self.node_d = GraphNode(id="node-d", name="D", type=DependencyNodeType.MODULE)

    def test_empty_graph(self) -> None:
        graph = DependencyGraph(nodes=[], edges=[])
        res = self.engine.compute_scc(graph)
        self.assertEqual(len(res.components), 0)

    def test_single_node(self) -> None:
        graph = DependencyGraph(nodes=[self.node_a], edges=[])
        res = self.engine.compute_scc(graph)
        self.assertEqual(res.components, [["node-a"]])

    def test_acyclic_graph(self) -> None:
        # A -> B -> C (Each node is its own SCC)
        edge1 = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        edge2 = GraphEdge(source_id="node-b", target_id="node-c", type=DependencyEdgeType.IMPORTS)
        graph = DependencyGraph(nodes=[self.node_a, self.node_b, self.node_c], edges=[edge1, edge2])
        res = self.engine.compute_scc(graph)

        # Expected: components are separate and sorted
        expected = [
            ["node-a"],
            ["node-b"],
            ["node-c"]
        ]
        self.assertEqual(res.components, expected)

    def test_self_cycle(self) -> None:
        # A -> A
        edge = GraphEdge(source_id="node-a", target_id="node-a", type=DependencyEdgeType.USAGE)
        graph = DependencyGraph(nodes=[self.node_a], edges=[edge])
        res = self.engine.compute_scc(graph)
        self.assertEqual(res.components, [["node-a"]])

    def test_multi_node_cycle_forms_single_scc(self) -> None:
        # A -> B -> C -> A
        edge_ab = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.USAGE)
        edge_bc = GraphEdge(source_id="node-b", target_id="node-c", type=DependencyEdgeType.USAGE)
        edge_ca = GraphEdge(source_id="node-c", target_id="node-a", type=DependencyEdgeType.USAGE)

        graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c],
            edges=[edge_ab, edge_bc, edge_ca]
        )
        res = self.engine.compute_scc(graph)

        self.assertEqual(res.components, [["node-a", "node-b", "node-c"]])

    def test_disconnected_graph_multiple_sccs(self) -> None:
        # Partition 1: A -> B -> A (SCC 1)
        edge_ab = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        edge_ba = GraphEdge(source_id="node-b", target_id="node-a", type=DependencyEdgeType.IMPORTS)

        # Partition 2: C -> D -> C (SCC 2)
        edge_cd = GraphEdge(source_id="node-c", target_id="node-d", type=DependencyEdgeType.IMPORTS)
        edge_dc = GraphEdge(source_id="node-d", target_id="node-c", type=DependencyEdgeType.IMPORTS)

        graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c, self.node_d],
            edges=[edge_ab, edge_ba, edge_cd, edge_dc]
        )
        res = self.engine.compute_scc(graph)

        expected = [
            ["node-a", "node-b"],
            ["node-c", "node-d"]
        ]
        self.assertEqual(res.components, expected)

    def test_immutable_results(self) -> None:
        res = self.engine.compute_scc(DependencyGraph(nodes=[], edges=[]))
        with self.assertRaises(Exception):
            res.components = []  # type: ignore


if __name__ == "__main__":
    unittest.main()
