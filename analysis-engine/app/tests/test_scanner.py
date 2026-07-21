"""Unit test suite for the scanner domain foundation and discovery engine."""

from datetime import datetime, timezone
from pathlib import Path
import tempfile
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
    Scanner,
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


class TestRepositoryScanner(unittest.TestCase):
    """Integration and discovery tests for Scanner class using temporary repositories."""

    def test_scanner_nonexistent_repository(self):
        fake_path = Path("/nonexistent/repo/path/12345")
        with self.assertRaises(RepositoryNotFoundError):
            Scanner(fake_path)

    def test_scanner_invalid_repository_path(self):
        with tempfile.NamedTemporaryFile() as tmp_file:
            with self.assertRaises(InvalidRepositoryError):
                Scanner(Path(tmp_file.name))

    def test_scanner_empty_repository(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            scanner = Scanner(tmp_dir)
            result = scanner.scan()

            self.assertEqual(result.repository_root, Path(tmp_dir).resolve())
            self.assertEqual(len(result.directories), 1)  # Root dir
            self.assertEqual(result.directories[0].depth, 0)
            self.assertEqual(len(result.files), 0)
            self.assertEqual(result.statistics.total_files, 0)
            self.assertEqual(result.statistics.source_files, 0)
            self.assertEqual(result.statistics.ignored_files, 0)
            self.assertEqual(result.statistics.directories, 1)

    def test_scanner_nested_directories_and_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()

            # Create structure:
            # /src
            # /src/api
            # /src/api/index.ts
            # /src/components
            # /src/components/Button.tsx
            # /app.jsx
            # /main.js
            # /README.md (unsupported)
            # /logo.png (unsupported)

            src_dir = root / "src"
            api_dir = src_dir / "api"
            comp_dir = src_dir / "components"

            api_dir.mkdir(parents=True, exist_ok=True)
            comp_dir.mkdir(parents=True, exist_ok=True)

            (api_dir / "index.ts").write_text("console.log('api');")
            (comp_dir / "Button.tsx").write_text("export const Button = () => {};")
            (root / "app.jsx").write_text("export default App;")
            (root / "main.js").write_text("console.log('main');")
            (root / "README.md").write_text("# Readme")
            (root / "logo.png").write_bytes(b"\x89PNG")

            scanner = Scanner(root)
            result = scanner.scan()

            # Verify directories
            dir_rel_paths = [str(d.relative_path) for d in result.directories]
            self.assertIn(".", dir_rel_paths)
            self.assertIn("src", dir_rel_paths)
            self.assertIn(str(Path("src/api")), dir_rel_paths)
            self.assertIn(str(Path("src/components")), dir_rel_paths)
            self.assertEqual(len(result.directories), 4)

            # Verify depths
            depth_map = {str(d.relative_path): d.depth for d in result.directories}
            self.assertEqual(depth_map["."], 0)
            self.assertEqual(depth_map["src"], 1)
            self.assertEqual(depth_map[str(Path("src/api"))], 2)
            self.assertEqual(depth_map[str(Path("src/components"))], 2)

            # Verify supported source files
            file_rel_paths = [str(f.relative_path) for f in result.files]
            self.assertIn("app.jsx", file_rel_paths)
            self.assertIn("main.js", file_rel_paths)
            self.assertIn(str(Path("src/api/index.ts")), file_rel_paths)
            self.assertIn(str(Path("src/components/Button.tsx")), file_rel_paths)
            self.assertNotIn("README.md", file_rel_paths)
            self.assertNotIn("logo.png", file_rel_paths)
            self.assertEqual(len(result.files), 4)

            # Verify languages
            lang_map = {f.filename: f.language for f in result.files}
            self.assertEqual(lang_map["index.ts"], "TypeScript")
            self.assertEqual(lang_map["Button.tsx"], "TypeScript")
            self.assertEqual(lang_map["app.jsx"], "JavaScript")
            self.assertEqual(lang_map["main.js"], "JavaScript")

            # Verify statistics
            self.assertEqual(result.statistics.total_files, 6)
            self.assertEqual(result.statistics.source_files, 4)
            self.assertEqual(result.statistics.ignored_files, 2)
            self.assertEqual(result.statistics.directories, 4)
            self.assertGreaterEqual(result.statistics.scan_duration_ms, 0.0)

    def test_scanner_determinism(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "b.ts").write_text("// b")
            (root / "a.ts").write_text("// a")
            (root / "z_dir").mkdir()
            scanner = Scanner(root)
            r1 = scanner.scan()
            r2 = scanner.scan()

            d1 = r1.model_dump()
            d2 = r2.model_dump()
            d1["statistics"].pop("scan_duration_ms")
            d2["statistics"].pop("scan_duration_ms")
            self.assertEqual(d1, d2)
            self.assertGreaterEqual(r1.statistics.scan_duration_ms, 0.0)
            self.assertGreaterEqual(r2.statistics.scan_duration_ms, 0.0)




if __name__ == "__main__":
    unittest.main()
