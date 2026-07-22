"""Unit tests for the ParsingPipeline orchestrator."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.scanner.models import DiscoveredFile, Language as ScannerLanguage
from app.parser.models import ParsedFile, ParseResult
from app.parser.exceptions import ParseError
from app.parser.base import SourceCodeParser
from app.plugins import PluginRegistry, PythonPlugin, JavaScriptPlugin, TypeScriptPlugin
from app.plugins.exceptions import PluginNotFoundError
from app.parser import ParsingPipeline


class TestParsingPipeline(unittest.TestCase):
    """Tests ParsingPipeline orchestration, mixed languages, and error recovery."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline = ParsingPipeline()

    def tearDown(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_empty_inputs(self) -> None:
        # 6. Empty inputs
        result = self.pipeline.parse_files([])
        self.assertEqual(result.parsed_count, 0)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(len(result.files), 0)

    def test_single_language_parsing(self) -> None:
        # 1. Single-language parsing
        file_path = Path(self.temp_dir) / "test.py"
        file_path.write_text("def run():\n    pass")

        discovered = DiscoveredFile(
            absolute_path=file_path,
            relative_path=Path("test.py"),
            extension=".py",
            size=file_path.stat().st_size,
            language=ScannerLanguage.PYTHON,
        )

        result = self.pipeline.parse_files([discovered])

        # Assert result aggregation
        self.assertEqual(result.parsed_count, 1)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].language, ScannerLanguage.PYTHON)
        self.assertGreater(result.parse_duration_ms, 0.0)

    def test_mixed_language_parsing(self) -> None:
        # 2. Mixed-language parsing
        py_path = Path(self.temp_dir) / "test.py"
        py_path.write_text("def run(): pass")

        js_path = Path(self.temp_dir) / "test.js"
        js_path.write_text("console.log(1);")

        ts_path = Path(self.temp_dir) / "test.ts"
        ts_path.write_text("const a: number = 2;")

        files = [
            DiscoveredFile(
                absolute_path=py_path,
                relative_path=Path("test.py"),
                extension=".py",
                size=py_path.stat().st_size,
                language=ScannerLanguage.PYTHON,
            ),
            DiscoveredFile(
                absolute_path=js_path,
                relative_path=Path("test.js"),
                extension=".js",
                size=js_path.stat().st_size,
                language=ScannerLanguage.JAVASCRIPT,
            ),
            DiscoveredFile(
                absolute_path=ts_path,
                relative_path=Path("test.ts"),
                extension=".ts",
                size=ts_path.stat().st_size,
                language=ScannerLanguage.TYPESCRIPT,
            ),
        ]

        result = self.pipeline.parse_files(files)

        self.assertEqual(result.parsed_count, 3)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(len(result.files), 3)

        languages = {f.language for f in result.files}
        self.assertEqual(languages, {ScannerLanguage.PYTHON, ScannerLanguage.JAVASCRIPT, ScannerLanguage.TYPESCRIPT})

    def test_unsupported_languages(self) -> None:
        # 3. Unsupported languages
        java_path = Path(self.temp_dir) / "test.java"
        java_path.write_text("class Test {}")

        discovered = DiscoveredFile(
            absolute_path=java_path,
            relative_path=Path("test.java"),
            extension=".java",
            size=java_path.stat().st_size,
            language=ScannerLanguage.UNKNOWN,
        )

        result = self.pipeline.parse_files([discovered])

        # UNKNOWN is immediately bypassed as unsupported without counting as parse error
        self.assertEqual(result.parsed_count, 0)
        self.assertEqual(result.failed_count, 0)

    def test_plugin_lookup_failure_handled(self) -> None:
        # 4. Plugin lookup failure handling (e.g. if plugin registry doesn't have the language)
        py_path = Path(self.temp_dir) / "test.py"
        py_path.write_text("print(1)")

        discovered = DiscoveredFile(
            absolute_path=py_path,
            relative_path=Path("test.py"),
            extension=".py",
            size=py_path.stat().st_size,
            language=ScannerLanguage.PYTHON,
        )

        # Create an empty registry without PythonPlugin
        empty_registry = PluginRegistry()
        custom_pipeline = ParsingPipeline(registry=empty_registry)

        result = custom_pipeline.parse_files([discovered])

        self.assertEqual(result.parsed_count, 0)
        self.assertEqual(result.failed_count, 1)

    def test_partial_failures_and_recovery(self) -> None:
        # 5. Partial failures & 7. Result aggregation
        # File 1 is valid Python
        py_path = Path(self.temp_dir) / "test.py"
        py_path.write_text("print(1)")

        # File 2 is missing (will raise file read error)
        missing_path = Path(self.temp_dir) / "missing.js"

        files = [
            DiscoveredFile(
                absolute_path=py_path,
                relative_path=Path("test.py"),
                extension=".py",
                size=py_path.stat().st_size,
                language=ScannerLanguage.PYTHON,
            ),
            DiscoveredFile(
                absolute_path=missing_path,
                relative_path=Path("missing.js"),
                extension=".js",
                size=100,
                language=ScannerLanguage.JAVASCRIPT,
            ),
        ]

        result = self.pipeline.parse_files(files)

        # Confirms the pipeline aggregates 1 success and recovers from the 1 failure to proceed
        self.assertEqual(result.parsed_count, 1)
        self.assertEqual(result.failed_count, 1)
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].path, py_path)


if __name__ == "__main__":
    unittest.main()
