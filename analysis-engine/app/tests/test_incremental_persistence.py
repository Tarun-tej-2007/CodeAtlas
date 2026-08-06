"""Unit and Integration tests for the Incremental Analysis Persistence subsystem."""

import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.incremental import (
    FileFingerprint,
    IncrementalAnalysisMetadata,
    IncrementalAnalysisResult,
    IncrementalAnalysisValidationError,
    IncrementalAnalysisRepository,
    IncrementalAnalysisPersistenceService,
    IncrementalStatus,
    RepositorySnapshot,
)


class InMemoryIncrementalAnalysisRepository(IncrementalAnalysisRepository):
    """Thread-safe in-memory database stub of IncrementalAnalysisRepository for testing purposes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._results: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}
        self.rollback_triggered = False

    def save_result(self, result_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        with self._lock:
            # Simulate atomic database check/transaction failure
            if self.rollback_triggered:
                raise RuntimeError("Transaction rollback triggered by test mock.")
            self._results[result_id] = result_data

    def get_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._results.get(result_id)

    def save_snapshot(self, commit_id: str, snapshot_data: Dict[str, Any]) -> None:
        with self._lock:
            if self.rollback_triggered:
                raise RuntimeError("Transaction rollback triggered by test mock.")
            # Overwrite previous snapshots for same commit atomically
            self._snapshots[commit_id] = snapshot_data

    def get_snapshot(self, commit_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._snapshots.get(commit_id)


class TestIncrementalPersistence(unittest.TestCase):
    """Verifies persistence mappings, serialization validations, update overwrites, and database failures."""

    def setUp(self) -> None:
        self.repo = InMemoryIncrementalAnalysisRepository()
        self.persistence = IncrementalAnalysisPersistenceService(self.repo)

        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
        self.fingerprint = FileFingerprint(
            path="src/main.py",
            hash="abc123hash",
            size=500,
            last_modified=self.time_utc,
        )
        self.snapshot = RepositorySnapshot(
            commit_id="commit1",
            fingerprints={"src/main.py": self.fingerprint},
        )
        self.metadata = IncrementalAnalysisMetadata(
            project_name="PersistProj",
            source_commit="commit_source",
            target_commit="commit1",
            created_at=self.time_utc,
            status=IncrementalStatus.COMPLETED,
        )
        self.result = IncrementalAnalysisResult(
            analysis_id=uuid.uuid4(),
            metadata=self.metadata,
            added_count=1,
            modified_count=0,
            deleted_count=0,
            unchanged_count=2,
            changed_files=(),
        )

    def test_constructor_validation(self) -> None:
        """Verifies constructor rejects None or invalid repository objects."""
        with self.assertRaises(ValueError):
            IncrementalAnalysisPersistenceService(None)  # type: ignore

        with self.assertRaises(TypeError):
            IncrementalAnalysisPersistenceService("not_a_repository")  # type: ignore

    def test_save_and_retrieve_snapshot(self) -> None:
        """Verifies snapshot persistence, retrieval, and mapping correctness."""
        self.persistence.save_snapshot(self.snapshot)

        retrieved = self.persistence.get_snapshot("commit1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.commit_id, "commit1")
        self.assertEqual(retrieved.fingerprints["src/main.py"].hash, "abc123hash")

    def test_update_and_overwrite_snapshot(self) -> None:
        """Verifies update overwrites previous snapshots for same commit atomically."""
        self.persistence.save_snapshot(self.snapshot)

        # Build modified snapshot with same commit_id
        updated_fingerprint = FileFingerprint(
            path="src/main.py",
            hash="new_hash",
            size=600,
            last_modified=self.time_utc,
        )
        updated_snap = RepositorySnapshot(
            commit_id="commit1",
            fingerprints={"src/main.py": updated_fingerprint},
        )

        self.persistence.save_snapshot(updated_snap)

        retrieved = self.persistence.get_snapshot("commit1")
        self.assertEqual(retrieved.fingerprints["src/main.py"].hash, "new_hash")
        self.assertEqual(retrieved.fingerprints["src/main.py"].size, 600)

    def test_missing_snapshot_retrieval(self) -> None:
        """Verifies missing snapshot retrieval returns None."""
        retrieved = self.persistence.get_snapshot("non_existent_commit")
        self.assertIsNone(retrieved)

    def test_save_and_retrieve_result(self) -> None:
        """Verifies result persistence, validation, and serialization correctness."""
        self.persistence.save_result(self.result)

        retrieved = self.persistence.get_result(self.result.analysis_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.analysis_id, self.result.analysis_id)
        self.assertEqual(retrieved.metadata.project_name, "PersistProj")

    def test_transaction_rollback_and_exception_propagation(self) -> None:
        """Verifies transaction failure triggers propagation of the exception."""
        self.repo.rollback_triggered = True

        with self.assertRaises(RuntimeError) as ctx:
            self.persistence.save_snapshot(self.snapshot)
        self.assertIn("Transaction rollback", str(ctx.exception))

    def test_validation_failures_on_corrupt_data(self) -> None:
        """Verifies validation failure exception raised if database payload is corrupt."""
        # Save invalid corrupted payload data directly to repo dict
        self.repo.save_snapshot("commit1", {"commit_id": "commit1", "fingerprints": "corrupt_data_string"})

        with self.assertRaises(IncrementalAnalysisValidationError):
            self.persistence.get_snapshot("commit1")

    def test_concurrent_saves(self) -> None:
        """Verifies thread-safety during concurrent snapshot save calls."""
        def run_saves(index: int):
            snap = RepositorySnapshot(
                commit_id=f"commit_{index}",
                fingerprints={},
            )
            self.persistence.save_snapshot(snap)
            ret = self.persistence.get_snapshot(f"commit_{index}")
            self.assertEqual(ret.commit_id, f"commit_{index}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_saves, i) for i in range(25)]
            for f in futures:
                f.result()


if __name__ == "__main__":
    unittest.main()
