"""Unit test suite for FileDiscoveryService and associated discovery exceptions."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from app.scanner import (
    FileDiscoveryService,
    DiscoveredFile,
    DiscoveryResult,
    FileDiscoveryError,
    DiscoveryRootNotFoundError,
    InvalidDiscoveryRootError,
    DiscoveryFailureError,
)


class TestFileDiscovery(unittest.TestCase):
    """Tests for FileDiscoveryService traversing, ignoring paths, and compiling metadata."""

    def setUp(self) -> None:
        self.service = FileDiscoveryService()
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_discover_files_recursively_and_metadata(self) -> None:
        # Create nested directory structure
        src_dir = self.root_path / "src"
        src_dir.mkdir()
        
        file1 = src_dir / "app.js"
        file1.write_text("console.log('hello');")
        
        file2 = self.root_path / "README.md"
        file2.write_text("# Readme")

        # Execute discovery
        result = self.service.discover_files(self.root_path)

        self.assertIsInstance(result, DiscoveryResult)
        self.assertEqual(len(result.files), 2)

        # 9, 10, 11, 12: Verify correctness of absolute/relative paths, extension, and size
        files_by_rel = {str(f.relative_path): f for f in result.files}
        self.assertIn("src/app.js", files_by_rel)
        self.assertIn("README.md", files_by_rel)

        app_js = files_by_rel["src/app.js"]
        self.assertEqual(app_js.absolute_path, file1.resolve())
        self.assertEqual(app_js.extension, ".js")
        self.assertEqual(app_js.size, len("console.log('hello');"))

        readme = files_by_rel["README.md"]
        self.assertEqual(readme.absolute_path, file2.resolve())
        self.assertEqual(readme.extension, ".md")
        self.assertEqual(readme.size, len("# Readme"))

    def test_empty_directory(self) -> None:
        # 2. Empty directory
        result = self.service.discover_files(self.root_path)
        self.assertEqual(len(result.files), 0)

    def test_missing_root_directory_raises_not_found(self) -> None:
        # 3. Missing root directory
        nonexistent = self.root_path / "nonexistent_folder"
        with self.assertRaises(DiscoveryRootNotFoundError):
            self.service.discover_files(nonexistent)

    def test_root_is_not_a_directory_raises_invalid_root(self) -> None:
        # 4. Root is not a directory
        dummy_file = self.root_path / "file.txt"
        dummy_file.touch()

        with self.assertRaises(InvalidDiscoveryRootError):
            self.service.discover_files(dummy_file)

    def test_ignores_specified_directories(self) -> None:
        # 5, 6, 7, 8: Verify ignore lists (.git, node_modules, build, dist)
        git_dir = self.root_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main")

        node_dir = self.root_path / "node_modules"
        node_dir.mkdir()
        (node_dir / "package.json").write_text("{}")

        build_dir = self.root_path / "build"
        build_dir.mkdir()
        (build_dir / "output.bin").write_text("010101")

        dist_dir = self.root_path / "dist"
        dist_dir.mkdir()
        (dist_dir / "index.js").write_text("main();")

        # Source code file (should NOT be ignored)
        src_file = self.root_path / "index.ts"
        src_file.write_text("import { x } from 'y';")

        result = self.service.discover_files(self.root_path)

        # Only index.ts should be found
        self.assertEqual(len(result.files), 1)
        self.assertEqual(str(result.files[0].relative_path), "index.ts")

    def test_custom_ignored_directories(self) -> None:
        custom_service = FileDiscoveryService(ignored_directories={"ignore_me"})
        
        ignored_sub = self.root_path / "ignore_me"
        ignored_sub.mkdir()
        (ignored_sub / "test.txt").write_text("data")

        normal_sub = self.root_path / ".git"  # .git is NOT in the custom list
        normal_sub.mkdir()
        (normal_sub / "test.txt").write_text("data")

        result = custom_service.discover_files(self.root_path)
        # Should find .git/test.txt but skip ignore_me/test.txt
        self.assertEqual(len(result.files), 1)
        self.assertEqual(str(result.files[0].relative_path), ".git/test.txt")

    def test_nested_directory_traversal(self) -> None:
        # 13. Nested directory traversal
        nested = self.root_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        (nested / "deep.txt").write_text("depth")

        result = self.service.discover_files(self.root_path)
        self.assertEqual(len(result.files), 1)
        self.assertEqual(str(result.files[0].relative_path), "a/b/c/deep.txt")


if __name__ == "__main__":
    unittest.main()
