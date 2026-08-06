"""Unit tests for the Incremental Analysis domain models, enums, exceptions, and DTO layouts."""

import json
import unittest
import uuid
from datetime import datetime, timezone
from pydantic import ValidationError

from app.incremental import (
    ChangeType,
    IncrementalStatus,
    IncrementalAnalysisValidationError,
    IncrementalAnalysisError,
    FileFingerprint,
    RepositorySnapshot,
    ChangedFile,
    IncrementalAnalysisMetadata,
    IncrementalAnalysisRequest,
    IncrementalAnalysisResult,
)


class TestIncrementalDomain(unittest.TestCase):
    """Verifies DTO validation, immutability, mapping constraints, and exception construction."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
        self.fingerprint = FileFingerprint(
            path="src/main.py",
            hash="abc123hash",
            size=1024,
            last_modified=self.time_utc,
        )

    def test_file_fingerprint_validations(self) -> None:
        """Verifies validation rules, empty strings, missing offsets, and timezone constraints."""
        # Valid construction
        self.assertEqual(self.fingerprint.path, "src/main.py")

        # Invalid path (empty/whitespace)
        with self.assertRaises(ValidationError):
            FileFingerprint(path="   ", hash="h", size=10, last_modified=self.time_utc)

        # Invalid hash (empty)
        with self.assertRaises(ValidationError):
            FileFingerprint(path="src.py", hash="", size=10, last_modified=self.time_utc)

        # Negative size
        with self.assertRaises(ValidationError):
            FileFingerprint(path="src.py", hash="h", size=-1, last_modified=self.time_utc)

        # Non-UTC timezone datetime
        local_time = datetime(2026, 8, 6, 12, 0, 0)
        with self.assertRaises(ValidationError):
            FileFingerprint(path="src.py", hash="h", size=5, last_modified=local_time)

    def test_dto_immutability(self) -> None:
        """Asserts that domain models are frozen and cannot be mutated after creation."""
        with self.assertRaises(ValidationError):
            # Attempt direct item assignment modification
            self.fingerprint.path = "new/path.py"  # type: ignore

    def test_repository_snapshot_mapping_immutability(self) -> None:
        """Verifies that the mapping collections inside RepositorySnapshot are protected with MappingProxyType."""
        snap = RepositorySnapshot(
            commit_id="commit1",
            fingerprints={"src/main.py": self.fingerprint},
        )
        self.assertEqual(snap.commit_id, "commit1")

        # Verify fingerprints mapping is read-only MappingProxyType
        with self.assertRaises(TypeError):
            snap.fingerprints["new/path.py"] = self.fingerprint  # type: ignore

        # Invalid commit_id validation
        with self.assertRaises(ValidationError):
            RepositorySnapshot(commit_id="   ", fingerprints={})

    def test_changed_file_structure(self) -> None:
        """Verifies ChangedFile structure validation and properties."""
        change = ChangedFile(
            path="src/main.py",
            change_type=ChangeType.MODIFIED,
            old_fingerprint=self.fingerprint,
            new_fingerprint=self.fingerprint,
        )
        self.assertEqual(change.change_type, ChangeType.MODIFIED)

        # Empty path reject
        with self.assertRaises(ValidationError):
            ChangedFile(path="", change_type=ChangeType.ADDED)

    def test_metadata_and_request_validations(self) -> None:
        """Verifies metadata tags, commit ID validation, request configurations, and extra_info mapping views."""
        meta = IncrementalAnalysisMetadata(
            project_name="CodeAtlas_Incremental",
            source_commit="c1",
            target_commit="c2",
            created_at=self.time_utc,
            status=IncrementalStatus.PENDING,
            extra_info={"pipeline": "github_actions"},
        )
        self.assertEqual(meta.project_name, "CodeAtlas_Incremental")
        
        # Verify read-only MappingProxyType protection on extra_info
        with self.assertRaises(TypeError):
            meta.extra_info["new_key"] = "val"  # type: ignore

        # Rejects whitespace values
        with self.assertRaises(ValidationError):
            IncrementalAnalysisMetadata(
                project_name="  ",
                source_commit="c1",
                target_commit="c2",
                created_at=self.time_utc,
                status=IncrementalStatus.COMPLETED,
            )

        # Request validators
        req = IncrementalAnalysisRequest(
            project_id=uuid.uuid4(),
            project_name="CodeAtlas",
            source_commit="commit_old",
            target_commit="commit_new",
            changed_files=(),
        )
        self.assertEqual(req.project_name, "CodeAtlas")

    def test_result_structure(self) -> None:
        """Verifies completed Result serialization and payload structure properties."""
        meta = IncrementalAnalysisMetadata(
            project_name="CodeAtlas_Incremental",
            source_commit="c1",
            target_commit="c2",
            created_at=self.time_utc,
            status=IncrementalStatus.COMPLETED,
        )
        result = IncrementalAnalysisResult(
            analysis_id=uuid.uuid4(),
            metadata=meta,
            added_count=1,
            modified_count=2,
            deleted_count=0,
            unchanged_count=50,
            changed_files=(),
        )
        self.assertEqual(result.added_count, 1)

    def test_exceptions_construction(self) -> None:
        """Verifies domain errors can be raised and inherit from base exceptions correctly."""
        with self.assertRaises(IncrementalAnalysisError):
            raise IncrementalAnalysisValidationError("Failed validation format.")

    def test_serialization_and_equality(self) -> None:
        """Verifies serialization compatibility and object equality properties."""
        dumped = self.fingerprint.model_dump()
        self.assertEqual(dumped["path"], "src/main.py")
        self.assertEqual(dumped["size"], 1024)

        fingerprint2 = FileFingerprint(
            path="src/main.py",
            hash="abc123hash",
            size=1024,
            last_modified=self.time_utc,
        )
        # Test equality
        self.assertEqual(self.fingerprint, fingerprint2)
        # Test hashability
        self.assertEqual(hash(self.fingerprint), hash(fingerprint2))


if __name__ == "__main__":
    unittest.main()
