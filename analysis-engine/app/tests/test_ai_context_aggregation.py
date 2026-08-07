"""Unit tests for the AIContextAggregationService component."""

import unittest
import uuid
from datetime import datetime, timezone

from pydantic import ValidationError

from app.ai import (
    AIContext,
    AIValidationError,
)
from app.ai.context_aggregation import AIContextAggregationService
from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.architecture.enums import AnalysisCategory, LayerType, SeverityLevel
from app.architecture.models import ArchitectureAnalysisResult, ArchitectureIssue, ArchitectureLayer, ArchitectureMetric
from app.governance.enums import GovernanceStatus, ViolationSeverity
from app.governance.models import GovernanceResult, PolicyViolation, GovernanceSummary
from app.decision.enums import DecisionCategory, DecisionPriority, DecisionStatus
from app.decision.models import ArchitectureDecision, DecisionMetadata, DecisionRelationship


class TestAIContextAggregation(unittest.TestCase):
    """Verifies that context aggregation is stateless, safe, deterministic, and robust."""

    def setUp(self) -> None:
        self.service = AIContextAggregationService()
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"

        # Mocking items
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)
        self.node_a = GraphNode(id="src\\a.py", name="a", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="src\\b.py", name="b", type=DependencyNodeType.MODULE)
        self.edge = GraphEdge(source_id="src\\a.py", target_id="src\\b.py", type=DependencyEdgeType.IMPORTS)
        self.dep_graph = DependencyGraph(nodes=[self.node_a, self.node_b], edges=[self.edge])

        self.arch_issue = ArchitectureIssue(
            id="issue-1",
            title="Layer violation",
            description="UI depends on DB directly.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Refactor layers.",
            location="src\\a.py",
        )
        self.arch_layer = ArchitectureLayer(
            id="layer-ui",
            name="UI",
            layer_type=LayerType.APPLICATION,
            node_ids=["src\\a.py"],
        )
        self.arch_metric = ArchitectureMetric(
            name="coupling",
            value=0.8,
            unit="dimensionless",
            description="Coupling ratio.",
        )
        self.arch_result = ArchitectureAnalysisResult(
            issues=[self.arch_issue],
            layers=[self.arch_layer],
            metrics=[self.arch_metric],
        )

        self.violation = PolicyViolation(
            violation_id=uuid.uuid4(),
            rule_id=uuid.uuid4(),
            rule_name="NoUItoDB",
            severity=ViolationSeverity.ERROR,
            message="UI imports DB.py",
        )
        self.governance_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=(self.violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )

        self.decision = ArchitectureDecision(
            decision_id=uuid.uuid4(),
            title="Use PostgreSQL",
            category=DecisionCategory.TECHNOLOGY,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.HIGH,
            context="Need rel database.",
            decision_text="We choose PG.",
            consequences="Relational safety.",
            metadata=DecisionMetadata(author="Lead", created_at=self.time_utc, updated_at=self.time_utc),
        )

    def test_invalid_parameters(self) -> None:
        """Verifies fail-fast validation on missing inputs."""
        with self.assertRaises(AIValidationError):
            self.service.build_context(None, self.commit_id)

        with self.assertRaises(AIValidationError):
            self.service.build_context(self.project_id, "")

    def test_empty_repository(self) -> None:
        """Verifies successful execution when all subsystems are empty/None."""
        ctx = self.service.build_context(self.project_id, self.commit_id)

        self.assertEqual(ctx.project_id, self.project_id)
        self.assertEqual(ctx.commit_id, self.commit_id)
        self.assertIsNone(ctx.dependency_graph_summary)
        self.assertEqual(ctx.architecture_issues, ())
        self.assertEqual(ctx.governance_violations, ())
        self.assertEqual(ctx.decisions_summary, ())
        self.assertEqual(ctx.files_count, 0)

    def test_only_one_subsystem(self) -> None:
        """Verifies behavior when only one subsystem is provided."""
        ctx = self.service.build_context(self.project_id, self.commit_id, dependency_graph=self.dep_graph)

        self.assertIsNotNone(ctx.dependency_graph_summary)
        self.assertIn("Node: src/a.py (module)", ctx.dependency_graph_summary)
        self.assertIn("Edge: src/a.py -> src/b.py (imports)", ctx.dependency_graph_summary)
        self.assertEqual(ctx.files_count, 2)
        self.assertEqual(ctx.architecture_issues, ())

    def test_all_subsystems_and_windows_path_normalization(self) -> None:
        """Verifies all outputs are aggregated, paths are normalized to forward slashes, and order is deterministic."""
        ctx = self.service.build_context(
            project_id=self.project_id,
            commit_id=self.commit_id,
            dependency_graph=self.dep_graph,
            arch_result=self.arch_result,
            governance_result=self.governance_result,
            decisions=(self.decision,),
        )

        # Path normalization check
        self.assertIn("Node: src/a.py (module)", ctx.dependency_graph_summary)
        self.assertIn("Location: src/a.py", ctx.architecture_issues[0])

        # Architecture checks
        self.assertEqual(len(ctx.architecture_issues), 1)
        self.assertIn("Layer violation", ctx.architecture_issues[0])

        # Governance checks
        self.assertEqual(len(ctx.governance_violations), 1)
        self.assertIn("NoUItoDB [error]", ctx.governance_violations[0])

        # Decision checks
        self.assertEqual(len(ctx.decisions_summary), 1)
        self.assertIn("Use PostgreSQL (technology)", ctx.decisions_summary[0])

    def test_duplicate_removal_and_ordering(self) -> None:
        """Verifies duplicate entries are discarded and output lists are sorted alphabetically."""
        node_dup = GraphNode(id="src/a.py", name="a", type=DependencyNodeType.MODULE)
        graph = DependencyGraph(nodes=[node_dup, self.node_a], edges=[])

        ctx = self.service.build_context(self.project_id, self.commit_id, dependency_graph=graph)

        # Count occurrences of "Node: src/a.py" in summary string
        summary = ctx.dependency_graph_summary
        self.assertEqual(summary.count("Node: src/a.py"), 1)


if __name__ == "__main__":
    unittest.main()
