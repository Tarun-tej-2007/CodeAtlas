"""Unit tests for DependencyGraph performance validation."""

import unittest

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import DependencyMetadata, GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.query import DependencyGraphQuery
from app.graph.traversal import GraphTraversal
from app.graph.cycle_detector import CycleDetector
from app.graph.scc import SCCEngine


class TestDependencyGraphPerformance(unittest.TestCase):
    """Validates query correctness, traversal determinism, and execution stability under larger synthetic graphs."""

    def setUp(self) -> None:
        self.query = DependencyGraphQuery()
        self.traversal = GraphTraversal()
        self.cycle_detector = CycleDetector()
        self.scc_engine = SCCEngine()

    def test_large_scale_synthetic_graph_correctness(self) -> None:
        # Create a synthetic grid-like graph structure of 400 nodes and edges
        nodes = []
        for i in range(400):
            nodes.append(
                GraphNode(
                    id=f"node-{i}",
                    name=f"Module_{i}",
                    type=DependencyNodeType.MODULE
                )
            )

        edges = []
        for i in range(399):
            # Chain: node-i -> node-(i+1)
            edges.append(
                GraphEdge(
                    source_id=f"node-{i}",
                    target_id=f"node-{i+1}",
                    type=DependencyEdgeType.IMPORTS
                )
            )

        # Introduce a cycle: node-399 -> node-200
        edges.append(
            GraphEdge(
                source_id="node-399",
                target_id="node-200",
                type=DependencyEdgeType.USAGE
            )
        )

        graph = DependencyGraph(
            nodes=nodes,
            edges=edges,
            metadata=DependencyMetadata(description="Performance Test Graph")
        )

        # 1. Verify index lookups (O(1))
        self.assertTrue(graph.has_node("node-200"))
        self.assertEqual(len(graph.get_outgoing_target_ids("node-0")), 1)
        self.assertEqual(graph.get_outgoing_target_ids("node-0")[0], "node-1")
        self.assertEqual(graph.get_outgoing_target_ids("node-399")[0], "node-200")

        # 2. Verify reachability (BFS traversal)
        reachable = self.query.get_reachable_nodes(graph, "node-398")
        # node-398 can reach node-398, node-399, and because of node-399 -> node-200 cycle, it reaches everything from 200 to 399!
        expected_reachable = [f"node-{x}" for x in range(200, 400)]
        expected_reachable.sort()
        self.assertEqual(reachable, expected_reachable)

        # 3. Verify shortest path computation
        # Path from node-398 to node-200: node-398 -> node-399 -> node-200
        path = self.query.shortest_path(graph, "node-398", "node-200")
        self.assertEqual(path, ["node-398", "node-399", "node-200"])

        # 4. Verify cycle detection
        cycles_res = self.cycle_detector.detect_cycles(graph)
        self.assertEqual(len(cycles_res.cycles), 1)
        # Cycle should start with lexicographically minimum node in the loop
        # Loop contains node-200 through node-399. Lexicographical min: "node-200"
        self.assertEqual(cycles_res.cycles[0][0], "node-200")
        self.assertEqual(cycles_res.cycles[0][-1], "node-200")

        # 5. Verify SCC computation
        scc_res = self.scc_engine.compute_scc(graph)
        # Components before 200 are single nodes. Nodes 200-399 form a single SCC.
        # Total components: 200 single nodes + 1 cycle component = 201 components
        self.assertEqual(len(scc_res.components), 201)
        
        # Check that the cycle component contains all nodes in the cycle
        cycle_scc = next(c for c in scc_res.components if len(c) > 1)
        self.assertEqual(len(cycle_scc), 200)
        self.assertIn("node-200", cycle_scc)
        self.assertIn("node-399", cycle_scc)


if __name__ == "__main__":
    unittest.main()
