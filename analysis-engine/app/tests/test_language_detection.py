"""Unit test suite for LanguageDetector and Language enum integration."""

import unittest
from pathlib import Path

from app.scanner import (
    Language,
    LanguageDetector,
    DiscoveredFile,
    DiscoveryResult,
)


class TestLanguageDetection(unittest.TestCase):
    """Tests for mapping file extensions to canonical strongly-typed Languages."""

    def setUp(self) -> None:
        self.detector = LanguageDetector()

    def _create_mock_file(self, filename: str, extension: str) -> DiscoveredFile:
        return DiscoveredFile(
            absolute_path=Path(f"/tmp/{filename}"),
            relative_path=Path(filename),
            extension=extension,
            size=123,
        )

    def test_detection_rules(self) -> None:
        # 1. Python
        py_file = self._create_mock_file("main.py", ".py")
        self.assertEqual(self.detector.detect(py_file), Language.PYTHON)

        # 2. JavaScript
        js_file = self._create_mock_file("app.js", ".js")
        self.assertEqual(self.detector.detect(js_file), Language.JAVASCRIPT)

        # 3. JSX
        jsx_file = self._create_mock_file("Component.jsx", ".jsx")
        self.assertEqual(self.detector.detect(jsx_file), Language.JAVASCRIPT)

        # 4. TypeScript
        ts_file = self._create_mock_file("types.ts", ".ts")
        self.assertEqual(self.detector.detect(ts_file), Language.TYPESCRIPT)

        # 5. TSX
        tsx_file = self._create_mock_file("Widget.tsx", ".tsx")
        self.assertEqual(self.detector.detect(tsx_file), Language.TYPESCRIPT)

    def test_unknown_extension_and_no_extension(self) -> None:
        # 6. Unknown extension
        txt_file = self._create_mock_file("notes.txt", ".txt")
        self.assertEqual(self.detector.detect(txt_file), Language.UNKNOWN)

        # 7. File with no extension
        no_ext_file = self._create_mock_file("LICENSE", "")
        self.assertEqual(self.detector.detect(no_ext_file), Language.UNKNOWN)

    def test_case_insensitive_matching(self) -> None:
        # 8. Uppercase extensions
        py_upper = self._create_mock_file("MAIN.PY", ".PY")
        self.assertEqual(self.detector.detect(py_upper), Language.PYTHON)

        tsx_upper = self._create_mock_file("WIDGET.TSX", ".TSX")
        self.assertEqual(self.detector.detect(tsx_upper), Language.TYPESCRIPT)

    def test_batch_detection(self) -> None:
        # 9. Batch detection
        files = [
            self._create_mock_file("a.py", ".py"),
            self._create_mock_file("b.js", ".js"),
            self._create_mock_file("c.txt", ".txt"),
        ]
        result = DiscoveryResult(files=files)

        enriched = self.detector.detect_files(result)

        self.assertEqual(len(enriched.files), 3)
        self.assertEqual(enriched.files[0].language, Language.PYTHON)
        self.assertEqual(enriched.files[1].language, Language.JAVASCRIPT)
        self.assertEqual(enriched.files[2].language, Language.UNKNOWN)

    def test_empty_discovery_result(self) -> None:
        # 10. Empty DiscoveryResult
        result = DiscoveryResult(files=[])
        enriched = self.detector.detect_files(result)
        self.assertEqual(len(enriched.files), 0)

    def test_existing_metadata_remains_unchanged(self) -> None:
        # 11. Existing metadata remains unchanged after detection
        file = self._create_mock_file("test.ts", ".ts")
        lang = self.detector.detect(file)
        
        # Build batch
        result = DiscoveryResult(files=[file])
        enriched = self.detector.detect_files(result)
        
        # Verify original model is unchanged
        self.assertEqual(file.language, Language.UNKNOWN)
        
        # Verify enriched model properties match original
        new_file = enriched.files[0]
        self.assertEqual(new_file.absolute_path, file.absolute_path)
        self.assertEqual(new_file.relative_path, file.relative_path)
        self.assertEqual(new_file.extension, file.extension)
        self.assertEqual(new_file.size, file.size)
        self.assertEqual(new_file.language, Language.TYPESCRIPT)

    def test_language_defaults_to_unknown(self) -> None:
        # 12. Language defaults to UNKNOWN when appropriate
        file = self._create_mock_file("somefile", "")
        self.assertEqual(file.language, Language.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
