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


from unittest.mock import MagicMock
from app.scanner.metadata import FileMetadataExtractor

class TestFileMetadataExtractor(unittest.TestCase):
    """Tests for FileMetadataExtractor component."""

    def test_extract_file_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            src_dir = root / "src"
            src_dir.mkdir()
            file_path = src_dir / "app.tsx"
            content = "export const App = () => <div>Hello</div>;"
            file_path.write_text(content)

            extractor = FileMetadataExtractor()
            metadata = extractor.extract(file_path, root)

            self.assertEqual(metadata.path, file_path)
            self.assertEqual(metadata.relative_path, Path("src/app.tsx"))
            self.assertEqual(metadata.filename, "app.tsx")
            self.assertEqual(metadata.extension, ".tsx")
            self.assertEqual(metadata.size_bytes, len(content.encode("utf-8")))
            self.assertEqual(metadata.language, "TypeScript")
            self.assertIsNotNone(metadata.modified_at.tzinfo)
            self.assertEqual(metadata.modified_at.tzinfo, timezone.utc)

    def test_extract_inaccessible_file_raises_file_access_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            file_path = root / "missing.ts"

            extractor = FileMetadataExtractor()
            with self.assertRaises(FileAccessError):
                extractor.extract(file_path, root)

    def test_extract_permission_error_raises_file_access_error(self):
        root = Path("/fake/repo")
        mock_path = MagicMock(spec=Path)
        mock_path.stat.side_effect = PermissionError("Permission denied")

        extractor = FileMetadataExtractor()
        with self.assertRaises(FileAccessError):
            extractor.extract(mock_path, root)

    def test_extract_file_outside_repository_root(self):
        with tempfile.TemporaryDirectory() as tmp_dir1, tempfile.TemporaryDirectory() as tmp_dir2:
            root = Path(tmp_dir1).resolve()
            outside_file = Path(tmp_dir2).resolve() / "outside.ts"
            outside_file.write_text("// outside")

            extractor = FileMetadataExtractor()
            with self.assertRaises(FileAccessError):
                extractor.extract(outside_file, root)


from app.scanner.filters import FilteringEngine

class TestFilteringEngine(unittest.TestCase):
    """Tests for FilteringEngine component."""

    def setUp(self):
        self.filters = FilteringEngine()

    def test_should_skip_ignored_directories(self):
        ignored_dirs = [
            ".git", ".github", "node_modules", ".next", "dist",
            "build", "coverage", "venv", ".venv", "__pycache__",
            ".idea", ".vscode"
        ]
        for dir_name in ignored_dirs:
            self.assertTrue(
                self.filters.should_skip_directory(Path(f"/repo/{dir_name}")),
                f"Directory {dir_name} should be skipped"
            )

    def test_should_not_skip_valid_directory(self):
        self.assertFalse(self.filters.should_skip_directory(Path("/repo/src")))
        self.assertFalse(self.filters.should_skip_directory(Path("/repo/components")))

    def test_should_skip_hidden_directory(self):
        self.assertTrue(self.filters.should_skip_directory(Path("/repo/.cache")))

    def test_should_skip_ignored_files(self):
        self.assertTrue(self.filters.should_skip_file(Path("/repo/.DS_Store")))
        self.assertTrue(self.filters.should_skip_file(Path("/repo/Thumbs.db")))

    def test_should_skip_hidden_files_except_supported_extensions(self):
        self.assertTrue(self.filters.should_skip_file(Path("/repo/.env")))
        self.assertTrue(self.filters.should_skip_file(Path("/repo/.eslintrc.json")))
        self.assertFalse(self.filters.should_skip_file(Path("/repo/.index.ts")))

    def test_is_supported_source_file(self):
        self.assertTrue(self.filters.is_supported_source_file(Path("main.js")))
        self.assertTrue(self.filters.is_supported_source_file(Path("App.jsx")))
        self.assertTrue(self.filters.is_supported_source_file(Path("index.ts")))
        self.assertTrue(self.filters.is_supported_source_file(Path("Button.tsx")))
        self.assertFalse(self.filters.is_supported_source_file(Path("styles.css")))
        self.assertFalse(self.filters.is_supported_source_file(Path("script.py")))

    def test_scanner_pruning_ignored_and_nested_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()

            src = root / "src"
            src.mkdir()
            (src / "app.ts").write_text("// app")

            nm = root / "node_modules"
            nm.mkdir()
            (nm / "dep.ts").write_text("// dependency")

            git_dir = root / ".git"
            git_dir.mkdir()
            (git_dir / "config.ts").write_text("// git config")

            nested_nm = src / "node_modules"
            nested_nm.mkdir()
            (nested_nm / "inner.ts").write_text("// inner")

            (root / ".DS_Store").write_bytes(b"")

            scanner = Scanner(root)
            result = scanner.scan()

            rel_dir_names = [str(d.relative_path) for d in result.directories]
            self.assertIn(".", rel_dir_names)
            self.assertIn("src", rel_dir_names)
            self.assertNotIn("node_modules", rel_dir_names)
            self.assertNotIn(".git", rel_dir_names)
            self.assertNotIn(str(Path("src/node_modules")), rel_dir_names)


            file_names = [f.filename for f in result.files]
            self.assertEqual(file_names, ["app.ts"])


