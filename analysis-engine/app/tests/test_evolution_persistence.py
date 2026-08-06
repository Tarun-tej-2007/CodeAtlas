"""Unit and integration tests for the Architecture Evolution Persistence Subsystem."""

import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from app.evolution import (
    ArchitecturalChange,
    ArchitecturalChangeType,
    ArchitecturalRisk,
    ArchitecturalRiskReport,
    ArchitectureEvolutionPersistenceService,
    ArchitectureEvolutionRepository,
    ArchitectureSnapshot,
    EvolutionMetadata,
    EvolutionPersistenceError,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionTrendResult,
    EvolutionValidationError,
    RiskSeverity,
)


class InMemoryArchitectureEvolutionRepository(ArchitectureEvolutionRepository):
    """Thread-safe in-memory database stub for testing."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._results: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}
        self._trends: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._risk_reports: Dict[uuid.UUID, Dict[str, Any]] = {}
        self.should_fail = False

    def save_result(self, result_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database write transaction failed.")
            self._results[result_id] = result_data

    def get_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database read transaction failed.")
            return self._results.get(result_id)

    def list_results(self) -> Tuple[Dict[str, Any], ...]:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database list transaction failed.")
            return tuple(self._results.values())

    def save_snapshot(self, commit_id: str, snapshot_data: Dict[str, Any]) -> None:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database write transaction failed.")
            self._snapshots[commit_id] = snapshot_data

    def get_snapshot(self, commit_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database read transaction failed.")
            return self._snapshots.get(commit_id)

    def save_trend(self, trend_id: uuid.UUID, trend_data: Dict[str, Any]) -> None:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database write transaction failed.")
            self._trends[trend_id] = trend_data

    def get_trend(self, trend_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database read transaction failed.")
            return self._trends.get(trend_id)

    def save_risk_report(self, report_id: uuid.UUID, report_data: Dict[str, Any]) -> None:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database write transaction failed.")
            self._risk_reports[report_id] = report_data

    def get_risk_report(self, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        with self._lock:
            if self.should_fail:
                raise RuntimeError("Database read transaction failed.")
            return self._risk_reports.get(report_id)


class TestEvolutionPersistence(unittest.TestCase):
    """Verifies DTO serialization/deserialization, query retrievals, validations and failures."""

    def setUp(self) -> None:
        self.repo = InMemoryArchitectureEvolutionRepository()
        self.persistence = ArchitectureEvolutionPersistenceService(self.repo)
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

    def test_constructor_validation(self) -> None:
        """Verifies type safety validations during setup checks."""
        with self.assertRaises(ValueError):
            ArchitectureEvolutionPersistenceService(None)  # type: ignore
        with self.assertRaises(TypeError):
            ArchitectureEvolutionPersistenceService("not_a_repo")  # type: ignore

    def test_save_and_retrieve_snapshot(self) -> None:
        """Verifies snapshot entity mappings, serialization properties and retrieval."""
        snapshot = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="commit_id_123",
            timestamp=self.time_utc,
            layers=("Domain", "Infrastructure"),
            components={"comp_1": {"metric": 10}},
        )
        self.persistence.save_snapshot(snapshot)

        retrieved = self.persistence.get_snapshot("commit_id_123")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.commit_id, "commit_id_123")
        self.assertEqual(retrieved.layers, ("Domain", "Infrastructure"))

    def test_save_and_retrieve_result(self) -> None:
        """Verifies result entity mappings, serialization properties and retrieval."""
        meta = EvolutionMetadata(
            project_name="PersistProj",
            source_commit="c1",
            target_commit="c2",
            created_at=self.time_utc,
            status=EvolutionStatus.COMPLETED,
        )
        changes = (
            ArchitecturalChange(
                component_name="module:a.py",
                change_type=ArchitecturalChangeType.ADDED,
            ),
        )
        result = EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=meta,
            changes=changes,
            summary=EvolutionSummary(added_count=1, removed_count=0, modified_count=0, unchanged_count=0),
        )
        self.persistence.save_result(result)

        retrieved = self.persistence.get_result(result.evolution_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.metadata.project_name, "PersistProj")
        self.assertEqual(len(retrieved.changes), 1)

    def test_save_and_retrieve_trend(self) -> None:
        """Verifies trend results can be persisted and loaded cleanly."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.2, 0.4),
            complexity_trend=(1.0, 2.0),
            tech_debt_trend=(5, 10),
            quality_trend=(90.0, 80.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 12),
            summary={"status": "degrading"},
        )
        trend_id = uuid.uuid4()
        self.persistence.save_trend(trend_id, trend)

        retrieved = self.persistence.get_trend(trend_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.coupling_trend, (0.2, 0.4))

    def test_save_and_retrieve_risk_report(self) -> None:
        """Verifies risk reports can be persisted and loaded cleanly."""
        risk = ArchitecturalRisk(
            name="Architectural Erosion",
            description="Quality is declining.",
            score=45.0,
            severity=RiskSeverity.MEDIUM,
            mitigation_recommendation="Fix it.",
        )
        report = ArchitecturalRiskReport(
            report_id=uuid.uuid4(),
            generated_at=self.time_utc,
            overall_risk_score=45.0,
            risks=(risk,),
        )
        self.persistence.save_risk_report(report.report_id, report)

        retrieved = self.persistence.get_risk_report(report.report_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.overall_risk_score, 45.0)
        self.assertEqual(len(retrieved.risks), 1)

    def test_update_existing_records(self) -> None:
        """Verifies that saving a snapshot with same commit overwrites atomically."""
        snapshot1 = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="commit1",
            timestamp=self.time_utc,
            layers=("LayerA",),
            components={},
        )
        snapshot2 = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="commit1",
            timestamp=self.time_utc,
            layers=("LayerB",),
            components={},
        )

        self.persistence.save_snapshot(snapshot1)
        self.persistence.save_snapshot(snapshot2)  # Overwrite

        retrieved = self.persistence.get_snapshot("commit1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.layers, ("LayerB",))

    def test_list_historical_results_chronological_ordering(self) -> None:
        """Verifies listing results orders them strictly chronologically by metadata.created_at."""
        meta1 = EvolutionMetadata(
            project_name="P1",
            source_commit="c1",
            target_commit="c2",
            created_at=datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc),
            status=EvolutionStatus.COMPLETED,
        )
        meta2 = EvolutionMetadata(
            project_name="P1",
            source_commit="c2",
            target_commit="c3",
            created_at=datetime(2026, 8, 6, 11, 0, 0, tzinfo=timezone.utc),  # Earlier!
            status=EvolutionStatus.COMPLETED,
        )

        res1 = EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=meta1,
            changes=(),
            summary=EvolutionSummary(added_count=0, removed_count=0, modified_count=0, unchanged_count=0),
        )
        res2 = EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=meta2,
            changes=(),
            summary=EvolutionSummary(added_count=0, removed_count=0, modified_count=0, unchanged_count=0),
        )

        self.persistence.save_result(res1)
        self.persistence.save_result(res2)

        results = self.persistence.list_results()
        self.assertEqual(len(results), 2)
        # res2 (11:00) should appear before res1 (12:00)
        self.assertEqual(results[0].evolution_id, res2.evolution_id)
        self.assertEqual(results[1].evolution_id, res1.evolution_id)

    def test_exception_propagation_and_rollback(self) -> None:
        """Verifies database errors propagate as EvolutionPersistenceError wrapper."""
        self.repo.should_fail = True

        snapshot = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="commit1",
            timestamp=self.time_utc,
            layers=(),
            components={},
        )

        with self.assertRaises(EvolutionPersistenceError):
            self.persistence.save_snapshot(snapshot)

    def test_concurrent_saves(self) -> None:
        """Verifies thread-safe concurrency behavior under multi-threaded saves."""
        snapshots = []
        for i in range(50):
            snapshots.append(
                ArchitectureSnapshot(
                    snapshot_id=uuid.uuid4(),
                    commit_id=f"commit_{i}",
                    timestamp=self.time_utc,
                    layers=(),
                    components={},
                )
            )

        def save_task(snap: ArchitectureSnapshot) -> None:
            self.persistence.save_snapshot(snap)

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(save_task, snapshots)

        # Retrieve and verify all 50 saved snapshots
        for i in range(50):
            retrieved = self.persistence.get_snapshot(f"commit_{i}")
            self.assertIsNotNone(retrieved)


if __name__ == "__main__":
    unittest.main()
