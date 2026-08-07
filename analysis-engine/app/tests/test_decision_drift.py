"""Unit tests for the DecisionDriftAnalyzerService and drift validations."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionPriority,
    DecisionStatus,
    DecisionMetadata,
    DecisionTraceLink,
    DecisionTraceGraph,
    DecisionDrift,
    DecisionDriftReport,
    DecisionDriftAnalyzerService,
    DecisionValidationError,
)


class TestDecisionDrift(unittest.TestCase):
    """Verifies intent-vs-implementation checks, classifications, and report generation."""

    def setUp(self) -> None:
        self.service = DecisionDriftAnalyzerService()
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-drift-xyz"
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={},
        )

    def test_empty_inputs_validation(self) -> None:
        """Verifies report behaves correctly with empty collections or parameters."""
        trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(),
            links_by_target={},
            links_by_decision={},
        )
        report = self.service.analyze_drift(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(),
            trace_graph=trace_graph,
        )
        self.assertEqual(report.project_id, self.project_id)
        self.assertEqual(len(report.drifts), 0)

    def test_orphaned_decision_detection(self) -> None:
        """Verifies accepted decisions with no targets trigger orphaned findings."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="Use FastAPI",
            category=DecisionCategory.TECHNOLOGY,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.HIGH,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=self.metadata,
            relationships=(),
        )
        trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(),
            links_by_target={},
            links_by_decision={},
        )

        report = self.service.analyze_drift(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
            trace_graph=trace_graph,
        )

        self.assertEqual(len(report.drifts), 1)
        self.assertEqual(report.drifts[0].classification, "orphaned_decision")

    def test_missing_implementation_detection(self) -> None:
        """Verifies missing files declared in target lists are detected."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="Use FastAPI",
            category=DecisionCategory.TECHNOLOGY,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.HIGH,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("file:src/missing.py",)},
            ),
            relationships=(),
        )
        link = DecisionTraceLink(
            target_id="src/missing.py",
            target_type="file",
            decision_id=dec_id,
        )
        trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(link,),
            links_by_target={"file:src/missing.py": (dec_id,)},
            links_by_decision={str(dec_id): ("file:src/missing.py",)},
        )

        # Mock DependencyGraph where src/missing.py is absent
        dependency_graph = MagicMock()
        dependency_graph.has_node.return_value = False

        report = self.service.analyze_drift(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
            trace_graph=trace_graph,
            dependency_graph=dependency_graph,
        )

        self.assertEqual(len(report.drifts), 1)
        self.assertEqual(report.drifts[0].classification, "missing_implementation")

    def test_governance_conflict_detection(self) -> None:
        """Verifies policy failure violations matching target rules are flagged."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="Use FastAPI",
            category=DecisionCategory.TECHNOLOGY,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.HIGH,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("policy:naming_rule",)},
            ),
            relationships=(),
        )
        link = DecisionTraceLink(
            target_id="naming_rule",
            target_type="policy",
            decision_id=dec_id,
        )
        trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(link,),
        )

        # Mock Governance result containing violations for naming_rule
        gov_result = MagicMock()
        violation = MagicMock()
        violation.rule_name = "naming_rule"
        violation.message = "Violation msg."
        gov_result.violations = (violation,)

        report = self.service.analyze_drift(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
            trace_graph=trace_graph,
            governance_result=gov_result,
        )

        self.assertEqual(len(report.drifts), 1)
        self.assertEqual(report.drifts[0].classification, "governance_conflict")

    def test_evolution_divergence_detection(self) -> None:
        """Verifies evolution metrics regressions matching targets are flagged."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="T",
            category=DecisionCategory.TECHNOLOGY,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.HIGH,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("evolution:evolution_01",)},
            ),
        )
        link = DecisionTraceLink(
            target_id="evolution_01",
            target_type="evolution",
            decision_id=dec_id,
        )
        trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(link,),
        )

        # Mock Evolution result showing regressions
        ev_result = MagicMock()
        ev_result.status = "warning"

        report = self.service.analyze_drift(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
            trace_graph=trace_graph,
            evolution_result=ev_result,
        )

        self.assertEqual(len(report.drifts), 1)
        self.assertEqual(report.drifts[0].classification, "evolution_divergence")


if __name__ == "__main__":
    unittest.main()
