"""Unit tests for CycleDetector module."""

import unittest

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.cycle_detector import CycleDetector


class TestCycleDetector(unittest.TestCase):
    """Tests directed graph cycle detection pathways, self loops, and determinism."""

    def setUp(self) -> None:
        self.detector = CycleDetector()
        self.node_a = GraphNode(id="node-a", name="A", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="node-b", name="B", type=DependencyNodeType.MODULE)
        self.node_c = GraphNode(id="node-c", name="C", type=DependencyNodeType.MODULE)
        self.node_d = GraphNode(id="node-d", name="D", type=DependencyNodeType.MODULE)

    def test_empty_graph(self) -> None:
        graph = DependencyGraph(nodes=[], edges=[])
        res = self.detector.detect_cycles(graph)
        self.assertEqual(len(res.cycles), 0)

    def test_single_node(self) -> None:
        graph = DependencyGraph(nodes=[self.node_a], edges=[])
        res = self.detector.detect_cycles(graph)
        self.assertEqual(len(res.cycles), 0)

    def test_acyclic_graph(self) -> None:
        # A -> B -> C
        edge1 = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        edge2 = GraphEdge(source_id="node-b", target_id="node-c", type=DependencyEdgeType.IMPORTS)
        graph = DependencyGraph(nodes=[self.node_a, self.node_b, self.node_c], edges=[edge1, edge2])
        res = self.detector.detect_cycles(graph)
        self.assertEqual(len(res.cycles), 0)

    def test_self_cycle(self) -> None:
        # A -> A
        edge = GraphEdge(source_id="node-a", target_id="node-a", type=DependencyEdgeType.USAGE)
        graph = DependencyGraph(nodes=[self.node_a], edges=[edge])
        res = self.detector.detect_cycles(graph)
        self.assertEqual(res.cycles, [["node-a", "node-a"]])

    def test_multi_node_cycle_and_determinism(self) -> None:
        # Cycle: C -> B -> A -> C
        edge_cb = GraphEdge(source_id="node-c", target_id="node-b", type=DependencyEdgeType.USAGE)
        edge_ba = GraphEdge(source_id="node-b", target_id="node-a", type=DependencyEdgeType.USAGE)
        edge_ac = GraphEdge(source_id="node-a", target_id="node-c", type=DependencyEdgeType.USAGE)

        graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c],
            edges=[edge_cb, edge_ba, edge_ac]
        )
        res = self.detector.detect_cycles(graph)

        # Expected unique rotated cycle: node-a -> node-c -> node-b -> node-a (starts with min element)
        self.assertEqual(res.cycles, [["node-a", "node-c", "node-b", "node-a"]])

    def test_disconnected_graph_with_multiple_cycles(self) -> None:
        # Partition 1: A -> B -> A (Cycle 1)
        edge_ab = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        edge_ba = GraphEdge(source_id="node-b", target_id="node-a", type=DependencyEdgeType.IMPORTS)

        # Partition 2: C -> D -> C (Cycle 2)
        edge_cd = GraphEdge(source_id="node-c", target_id="node-d", type=DependencyEdgeType.IMPORTS)
        edge_dc = GraphEdge(source_id="node-d", target_id="node-c", type=DependencyEdgeType.IMPORTS)

        graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c, self.node_d],
            edges=[edge_ab, edge_ba, edge_cd, edge_dc]
        )
        res = self.detector.detect_cycles(graph)

        # Output ordering must be deterministic: cycle starting with node-a first, then node-c
        expected = [
            ["node-a", "node-b", "node-a"],
            ["node-c", "node-d", "node-c"]
        ]
        self.assertEqual(res.cycles, expected)

    def test_immutable_results(self) -> None:
        res = self.detector.detect_cycles(DependencyGraph(nodes=[], edges=[]))
        with self.assertRaises(Exception):
            res.cycles = []  # type: ignore


if __name__ == "__main__":
    unittest.main()
