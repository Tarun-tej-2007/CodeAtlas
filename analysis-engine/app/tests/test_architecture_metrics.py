"""Unit tests for the Architecture Metrics Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType
from app.architecture.enums import LayerType
from app.architecture.models import ArchitectureLayer
from app.architecture.layer_dependency import LayerDependency, LayerDependencyResult
from app.architecture.metrics import (
    LayerMetrics,
    ArchitectureMetricsResult,
    ArchitectureMetricsEngine,
)


class TestArchitectureMetrics(unittest.TestCase):
    """Verifies coupling, instability calculation, division-by-zero safety, and concurrent execution."""

    def setUp(self) -> None:
        self.engine = ArchitectureMetricsEngine()
        self.layers = [
            ArchitectureLayer(id="presentation", name="Presentation", layer_type=LayerType.PRESENTATION, node_ids=["n1"]),
            ArchitectureLayer(id="domain", name="Domain", layer_type=LayerType.DOMAIN, node_ids=["n2"]),
            ArchitectureLayer(id="infrastructure", name="Infrastructure", layer_type=LayerType.INFRASTRUCTURE, node_ids=["n3"]),
        ]

    def test_empty_architecture(self) -> None:
        dep_result = LayerDependencyResult(dependencies=[])
        res = self.engine.compute_metrics([], dep_result)
        
        self.assertEqual(res.layer_metrics, [])
        self.assertEqual(res.average_instability, 0.0)
        self.assertEqual(res.total_afferent_coupling, 0)
        self.assertEqual(res.total_efferent_coupling, 0)

    def test_single_layer(self) -> None:
        # Isolated single layer
        layer = ArchitectureLayer(id="core", name="Core", layer_type=LayerType.DOMAIN, node_ids=["n1"])
        dep_result = LayerDependencyResult(dependencies=[])
        res = self.engine.compute_metrics([layer], dep_result)

        self.assertEqual(len(res.layer_metrics), 1)
        lm = res.layer_metrics[0]
        self.assertEqual(lm.layer_id, "core")
        self.assertEqual(lm.afferent_coupling, 0)
        self.assertEqual(lm.efferent_coupling, 0)
        self.assertEqual(lm.instability, 0.0) # Zero-division handled safely

    def test_multiple_layers_and_coupling_calculation(self) -> None:
        # Configuration:
        # presentation -> domain (count=3)
        # domain -> infrastructure (count=2)
        # presentation -> infrastructure (count=1)
        deps = [
            LayerDependency(source_layer_id="presentation", target_layer_id="domain", dependency_count=3),
            LayerDependency(source_layer_id="domain", target_layer_id="infrastructure", dependency_count=2),
            LayerDependency(source_layer_id="presentation", target_layer_id="infrastructure", dependency_count=1),
        ]
        dep_result = LayerDependencyResult(dependencies=deps)

        res = self.engine.compute_metrics(self.layers, dep_result)

        # Expected sorted order: domain, infrastructure, presentation
        self.assertEqual(len(res.layer_metrics), 3)
        
        lm_dom = res.layer_metrics[0]
        self.assertEqual(lm_dom.layer_id, "domain")
        self.assertEqual(lm_dom.afferent_coupling, 3) # incoming from presentation (3)
        self.assertEqual(lm_dom.efferent_coupling, 2) # outgoing to infrastructure (2)
        self.assertEqual(lm_dom.instability, 2.0 / (3 + 2)) # 0.4

        lm_infra = res.layer_metrics[1]
        self.assertEqual(lm_infra.layer_id, "infrastructure")
        self.assertEqual(lm_infra.afferent_coupling, 2 + 1) # incoming from domain (2) + presentation (1) = 3
        self.assertEqual(lm_infra.efferent_coupling, 0)
        self.assertEqual(lm_infra.instability, 0.0)

        lm_pres = res.layer_metrics[2]
        self.assertEqual(lm_pres.layer_id, "presentation")
        self.assertEqual(lm_pres.afferent_coupling, 0)
        self.assertEqual(lm_pres.efferent_coupling, 3 + 1) # outgoing to domain (3) + infrastructure (1) = 4
        self.assertEqual(lm_pres.instability, 1.0) # 4 / (0 + 4) = 1.0

        # Aggregates
        self.assertEqual(res.total_afferent_coupling, 3 + 3 + 0) # 6
        self.assertEqual(res.total_efferent_coupling, 2 + 0 + 4) # 6
        # average instability = (0.4 + 0.0 + 1.0) / 3 = 0.4666...
        self.assertAlmostEqual(res.average_instability, 1.4 / 3.0)

    def test_serialization_and_dump(self) -> None:
        lm = LayerMetrics(
            layer_id="domain",
            afferent_coupling=2,
            efferent_coupling=3,
            instability=0.6
        )
        dump = lm.model_dump()
        self.assertEqual(dump["layer_id"], "domain")
        self.assertEqual(dump["instability"], 0.6)

        json_str = lm.model_dump_json()
        self.assertIn('"layer_id":"domain"', json_str)
        self.assertIn('"instability":0.6', json_str)

    def test_immutability(self) -> None:
        lm = LayerMetrics(
            layer_id="domain",
            afferent_coupling=2,
            efferent_coupling=3,
            instability=0.6
        )
        with self.assertRaises((ValidationError, TypeError)):
            lm.afferent_coupling = 5  # type: ignore

    def test_stateless_repeated_execution(self) -> None:
        deps = [LayerDependency(source_layer_id="presentation", target_layer_id="domain", dependency_count=3)]
        dep_result = LayerDependencyResult(dependencies=deps)

        res1 = self.engine.compute_metrics(self.layers, dep_result)
        res2 = self.engine.compute_metrics(self.layers, dep_result)
        self.assertEqual(res1, res2)

    def test_thread_safety(self) -> None:
        deps = [
            LayerDependency(source_layer_id="presentation", target_layer_id="domain", dependency_count=3),
            LayerDependency(source_layer_id="domain", target_layer_id="infrastructure", dependency_count=2),
        ]
        dep_result = LayerDependencyResult(dependencies=deps)

        def run_compute():
            return self.engine.compute_metrics(self.layers, dep_result)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_compute) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
