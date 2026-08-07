"""Unit tests for the AIAnalysisPersistenceService component."""

import threading
import unittest
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.ai import (
    AIAnalysis,
    AIAnalysisStatus,
    AIAnalysisType,
    AIContext,
    AIMetadata,
    AIProvider,
    AIRecommendation,
    AIResult,
    AIUsageStatistics,
    AIPersistenceError,
    AIRepository,
    ArchitectureReview,
    RefactoringRoadmap,
)
from app.ai.ai_persistence import AIAnalysisPersistenceService


class InMemoryAIRepository(AIRepository):
    """In-memory thread-safe implementation of AIRepository for testing."""

    def __init__(self) -> None:
        self._store: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def save_data(self, key: str, data: dict) -> None:
        with self._lock:
            self._store[key] = data

    def get_data(self, key: str) -> Optional[dict]:
        with self._lock:
            return self._store.get(key)

    def delete_data(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]

    def list_keys(self, prefix: str) -> Tuple[str, ...]:
        with self._lock:
            return tuple(k for k in self._store.keys() if k.startswith(prefix))


class FailingAIRepository(AIRepository):
    """Mock repository that raises errors for exception translation validation."""

    def save_data(self, key: str, data: dict) -> None:
        raise RuntimeError("Disk write failure")

    def get_data(self, key: str) -> Optional[dict]:
        raise RuntimeError("Disk read failure")

    def delete_data(self, key: str) -> None:
        raise RuntimeError("Disk delete failure")

    def list_keys(self, prefix: str) -> Tuple[str, ...]:
        raise RuntimeError("Disk list failure")


class TestAIPersistence(unittest.TestCase):
    """Verifies that serialization, DTO validation, and storage aggregation function correctly."""

    def setUp(self) -> None:
        self.repository = InMemoryAIRepository()
        self.service = AIAnalysisPersistenceService(self.repository)

        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)

        self.metadata = AIMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            provider=AIProvider.MOCK,
            model_name="mock-model",
            temperature=0.0,
            extra_info={},
        )
        self.analysis = AIAnalysis(
            analysis_id=uuid.uuid4(),
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            status=AIAnalysisStatus.COMPLETED,
            started_at=self.time_utc,
            completed_at=self.time_utc,
            statistics=AIUsageStatistics(),
            recommendations=(
                AIRecommendation(
                    title="R1",
                    description="Desc 1",
                    category="architecture",
                    priority="critical",
                ),
            ),
        )

        self.result = AIResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis=self.analysis,
            extra_info={
                "review": ArchitectureReview(
                    project_id=self.project_id,
                    commit_id=self.commit_id,
                    executive_summary="Review text",
                    roadmap=RefactoringRoadmap(estimated_workload="low"),
                )
            },
        )

    def test_save_and_retrieve_analysis_roundtrip(self) -> None:
        """Verifies full serialization/deserialization and DTO reconstruction for AIAnalysis."""
        self.service.save_analysis(self.project_id, self.analysis)

        retrieved = self.service.get_analysis(self.analysis.analysis_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.analysis_id, self.analysis.analysis_id)
        self.assertEqual(retrieved.commit_id, self.analysis.commit_id)
        self.assertEqual(len(retrieved.recommendations), 1)
        self.assertEqual(retrieved.recommendations[0].title, "R1")

    def test_save_and_retrieve_result_roundtrip(self) -> None:
        """Verifies full serialization/deserialization for AIResult."""
        self.service.save_result(self.project_id, self.result)

        retrieved = self.service.get_result(self.project_id, self.commit_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.project_id, self.project_id)
        self.assertEqual(retrieved.commit_id, self.commit_id)
        self.assertEqual(retrieved.analysis.analysis_id, self.analysis.analysis_id)

        # Check nested review object inside extra_info
        review = retrieved.extra_info.get("review")
        self.assertIsNotNone(review)
        self.assertEqual(review.executive_summary, "Review text")

    def test_overwrite_behavior(self) -> None:
        """Verifies that writing to the same project and commit overwrites the existing result."""
        self.service.save_result(self.project_id, self.result)

        updated_result = AIResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis=self.analysis,
            extra_info={},
        )
        self.service.save_result(self.project_id, updated_result)

        retrieved = self.service.get_result(self.project_id, self.commit_id)
        self.assertEqual(retrieved.extra_info, {})

    def test_missing_records(self) -> None:
        """Verifies that query queries return None for non-existent IDs."""
        self.assertIsNone(self.service.get_analysis(uuid.uuid4()))
        self.assertIsNone(self.service.get_result(self.project_id, "non-existent-commit"))

    def test_list_analyses_and_deterministic_ordering(self) -> None:
        """Verifies analyses listing sorted by started_at descending."""
        a1 = self.analysis
        a2 = AIAnalysis(
            analysis_id=uuid.uuid4(),
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.SECURITY_REVIEW,
            status=AIAnalysisStatus.COMPLETED,
            started_at=datetime(2026, 8, 7, 11, 0, 0, tzinfo=timezone.utc),
            completed_at=self.time_utc,
        )
        self.service.save_analysis(self.project_id, a1)
        self.service.save_analysis(self.project_id, a2)

        analyses = self.service.list_analyses(self.project_id)
        self.assertEqual(len(analyses), 2)
        # a2 has later started_at (11:00) than a1 (10:00), so it must be first
        self.assertEqual(analyses[0].analysis_id, a2.analysis_id)
        self.assertEqual(analyses[1].analysis_id, a1.analysis_id)

    def test_delete_result(self) -> None:
        """Verifies result removal functionality."""
        self.service.save_result(self.project_id, self.result)
        self.assertIsNotNone(self.service.get_result(self.project_id, self.commit_id))

        self.service.delete_result(self.project_id, self.commit_id)
        self.assertIsNone(self.service.get_result(self.project_id, self.commit_id))

    def test_exception_translation(self) -> None:
        """Verifies that generic repository errors translate to AIPersistenceError."""
        failing_service = AIAnalysisPersistenceService(FailingAIRepository())

        with self.assertRaises(AIPersistenceError):
            failing_service.save_analysis(self.project_id, self.analysis)

        with self.assertRaises(AIPersistenceError):
            failing_service.get_analysis(self.analysis.analysis_id)

        with self.assertRaises(AIPersistenceError):
            failing_service.list_analyses(self.project_id)

        with self.assertRaises(AIPersistenceError):
            failing_service.delete_result(self.project_id, self.commit_id)

    def test_thread_safety(self) -> None:
        """Simulates parallel concurrent saves and list queries to verify thread-safety."""
        threads = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                analysis = AIAnalysis(
                    analysis_id=uuid.uuid4(),
                    project_id=self.project_id,
                    commit_id=f"commit-{worker_id}",
                    analysis_type=AIAnalysisType.SECURITY_REVIEW,
                    status=AIAnalysisStatus.COMPLETED,
                    started_at=datetime.now(timezone.utc),
                )
                self.service.save_analysis(self.project_id, analysis)
                self.service.list_analyses(self.project_id)
            except Exception as e:
                errors.append(e)

        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Thread safety test failed with errors: {errors}")


if __name__ == "__main__":
    unittest.main()
