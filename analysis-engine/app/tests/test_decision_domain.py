"""Unit tests for the Architecture Decision Intelligence domain models, enums, exceptions, and validation rules."""

import json
import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from pydantic import ValidationError

from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionError,
    DecisionMetadata,
    DecisionPersistenceError,
    DecisionPriority,
    DecisionRelationship,
    DecisionRelationshipType,
    DecisionRequest,
    DecisionResult,
    DecisionStatus,
    DecisionTraceabilityError,
    DecisionValidationError,
)


class TestDecisionDomain(unittest.TestCase):
    """Verifies DTO validation, immutability, mapping protection, and serialization for the decision domain."""

    def setUp(self) -> None:
        self.source_id = uuid.uuid4()
        self.target_id = uuid.uuid4()
        self.time_utc = datetime.now(timezone.utc)

        # Valid sub-models
        self.relationship = DecisionRelationship(
            source_decision_id=self.source_id,
            target_decision_id=self.target_id,
            relationship_type=DecisionRelationshipType.SUPERSEDES,
        )
        self.metadata = DecisionMetadata(
            author="Architect A",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            tags=("adr", "security"),
            extra_info={"compiler": "v1"},
        )
        self.decision = ArchitectureDecision(
            decision_id=self.source_id,
            title="Use FastAPI",
            category=DecisionCategory.TECHNOLOGY,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.HIGH,
            context="Need high performance routing.",
            decision_text="FastAPI chosen.",
            consequences="Adds typing overhead.",
            metadata=self.metadata,
            relationships=(self.relationship,),
        )

    def test_decision_relationship_instantiation(self) -> None:
        """Verifies correct property binding on DecisionRelationship model."""
        rel = self.relationship
        self.assertEqual(rel.source_decision_id, self.source_id)
        self.assertEqual(rel.target_decision_id, self.target_id)
        self.assertEqual(rel.relationship_type, DecisionRelationshipType.SUPERSEDES)

    def test_decision_metadata_utc_timezone_validation(self) -> None:
        """Verifies that naive or non-UTC datetimes trigger validation errors in DecisionMetadata."""
        naive_time = datetime.now()
        with self.assertRaises(ValidationError):
            DecisionMetadata(
                author="Architect A",
                created_at=naive_time,
                updated_at=self.time_utc,
                extra_info={},
            )

    def test_mapping_proxy_protection_metadata(self) -> None:
        """Verifies metadata extra_info is protected under read-only MappingProxyType views."""
        meta = self.metadata
        self.assertIsInstance(meta.extra_info, MappingProxyType)
        with self.assertRaises(TypeError):
            meta.extra_info["new_key"] = "failure"  # type: ignore

    def test_decision_immutability(self) -> None:
        """Verifies that models are frozen and raise errors on mutation attempts."""
        dec = self.decision
        with self.assertRaises(ValidationError):
            dec.title = "Altered Title"  # type: ignore

    def test_decision_request_instantiation(self) -> None:
        """Verifies correct property binding on DecisionRequest model."""
        project_id = uuid.uuid4()
        req = DecisionRequest(
            project_id=project_id,
            decision=self.decision,
            correlation_id="corr-123",
        )
        self.assertEqual(req.project_id, project_id)
        self.assertEqual(req.decision.title, "Use FastAPI")
        self.assertEqual(req.correlation_id, "corr-123")

    def test_decision_result_serialization(self) -> None:
        """Verifies json serialization and deserialization of the DecisionResult DTO."""
        res = DecisionResult(
            project_id=uuid.uuid4(),
            decision=self.decision,
            status=DecisionStatus.ACCEPTED,
            processed_at=self.time_utc,
            extra_info={"pipeline": "stage-1"},
        )
        dump = res.model_dump_json()
        parsed = json.loads(dump)

        self.assertEqual(parsed["status"], "accepted")
        self.assertEqual(parsed["extra_info"]["pipeline"], "stage-1")

    def test_exceptions_hierarchy(self) -> None:
        """Verifies subsystem exception classes inherit from base DecisionError."""
        self.assertTrue(issubclass(DecisionValidationError, DecisionError))
        self.assertTrue(issubclass(DecisionPersistenceError, DecisionError))
        self.assertTrue(issubclass(DecisionTraceabilityError, DecisionError))


if __name__ == "__main__":
    unittest.main()
