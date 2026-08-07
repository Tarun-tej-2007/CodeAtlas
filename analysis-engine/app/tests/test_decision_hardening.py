"""Unit and integration tests for Decision Intelligence production hardening."""

import logging
import threading
import time
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.decision.cache import execution_cache
from app.decision.exceptions import (
    DecisionError,
    DecisionPersistenceError,
    DecisionTraceabilityError,
    DecisionValidationError,
)
from app.decision.enums import DecisionCategory, DecisionPriority, DecisionStatus
from app.decision.interfaces import (
    DecisionBuilder,
    DecisionDriftAnalyzer,
    DecisionHealthAnalyzer,
    DecisionPersistence,
    DecisionTraceabilityProvider,
)
from app.decision.models import (
    ArchitectureDecision,
    DecisionAnalysisResult,
    DecisionDriftReport,
    DecisionHealth,
    DecisionHealthReport,
    DecisionRequest,
    DecisionTraceGraph,
    DecisionMetadata,
)
from app.decision.decision_intelligence import DecisionIntelligenceService


class TestDecisionHardening(unittest.TestCase):
    """Verifies timing metrics tracking, correlation propagation, exception translation and context cleanups."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.decision_id = uuid.uuid4()
        self.commit_id = "commit-hardening-123"
        self.correlation_id = "corr-hardening-test-uuid"
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={},
        )

        # Build mocked sub-engines
        self.builder = MagicMock(spec=DecisionBuilder)
        self.traceability = MagicMock(spec=DecisionTraceabilityProvider)
        self.drift = MagicMock(spec=DecisionDriftAnalyzer)
        self.health = MagicMock(spec=DecisionHealthAnalyzer)
        self.persistence = MagicMock(spec=DecisionPersistence)

        # Build standard output responses
        self.decision = ArchitectureDecision(
            decision_id=self.decision_id,
            title="T",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.LOW,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=self.metadata,
        )

        self.trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id=self.commit_id,
            links=(),
        )

        self.drift_report = DecisionDriftReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            drifts=(),
        )

        self.health_report = DecisionHealthReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            health=DecisionHealth(
                overall_score=100.0,
                classification="Excellent",
                recommendations=(),
            ),
        )

        self.persistence.list_decisions.return_value = (self.decision,)
        self.builder.build_from_request.return_value = self.decision
        self.traceability.trace_decisions.return_value = self.trace_graph
        self.drift.analyze_drift.return_value = self.drift_report
        self.health.analyze_health.return_value = self.health_report

        self.service = DecisionIntelligenceService(
            builder=self.builder,
            traceability_provider=self.traceability,
            drift_analyzer=self.drift,
            health_analyzer=self.health,
            persistence=self.persistence,
        )

        # Set up a test log interceptor handler
        self.logger = logging.getLogger("analysis-engine.decision")
        self.log_messages = []

        class InterceptHandler(logging.Handler):
            def emit(self, record):
                self.messages.append(record.getMessage())

        self.handler = InterceptHandler()
        self.handler.messages = self.log_messages
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def tearDown(self) -> None:
        self.logger.removeHandler(self.handler)

    def test_verify_decision_success_flow(self) -> None:
        """Verifies overall orchestration succeeds and records execution timings and correlation ID."""
        req = DecisionRequest(
            project_id=self.project_id,
            decision=self.decision,
        )

        result = self.service.analyze_project_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            requests=(req,),
            correlation_id=self.correlation_id,
        )

        # Assert correct DTO compilation
        self.assertEqual(result.project_id, self.project_id)
        self.assertEqual(result.commit_id, self.commit_id)

        # Assert timings are logged and included in extra_info
        metrics = result.extra_info.get("metrics")
        self.assertIsNotNone(metrics)
        self.assertIn("decision_build_ms", metrics)
        self.assertIn("traceability_analysis_ms", metrics)
        self.assertIn("drift_analysis_ms", metrics)
        self.assertIn("health_analysis_ms", metrics)
        self.assertIn("persistence_ms", metrics)
        self.assertIn("total_orchestration_ms", metrics)

        # Correlation ID present in extra_info
        self.assertEqual(result.extra_info.get("correlation_id"), self.correlation_id)

        # Logging messages contain correlation ID
        log_str = "".join(self.log_messages)
        self.assertIn(self.correlation_id, log_str)

    def test_cache_cleanup_after_exceptions(self) -> None:
        """Verifies cache context is completely cleaned up and reset even when run fails."""
        self.persistence.list_decisions.side_effect = RuntimeError("DB disconnect")
        req = DecisionRequest(
            project_id=self.project_id,
            decision=self.decision,
        )

        with self.assertRaises(DecisionPersistenceError):
            self.service.analyze_project_decisions(
                project_id=self.project_id,
                commit_id=self.commit_id,
                requests=(req,),
                correlation_id=self.correlation_id,
            )

        # Execution cache context must be completely empty/reset to None default outside block
        self.assertIsNone(execution_cache.get())


if __name__ == "__main__":
    unittest.main()
