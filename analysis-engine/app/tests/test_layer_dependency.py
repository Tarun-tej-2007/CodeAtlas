"""Unit tests for the Layer Dependency Analysis Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.architecture.enums import LayerType
from app.architecture.models import ArchitectureLayer
from app.architecture.layer_dependency import (
    LayerDependency,
    LayerDependencyResult,
    LayerDependencyAnalyzer,
)


class TestLayerDependency(unittest.TestCase):
    """Verifies dependency aggregation, enums mapping, determinism, and concurrency checks."""

    def setUp(self) -> None:
        self.analyzer = LayerDependencyAnalyzer()
        self.layer_pres = ArchitectureLayer(
            id="presentation",
            name="Presentation Layer",
            layer_type=LayerType.PRESENTATION,
            node_ids=["node-controller", "node-view"]
        )
        self.layer_dom = ArchitectureLayer(
            id="domain",
            name="Domain Layer",
            layer_type=LayerType.DOMAIN,
            node_ids=["node-entity", "node-repo-interface"]
        )
        self.layer_infra = ArchitectureLayer(
            id="infrastructure",
            name="Infrastructure Layer",
            layer_type=LayerType.INFRASTRUCTURE,
            node_ids=["node-db", "node-http-client"]
        )
        self.layers = [self.layer_pres, self.layer_dom, self.layer_infra]

        # Dummy node list for validation
        self.nodes = [
            GraphNode(id="node-controller", name="C", type=DependencyNodeType.MODULE),
            GraphNode(id="node-view", name="V", type=DependencyNodeType.MODULE),
            GraphNode(id="node-entity", name="E", type=DependencyNodeType.CLASS),
            GraphNode(id="node-repo-interface", name="RI", type=DependencyNodeType.INTERFACE),
            GraphNode(id="node-db", name="DB", type=DependencyNodeType.MODULE),
            GraphNode(id="node-http-client", name="HTTP", type=DependencyNodeType.MODULE),
        ]

    def test_empty_graph(self) -> None:
        graph = DependencyGraph(nodes=[], edges=[])
        res = self.analyzer.analyze(graph, self.layers)
        self.assertEqual(res.dependencies, [])

    def test_no_inter_layer_dependencies(self) -> None:
        # Only intra-layer dependency: controller -> view
        edge = GraphEdge(
            source_id="node-controller",
            target_id="node-view",
            type=DependencyEdgeType.USAGE
        )
        graph = DependencyGraph(nodes=self.nodes, edges=[edge])
        res = self.analyzer.analyze(graph, self.layers)
        self.assertEqual(res.dependencies, [])

    def test_single_inter_layer_dependency(self) -> None:
        # One dependency: controller (pres) -> entity (domain)
        edge = GraphEdge(
            source_id="node-controller",
            target_id="node-entity",
            type=DependencyEdgeType.USAGE
        )
        graph = DependencyGraph(nodes=self.nodes, edges=[edge])
        res = self.analyzer.analyze(graph, self.layers)

        self.assertEqual(len(res.dependencies), 1)
        dep = res.dependencies[0]
        self.assertEqual(dep.source_layer_id, "presentation")
        self.assertEqual(dep.target_layer_id, "domain")
        self.assertEqual(dep.dependency_count, 1)
        self.assertEqual(dep.edge_types, [DependencyEdgeType.USAGE])

    def test_dependency_aggregation_and_multiple_edge_types(self) -> None:
        # Multiple node-level links between presentation and domain
        # 1. controller -> entity (USAGE)
        # 2. view -> repo-interface (IMPORTS)
        # 3. controller -> repo-interface (CALLS)
        edges = [
            GraphEdge(source_id="node-controller", target_id="node-entity", type=DependencyEdgeType.USAGE),
            GraphEdge(source_id="node-view", target_id="node-repo-interface", type=DependencyEdgeType.IMPORTS),
            GraphEdge(source_id="node-controller", target_id="node-repo-interface", type=DependencyEdgeType.CALLS),
        ]
        graph = DependencyGraph(nodes=self.nodes, edges=edges)
        res = self.analyzer.analyze(graph, self.layers)

        self.assertEqual(len(res.dependencies), 1)
        dep = res.dependencies[0]
        self.assertEqual(dep.source_layer_id, "presentation")
        self.assertEqual(dep.target_layer_id, "domain")
        self.assertEqual(dep.dependency_count, 3)
        # Should be sorted lexicographically: calls, imports, usage
        self.assertEqual(
            dep.edge_types,
            [DependencyEdgeType.CALLS, DependencyEdgeType.IMPORTS, DependencyEdgeType.USAGE]
        )

    def test_deterministic_ordering(self) -> None:
        # Dependencies in multiple directions:
        # 1. domain -> infrastructure
        # 2. presentation -> domain
        edges = [
            GraphEdge(source_id="node-repo-interface", target_id="node-db", type=DependencyEdgeType.USAGE),
            GraphEdge(source_id="node-controller", target_id="node-entity", type=DependencyEdgeType.USAGE),
        ]
        graph = DependencyGraph(nodes=self.nodes, edges=edges)
        res = self.analyzer.analyze(graph, self.layers)

        # Expected order sorted: domain -> infrastructure, presentation -> domain
        self.assertEqual(len(res.dependencies), 2)
        self.assertEqual(res.dependencies[0].source_layer_id, "domain")
        self.assertEqual(res.dependencies[0].target_layer_id, "infrastructure")
        self.assertEqual(res.dependencies[1].source_layer_id, "presentation")
        self.assertEqual(res.dependencies[1].target_layer_id, "domain")

    def test_stateless_repeated_execution(self) -> None:
        edge = GraphEdge(source_id="node-controller", target_id="node-entity", type=DependencyEdgeType.USAGE)
        graph = DependencyGraph(nodes=self.nodes, edges=[edge])

        res1 = self.analyzer.analyze(graph, self.layers)
        res2 = self.analyzer.analyze(graph, self.layers)
        self.assertEqual(res1, res2)

    def test_immutability(self) -> None:
        dep = LayerDependency(
            source_layer_id="presentation",
            target_layer_id="domain",
            dependency_count=5
        )
        with self.assertRaises((ValidationError, TypeError)):
            dep.dependency_count = 10  # type: ignore

    def test_thread_safety(self) -> None:
        edges = [
            GraphEdge(source_id="node-controller", target_id="node-entity", type=DependencyEdgeType.USAGE),
            GraphEdge(source_id="node-repo-interface", target_id="node-db", type=DependencyEdgeType.USAGE),
        ]
        graph = DependencyGraph(nodes=self.nodes, edges=edges)

        def run_analysis():
            return self.analyzer.analyze(graph, self.layers)

        # Run analysis across 8 parallel threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analysis) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
