"""Unit tests for the Dashboard Persistence service."""

import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from app.dashboard import (
    DashboardStatus,
    DashboardValidationError,
    DashboardMetadata,
    DashboardModel,
    DashboardRepository,
    DashboardPersistenceService,
    AIDashboardAnalysisResult,
)


class InMemoryDashboardRepository(DashboardRepository):
    """Thread-safe in-memory implementation of DashboardRepository for testing purposes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[uuid.UUID, Any] = {}

    def save(self, dashboard_id: uuid.UUID, dashboard: Any) -> None:
        with self._lock:
            self._store[dashboard_id] = dashboard

    def get(self, dashboard_id: uuid.UUID) -> Any:
        with self._lock:
            return self._store.get(dashboard_id)

    def list_dashboards(self) -> Tuple[Any, ...]:
        with self._lock:
            # Deterministic sorting by key
            return tuple(self._store[k] for k in sorted(self._store.keys()))

    def delete(self, dashboard_id: uuid.UUID) -> None:
        with self._lock:
            if dashboard_id in self._store:
                del self._store[dashboard_id]


class TestDashboardPersistence(unittest.TestCase):
    """Verifies DTO lifecycle, invalid dependencies, DTO type constraints, and concurrent operations."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.repo = InMemoryDashboardRepository()
        self.service = DashboardPersistenceService(self.repo)

        self.metadata = DashboardMetadata(
            project_name="PersistProj",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
        )
        self.dashboard = DashboardModel(
            metadata=self.metadata,
            widgets={},
        )

    def test_constructor_validation(self) -> None:
        """Verifies constructor rejects None or invalid repository objects."""
        with self.assertRaises(ValueError):
            DashboardPersistenceService(None)  # type: ignore

        with self.assertRaises(TypeError):
            DashboardPersistenceService("not_a_repo")  # type: ignore

    def test_save_and_retrieve_dashboard_model(self) -> None:
        """Verifies DashboardModel persistence, retrieval, and immutable DTO matching."""
        self.service.save_dashboard(self.dashboard)

        retrieved = self.service.get_dashboard(self.dashboard.id)
        self.assertEqual(retrieved.id, self.dashboard.id)
        self.assertEqual(retrieved.metadata.project_name, "PersistProj")

    def test_save_and_retrieve_ai_dashboard_analysis_result(self) -> None:
        """Verifies AIDashboardAnalysisResult wraps correctly, resolving inner dashboard UUIDs."""
        from app.ai_service.models import AIResponse
        from app.ai_service.enums import ResponseStatus

        mock_ai_res = AIResponse(
            id="res-id-1",
            request_id="req-id-1",
            text_content="content",
            status=ResponseStatus.SUCCESS,
        )
        ai_result = AIDashboardAnalysisResult(
            dashboard=self.dashboard,
            ai_response=mock_ai_res,
        )

        self.service.save_dashboard(ai_result)

        retrieved = self.service.get_dashboard(self.dashboard.id)
        self.assertEqual(retrieved.dashboard.id, self.dashboard.id)

    def test_save_rejections(self) -> None:
        """Verifies invalid types or None reports are rejected with DashboardValidationError."""
        with self.assertRaises(DashboardValidationError):
            self.service.save_dashboard(None)

        with self.assertRaises(DashboardValidationError):
            self.service.save_dashboard("invalid_string_dto")

    def test_delete_operations(self) -> None:
        """Verifies delete cleans up records and invalid UUID parameters raise validation errors."""
        self.service.save_dashboard(self.dashboard)
        self.assertTrue(self.repo.get(self.dashboard.id) is not None)

        self.service.delete_dashboard(self.dashboard.id)
        self.assertIsNone(self.service.get_dashboard(self.dashboard.id))

        with self.assertRaises(DashboardValidationError):
            self.service.delete_dashboard(None)  # type: ignore

    def test_list_dashboards(self) -> None:
        """Verifies list_dashboards returns immutable sorted list of entries."""
        dash2 = DashboardModel(
            metadata=DashboardMetadata(
                project_name="OtherProj",
                created_at=self.time_utc,
                status=DashboardStatus.PENDING,
            ),
            widgets={},
        )

        self.service.save_dashboard(self.dashboard)
        self.service.save_dashboard(dash2)

        listed = self.service.list_dashboards()
        self.assertIsInstance(listed, tuple)
        self.assertEqual(len(listed), 2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety during parallel, concurrent save/read executions."""
        def run_operations(index: int):
            r = DashboardModel(
                metadata=DashboardMetadata(
                    project_name=f"Proj_{index}",
                    created_at=self.time_utc,
                    status=DashboardStatus.READY,
                ),
                widgets={},
            )
            self.service.save_dashboard(r)
            ret = self.service.get_dashboard(r.id)
            self.assertEqual(ret.metadata.project_name, f"Proj_{index}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_operations, i) for i in range(20)]
            for f in futures:
                f.result()

        self.assertEqual(len(self.service.list_dashboards()), 20)


if __name__ == "__main__":
    unittest.main()
