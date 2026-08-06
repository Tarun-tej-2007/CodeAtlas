"""Unit tests for the Architecture Evolution Domain Foundation models, enums, and validations."""

import json
import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType

from pydantic import ValidationError

from app.evolution import (
    ArchitecturalChange,
    ArchitecturalChangeType,
    ArchitectureSnapshot,
    EvolutionError,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionValidationError,
)


class TestEvolutionDomain(unittest.TestCase):
    """Verifies validations, serialization, mapping proxy immutabilities, equality, and exception flows."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
        self.project_name = "EvolProj"
        self.source_commit = "commit_source"
        self.target_commit = "commit_target"

    def test_architectural_change_valid_construction(self) -> None:
        """Verifies construction of valid ArchitecturalChange model and metadata protection."""
        change = ArchitecturalChange(
            component_name="src/components",
            change_type=ArchitecturalChangeType.ADDED,
            description="Created components folder",
            metadata={"priority": "high"},
        )

        self.assertEqual(change.component_name, "src/components")
        self.assertEqual(change.change_type, ArchitecturalChangeType.ADDED)
        self.assertIsInstance(change.metadata, MappingProxyType)
        self.assertEqual(change.metadata["priority"], "high")

        # Verify model immutability
        with self.assertRaises(ValidationError):
            change.component_name = "modified"  # type: ignore

        # Verify mapping proxy immutability
        with self.assertRaises(TypeError):
            change.metadata["priority"] = "low"  # type: ignore

    def test_architectural_change_validation_failures(self) -> None:
        """Verifies validations block invalid component names."""
        with self.assertRaises(ValidationError):
            # Empty component name
            ArchitecturalChange(
                component_name="   ",
                change_type=ArchitecturalChangeType.ADDED,
            )

    def test_architecture_snapshot_valid_construction(self) -> None:
        """Verifies valid ArchitectureSnapshot model, UTC time constraints, and serialization."""
        snap = ArchitectureSnapshot(
            commit_id=self.target_commit,
            timestamp=self.time_utc,
            layers=("Domain", "Infrastructure"),
            components={"Domain": ["models", "interfaces"]},
        )

        self.assertEqual(snap.commit_id, self.target_commit)
        self.assertEqual(snap.timestamp, self.time_utc)
        self.assertEqual(snap.layers, ("Domain", "Infrastructure"))
        self.assertIsInstance(snap.components, MappingProxyType)

        # Verify serialization to JSON
        dumped_json = snap.model_dump_json()
        data = json.loads(dumped_json)
        self.assertEqual(data["commit_id"], self.target_commit)
        self.assertEqual(data["components"]["Domain"], ["models", "interfaces"])

    def test_architecture_snapshot_timezone_validation(self) -> None:
        """Verifies snapshot validator rejects naive timestamps."""
        naive_time = datetime(2026, 8, 6, 12, 0, 0)
        with self.assertRaises(ValidationError):
            ArchitectureSnapshot(
                commit_id=self.target_commit,
                timestamp=naive_time,
            )

    def test_evolution_metadata_and_request_validations(self) -> None:
        """Verifies scope validation constraints reject empty strings."""
        # Valid request
        req = EvolutionRequest(
            project_id=uuid.uuid4(),
            project_name=self.project_name,
            source_commit=self.source_commit,
            target_commit=self.target_commit,
        )
        self.assertEqual(req.project_name, self.project_name)

        # Invalid request with empty strings
        with self.assertRaises(ValidationError):
            EvolutionRequest(
                project_id=uuid.uuid4(),
                project_name="",
                source_commit="c1",
                target_commit="c2",
            )

        # Metadata timezone validation
        naive_time = datetime(2026, 8, 6, 12, 0, 0)
        with self.assertRaises(ValidationError):
            EvolutionMetadata(
                project_name=self.project_name,
                source_commit=self.source_commit,
                target_commit=self.target_commit,
                created_at=naive_time,
                status=EvolutionStatus.COMPLETED,
            )

    def test_evolution_result_full_graph_hierarchy(self) -> None:
        """Verifies result object integrates metadata, change sets, summaries, and value equality."""
        metadata = EvolutionMetadata(
            project_name=self.project_name,
            source_commit=self.source_commit,
            target_commit=self.target_commit,
            created_at=self.time_utc,
            status=EvolutionStatus.COMPLETED,
            extra_info={"user": "admin"},
        )
        summary = EvolutionSummary(added_count=1, removed_count=0, modified_count=0, unchanged_count=5)
        change = ArchitecturalChange(
            component_name="Domain",
            change_type=ArchitecturalChangeType.ADDED,
        )

        res1 = EvolutionResult(
            metadata=metadata,
            changes=(change,),
            summary=summary,
        )

        res2 = EvolutionResult(
            evolution_id=res1.evolution_id,
            metadata=metadata,
            changes=(change,),
            summary=summary,
        )

        # Equality check
        self.assertEqual(res1, res2)

    def test_custom_exception_construction(self) -> None:
        """Verifies domain base error and validator exception inheritance."""
        err = EvolutionValidationError("Validation error occurred.")
        self.assertIsInstance(err, EvolutionError)
        self.assertEqual(str(err), "Validation error occurred.")


if __name__ == "__main__":
    unittest.main()
