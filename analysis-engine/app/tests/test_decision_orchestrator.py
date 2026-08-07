"""Unit tests for the DecisionIntelligenceService pipeline orchestrator."""

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
    DecisionRequest,
    DecisionBuilderService,
    DecisionTraceabilityService,
    DecisionDriftAnalyzerService,
    DecisionHealthAnalyzerService,
    DecisionIntelligenceService,
    DecisionPersistence,
    DecisionPersistenceError,
    DecisionTraceabilityError,
    DecisionValidationError,
)


class TestDecisionOrchestrator(unittest.TestCase):
    """Verifies pipeline stage coordination, exception translations, short-circuit, and DI."""

    def setUp(self) -> None:
        self.builder = DecisionBuilderService()
        self.traceability = DecisionTraceabilityService()
        self.drift = DecisionDriftAnalyzerService()
        self.health = DecisionHealthAnalyzerService()
        self.persistence = MagicMock(spec=DecisionPersistence)

        self.service = DecisionIntelligenceService(
            builder=self.builder,
            traceability_provider=self.traceability,
            drift_analyzer=self.drift,
            health_analyzer=self.health,
            persistence=self.persistence,
        )

        self.project_id = uuid.uuid4()
        self.commit_id = "commit-orchestration-123"
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)

    def test_empty_repository_short_circuit(self) -> None:
        """Verifies pipeline short-circuits to empty default response when no decisions exist."""
        self.persistence.list_decisions.return_value = ()
        result = self.service.analyze_project_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            requests=(),
        )

        self.assertEqual(result.project_id, self.project_id)
        self.assertEqual(len(result.decisions), 0)
        self.assertEqual(len(result.trace_graph.links), 0)
        self.assertEqual(result.health_report.health.overall_score, 100.0)

    def test_single_decision_workflow_orchestration(self) -> None:
        """Verifies full builder-traceability-drift-health workflow completes successfully for one item."""
        self.persistence.list_decisions.return_value = ()
        dec = ArchitectureDecision(
            decision_id=uuid.uuid4(),
            title="Use PostgreSQL",
            category=DecisionCategory.INFRASTRUCTURE,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.CRITICAL,
            context="The database should be PostgreSQL.",
            decision_text="We accept PostgreSQL.",
            consequences="Requires DBA knowledge.",
            metadata=DecisionMetadata(
                author="Lead Architect",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("file:src/db.py",)},
            ),
        )
        req = DecisionRequest(
            project_id=self.project_id,
            decision=dec,
        )

        result = self.service.analyze_project_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            requests=(req,),
        )

        # Persistence save check
        self.persistence.save_decision.assert_called_once()
        self.assertEqual(len(result.decisions), 1)
        self.assertEqual(result.decisions[0].title, "Use PostgreSQL")
        self.assertEqual(len(result.trace_graph.links), 1)
        self.assertEqual(result.trace_graph.links[0].target_id, "src/db.py")

    def test_exception_translation_persistence(self) -> None:
        """Verifies pipeline translates storage failures to DecisionPersistenceError."""
        self.persistence.list_decisions.side_effect = Exception("DB disconnect")
        with self.assertRaises(DecisionPersistenceError):
            self.service.analyze_project_decisions(
                project_id=self.project_id,
                commit_id=self.commit_id,
                requests=(),
            )


if __name__ == "__main__":
    unittest.main()
