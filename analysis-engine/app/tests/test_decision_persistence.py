"""Unit tests for DecisionPersistenceService and serialization operations."""

import threading
import unittest
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionPriority,
    DecisionStatus,
    DecisionMetadata,
    DecisionRepository,
    DecisionPersistenceService,
    DecisionPersistenceError,
)


class InMemoryDecisionRepository(DecisionRepository):
    """In-memory thread-safe implementation of DecisionRepository for unit testing."""

    def __init__(self) -> None:
        self._data: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def save_data(self, key: str, data: dict) -> None:
        with self._lock:
            self._data[key] = data

    def get_data(self, key: str) -> Optional[dict]:
        with self._lock:
            return self._data.get(key)

    def list_keys_starting_with(self, prefix: str) -> Tuple[str, ...]:
        with self._lock:
            matching = [k for k in self._data.keys() if k.startswith(prefix)]
            return tuple(matching)


class TestDecisionPersistence(unittest.TestCase):
    """Verifies artifact save/load, serialization roundtrips, thread-safety, and exception handling."""

    def setUp(self) -> None:
        self.repository = InMemoryDecisionRepository()
        self.service = DecisionPersistenceService(self.repository)
        self.project_id = uuid.uuid4()
        self.decision_id = uuid.uuid4()
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={"targets": ("file:src/app.py",)},
        )

        self.decision = ArchitectureDecision(
            decision_id=self.decision_id,
            title="Use FastAPI",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.CRITICAL,
            context="Legacy framework is slow.",
            decision_text="We choose FastAPI for modern API capabilities.",
            consequences="Fast API development.",
            metadata=self.metadata,
        )

    def test_save_and_retrieve_decision_roundtrip(self) -> None:
        """Verifies full serialization and deserialization validation flow for a single decision."""
        self.service.save_decision(self.project_id, self.decision)

        retrieved = self.service.get_decision(self.decision_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.decision_id, self.decision_id)
        self.assertEqual(retrieved.title, "Use FastAPI")
        self.assertEqual(retrieved.metadata.author, "Lead Architect")

    def test_list_decisions_ordering(self) -> None:
        """Verifies deterministic sorting of decisions by ID during list queries."""
        dec1_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
        dec2_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        dec1 = self.decision.model_copy(update={"decision_id": dec1_id, "title": "Second"})
        dec2 = self.decision.model_copy(update={"decision_id": dec2_id, "title": "First"})

        self.service.save_decision(self.project_id, dec1)
        self.service.save_decision(self.project_id, dec2)

        results = self.service.list_decisions(self.project_id)
        self.assertEqual(len(results), 2)
        # dec2 has smaller UUID than dec1, so dec2 (First) must be first
        self.assertEqual(results[0].decision_id, dec2_id)
        self.assertEqual(results[1].decision_id, dec1_id)

    def test_missing_decision_returns_none(self) -> None:
        """Verifies retrieval queries return None for non-existent decision records."""
        retrieved = self.service.get_decision(uuid.uuid4())
        self.assertIsNone(retrieved)

    def test_atomic_overwrite(self) -> None:
        """Verifies overwriting an existing decision record replaces its data in storage."""
        self.service.save_decision(self.project_id, self.decision)

        updated_dec = self.decision.model_copy(update={"title": "Use FastAPI Modern"})
        self.service.save_decision(self.project_id, updated_dec)

        retrieved = self.service.get_decision(self.decision_id)
        self.assertEqual(retrieved.title, "Use FastAPI Modern")

    def test_exception_translation_on_repository_failure(self) -> None:
        """Verifies infrastructure exceptions are correctly wrapped inside DecisionPersistenceError."""
        # Mock repository to raise an exception
        fail_repository = MagicRepositoryFail()
        fail_service = DecisionPersistenceService(fail_repository)

        with self.assertRaises(DecisionPersistenceError):
            fail_service.save_decision(self.project_id, self.decision)


class MagicRepositoryFail(DecisionRepository):
    """Mock repository designed to trigger save errors."""

    def save_data(self, key: str, data: dict) -> None:
        raise Exception("Disk write failure")

    def get_data(self, key: str) -> Optional[dict]:
        raise Exception("Disk read failure")

    def list_keys_starting_with(self, prefix: str) -> Tuple[str, ...]:
        raise Exception("Database query failure")


if __name__ == "__main__":
    unittest.main()