from app.scanner.config import ScannerConfig

class TestScannerPipelineAndConfig(unittest.TestCase):
    """Tests for ScannerConfig, pipeline orchestration, and dependency injection."""

    def test_scanner_config_defaults_and_immutability(self):
        config = ScannerConfig()
        self.assertFalse(config.follow_symlinks)
        self.assertFalse(config.include_hidden)
        self.assertTrue(config.respect_default_filters)
        self.assertTrue(config.collect_statistics)

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            config.follow_symlinks = True

    def test_scanner_dependency_injection(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "index.ts").write_text("// index")

            config = ScannerConfig()
            filters = FilteringEngine(config=config)
            extractor = FileMetadataExtractor()

            scanner = Scanner(
                repository_root=root,
                config=config,
                filters=filters,
                metadata_extractor=extractor,
            )

            self.assertEqual(scanner.config, config)
            self.assertEqual(scanner.filters, filters)
            self.assertEqual(scanner.extractor, extractor)

            result = scanner.scan()
            self.assertEqual(len(result.files), 1)

    def test_include_hidden_configuration(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()

            hidden_dir = root / ".hidden_dir"
            hidden_dir.mkdir()
            (hidden_dir / "hidden.ts").write_text("// hidden file")
            (root / "regular.ts").write_text("// regular file")

            config = ScannerConfig(include_hidden=True, respect_default_filters=False)
            scanner = Scanner(root, config=config)
            result = scanner.scan()

            file_names = [f.filename for f in result.files]
            self.assertIn("hidden.ts", file_names)
            self.assertIn("regular.ts", file_names)

    def test_symlink_policy(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            real_file = root / "real.ts"
            real_file.write_text("// real")

            symlink_file = root / "link.ts"
            try:
                symlink_file.symlink_to(real_file)
            except (OSError, NotImplementedError):
                return

            scanner_no_sym = Scanner(root, config=ScannerConfig(follow_symlinks=False))
            res_no_sym = scanner_no_sym.scan()
            files_no_sym = [f.filename for f in res_no_sym.files]
            self.assertIn("real.ts", files_no_sym)
            self.assertNotIn("link.ts", files_no_sym)

            scanner_sym = Scanner(root, config=ScannerConfig(follow_symlinks=True))
            res_sym = scanner_sym.scan()
            files_sym = [f.filename for f in res_sym.files]
            self.assertIn("real.ts", files_sym)
            self.assertIn("link.ts", files_sym)

    def test_collect_statistics_disabled(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "app.ts").write_text("// app")

            config = ScannerConfig(collect_statistics=False)
            scanner = Scanner(root, config=config)
            result = scanner.scan()

            self.assertEqual(result.statistics.scan_duration_ms, 0.0)
            self.assertEqual(len(result.files), 1)


class TestScannerRobustnessAndOptimization(unittest.TestCase):
    """Robustness, performance, and edge-case tests for Scanner component."""

    def test_unicode_filenames_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            unicode_dir = root / "代码" / "ñandú"
            unicode_dir.mkdir(parents=True)

            (unicode_dir / "文件.ts").write_text("// unicode file", encoding="utf-8")
            (unicode_dir / "⚡spark.js").write_text("// spark", encoding="utf-8")

            scanner = Scanner(root)
            result = scanner.scan()

            file_names = [f.filename for f in result.files]
            self.assertIn("文件.ts", file_names)
            self.assertIn("⚡spark.js", file_names)

    def test_deeply_nested_directory_tree(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            deep_path = root
            for level in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]:
                deep_path = deep_path / level

            deep_path.mkdir(parents=True)
            (deep_path / "deep.tsx").write_text("export const Deep = () => null;")

            scanner = Scanner(root)
            result = scanner.scan()

            self.assertEqual(len(result.files), 1)
            self.assertEqual(result.files[0].filename, "deep.tsx")
            self.assertEqual(result.files[0].relative_path, Path("a/b/c/d/e/f/g/h/i/j/deep.tsx"))
            self.assertEqual(len(result.directories), 11)

    def test_repository_with_only_ignored_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / ".DS_Store").write_bytes(b"")
            (root / "Thumbs.db").write_bytes(b"")
            (root / ".env").write_text("SECRET=123")

            scanner = Scanner(root)
            result = scanner.scan()

            self.assertEqual(len(result.files), 0)
            self.assertEqual(result.statistics.source_files, 0)
            self.assertEqual(result.statistics.ignored_files, 3)

    def test_repository_with_zero_source_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "readme.md").write_text("# Readme")
            (root / "data.json").write_text("{}")
            (root / "script.py").write_text("print(1)")

            scanner = Scanner(root)
            result = scanner.scan()

            self.assertEqual(len(result.files), 0)
            self.assertEqual(result.statistics.source_files, 0)
            self.assertEqual(result.statistics.ignored_files, 3)
            self.assertEqual(result.statistics.directories, 1)

    def test_symlink_loop_protection(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            dir_a = root / "dir_a"
            dir_b = root / "dir_b"
            dir_a.mkdir()
            dir_b.mkdir()

            try:
                (dir_a / "link_b").symlink_to(dir_b, target_is_directory=True)
                (dir_b / "link_a").symlink_to(dir_a, target_is_directory=True)
            except (OSError, NotImplementedError):
                return

            scanner = Scanner(root, config=ScannerConfig(follow_symlinks=True))
            result = scanner.scan()
            self.assertIsNotNone(result)

    def test_configuration_combination(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            hidden_git = root / ".git"
            hidden_git.mkdir()
            (hidden_git / "git_source.ts").write_text("// hidden git source")

            config = ScannerConfig(
                include_hidden=True,
                respect_default_filters=False,
                follow_symlinks=False,
                collect_statistics=True,
            )
            scanner = Scanner(root, config=config)
            result = scanner.scan()

            file_names = [f.filename for f in result.files]
            self.assertIn("git_source.ts", file_names)

    def test_performance_sanity_check(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            src_dir = root / "src"
            src_dir.mkdir()

            for i in range(50):
                (src_dir / f"file_{i}.ts").write_text(f"// file {i}")

            scanner = Scanner(root)
            result = scanner.scan()

            self.assertEqual(result.statistics.source_files, 50)
            self.assertLess(result.statistics.scan_duration_ms, 500.0)


if __name__ == "__main__":
    unittest.main()




