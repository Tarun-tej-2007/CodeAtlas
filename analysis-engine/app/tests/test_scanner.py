"""Unit test suite for the scanner domain foundation."""

from datetime import datetime, timezone
from pathlib import Path
import unittest

from app.scanner import (
    EXTENSION_LANGUAGE_MAP,
    IGNORED_DIRECTORIES,
    IGNORED_FILES,
    SUPPORTED_EXTENSIONS,
    DirectoryMetadata,
    FileAccessError,
    FileMetadata,
    InvalidRepositoryError,
    RepositoryNotFoundError,
    ScanResult,
    ScanStatistics,
    ScannerError,
    UnsupportedLanguageError,
)


class TestScannerFoundation(unittest.TestCase):
    """Tests for scanner domain models, exceptions, and constants."""

    def test_file_metadata_instantiation_and_immutability(self):
        now = datetime.now(timezone.utc)
        file_meta = FileMetadata(
            path=Path("/repo/src/index.ts"),
            relative_path=Path("src/index.ts"),
            filename="index.ts",
            extension=".ts",
            size_bytes=2048,
            modified_at=now,
            language="TypeScript",
        )
        self.assertEqual(file_meta.filename, "index.ts")
        self.assertEqual(file_meta.extension, ".ts")
        self.assertEqual(file_meta.size_bytes, 2048)
        self.assertEqual(file_meta.language, "TypeScript")

        # Test immutability
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            file_meta.filename = "new_name.ts"


    def test_directory_metadata_instantiation(self):
        dir_meta = DirectoryMetadata(
            path=Path("/repo/src/components"),
            relative_path=Path("src/components"),
            depth=2,
        )
        self.assertEqual(str(dir_meta.relative_path), "src/components")
        self.assertEqual(dir_meta.depth, 2)

    def test_scan_statistics_defaults(self):
        stats = ScanStatistics()
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.source_files, 0)
        self.assertEqual(stats.ignored_files, 0)
        self.assertEqual(stats.directories, 0)
        self.assertEqual(stats.scan_duration_ms, 0.0)

    def test_scan_result_composition(self):
        repo_root = Path("/repo")
        result = ScanResult(repository_root=repo_root)
        self.assertEqual(result.repository_root, repo_root)
        self.assertEqual(len(result.files), 0)
        self.assertEqual(len(result.directories), 0)

    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(RepositoryNotFoundError, ScannerError))
        self.assertTrue(issubclass(InvalidRepositoryError, ScannerError))
        self.assertTrue(issubclass(UnsupportedLanguageError, ScannerError))
        self.assertTrue(issubclass(FileAccessError, ScannerError))

    def test_constants_definitions(self):
        self.assertIn(".js", SUPPORTED_EXTENSIONS)
        self.assertIn(".jsx", SUPPORTED_EXTENSIONS)
        self.assertIn(".ts", SUPPORTED_EXTENSIONS)
        self.assertIn(".tsx", SUPPORTED_EXTENSIONS)

        self.assertIn("node_modules", IGNORED_DIRECTORIES)
        self.assertIn(".git", IGNORED_DIRECTORIES)
        self.assertIn(".DS_Store", IGNORED_FILES)

        self.assertEqual(EXTENSION_LANGUAGE_MAP[".ts"], "TypeScript")
        self.assertEqual(EXTENSION_LANGUAGE_MAP[".js"], "JavaScript")


if __name__ == "__main__":
    unittest.main()
