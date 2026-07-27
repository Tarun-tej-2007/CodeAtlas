"""Unit tests for the dependency graph domain foundation."""

import unittest
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.exceptions import (
    DuplicateEdgeError,
    DuplicateNodeError,
    GraphValidationError,
)
from app.graph.dependency_models import GraphNode, GraphEdge, DependencyMetadata
from app.graph.dependency_graph import DependencyGraph


class TestDependencyGraphDomain(unittest.TestCase):
    """Verifies graph node integrity constraints, duplicate detections, read-only lookups, and immutability."""

    def setUp(self) -> None:
        self.node_a = GraphNode(id="node-a", name="ModuleA", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="node-b", name="ClassB", type=DependencyNodeType.CLASS)
        self.node_c = GraphNode(id="node-c", name="FuncC", type=DependencyNodeType.FUNCTION)

    def test_successful_graph_construction_and_lookups(self) -> None:
        # Edge: A imports B, B calls C
        edge_1 = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        edge_2 = GraphEdge(source_id="node-b", target_id="node-c", type=DependencyEdgeType.CALLS)

        graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c],
            edges=[edge_1, edge_2],
            metadata=DependencyMetadata(description="Clean Dependency Graph")
        )

        # 1. Lookup node exists
        self.assertTrue(graph.has_node("node-a"))
        self.assertFalse(graph.has_node("non-existent"))
        self.assertEqual(graph.get_node("node-b"), self.node_b)

        # 2. Lookup outgoing edges
        out_a = graph.get_outgoing_edges("node-a")
        self.assertEqual(len(out_a), 1)
        self.assertEqual(out_a[0], edge_1)

        out_c = graph.get_outgoing_edges("node-c")
        self.assertEqual(len(out_c), 0)

        # 3. Lookup incoming edges
        in_b = graph.get_incoming_edges("node-b")
        self.assertEqual(len(in_b), 1)
        self.assertEqual(in_b[0], edge_1)

        in_c = graph.get_incoming_edges("node-c")
        self.assertEqual(len(in_c), 1)
        self.assertEqual(in_c[0], edge_2)

        # 4. Deterministic ordering check (preserves initial lists order)
        self.assertEqual(graph.nodes, [self.node_a, self.node_b, self.node_c])
        self.assertEqual(graph.edges, [edge_1, edge_2])

    def test_duplicate_nodes_raise_error(self) -> None:
        # Duplicate Node ID
        node_dup = GraphNode(id="node-a", name="DupA", type=DependencyNodeType.VARIABLE)
        
        with self.assertRaises(DuplicateNodeError):
            DependencyGraph(nodes=[self.node_a, node_dup], edges=[])

    def test_duplicate_edges_raise_error(self) -> None:
        edge_1 = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.CALLS)
        edge_dup = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.CALLS)

        with self.assertRaises(DuplicateEdgeError):
            DependencyGraph(
                nodes=[self.node_a, self.node_b],
                edges=[edge_1, edge_dup]
            )

    def test_invalid_node_reference_raises_validation_error(self) -> None:
        # Edge source references non-existent node-ghost
        edge_bad = GraphEdge(source_id="node-ghost", target_id="node-b", type=DependencyEdgeType.USAGE)

        with self.assertRaises(GraphValidationError):
            DependencyGraph(
                nodes=[self.node_a, self.node_b],
                edges=[edge_bad]
            )

    def test_model_immutability(self) -> None:
        edge = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        graph = DependencyGraph(
            nodes=[self.node_a, self.node_b],
            edges=[edge]
        )

        # Confirm GraphNode is frozen
        with self.assertRaises((ValidationError, TypeError)):
            self.node_a.name = "MutatedName"  # type: ignore

        # Confirm GraphEdge is frozen
        with self.assertRaises((ValidationError, TypeError)):
            edge.source_id = "node-c"  # type: ignore

        # Confirm DependencyGraph is frozen
        with self.assertRaises((ValidationError, TypeError)):
            graph.nodes = []  # type: ignore


if __name__ == "__main__":
    unittest.main()
