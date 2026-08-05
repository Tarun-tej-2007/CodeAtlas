"""Unit tests for the Report Persistence service."""

import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from app.reporting import (
    ReportFormat,
    ReportGenerationError,
    ReportMetadata,
    AnalysisReport,
    ReportRepository,
    ReportPersistenceService,
    AIReportAnalysisResult,
)


class InMemoryReportRepository(ReportRepository):
    """Thread-safe in-memory implementation of ReportRepository for testing purposes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[uuid.UUID, Any] = {}

    def save(self, report_id: uuid.UUID, report: Any) -> None:
        with self._lock:
            self._store[report_id] = report

    def get(self, report_id: uuid.UUID) -> Any:
        with self._lock:
            return self._store.get(report_id)

    def list_reports(self) -> Tuple[Any, ...]:
        with self._lock:
            # Deterministic sorting by key
            return tuple(self._store[k] for k in sorted(self._store.keys()))

    def delete(self, report_id: uuid.UUID) -> None:
        with self._lock:
            if report_id in self._store:
                del self._store[report_id]


class TestReportingPersistence(unittest.TestCase):
    """Verifies DTO lifecycle, invalid dependencies, DTO type constraints, and concurrent operations."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.repo = InMemoryReportRepository()
        self.service = ReportPersistenceService(self.repo)

        self.metadata = ReportMetadata(
            project_name="PersistProj",
            generated_at=self.time_utc,
            format=ReportFormat.JSON,
        )
        self.report = AnalysisReport(
            metadata=self.metadata,
            sections={},
        )

    def test_constructor_validation(self) -> None:
        """Verifies constructor rejects None or invalid repository objects."""
        with self.assertRaises(ValueError):
            ReportPersistenceService(None)  # type: ignore

        with self.assertRaises(TypeError):
            ReportPersistenceService("not_a_repo")  # type: ignore

    def test_save_and_retrieve_analysis_report(self) -> None:
        """Verifies AnalysisReport persistence, retrieval, and immutable DTO matching."""
        self.service.save_report(self.report)

        retrieved = self.service.get_report(self.report.id)
        self.assertEqual(retrieved.id, self.report.id)
        self.assertEqual(retrieved.metadata.project_name, "PersistProj")

    def test_save_and_retrieve_ai_report_analysis_result(self) -> None:
        """Verifies AIReportAnalysisResult wraps correctly, resolving inner report UUIDs."""
        from app.ai_service.models import AIResponse
        from app.ai_service.enums import ResponseStatus

        mock_ai_res = AIResponse(
            id="res-id-1",
            request_id="req-id-1",
            text_content="content",
            status=ResponseStatus.SUCCESS,
        )
        ai_result = AIReportAnalysisResult(
            report=self.report,
            ai_response=mock_ai_res,
        )

        self.service.save_report(ai_result)

        retrieved = self.service.get_report(self.report.id)
        self.assertEqual(retrieved.report.id, self.report.id)

    def test_save_rejections(self) -> None:
        """Verifies invalid types or None reports are rejected with ReportGenerationError."""
        with self.assertRaises(ReportGenerationError):
            self.service.save_report(None)

        with self.assertRaises(ReportGenerationError):
            self.service.save_report("invalid_string_dto")

    def test_delete_operations(self) -> None:
        """Verifies delete cleans up records and invalid UUID parameters raise validation errors."""
        self.service.save_report(self.report)
        self.assertTrue(self.repo.get(self.report.id) is not None)

        self.service.delete_report(self.report.id)
        self.assertIsNone(self.service.get_report(self.report.id))

        with self.assertRaises(ReportGenerationError):
            self.service.delete_report(None)  # type: ignore

    def test_list_reports(self) -> None:
        """Verifies list_reports returns immutable sorted list of entries."""
        rep2 = AnalysisReport(
            metadata=ReportMetadata(
                project_name="OtherProj",
                generated_at=self.time_utc,
                format=ReportFormat.HTML,
            ),
            sections={},
        )

        self.service.save_report(self.report)
        self.service.save_report(rep2)

        listed = self.service.list_reports()
        self.assertIsInstance(listed, tuple)
        self.assertEqual(len(listed), 2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety during parallel, concurrent save/read executions."""
        def run_operations(index: int):
            r = AnalysisReport(
                metadata=ReportMetadata(
                    project_name=f"Proj_{index}",
                    generated_at=self.time_utc,
                    format=ReportFormat.JSON,
                ),
                sections={},
            )
            self.service.save_report(r)
            ret = self.service.get_report(r.id)
            self.assertEqual(ret.metadata.project_name, f"Proj_{index}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_operations, i) for i in range(30)]
            for f in futures:
                f.result()

        self.assertEqual(len(self.service.list_reports()), 30)


if __name__ == "__main__":
    unittest.main()
