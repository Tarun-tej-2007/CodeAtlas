"""Unit tests for the DecisionBuilderService and constraints validation."""

import unittest
import uuid
from datetime import datetime, timezone

from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionPriority,
    DecisionRelationship,
    DecisionRelationshipType,
    DecisionRequest,
    DecisionStatus,
    DecisionBuilderService,
    DecisionMetadata,
    DecisionValidationError,
)


class TestDecisionBuilder(unittest.TestCase):
    """Verifies construction, transition lifecycle, semantic version, and ordering validations."""

    def setUp(self) -> None:
        self.service = DecisionBuilderService()
        self.project_id = uuid.uuid4()
        self.decision_id = uuid.uuid4()
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={"version": "1.2.3"},
        )

    def test_single_decision_construction(self) -> None:
        """Verifies clean decision construction and normalization of whitespace in strings."""
        dec = self.service.build_decision(
            title="   Migrate to PostgreSQL   ",
            category=DecisionCategory.INFRASTRUCTURE,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.CRITICAL,
            context="   Legacy DB is slow.   ",
            decision_text="   PostgreSQL is standard.   ",
            consequences="   Migration effort required.   ",
            metadata=self.metadata,
        )
        self.assertEqual(dec.title, "Migrate to PostgreSQL")
        self.assertEqual(dec.context, "Legacy DB is slow.")
        self.assertEqual(dec.decision_text, "PostgreSQL is standard.")
        self.assertEqual(dec.consequences, "Migration effort required.")

    def test_semantic_version_metadata_validation(self) -> None:
        """Verifies that builder accepts valid semver and rejects invalid formats."""
        # Valid semver
        valid_meta = DecisionMetadata(
            author="A",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={"version": "2.0.0-rc.1+build.123"},
        )
        dec = self.service.build_decision(
            title="T", category=DecisionCategory.DESIGN, status=DecisionStatus.DRAFT,
            priority=DecisionPriority.LOW, context="C", decision_text="D", consequences="Con",
            metadata=valid_meta,
        )
        self.assertEqual(dec.metadata.extra_info.get("version"), "2.0.0-rc.1+build.123")

        # Invalid semver
        invalid_meta = DecisionMetadata(
            author="A",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={"version": "v1.2"},
        )
        with self.assertRaises(DecisionValidationError):
            self.service.build_decision(
                title="T", category=DecisionCategory.DESIGN, status=DecisionStatus.DRAFT,
                priority=DecisionPriority.LOW, context="C", decision_text="D", consequences="Con",
                metadata=invalid_meta,
            )

    def test_lifecycle_transitions_validation(self) -> None:
        """Verifies valid and invalid lifecycle transition rules."""
        # Valid transition: Draft -> Proposed
        self.service.validate_transition(DecisionStatus.DRAFT, DecisionStatus.PROPOSED)

        # Valid transition: Accepted -> Superseded
        self.service.validate_transition(DecisionStatus.ACCEPTED, DecisionStatus.SUPERSEDED)

        # Invalid transition: Deprecated -> Draft
        with self.assertRaises(DecisionValidationError):
            self.service.validate_transition(DecisionStatus.DEPRECATED, DecisionStatus.DRAFT)

    def test_relationship_normalization_and_ordering(self) -> None:
        """Verifies relationships are sorted deterministically and self-reference is forbidden."""
        target_id1 = uuid.uuid4()
        target_id2 = uuid.uuid4()

        # Target ID 2 is lexicographically larger/smaller than 1 depending on UUID representation
        # We will sort targets by string representation
        uuid_list = sorted([target_id1, target_id2], key=str)
        t_first, t_second = uuid_list[0], uuid_list[1]

        r1 = DecisionRelationship(
            source_decision_id=self.decision_id,
            target_decision_id=t_second,
            relationship_type=DecisionRelationshipType.SUPERSEDES,
        )
        r2 = DecisionRelationship(
            source_decision_id=self.decision_id,
            target_decision_id=t_first,
            relationship_type=DecisionRelationshipType.RELATES_TO,
        )

        dec = self.service.build_decision(
            title="T", category=DecisionCategory.DESIGN, status=DecisionStatus.DRAFT,
            priority=DecisionPriority.LOW, context="C", decision_text="D", consequences="Con",
            metadata=self.metadata,
            relationships=(r1, r2),
            decision_id=self.decision_id,
        )

        # Assert sorted order: t_first should come first
        self.assertEqual(dec.relationships[0].target_decision_id, t_first)
        self.assertEqual(dec.relationships[1].target_decision_id, t_second)

    def test_duplicate_relationships_detection(self) -> None:
        """Verifies duplicate relationship definitions trigger validation failure."""
        target_id = uuid.uuid4()
        r1 = DecisionRelationship(
            source_decision_id=self.decision_id,
            target_decision_id=target_id,
            relationship_type=DecisionRelationshipType.SUPERSEDES,
        )
        r2 = DecisionRelationship(
            source_decision_id=self.decision_id,
            target_decision_id=target_id,
            relationship_type=DecisionRelationshipType.SUPERSEDES,
        )

        with self.assertRaises(DecisionValidationError):
            self.service.build_decision(
                title="T", category=DecisionCategory.DESIGN, status=DecisionStatus.DRAFT,
                priority=DecisionPriority.LOW, context="C", decision_text="D", consequences="Con",
                metadata=self.metadata,
                relationships=(r1, r2),
                decision_id=self.decision_id,
            )

    def test_self_reference_relationship_rejection(self) -> None:
        """Verifies that decision cannot reference itself in relationships."""
        r = DecisionRelationship(
            source_decision_id=self.decision_id,
            target_decision_id=self.decision_id,
            relationship_type=DecisionRelationshipType.RELATES_TO,
        )

        with self.assertRaises(DecisionValidationError):
            self.service.build_decision(
                title="T", category=DecisionCategory.DESIGN, status=DecisionStatus.DRAFT,
                priority=DecisionPriority.LOW, context="C", decision_text="D", consequences="Con",
                metadata=self.metadata,
                relationships=(r,),
                decision_id=self.decision_id,
            )

    def test_invalid_requests(self) -> None:
        """Verifies builder rejects empty parameter inputs."""
        with self.assertRaises(DecisionValidationError):
            self.service.build_decision(
                title="", category=DecisionCategory.DESIGN, status=DecisionStatus.DRAFT,
                priority=DecisionPriority.LOW, context="C", decision_text="D", consequences="Con",
                metadata=self.metadata,
            )


if __name__ == "__main__":
    unittest.main()
