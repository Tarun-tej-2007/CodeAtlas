"""Robustness, performance, and optimization unit tests for the parser pipeline."""

from pathlib import Path
import tempfile
import unittest

from app.parser import (
    Language,
    ParsedFile,
    ParseResult,
    ParserRegistry,
    RepositoryParser,
    TreeSitterParser,
    get_treesitter_language,
)
from app.parser.ast import ASTBuilder, ASTDocument
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor
from app.scanner import Scanner


class TestParserPipelineRobustness(unittest.TestCase):
    """Test suite covering parser robustness, caching, malformed syntax, and performance benchmarks."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()

    def test_grammar_lru_caching(self) -> None:
        lang_js1 = get_treesitter_language(Language.JAVASCRIPT)
        lang_js2 = get_treesitter_language(Language.JAVASCRIPT)
        self.assertIs(lang_js1, lang_js2)

        lang_ts1 = get_treesitter_language(Language.TYPESCRIPT)
        lang_ts2 = get_treesitter_language(Language.TYPESCRIPT)
        self.assertIs(lang_ts1, lang_ts2)

    def test_malformed_javascript_syntax_recovery(self) -> None:
        malformed_js = "const = ; function ( { let x ="
        parser = TreeSitterParser(Language.JAVASCRIPT)

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            file_path = root / "bad.js"
            file_path.write_text(malformed_js)

            # Tree-sitter must not crash on invalid syntax
            parsed = parser.parse_file(file_path, root)
            self.assertEqual(parsed.language, Language.JAVASCRIPT)
            self.assertIsNotNone(parsed.tree)

            # ASTBuilder must convert invalid syntax nodes without raising exceptions
            ast_doc = self.builder.build_document(parsed)
            self.assertIsInstance(ast_doc, ASTDocument)

            # Symbol and Module extractors must not crash on malformed ASTs
            symbols = self.symbol_extractor.extract(ast_doc)
            modules = self.module_analyzer.analyze(ast_doc)
            self.assertIsNotNone(symbols)
            self.assertIsNotNone(modules)

    def test_malformed_typescript_syntax_recovery(self) -> None:
        malformed_ts = "interface { ::: } type = ; class {"
        parser = TreeSitterParser(Language.TYPESCRIPT)

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            file_path = root / "bad.ts"
            file_path.write_text(malformed_ts)

            parsed = parser.parse_file(file_path, root)
            ast_doc = self.builder.build_document(parsed)
            symbols = self.symbol_extractor.extract(ast_doc)
            modules = self.module_analyzer.analyze(ast_doc)

            self.assertIsNotNone(ast_doc)
            self.assertIsNotNone(symbols)
            self.assertIsNotNone(modules)

    def test_empty_repository_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            scanner = Scanner(root)
            scan_res = scanner.scan()

            repo_parser = RepositoryParser()
            parse_res = repo_parser.parse(scan_res)

            self.assertEqual(parse_res.parsed_count, 0)
            self.assertEqual(parse_res.failed_count, 0)
            self.assertEqual(len(parse_res.files), 0)

    def test_large_repository_simulation_performance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            src = root / "src"
            src.mkdir()

            # Create 50 JS and 50 TS files
            for i in range(50):
                (src / f"module_{i}.js").write_text(f"import React from 'react'; export const a{i} = {i};")
                (src / f"service_{i}.ts").write_text(f"export interface Service{i} {{ id: number; }}")

            scanner = Scanner(root)
            scan_res = scanner.scan()
            self.assertEqual(scan_res.statistics.source_files, 100)

            repo_parser = RepositoryParser()
            parse_res = repo_parser.parse(scan_res)

            self.assertEqual(parse_res.parsed_count, 100)
            self.assertEqual(parse_res.failed_count, 0)
            self.assertLess(parse_res.parse_duration_ms, 1000.0)  # Under 1 second for 100 files

            # Full pipeline pass (AST -> Symbol -> Module)
            for parsed_file in parse_res.files:
                doc = self.builder.build_document(parsed_file)
                syms = self.symbol_extractor.extract(doc)
                mods = self.module_analyzer.analyze(doc)
                self.assertGreaterEqual(syms.count, 0)
                self.assertGreaterEqual(mods.export_count, 0)

    def test_repeated_parsing_consistency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            (root / "app.js").write_text("import foo from 'foo'; export function main() { return foo(); }")

            scanner = Scanner(root)
            scan_res = scanner.scan()

            repo_parser = RepositoryParser()
            res1 = repo_parser.parse(scan_res)
            res2 = repo_parser.parse(scan_res)

            self.assertEqual(res1.parsed_count, res2.parsed_count)
            self.assertEqual(res1.files[0].source_code, res2.files[0].source_code)

            doc1 = self.builder.build_document(res1.files[0])
            doc2 = self.builder.build_document(res2.files[0])
            self.assertEqual(doc1.root.model_dump(), doc2.root.model_dump())

    def test_registry_parser_instance_reuse(self) -> None:
        registry = ParserRegistry()
        parser_js1 = TreeSitterParser(Language.JAVASCRIPT)
        registry.register(Language.JAVASCRIPT, parser_js1)

        fetched = registry.get(Language.JAVASCRIPT)
        self.assertIs(fetched, parser_js1)


if __name__ == "__main__":
    unittest.main()
