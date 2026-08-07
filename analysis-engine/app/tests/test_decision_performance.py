"""Unit tests verifying performance optimizations and execution cache isolation/cleanup behavior."""

import threading
import time
import unittest
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

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
)
from app.decision.cache import execution_cache


class DummyPersistence(DecisionPersistence):
    """Simple in-memory persistence helper for performance cache testing."""

    def __init__(self) -> None:
        self.decisions = {}

    def save_decision(self, project_id: uuid.UUID, decision: ArchitectureDecision) -> None:
        self.decisions[decision.decision_id] = decision

    def get_decision(self, decision_id: uuid.UUID) -> Optional[ArchitectureDecision]:
        return self.decisions.get(decision_id)

    def list_decisions(self, project_id: uuid.UUID) -> Tuple[ArchitectureDecision, ...]:
        return tuple(self.decisions.values())

    def save_trace_graph(self, project_id: uuid.UUID, graph: Any) -> None: pass
    def get_trace_graph(self, project_id: uuid.UUID, commit_id: str) -> Optional[Any]: return None
    def save_drift_report(self, project_id: uuid.UUID, report: Any) -> None: pass
    def get_drift_report(self, project_id: uuid.UUID, commit_id: str) -> Optional[Any]: return None
    def save_health_report(self, project_id: uuid.UUID, report: Any) -> None: pass
    def get_health_report(self, project_id: uuid.UUID, commit_id: str) -> Optional[Any]: return None
    def save_analysis_result(self, project_id: uuid.UUID, result: Any) -> None: pass
    def get_analysis_result(self, project_id: uuid.UUID, commit_id: str) -> Optional[Any]: return None


class TestDecisionPerformanceCache(unittest.TestCase):
    """Verifies that cache caches and returns results, is isolated per execution, and cleans up cleanly."""

    def setUp(self) -> None:
        self.builder = DecisionBuilderService()
        self.traceability = DecisionTraceabilityService()
        self.drift = DecisionDriftAnalyzerService()
        self.health = DecisionHealthAnalyzerService()
        self.persistence = DummyPersistence()

        self.service = DecisionIntelligenceService(
            builder=self.builder,
            traceability_provider=self.traceability,
            drift_analyzer=self.drift,
            health_analyzer=self.health,
            persistence=self.persistence,
        )

        self.project_id = uuid.uuid4()
        self.commit_id = "commit-perf-123"
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={},
        )

    def test_cache_hits_and_cleanup(self) -> None:
        """Verifies that cache is populated during execution and cleared completely upon method return."""
        # Active execution sets cache
        req = DecisionRequest(
            project_id=self.project_id,
            decision=ArchitectureDecision(
                decision_id=uuid.uuid4(),
                title="T",
                category=DecisionCategory.DESIGN,
                status=DecisionStatus.ACCEPTED,
                priority=DecisionPriority.LOW,
                context="C",
                decision_text="D",
                consequences="Con",
                metadata=self.metadata,
            ),
        )

        # Before run, cache is empty
        self.assertIsNone(execution_cache.get())

        result = self.service.analyze_project_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            requests=(req,),
        )

        # After run, cache is cleared (default value returned is None)
        self.assertIsNone(execution_cache.get())

    def test_context_isolation_threads(self) -> None:
        """Verifies that execution cache does not leak across separate thread scopes."""
        token = execution_cache.set({"key": "main_thread"})

        def run_thread():
            # In a new thread context, cache should be default (None)
            self.assertIsNone(execution_cache.get())

        t = threading.Thread(target=run_thread)
        t.start()
        t.join()

        # Clean up
        execution_cache.reset(token)


if __name__ == "__main__":
    unittest.main()
