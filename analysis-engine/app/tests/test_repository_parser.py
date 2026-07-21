"""Unit and integration test suite for RepositoryParser and TreeSitterParser."""

from pathlib import Path
import tempfile
import unittest

from app.parser import (
    BaseParser,
    Language,
    ParsedFile,
    ParseFailureError,
    ParserRegistry,
    RepositoryParser,
    TreeSitterParser,
)
from app.scanner import Scanner


class FaultyParser(BaseParser):
    """Fails intentionally for testing error handling in RepositoryParser."""

    def parse_file(self, file_path: Path, repository_root: Path) -> ParsedFile:
        raise ParseFailureError(f"Simulated failure parsing '{file_path}'")


class TestRepositoryParser(unittest.TestCase):
    """Integration and unit tests for RepositoryParser pipeline."""

    def test_tree_sitter_parser_parse_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            js_file = root / "app.js"
            js_content = "function hello() { return 'world'; }"
            js_file.write_text(js_content)

            parser = TreeSitterParser(Language.JAVASCRIPT)
            parsed = parser.parse_file(js_file, root)

            self.assertEqual(parsed.path, js_file)
            self.assertEqual(parsed.relative_path, Path("app.js"))
            self.assertEqual(parsed.language, Language.JAVASCRIPT)
            self.assertEqual(parsed.source_code, js_content)
            self.assertIsNotNone(parsed.tree)
            self.assertEqual(parsed.tree.root_node.type, "program")

    def test_repository_parser_integration_with_scanner(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()

            src = root / "src"
            src.mkdir()

            (root / "main.js").write_text("const a = 1;")
            (root / "app.jsx").write_text("export const App = () => <div/>;")
            (src / "utils.ts").write_text("export type ID = string;")
            (src / "Button.tsx").write_text("export const Button = () => <button/>;")
            (root / "README.md").write_text("# Documentation")

            # Step 1: Scan
            scanner = Scanner(root)
            scan_result = scanner.scan()
            self.assertEqual(scan_result.statistics.source_files, 4)

            # Step 2: Parse
            repo_parser = RepositoryParser()
            parse_result = repo_parser.parse(scan_result)

            self.assertEqual(parse_result.parsed_count, 4)
            self.assertEqual(parse_result.failed_count, 0)
            self.assertEqual(len(parse_result.files), 4)
            self.assertGreaterEqual(parse_result.parse_duration_ms, 0.0)

            # Verify parsed languages
            lang_map = {f.filename if hasattr(f, 'filename') else f.path.name: f.language for f in parse_result.files}
            self.assertEqual(lang_map["main.js"], Language.JAVASCRIPT)
            self.assertEqual(lang_map["app.jsx"], Language.JAVASCRIPT)
            self.assertEqual(lang_map["utils.ts"], Language.TYPESCRIPT)
            self.assertEqual(lang_map["Button.tsx"], Language.TYPESCRIPT)

    def test_repository_parser_empty_scan_result(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            scanner = Scanner(root)
            scan_result = scanner.scan()

            repo_parser = RepositoryParser()
            parse_result = repo_parser.parse(scan_result)

            self.assertEqual(parse_result.parsed_count, 0)
            self.assertEqual(parse_result.failed_count, 0)
            self.assertEqual(len(parse_result.files), 0)

    def test_repository_parser_resilience_on_file_failures(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "good1.js").write_text("const x = 10;")
            (root / "faulty.js").write_text("const y = 20;")
            (root / "good2.ts").write_text("const z: number = 30;")

            scanner = Scanner(root)
            scan_result = scanner.scan()

            # Register a FaultyParser for JavaScript
            registry = ParserRegistry()
            registry.register(Language.JAVASCRIPT, FaultyParser())
            registry.register(Language.TYPESCRIPT, TreeSitterParser(Language.TYPESCRIPT))

            repo_parser = RepositoryParser(registry=registry)
            parse_result = repo_parser.parse(scan_result)

            # Faulty JS files (good1.js & faulty.js) should fail, good2.ts should succeed
            self.assertEqual(parse_result.parsed_count, 1)
            self.assertEqual(parse_result.failed_count, 2)
            self.assertEqual(len(parse_result.files), 1)
            self.assertEqual(parse_result.files[0].path.name, "good2.ts")

    def test_repository_parser_unsupported_language_resilience(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "valid.js").write_text("const a = 1;")

            scanner = Scanner(root)
            scan_result = scanner.scan()

            # Registry missing JavaScript
            registry = ParserRegistry()
            repo_parser = RepositoryParser(registry=registry)

            parse_result = repo_parser.parse(scan_result)
            self.assertEqual(parse_result.parsed_count, 0)
            self.assertEqual(parse_result.failed_count, 1)
            self.assertEqual(len(parse_result.files), 0)

    def test_parser_reuse_efficiency(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            for i in range(10):
                (root / f"file_{i}.ts").write_text(f"export const v{i} = {i};")

            scanner = Scanner(root)
            scan_result = scanner.scan()

            repo_parser = RepositoryParser()
            parse_result = repo_parser.parse(scan_result)

            self.assertEqual(parse_result.parsed_count, 10)
            self.assertEqual(parse_result.failed_count, 0)


if __name__ == "__main__":
    unittest.main()
