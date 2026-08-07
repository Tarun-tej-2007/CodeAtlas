"""Unit tests for the DecisionHealthAnalyzerService and health report scoring checks."""

import unittest
import uuid
from datetime import datetime, timezone, timedelta

from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionPriority,
    DecisionStatus,
    DecisionMetadata,
    DecisionTraceGraph,
    DecisionDriftReport,
    DecisionHealth,
    DecisionHealthReport,
    DecisionHealthAnalyzerService,
    DecisionValidationError,
)


class TestDecisionHealthAnalyzer(unittest.TestCase):
    """Verifies decision quality checks, freshness decay metrics, drift impact, and recommendation outputs."""

    def setUp(self) -> None:
        self.service = DecisionHealthAnalyzerService()
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-health-abc"
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={},
        )

        self.drift_report = DecisionDriftReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            drifts=(),
        )

        self.trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(),
        )

    def test_empty_repository(self) -> None:
        """Verifies evaluation constructs an Excellent report when input is empty."""
        report = self.service.analyze_health(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(),
            drift_report=self.drift_report,
            trace_graph=self.trace_graph,
        )
        self.assertEqual(report.health.overall_score, 100.0)
        self.assertEqual(report.health.classification, "Excellent")
        self.assertEqual(len(report.health.recommendations), 0)

    def test_orphaned_decision_impact(self) -> None:
        """Verifies score degradation and recommendation generation for orphaned decisions."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="Use PostgreSQL",
            category=DecisionCategory.INFRASTRUCTURE,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.CRITICAL,
            context="The database should be PostgreSQL.",
            decision_text="We accept PostgreSQL.",
            consequences="Requires DBA knowledge.",
            metadata=self.metadata,
        )

        report = self.service.analyze_health(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
            drift_report=self.drift_report,
            trace_graph=self.trace_graph,
        )

        # Orphaned Acceptance -> -15 to traceability, -10 to overall
        self.assertEqual(report.health.category_scores["traceability"], 85.0)
        self.assertEqual(report.health.overall_score, 90.0)
        self.assertIn("Define traceability targets for orphaned decisions.", report.health.recommendations)

    def test_stale_decision_decay(self) -> None:
        """Verifies score reduction for stale decisions older than 180 days."""
        stale_time = datetime.now(timezone.utc) - timedelta(days=200)
        stale_meta = DecisionMetadata(
            author="Lead Architect",
            created_at=stale_time,
            updated_at=stale_time,
            extra_info={"targets": ("file:src/app.py",)},
        )
        dec = ArchitectureDecision(
            decision_id=uuid.uuid4(),
            title="Use PostgreSQL",
            category=DecisionCategory.INFRASTRUCTURE,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.CRITICAL,
            context="The database should be PostgreSQL.",
            decision_text="We accept PostgreSQL.",
            consequences="Requires DBA knowledge.",
            metadata=stale_meta,
        )

        report = self.service.analyze_health(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
            drift_report=self.drift_report,
            trace_graph=self.trace_graph,
        )

        self.assertEqual(report.health.category_scores["freshness"], 90.0)
        self.assertEqual(report.health.overall_score, 95.0)
        self.assertIn("Review and refresh stale decisions older than 6 months.", report.health.recommendations)

    def test_validation_failures(self) -> None:
        """Verifies check throws DecisionValidationError on invalid project or commit ID arguments."""
        with self.assertRaises(DecisionValidationError):
            self.service.analyze_health(
                project_id=None,
                commit_id="commit1",
                decisions=(),
                drift_report=self.drift_report,
                trace_graph=self.trace_graph,
            )


if __name__ == "__main__":
    unittest.main()
