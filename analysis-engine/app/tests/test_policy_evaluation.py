"""Unit tests for the PolicyEvaluationService and rule evaluation logic."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.architecture.models import ArchitectureAnalysisResult, ArchitectureLayer, ArchitectureMetric
from app.evolution.interfaces import ArchitectureAnalysisProvider
from app.governance import (
    GovernancePolicy,
    GovernanceRequest,
    GovernanceStatus,
    PolicyCategory,
    PolicyDefinitionService,
    PolicyEvaluationService,
    PolicyMetadata,
    PolicyRule,
    RuleType,
    ViolationSeverity,
)
from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.models import QualityMetric, QualityReport, QualitySummary
from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.models import TechnicalDebtItem, TechnicalDebtReport, TechnicalDebtSummary


class TestPolicyEvaluation(unittest.TestCase):
    """Verifies complete evaluation logic of various rule types against mocked platforms outputs."""

    def setUp(self) -> None:
        self.provider = MagicMock(spec=ArchitectureAnalysisProvider)
        self.service = PolicyEvaluationService(self.provider)
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
        self.project_id = uuid.uuid4()

        # Setup standard mock objects
        self.graph = DependencyGraph(
            nodes=[
                GraphNode(id="src/app.py", name="app", type=DependencyNodeType.MODULE),
                GraphNode(id="src/db.py", name="db", type=DependencyNodeType.MODULE),
            ],
            edges=[
                GraphEdge(source_id="src/app.py", target_id="src/db.py", type=DependencyEdgeType.IMPORTS)
            ],
        )

        self.arch_result = ArchitectureAnalysisResult(
            issues=[],
            layers=[
                ArchitectureLayer(id="ui", name="UI", layer_type="presentation", node_ids=["src/app.py"]),
                ArchitectureLayer(id="db", name="DB", layer_type="data", node_ids=["src/db.py"]),
            ],
            metrics=[
                ArchitectureMetric(
                    name="coupling",
                    value=0.5,
                    unit="ratio",
                    description="Coupling ratio metric.",
                )
            ],
        )

        self.quality_report = QualityReport(
            project_name="Atlas",
            generated_at=self.time_utc,
            metrics=(
                QualityMetric(
                    name="complexity",
                    category=MetricCategory.COMPLEXITY,
                    value=12.0,
                    level=QualityLevel.GOOD,
                    description="Cognitive Complexity metric.",
                ),
            ),
            summary=QualitySummary(
                overall_score=85.0,
                overall_level=QualityLevel.GOOD,
                metrics_by_category={MetricCategory.COMPLEXITY: 12.0},
            ),
        )

        self.tech_debt_report = TechnicalDebtReport(
            project_name="Atlas",
            generated_at=self.time_utc,
            items=(),
            summary=TechnicalDebtSummary(
                total_items=0,
                total_effort_minutes=150,
                items_by_category={},
                effort_by_severity={},
            ),
        )

        # Mock standard provider returns
        self.provider.get_dependency_graph.return_value = self.graph
        self.provider.get_architecture_result.return_value = self.arch_result
        self.provider.get_quality_report.return_value = self.quality_report
        self.provider.get_technical_debt_report.return_value = self.tech_debt_report

    def test_empty_repository(self) -> None:
        """Verifies policy evaluation handles empty repository states gracefully without errors."""
        self.provider.get_dependency_graph.return_value = DependencyGraph(nodes=[], edges=[])
        self.provider.get_architecture_result.return_value = None
        self.provider.get_quality_report.return_value = None
        self.provider.get_technical_debt_report.return_value = None

        r = PolicyRule(
            name="ThresholdRule",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 10},
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 0)

    def test_empty_policy_set(self) -> None:
        """Verifies evaluation of request with empty policies list succeeds with PASSED status."""
        req = GovernanceRequest(
            project_id=self.project_id,
            project_name="P",
            commit_id="c1",
            policies=(),
        )
        res = self.service.evaluate_request(req)
        self.assertEqual(res.status, GovernanceStatus.PASSED)
        self.assertEqual(len(res.violations), 0)
        self.assertEqual(res.summary.total_rules, 0)

    def test_forbidden_dependency_violation(self) -> None:
        """Verifies detection of forbidden dependency links."""
        # Rule forbids app depending on db
        r = PolicyRule(
            name="No_App_To_DB",
            rule_type=RuleType.FORBIDDEN_DEPENDENCY,
            severity=ViolationSeverity.ERROR,
            configuration={
                "source_module": "src/app.py",
                "forbidden_modules": ("src/db.py",),
            },
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 1)
        self.assertIn("depends on forbidden module 'src/db.py'", violations[0].message)

    def test_required_dependency_violation(self) -> None:
        """Verifies detection of missing required dependencies."""
        # Rule requires app to depend on missing.py
        r = PolicyRule(
            name="Req_Missing",
            rule_type=RuleType.REQUIRED_DEPENDENCY,
            severity=ViolationSeverity.WARNING,
            configuration={
                "source_module": "src/app.py",
                "required_modules": ("src/missing.py",),
            },
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 1)
        self.assertIn("does not depend on required module 'src/missing.py'", violations[0].message)

    def test_layering_constraint_violation(self) -> None:
        """Verifies layer boundaries dependency constraints enforcement."""
        # Allowed UI layers does not list DB layer
        r = PolicyRule(
            name="Layer_Rule",
            rule_type=RuleType.LAYER_ORDERING,
            severity=ViolationSeverity.ERROR,
            configuration={"allowed_layer_dependencies": {"UI": ()}},
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 1)
        self.assertIn("depends on Layer 'DB' (src/db.py) which is not allowed", violations[0].message)

    def test_naming_convention_violation(self) -> None:
        """Verifies naming convention pattern checks."""
        r = PolicyRule(
            name="Naming_Convention",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.WARNING,
            configuration={"naming_pattern": "^test_.*"},
        )
        violations = self.service.evaluate_rule("c1", r)
        # Both app.py and db.py violate ^test_
        self.assertEqual(len(violations), 2)

    def test_ownership_violation(self) -> None:
        """Verifies ownership declaration constraints checks."""
        # DB node has no owner metadata defined
        r = PolicyRule(
            name="Require_Owner",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.INFO,
            configuration={"require_owner": True},
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 2)  # both have no owner
        self.assertIn("has no owner defined", violations[0].message)

    def test_complexity_threshold_violation(self) -> None:
        """Verifies complexity threshold constraints checks."""
        r = PolicyRule(
            name="Complexity_Max",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 10},
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 1)
        self.assertIn("exceeds maximum threshold of 10", violations[0].message)

    def test_coupling_threshold_violation(self) -> None:
        """Verifies coupling threshold constraints checks."""
        r = PolicyRule(
            name="Coupling_Max",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "coupling", "max_threshold": 0.2},
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 1)
        self.assertIn("exceeds maximum threshold of 0.2", violations[0].message)

    def test_technical_debt_threshold_violation(self) -> None:
        """Verifies technical debt minutes constraints checks."""
        r = PolicyRule(
            name="Debt_Max",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "effort_minutes", "max_threshold": 100},
        )
        violations = self.service.evaluate_rule("c1", r)
        self.assertEqual(len(violations), 2)  # "technical_debt_effort" and "effort_minutes" both match and exceed 100
        self.assertIn("exceeds maximum threshold of 100", violations[0].message)

    def test_evaluation_request_compilation(self) -> None:
        """Verifies evaluate_request integrates multiple policies and returns deterministic results."""
        r_complexity = PolicyRule(
            name="Complexity_Max",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 10},
        )
        r_coupling = PolicyRule(
            name="Coupling_Max",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.WARNING,
            configuration={"metric_name": "coupling", "max_threshold": 1.0},  # Passes (0.5 < 1.0)
        )

        meta = PolicyMetadata(
            name="AtlasPolicy",
            version="1.0.0",
            category=PolicyCategory.QUALITY,
            created_at=self.time_utc,
        )
        policy = GovernancePolicy(metadata=meta, rules=(r_complexity, r_coupling))

        req = GovernanceRequest(
            project_id=self.project_id,
            project_name="Atlas",
            commit_id="c1",
            policies=(policy,),
            correlation_id="test-corr",
        )

        res = self.service.evaluate_request(req)

        self.assertEqual(res.status, GovernanceStatus.FAILED)  # Due to complexity rule violation (severity ERROR)
        self.assertEqual(res.summary.total_rules, 2)
        self.assertEqual(res.summary.passed_count, 1)
        self.assertEqual(res.summary.failed_count, 1)
        self.assertEqual(len(res.violations), 1)


if __name__ == "__main__":
    unittest.main()
