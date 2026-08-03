"""Unit tests for the Architecture Smell Detection Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.architecture.enums import LayerType
from app.architecture.models import ArchitectureLayer
from app.architecture.layer_dependency import LayerDependency, LayerDependencyResult
from app.architecture.layer_rules import LayerRuleViolation, LayerRuleValidationResult
from app.architecture.metrics import LayerMetrics, ArchitectureMetricsResult
from app.architecture.smell_detector import (
    SmellDetectorConfig,
    ArchitectureSmellDetector,
)


class TestSmellDetector(unittest.TestCase):
    """Verifies smell detection algorithms, configuration overrides, determinism, and concurrency checks."""

    def setUp(self) -> None:
        self.detector = ArchitectureSmellDetector()
        
        # Default empty/minimal inputs
        self.nodes = [
            GraphNode(id="n-ui", name="UI", type=DependencyNodeType.MODULE),
            GraphNode(id="n-biz", name="Biz", type=DependencyNodeType.MODULE),
            GraphNode(id="n-db", name="DB", type=DependencyNodeType.MODULE),
        ]
        self.graph = DependencyGraph(nodes=self.nodes, edges=[])
        
        self.layers = [
            ArchitectureLayer(id="presentation", name="Pres", layer_type=LayerType.PRESENTATION, node_ids=["n-ui"]),
            ArchitectureLayer(id="domain", name="Domain", layer_type=LayerType.DOMAIN, node_ids=["n-biz"]),
            ArchitectureLayer(id="infrastructure", name="Infra", layer_type=LayerType.INFRASTRUCTURE, node_ids=["n-db"]),
        ]
        self.dependencies = LayerDependencyResult(dependencies=[])
        self.validation = LayerRuleValidationResult(violations=[], diagnostics=[])
        self.metrics = ArchitectureMetricsResult(
            layer_metrics=[
                LayerMetrics(layer_id="presentation", afferent_coupling=0, efferent_coupling=0, instability=0.0),
                LayerMetrics(layer_id="domain", afferent_coupling=0, efferent_coupling=0, instability=0.0),
                LayerMetrics(layer_id="infrastructure", afferent_coupling=0, efferent_coupling=0, instability=0.0),
            ],
            average_instability=0.0,
            total_afferent_coupling=0,
            total_efferent_coupling=0
        )

    def test_no_smells_detected(self) -> None:
        res = self.detector.detect_smells(
            self.graph, self.layers, self.dependencies, self.validation, self.metrics
        )
        self.assertEqual(res.issues, [])
        self.assertIn("Completed smell detection. Detected 0 issues.", res.diagnostics)

    def test_cyclic_dependency_detection(self) -> None:
        # Create a dependency cycle: UI -> Biz -> DB -> UI
        edges = [
            GraphEdge(source_id="n-ui", target_id="n-biz", type=DependencyEdgeType.USAGE),
            GraphEdge(source_id="n-biz", target_id="n-db", type=DependencyEdgeType.USAGE),
            GraphEdge(source_id="n-db", target_id="n-ui", type=DependencyEdgeType.USAGE),
        ]
        graph = DependencyGraph(nodes=self.nodes, edges=edges)
        
        res = self.detector.detect_smells(
            graph, self.layers, self.dependencies, self.validation, self.metrics
        )
        # Should detect cyclic dependency
        self.assertEqual(len(res.issues), 1)
        issue = res.issues[0]
        self.assertEqual(issue.title, "Cyclic Dependency Detected")
        self.assertEqual(issue.metadata["smell_type"], "cyclic_dependency")

    def test_layer_violations_mapping(self) -> None:
        violation = LayerRuleViolation(
            rule_id="rule-1",
            source_layer_id="presentation",
            target_layer_id="infrastructure",
            dependency_count=3,
            message="Boundary violation detected."
        )
        validation = LayerRuleValidationResult(violations=[violation], diagnostics=[])
        
        res = self.detector.detect_smells(
            self.graph, self.layers, self.dependencies, validation, self.metrics
        )
        self.assertEqual(len(res.issues), 1)
        self.assertEqual(res.issues[0].title, "Layer Dependency Violation")
        self.assertEqual(res.issues[0].metadata["rule_id"], "rule-1")

    def test_high_coupling(self) -> None:
        # Presentation has efferent coupling = 25 (threshold=20)
        metrics = ArchitectureMetricsResult(
            layer_metrics=[
                LayerMetrics(layer_id="presentation", afferent_coupling=0, efferent_coupling=25, instability=1.0),
                LayerMetrics(layer_id="domain", afferent_coupling=0, efferent_coupling=0, instability=0.0),
                LayerMetrics(layer_id="infrastructure", afferent_coupling=0, efferent_coupling=0, instability=0.0),
            ],
            average_instability=0.33,
            total_afferent_coupling=0,
            total_efferent_coupling=25
        )
        res = self.detector.detect_smells(
            self.graph, self.layers, self.dependencies, self.validation, metrics
        )
        self.assertTrue(any(i.title == "High Efferent Coupling (Ce)" for i in res.issues))

    def test_unstable_dependency(self) -> None:
        # Dependency: presentation -> domain (count=5)
        # presentation instability = 0.9 (unstable)
        # domain instability = 0.2 (stable)
        # Difference = 0.7 > threshold 0.3
        deps = [LayerDependency(source_layer_id="presentation", target_layer_id="domain", dependency_count=5)]
        dependencies = LayerDependencyResult(dependencies=deps)
        
        metrics = ArchitectureMetricsResult(
            layer_metrics=[
                LayerMetrics(layer_id="presentation", afferent_coupling=0, efferent_coupling=5, instability=0.9),
                LayerMetrics(layer_id="domain", afferent_coupling=5, efferent_coupling=0, instability=0.2),
                LayerMetrics(layer_id="infrastructure", afferent_coupling=0, efferent_coupling=0, instability=0.0),
            ],
            average_instability=0.37,
            total_afferent_coupling=5,
            total_efferent_coupling=5
        )
        res = self.detector.detect_smells(
            self.graph, self.layers, dependencies, self.validation, metrics
        )
        self.assertTrue(any(i.title == "Unstable Dependency Boundary" for i in res.issues))

    def test_low_cohesion(self) -> None:
        # Cohesion of presentation:
        # internal edge (UI -> UI) = 1
        # external coupling (Ca + Ce) = 10
        # total = 11, cohesion = 1/11 = 0.09 < 0.20
        # We need an internal edge (intra-layer) n-ui -> n-ui
        # Pydantic validates DuplicateEdgeError if they are identical, so we need two nodes in presentation
        nodes = [
            GraphNode(id="n-ui1", name="UI1", type=DependencyNodeType.MODULE),
            GraphNode(id="n-ui2", name="UI2", type=DependencyNodeType.MODULE),
            GraphNode(id="n-biz", name="Biz", type=DependencyNodeType.MODULE),
        ]
        edge_internal = GraphEdge(source_id="n-ui1", target_id="n-ui2", type=DependencyEdgeType.USAGE)
        graph = DependencyGraph(nodes=nodes, edges=[edge_internal])
        
        layers = [
            ArchitectureLayer(id="presentation", name="Pres", layer_type=LayerType.PRESENTATION, node_ids=["n-ui1", "n-ui2"]),
            ArchitectureLayer(id="domain", name="Domain", layer_type=LayerType.DOMAIN, node_ids=["n-biz"]),
        ]
        metrics = ArchitectureMetricsResult(
            layer_metrics=[
                LayerMetrics(layer_id="presentation", afferent_coupling=0, efferent_coupling=10, instability=1.0),
                LayerMetrics(layer_id="domain", afferent_coupling=0, efferent_coupling=0, instability=0.0),
            ],
            average_instability=0.5,
            total_afferent_coupling=0,
            total_efferent_coupling=10
        )
        
        res = self.detector.detect_smells(
            graph, layers, self.dependencies, self.validation, metrics
        )
        self.assertEqual(len(res.issues), 1)
        self.assertEqual(res.issues[0].title, "Low Layer Cohesion")

    def test_god_component(self) -> None:
        # God layer: node count threshold is 5
        config = SmellDetectorConfig(god_layer_node_count_threshold=2)
        detector = ArchitectureSmellDetector(config)
        
        layers = [
            ArchitectureLayer(id="presentation", name="Pres", layer_type=LayerType.PRESENTATION, node_ids=["n-1", "n-2", "n-3"]),
        ]
        res = detector.detect_smells(
            self.graph, layers, self.dependencies, self.validation, self.metrics
        )
        self.assertEqual(len(res.issues), 1)
        self.assertEqual(res.issues[0].title, "God Layer Component")

    def test_feature_envy(self) -> None:
        # presentation has efferent coupling = 5, target = domain (5)
        # ratio = 5/5 = 1.0 > 0.7
        config = SmellDetectorConfig(feature_envy_min_edges=3, feature_envy_ratio=0.7)
        detector = ArchitectureSmellDetector(config)
        
        deps = [LayerDependency(source_layer_id="presentation", target_layer_id="domain", dependency_count=5)]
        dependencies = LayerDependencyResult(dependencies=deps)
        
        metrics = ArchitectureMetricsResult(
            layer_metrics=[
                LayerMetrics(layer_id="presentation", afferent_coupling=0, efferent_coupling=5, instability=1.0),
                LayerMetrics(layer_id="domain", afferent_coupling=5, efferent_coupling=0, instability=0.0),
            ],
            average_instability=0.5,
            total_afferent_coupling=5,
            total_efferent_coupling=5
        )
        
        res = detector.detect_smells(
            self.graph, self.layers, dependencies, self.validation, metrics
        )
        self.assertTrue(any(i.title == "Layer Feature Envy" for i in res.issues))

    def test_immutability(self) -> None:
        config = SmellDetectorConfig()
        with self.assertRaises((ValidationError, TypeError)):
            config.coupling_threshold = 10  # type: ignore

    def test_stateless_repeated_execution(self) -> None:
        res1 = self.detector.detect_smells(
            self.graph, self.layers, self.dependencies, self.validation, self.metrics
        )
        res2 = self.detector.detect_smells(
            self.graph, self.layers, self.dependencies, self.validation, self.metrics
        )
        self.assertEqual(res1, res2)

    def test_thread_safety(self) -> None:
        def run_detect():
            return self.detector.detect_smells(
                self.graph, self.layers, self.dependencies, self.validation, self.metrics
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_detect) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
