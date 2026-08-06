"""Unit tests for the SHA-256 File Fingerprint Generator."""

import os
import shutil
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.incremental import (
    IncrementalAnalysisValidationError,
    IncrementalAnalysisFileSystemError,
    SHA256FingerprintGenerator,
    FileFingerprint,
)


class TestFingerprintGenerator(unittest.TestCase):
    """Verifies fingerprint checksums, identical inputs comparison, missing files handling, and transient deletes."""

    def setUp(self) -> None:
        self.workspace_dir = Path(__file__).parent.resolve() / "temp_fingerprint_test"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.generator = SHA256FingerprintGenerator(base_dir=self.workspace_dir)

    def tearDown(self) -> None:
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)

    def test_invalid_arguments(self) -> None:
        """Verifies validations reject empty or invalid paths."""
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.generator.generate_fingerprint("")  # type: ignore

        with self.assertRaises(IncrementalAnalysisValidationError):
            self.generator.generate_fingerprint(None)  # type: ignore

    def test_missing_and_directory_inputs(self) -> None:
        """Verifies error responses for missing files and directories."""
        # Rejects directories
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.generator.generate_fingerprint(str(self.workspace_dir))

        # Rejects missing path
        non_existent = self.workspace_dir / "missing.txt"
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.generator.generate_fingerprint(str(non_existent))

    def test_stable_sha256_generation_and_identical_files(self) -> None:
        """Verifies stable checksum compilation and identical fingerprints for identical inputs."""
        f1 = self.workspace_dir / "f1.txt"
        f1.write_text("stable content", encoding="utf-8")

        f2 = self.workspace_dir / "f2.txt"
        f2.write_text("stable content", encoding="utf-8")

        fp1 = self.generator.generate_fingerprint(str(f1))
        fp2 = self.generator.generate_fingerprint(str(f2))

        self.assertEqual(fp1.hash, fp2.hash)
        self.assertEqual(fp1.size, fp2.size)
        self.assertEqual(fp1.path, "f1.txt")
        self.assertEqual(fp2.path, "f2.txt")
        self.assertEqual(fp1.last_modified.tzinfo, timezone.utc)

    def test_modified_content_differences(self) -> None:
        """Verifies modified contents trigger distinct hash fingerprints."""
        f1 = self.workspace_dir / "f1.txt"
        f1.write_text("stable content", encoding="utf-8")

        fp1 = self.generator.generate_fingerprint(str(f1))

        # Mutate content
        f1.write_text("mutated content", encoding="utf-8")
        fp2 = self.generator.generate_fingerprint(str(f1))

        self.assertNotEqual(fp1.hash, fp2.hash)

    def test_empty_and_binary_files(self) -> None:
        """Verifies fingerprint processing of empty files and binary payloads."""
        # Empty file
        empty_file = self.workspace_dir / "empty.txt"
        empty_file.touch()

        fp_empty = self.generator.generate_fingerprint(str(empty_file))
        self.assertEqual(fp_empty.size, 0)
        # Empty string SHA-256 hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        self.assertEqual(fp_empty.hash, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

        # Binary file
        bin_file = self.workspace_dir / "bin.dat"
        bin_file.write_bytes(b"\x00\x01\x02\x03\xff")

        fp_bin = self.generator.generate_fingerprint(str(bin_file))
        self.assertEqual(fp_bin.size, 5)

    def test_large_file_buffered_hashing(self) -> None:
        """Verifies buffered reader capability handles large files correctly without holding full files in memory."""
        large_file = self.workspace_dir / "large.dat"
        # Write 2MB of repeating chunk blocks
        chunk = b"A" * 1024 * 128  # 128KB chunk
        with open(large_file, "wb") as f:
            for _ in range(16):
                f.write(chunk)

        fp = self.generator.generate_fingerprint(str(large_file))
        self.assertEqual(fp.size, 2097152)

    def test_transient_deletion_race(self) -> None:
        """Verifies handling when a file is deleted right after path existence validation."""
        f1 = self.workspace_dir / "race.txt"
        f1.write_text("content", encoding="utf-8")

        # Mock open to raise FileNotFoundError to simulate file deletion right when we open it
        with patch("builtins.open", side_effect=FileNotFoundError("Mock delete race")):
            with self.assertRaises(IncrementalAnalysisFileSystemError) as ctx:
                self.generator.generate_fingerprint(str(f1))
            self.assertIn("Transient filesystem deletion race occurred", str(ctx.exception))

    def test_path_normalization(self) -> None:
        """Verifies path slashes normalization across operating systems."""
        # Use sub-folder
        sub = self.workspace_dir / "nested" / "sub"
        sub.mkdir(parents=True, exist_ok=True)

        target = sub / "app.py"
        target.write_text("import os", encoding="utf-8")

        # Normalization with backslashes parameter to simulate Windows formats
        rel_win_format = "nested\\sub\\app.py"
        fp = self.generator.generate_fingerprint(str(target), relative_path=rel_win_format)
        self.assertEqual(fp.path, "nested/sub/app.py")


if __name__ == "__main__":
    unittest.main()
