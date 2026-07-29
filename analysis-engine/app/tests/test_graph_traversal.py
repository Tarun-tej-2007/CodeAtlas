"""Unit tests for GraphTraversal module."""

import unittest

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.traversal import GraphTraversal


class TestGraphTraversal(unittest.TestCase):
    """Tests BFS and DFS graph traversal generator pathways and determinism."""

    def setUp(self) -> None:
        self.traversal = GraphTraversal()
        self.node_a = GraphNode(id="node-a", name="A", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="node-b", name="B", type=DependencyNodeType.MODULE)
        self.node_c = GraphNode(id="node-c", name="C", type=DependencyNodeType.MODULE)
        self.node_d = GraphNode(id="node-d", name="D", type=DependencyNodeType.MODULE)

        # Graph setup:
        # A -> C
        # A -> B
        # B -> D
        # C -> D
        self.edge_ac = GraphEdge(source_id="node-a", target_id="node-c", type=DependencyEdgeType.IMPORTS)
        self.edge_ab = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        self.edge_bd = GraphEdge(source_id="node-b", target_id="node-d", type=DependencyEdgeType.USAGE)
        self.edge_cd = GraphEdge(source_id="node-c", target_id="node-d", type=DependencyEdgeType.USAGE)

        self.graph = DependencyGraph(
            nodes=[self.node_a, self.node_b, self.node_c, self.node_d],
            edges=[self.edge_ac, self.edge_ab, self.edge_bd, self.edge_cd]
        )

    def test_bfs_traversal(self) -> None:
        # From A: BFS yields A, then neighbours B and C in sorted order, then D
        bfs_order = list(self.traversal.bfs(self.graph, "node-a"))
        self.assertEqual(bfs_order, ["node-a", "node-b", "node-c", "node-d"])

    def test_dfs_traversal(self) -> None:
        # From A: DFS yields A, then popped B (first sorted pushed reverse), then D
        # Stack trace:
        # start: [A]
        # visit A -> push reverse sorted neighbours [C, B] -> stack: [C, B]
        # pop B -> visit B -> push reverse sorted neighbours [D] -> stack: [C, D]
        # pop D -> visit D -> stack: [C]
        # pop C -> visit C -> stack: []
        dfs_order = list(self.traversal.dfs(self.graph, "node-a"))
        self.assertEqual(dfs_order, ["node-a", "node-b", "node-d", "node-c"])

    def test_empty_graph(self) -> None:
        empty = DependencyGraph(nodes=[], edges=[])
        self.assertEqual(list(self.traversal.bfs(empty, "node-a")), [])
        self.assertEqual(list(self.traversal.dfs(empty, "node-a")), [])


if __name__ == "__main__":
    unittest.main()
