"""Unit test suite for HierarchicalLayoutEngine and layout components."""

import unittest
from pydantic import ValidationError

from app.visualization import (
    EdgeKind,
    GroupKind,
    LayoutKind,
    NodeKind,
    Position,
    VisualizationEdge,
    VisualizationGraph,
    VisualizationGroup,
    VisualizationMetadata,
    VisualizationNode,
)
from app.visualization.layouts import (
    CyclicLayoutError,
    InvalidLayoutGraph,
    HierarchicalLayoutEngine,
)


class TestGraphLayoutEngine(unittest.TestCase):
    """Tests for HierarchicalLayoutEngine layout strategies, validations, and constraints."""

    def setUp(self) -> None:
        self.engine = HierarchicalLayoutEngine(
            horizontal_spacing=200.0,
            vertical_spacing=100.0,
        )

    def test_empty_graph(self) -> None:
        empty = VisualizationGraph()
        layout_graph = self.engine.layout(empty)

        self.assertEqual(len(layout_graph.nodes), 0)
        self.assertEqual(len(layout_graph.edges), 0)
        self.assertEqual(layout_graph.metadata.layout, LayoutKind.NONE)

    def test_single_node(self) -> None:
        node = VisualizationNode(id="n1", label="root", kind=NodeKind.MODULE)
        graph = VisualizationGraph(
            nodes=(node,),
            metadata=VisualizationMetadata(node_count=1),
        )

        res = self.engine.layout(graph)
        self.assertEqual(len(res.nodes), 1)
        self.assertEqual(res.nodes[0].position, Position(x=0.0, y=0.0))
        self.assertEqual(res.metadata.layout, LayoutKind.HIERARCHICAL)

    def test_linear_chain(self) -> None:
        # n1 -> n2 -> n3
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.CLASS)
        n3 = VisualizationNode(id="n3", label="n3", kind=NodeKind.FUNCTION)

        e1 = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)
        e2 = VisualizationEdge(id="e2", source="n2", target="n3", kind=EdgeKind.CALL)

        graph = VisualizationGraph(
            nodes=(n1, n2, n3),
            edges=(e1, e2),
        )

        res = self.engine.layout(graph)
        pos_map = {node.id: node.position for node in res.nodes}

        self.assertEqual(pos_map["n1"], Position(x=0.0, y=0.0))
        self.assertEqual(pos_map["n2"], Position(x=0.0, y=100.0))
        self.assertEqual(pos_map["n3"], Position(x=0.0, y=200.0))

    def test_balanced_tree(self) -> None:
        #      n1
        #     /  \
        #    n2  n3
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.CLASS)
        n3 = VisualizationNode(id="n3", label="n3", kind=NodeKind.CLASS)

        e1 = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)
        e2 = VisualizationEdge(id="e2", source="n1", target="n3", kind=EdgeKind.CONTAINS)

        graph = VisualizationGraph(
            nodes=(n1, n2, n3),
            edges=(e1, e2),
        )

        res = self.engine.layout(graph)
        pos_map = {node.id: node.position for node in res.nodes}

        self.assertEqual(pos_map["n1"], Position(x=0.0, y=0.0))
        # Siblings on Level 1 are sorted alphabetically: n2 then n3
        self.assertEqual(pos_map["n2"], Position(x=0.0, y=100.0))
        self.assertEqual(pos_map["n3"], Position(x=200.0, y=100.0))

    def test_multiple_roots(self) -> None:
        # Roots: n1, n2
        n1 = VisualizationNode(id="n1", label="r1", kind=NodeKind.MODULE)
        n2 = VisualizationNode(id="n2", label="r2", kind=NodeKind.MODULE)
        n3 = VisualizationNode(id="n3", label="c1", kind=NodeKind.CLASS)

        e1 = VisualizationEdge(id="e1", source="n1", target="n3", kind=EdgeKind.CONTAINS)
        e2 = VisualizationEdge(id="e2", source="n2", target="n3", kind=EdgeKind.CONTAINS)

        graph = VisualizationGraph(
            nodes=(n1, n2, n3),
            edges=(e1, e2),
        )

        res = self.engine.layout(graph)
        pos_map = {node.id: node.position for node in res.nodes}

        # Level 0 sorted: n1, n2
        self.assertEqual(pos_map["n1"], Position(x=0.0, y=0.0))
        self.assertEqual(pos_map["n2"], Position(x=200.0, y=0.0))
        # Level 1: n3
        self.assertEqual(pos_map["n3"], Position(x=0.0, y=100.0))

    def test_disconnected_graph(self) -> None:
        # Component A: n1 -> n2
        # Component B: n3
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.CLASS)
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.METHOD)
        n3 = VisualizationNode(id="n3", label="n3", kind=NodeKind.CLASS)

        e1 = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)

        graph = VisualizationGraph(
            nodes=(n1, n2, n3),
            edges=(e1,),
        )

        res = self.engine.layout(graph)
        pos_map = {node.id: node.position for node in res.nodes}

        # Level 0 roots sorted: n1, n3
        self.assertEqual(pos_map["n1"], Position(x=0.0, y=0.0))
        self.assertEqual(pos_map["n3"], Position(x=200.0, y=0.0))
        # Level 1: n2
        self.assertEqual(pos_map["n2"], Position(x=0.0, y=100.0))

    def test_diamond_dependency(self) -> None:
        #      n1
        #     /  \
        #    n2  n3
        #     \  /
        #      n4
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.CLASS)
        n3 = VisualizationNode(id="n3", label="n3", kind=NodeKind.CLASS)
        n4 = VisualizationNode(id="n4", label="n4", kind=NodeKind.FUNCTION)

        e1 = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)
        e2 = VisualizationEdge(id="e2", source="n1", target="n3", kind=EdgeKind.CONTAINS)
        e3 = VisualizationEdge(id="e3", source="n2", target="n4", kind=EdgeKind.CALL)
        e4 = VisualizationEdge(id="e4", source="n3", target="n4", kind=EdgeKind.CALL)

        graph = VisualizationGraph(
            nodes=(n1, n2, n3, n4),
            edges=(e1, e2, e3, e4),
        )

        res = self.engine.layout(graph)
        pos_map = {node.id: node.position for node in res.nodes}

        self.assertEqual(pos_map["n1"], Position(x=0.0, y=0.0))
        self.assertEqual(pos_map["n2"], Position(x=0.0, y=100.0))
        self.assertEqual(pos_map["n3"], Position(x=200.0, y=100.0))
        # n4 is correctly placed at y=200.0 (longest path from n1)
        self.assertEqual(pos_map["n4"], Position(x=0.0, y=200.0))

    def test_cycle_detection(self) -> None:
        # Self loop: n1 -> n1
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        e1 = VisualizationEdge(id="e1", source="n1", target="n1", kind=EdgeKind.CONTAINS)
        g1 = VisualizationGraph(nodes=(n1,), edges=(e1,))

        with self.assertRaises(CyclicLayoutError):
            self.engine.layout(g1)

        # Mutual cycle: n1 -> n2 -> n1
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.MODULE)
        e2 = VisualizationEdge(id="e2", source="n1", target="n2", kind=EdgeKind.CONTAINS)
        e3 = VisualizationEdge(id="e3", source="n2", target="n1", kind=EdgeKind.CONTAINS)
        g2 = VisualizationGraph(nodes=(n1, n2), edges=(e2, e3))

        with self.assertRaises(CyclicLayoutError):
            self.engine.layout(g2)

    def test_invalid_graph_validation(self) -> None:
        # Missing source node
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.CLASS)
        e1 = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)
        g1 = VisualizationGraph(nodes=(n2,), edges=(e1,))

        with self.assertRaises(InvalidLayoutGraph):
            self.engine.layout(g1)

        # Duplicate node ID
        n2_dup = VisualizationNode(id="n2", label="n2_dup", kind=NodeKind.FUNCTION)
        # Note: Pydantic tuple fields validate elements, but duplicate node IDs
        # are handled by the layout engine.
        g2 = VisualizationGraph(nodes=(n2, n2_dup))

        with self.assertRaises(InvalidLayoutGraph):
            self.engine.layout(g2)

        # Null graph
        with self.assertRaises(InvalidLayoutGraph):
            self.engine.layout(None)  # type: ignore

    def test_deterministic_ordering(self) -> None:
        # Re-layout should yield exactly matching positions
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.CLASS)
        e1 = VisualizationEdge(id="e1", source="n1", target="n2", kind=EdgeKind.CONTAINS)

        graph = VisualizationGraph(nodes=(n1, n2), edges=(e1,))

        res1 = self.engine.layout(graph)
        res2 = self.engine.layout(graph)

        self.assertEqual(res1.model_dump(), res2.model_dump())

    def test_graph_immutability(self) -> None:
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        graph = VisualizationGraph(nodes=(n1,))

        self.assertIsNone(n1.position)
        res = self.engine.layout(graph)

        # Original graph should remain unchanged
        self.assertIsNone(graph.nodes[0].position)
        self.assertIsNotNone(res.nodes[0].position)

    def test_preserved_metadata_styles_groups_edges(self) -> None:
        n1 = VisualizationNode(id="n1", label="n1", kind=NodeKind.MODULE)
        e1 = VisualizationEdge(id="e1", source="n1", target="n1", kind=EdgeKind.CALL) # Wait, cycle will raise error, let's not make it cycle
        e2 = VisualizationEdge(id="e2", source="n1", target="n2", kind=EdgeKind.CALL)
        n2 = VisualizationNode(id="n2", label="n2", kind=NodeKind.CLASS)

        group = VisualizationGroup(
            id="g1",
            label="RootGroup",
            kind=GroupKind.PACKAGE,
            members=("n1", "n2"),
            metadata={"g_meta": "val"},
        )

        meta = VisualizationMetadata(
            node_count=2,
            edge_count=1,
            group_count=1,
            graph_version="2.0",
        )

        graph = VisualizationGraph(
            nodes=(n1, n2),
            edges=(e2,),
            groups=(group,),
            metadata=meta,
        )

        res = self.engine.layout(graph)

        self.assertEqual(res.metadata.graph_version, "2.0")
        self.assertEqual(res.metadata.node_count, 2)
        self.assertEqual(res.metadata.edge_count, 1)
        self.assertEqual(res.metadata.group_count, 1)
        self.assertEqual(res.metadata.layout, LayoutKind.HIERARCHICAL)

        self.assertEqual(res.groups[0].id, "g1")
        self.assertEqual(res.groups[0].metadata["g_meta"], "val")
        self.assertEqual(res.edges[0].id, "e2")


if __name__ == "__main__":
    unittest.main()
