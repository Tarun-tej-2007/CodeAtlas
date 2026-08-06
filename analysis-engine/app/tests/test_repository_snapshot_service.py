"""Unit tests for the Repository Snapshot Service."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock
from pathlib import Path

from app.incremental import (
    IncrementalAnalysisValidationError,
    RepositorySnapshotService,
)
from app.scanner.pipeline import ScannerPipeline


class TestRepositorySnapshotService(unittest.TestCase):
    """Verifies repository snapshot compilation, deterministic ordering, empty states, and validations."""

    def setUp(self) -> None:
        # Create temp folder inside workspace path for safety
        self.workspace_dir = Path(__file__).parent.resolve() / "temp_snapshots_test"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.service = RepositorySnapshotService()

    def tearDown(self) -> None:
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)

    def test_invalid_parameters(self) -> None:
        """Verifies validations reject invalid or None parameters."""
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.service.create_snapshot(None, "commit1")  # type: ignore

        with self.assertRaises(IncrementalAnalysisValidationError):
            self.service.create_snapshot(self.workspace_dir, " ")  # type: ignore

        non_existent = self.workspace_dir / "non_existent_folder"
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.service.create_snapshot(non_existent, "commit1")

    def test_empty_repository(self) -> None:
        """Verifies snapshot of empty directory compiles successfully with zero files."""
        snap = self.service.create_snapshot(self.workspace_dir, "commit_empty")
        self.assertEqual(snap.commit_id, "commit_empty")
        self.assertEqual(len(snap.fingerprints), 0)

    def test_single_file_repository(self) -> None:
        """Verifies snapshot of a single file compiles properly containing exact fingerprints."""
        test_file = self.workspace_dir / "test.py"
        test_file.write_text("print('hello')", encoding="utf-8")

        snap = self.service.create_snapshot(self.workspace_dir, "commit_single")
        self.assertEqual(snap.commit_id, "commit_single")
        self.assertEqual(len(snap.fingerprints), 1)
        self.assertIn("test.py", snap.fingerprints)

        fp = snap.fingerprints["test.py"]
        self.assertEqual(fp.path, "test.py")
        self.assertEqual(fp.size, 14)
        self.assertIsNotNone(fp.hash)

    def test_multiple_file_repository_and_deterministic_ordering(self) -> None:
        """Verifies deterministic output order across multiple file changes."""
        # Create files in non-alphabetical order
        f_b = self.workspace_dir / "b.js"
        f_b.write_text("console.log()", encoding="utf-8")
        f_a = self.workspace_dir / "a.py"
        f_a.write_text("x = 10", encoding="utf-8")
        f_c = self.workspace_dir / "c.ts"
        f_c.write_text("let y: number = 5;", encoding="utf-8")

        snap1 = self.service.create_snapshot(self.workspace_dir, "commit_multi")
        snap2 = self.service.create_snapshot(self.workspace_dir, "commit_multi")

        # Verify deterministic output matches
        self.assertEqual(list(snap1.fingerprints.keys()), ["a.py", "b.js", "c.ts"])
        self.assertEqual(snap1.fingerprints, snap2.fingerprints)

    def test_ignored_files_are_excluded(self) -> None:
        """Verifies that the scanner's ignore rules are respected and exclude ignored directories/files."""
        # Create a .git folder and a text file inside it
        git_dir = self.workspace_dir / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.write_text("config info", encoding="utf-8")

        # Create a valid file outside
        test_file = self.workspace_dir / "app.js"
        test_file.write_text("alert(1)", encoding="utf-8")

        snap = self.service.create_snapshot(self.workspace_dir, "commit_ignore")
        # .git files should be filtered out by standard FileDiscoveryService/pipeline
        self.assertNotIn(".git/config", snap.fingerprints)
        self.assertIn("app.js", snap.fingerprints)

    def test_dependency_injection_custom_scanner(self) -> None:
        """Verifies constructor dependency injection accepts and uses a custom ScannerPipeline."""
        mock_pipeline = MagicMock(spec=ScannerPipeline)
        mock_pipeline.scan.return_value.discovery_result = None

        custom_service = RepositorySnapshotService(scanner_pipeline=mock_pipeline)
        snap = custom_service.create_snapshot(self.workspace_dir, "commit_mock")
        
        self.assertEqual(len(snap.fingerprints), 0)
        mock_pipeline.scan.assert_called_once_with(self.workspace_dir.resolve())


if __name__ == "__main__":
    unittest.main()
