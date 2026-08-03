"""Comprehensive Integration and Validation tests for the complete Architecture Analysis Subsystem."""

import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphNode, GraphEdge
from app.graph.dependency_graph import DependencyGraph

from app.architecture import (
    LayerType,
    AnalysisCategory,
    SeverityLevel,
    ArchitectureLayer,
    LayerDetectionRule,
    LayerDetector,
    LayerDependencyAnalyzer,
    LayerRule,
    LayerRuleValidator,
    ArchitectureMetricsEngine,
    ArchitectureSmellDetector,
    SmellDetectorConfig,
)


class TestArchitectureValidation(unittest.TestCase):
    """Exercises the complete architecture analysis pipeline end-to-end under high concurrency."""

    def setUp(self) -> None:
        self.detector_rules = [
            LayerDetectionRule(
                layer_id="presentation",
                layer_name="Presentation Layer",
                layer_type=LayerType.PRESENTATION,
                id_patterns=[r".*/controllers/.*"]
            ),
            LayerDetectionRule(
                layer_id="domain",
                layer_name="Domain Layer",
                layer_type=LayerType.DOMAIN,
                id_patterns=[r".*/services/.*"]
            ),
            LayerDetectionRule(
                layer_id="infrastructure",
                layer_name="Infrastructure Layer",
                layer_type=LayerType.INFRASTRUCTURE,
                id_patterns=[r".*/db/.*"]
            )
        ]
        self.detector = LayerDetector(self.detector_rules)
        self.dep_analyzer = LayerDependencyAnalyzer()
        
        self.validation_rules = [
            LayerRule(id="rule-pres-to-dom", name="Pres to Dom", source_layer="presentation", target_layer="domain", allow=True),
            LayerRule(id="rule-dom-to-infra", name="Dom to Infra", source_layer="domain", target_layer="infrastructure", allow=True),
            LayerRule(id="rule-no-pres-to-infra", name="No Pres to Infra", source_layer="presentation", target_layer="infrastructure", allow=False),
        ]
        self.validator = LayerRuleValidator()
        self.metrics_engine = ArchitectureMetricsEngine()
        
        self.smell_config = SmellDetectorConfig(
            coupling_threshold=5,
            cohesion_threshold=0.1,
            god_layer_node_count_threshold=10
        )
        self.smell_detector = ArchitectureSmellDetector(self.smell_config)

    def test_end_to_end_pipeline_execution(self) -> None:
        # 1. Setup mock nodes and edges
        nodes = [
            GraphNode(id="src/controllers/user_controller.py", name="user_controller", type=DependencyNodeType.MODULE),
            GraphNode(id="src/services/user_service.py", name="user_service", type=DependencyNodeType.MODULE),
            GraphNode(id="src/db/connection.py", name="connection", type=DependencyNodeType.MODULE),
        ]
        edges = [
            # Allowed dependency Presentation -> Domain
            GraphEdge(source_id="src/controllers/user_controller.py", target_id="src/services/user_service.py", type=DependencyEdgeType.USAGE),
            # Allowed dependency Domain -> Infrastructure
            GraphEdge(source_id="src/services/user_service.py", target_id="src/db/connection.py", type=DependencyEdgeType.USAGE),
            # Violating dependency Presentation -> Infrastructure
            GraphEdge(source_id="src/controllers/user_controller.py", target_id="src/db/connection.py", type=DependencyEdgeType.USAGE),
            # Cycle dependency forming a loop: Infrastructure -> Presentation (leads to cycle)
            GraphEdge(source_id="src/db/connection.py", target_id="src/controllers/user_controller.py", type=DependencyEdgeType.USAGE),
        ]
        graph = DependencyGraph(nodes=nodes, edges=edges)

        # 2. Run Layer Detection
        layers = self.detector.detect_layers(graph)
        self.assertEqual(len(layers), 3)
        self.assertEqual(layers[0].id, "domain")
        self.assertEqual(layers[1].id, "infrastructure")
        self.assertEqual(layers[2].id, "presentation")

        # 3. Run Layer Dependency Aggregation
        deps = self.dep_analyzer.analyze(graph, layers)
        # Expected inter-layer transitions:
        # presentation -> domain (1)
        # presentation -> infrastructure (1)
        # domain -> infrastructure (1)
        # infrastructure -> presentation (1)
        self.assertEqual(len(deps.dependencies), 4)

        # 4. Run Boundary Rule Validation
        validation_res = self.validator.validate(deps, layers, self.validation_rules)
        # Violation detected: presentation -> infrastructure is forbidden
        self.assertEqual(len(validation_res.violations), 1)
        self.assertEqual(validation_res.violations[0].rule_id, "rule-no-pres-to-infra")

        # 5. Run Metrics Computation
        metrics_res = self.metrics_engine.compute_metrics(layers, deps)
        self.assertEqual(len(metrics_res.layer_metrics), 3)

        # 6. Run Smell Detection
        analysis_result = self.smell_detector.detect_smells(
            graph, layers, deps, validation_res, metrics_res
        )

        # 7. Asserts on issues
        # Check cyclic dependency smell is detected
        self.assertTrue(any(i.title == "Cyclic Dependency Detected" for i in analysis_result.issues))
        # Check layer boundary violation is detected
        self.assertTrue(any(i.title == "Layer Dependency Violation" for i in analysis_result.issues))

        # Check metrics are correctly translated in final analysis result
        self.assertTrue(any(m.name == "average_instability" for m in analysis_result.metrics))
        self.assertTrue(any(m.name == "layer_domain_instability" for m in analysis_result.metrics))

        # Validate serialization of final payload
        json_payload = analysis_result.model_dump_json()
        self.assertIn("issues", json_payload)
        self.assertIn("metrics", json_payload)

    def test_thread_safety_under_load(self) -> None:
        nodes = [
            GraphNode(id="src/controllers/user_controller.py", name="user_controller", type=DependencyNodeType.MODULE),
            GraphNode(id="src/services/user_service.py", name="user_service", type=DependencyNodeType.MODULE),
            GraphNode(id="src/db/connection.py", name="connection", type=DependencyNodeType.MODULE),
        ]
        edges = [
            GraphEdge(source_id="src/controllers/user_controller.py", target_id="src/services/user_service.py", type=DependencyEdgeType.USAGE),
            GraphEdge(source_id="src/services/user_service.py", target_id="src/db/connection.py", type=DependencyEdgeType.USAGE),
        ]
        graph = DependencyGraph(nodes=nodes, edges=edges)

        def run_full_pipeline():
            layers = self.detector.detect_layers(graph)
            deps = self.dep_analyzer.analyze(graph, layers)
            validation_res = self.validator.validate(deps, layers, self.validation_rules)
            metrics_res = self.metrics_engine.compute_metrics(layers, deps)
            return self.smell_detector.detect_smells(
                graph, layers, deps, validation_res, metrics_res
            )

        # Execute 20 runs in parallel using 8 thread pool workers to assert stateless thread-confinement
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_full_pipeline) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for result in results:
            self.assertEqual(result.issues, first.issues)
            self.assertEqual(len(result.metrics), len(first.metrics))


if __name__ == "__main__":
    unittest.main()
