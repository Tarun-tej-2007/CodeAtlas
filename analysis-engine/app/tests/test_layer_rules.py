"""Unit tests for the Layer Rule Validation Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType
from app.architecture.enums import LayerType
from app.architecture.models import ArchitectureLayer
from app.architecture.layer_dependency import LayerDependency, LayerDependencyResult
from app.architecture.layer_rules import (
    LayerRule,
    LayerRuleViolation,
    LayerRuleValidationResult,
    LayerRuleValidator,
)


class TestLayerRules(unittest.TestCase):
    """Verifies architectural rule matching, boundaries violation, and multithreaded runs."""

    def setUp(self) -> None:
        self.validator = LayerRuleValidator()
        self.layers = [
            ArchitectureLayer(id="presentation", name="Presentation", layer_type=LayerType.PRESENTATION, node_ids=["node1"]),
            ArchitectureLayer(id="domain", name="Domain", layer_type=LayerType.DOMAIN, node_ids=["node2"]),
            ArchitectureLayer(id="infrastructure", name="Infrastructure", layer_type=LayerType.INFRASTRUCTURE, node_ids=["node3"]),
        ]

    def test_empty_rules(self) -> None:
        # Dependency presentation -> domain exists, but rules are empty
        dep = LayerDependency(
            source_layer_id="presentation",
            target_layer_id="domain",
            dependency_count=5,
            edge_types=[DependencyEdgeType.USAGE]
        )
        dep_result = LayerDependencyResult(dependencies=[dep])
        
        res = self.validator.validate(dep_result, self.layers, [])
        self.assertEqual(res.violations, [])
        self.assertIn("Validation completed. Detected 0 violations.", res.diagnostics)

    def test_allowed_dependency(self) -> None:
        # Rule explicitly allows presentation -> domain
        rule = LayerRule(
            id="rule-pres-to-dom",
            name="Allow presentation to domain",
            source_layer="presentation",
            target_layer="domain",
            allow=True,
            metadata={"priority": "high"}
        )
        dep = LayerDependency(
            source_layer_id="presentation",
            target_layer_id="domain",
            dependency_count=3,
            edge_types=[DependencyEdgeType.USAGE]
        )
        dep_result = LayerDependencyResult(dependencies=[dep])

        res = self.validator.validate(dep_result, self.layers, [rule])
        self.assertEqual(res.violations, [])

    def test_denied_dependency_and_metadata_preservation(self) -> None:
        # Rule disallows presentation -> infrastructure
        rule = LayerRule(
            id="rule-no-pres-to-infra",
            name="Disallow presentation to infrastructure",
            source_layer="presentation",
            target_layer="infrastructure",
            allow=False,
            metadata={"severity": "high"}
        )
        dep = LayerDependency(
            source_layer_id="presentation",
            target_layer_id="infrastructure",
            dependency_count=2,
            edge_types=[DependencyEdgeType.USAGE]
        )
        dep_result = LayerDependencyResult(dependencies=[dep])

        res = self.validator.validate(dep_result, self.layers, [rule])
        
        self.assertEqual(len(res.violations), 1)
        violation = res.violations[0]
        self.assertEqual(violation.rule_id, "rule-no-pres-to-infra")
        self.assertEqual(violation.source_layer_id, "presentation")
        self.assertEqual(violation.target_layer_id, "infrastructure")
        self.assertEqual(violation.dependency_count, 2)
        self.assertEqual(violation.metadata, {"rule_name": "Disallow presentation to infrastructure"})
        self.assertIn("Layer boundary violation", violation.message)

    def test_deterministic_ordering(self) -> None:
        # Multiple violations triggered:
        # Rule 2: domain -> presentation (disallowed)
        # Rule 1: presentation -> infrastructure (disallowed)
        rule1 = LayerRule(id="rule-1", name="R1", source_layer="presentation", target_layer="infrastructure", allow=False)
        rule2 = LayerRule(id="rule-2", name="R2", source_layer="domain", target_layer="presentation", allow=False)
        
        dep1 = LayerDependency(source_layer_id="presentation", target_layer_id="infrastructure", dependency_count=1)
        dep2 = LayerDependency(source_layer_id="domain", target_layer_id="presentation", dependency_count=4)
        dep_result = LayerDependencyResult(dependencies=[dep1, dep2])

        res = self.validator.validate(dep_result, self.layers, [rule1, rule2])

        # Violations should be sorted by rule_id: rule-1, then rule-2
        self.assertEqual(len(res.violations), 2)
        self.assertEqual(res.violations[0].rule_id, "rule-1")
        self.assertEqual(res.violations[1].rule_id, "rule-2")

    def test_stateless_repeated_execution(self) -> None:
        rule = LayerRule(id="rule-1", name="R1", source_layer="presentation", target_layer="infrastructure", allow=False)
        dep = LayerDependency(source_layer_id="presentation", target_layer_id="infrastructure", dependency_count=1)
        dep_result = LayerDependencyResult(dependencies=[dep])

        res1 = self.validator.validate(dep_result, self.layers, [rule])
        res2 = self.validator.validate(dep_result, self.layers, [rule])
        self.assertEqual(res1, res2)

    def test_immutability(self) -> None:
        violation = LayerRuleViolation(
            rule_id="r1",
            source_layer_id="pres",
            target_layer_id="infra",
            dependency_count=3,
            message="Violated boundary"
        )
        with self.assertRaises((ValidationError, TypeError)):
            violation.dependency_count = 10  # type: ignore

    def test_thread_safety(self) -> None:
        rule = LayerRule(id="rule-1", name="R1", source_layer="presentation", target_layer="infrastructure", allow=False)
        dep = LayerDependency(source_layer_id="presentation", target_layer_id="infrastructure", dependency_count=1)
        dep_result = LayerDependencyResult(dependencies=[dep])

        def run_validation():
            return self.validator.validate(dep_result, self.layers, [rule])

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_validation) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
