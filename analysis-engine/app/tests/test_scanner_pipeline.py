"""Unit test suite for ScannerPipeline and ScanResult integration."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.scanner import (
    Language,
    ScannerPipeline,
    ScanResult,
    FileDiscoveryService,
    LanguageDetector,
    DiscoveredFile,
    DiscoveryResult,
)
from app.scanner.exceptions import (
    DiscoveryFailureError,
    DiscoveryRootNotFoundError,
    InvalidDiscoveryRootError,
)


class TestScannerPipeline(unittest.TestCase):
    """Tests orchestrating Discovery and Language services inside the ScannerPipeline."""

    def setUp(self) -> None:
        self.pipeline = ScannerPipeline()
        self.temp_dir = tempfile.mkdtemp()
        self.root_path = Path(self.temp_dir)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_successful_pipeline_execution_e2e(self) -> None:
        # Create a mock repository setup
        (self.root_path / "main.py").write_text("print('hello')")
        (self.root_path / "app.js").write_text("console.log('js')")
        (self.root_path / "notes.txt").write_text("some random text")
        
        # 1. Successful pipeline execution
        result = self.pipeline.scan(self.root_path)

        self.assertIsInstance(result, ScanResult)
        self.assertEqual(result.repository_root, self.root_path)

        # 3. Correct language statistics
        self.assertEqual(result.languages.get(Language.PYTHON), 1)
        self.assertEqual(result.languages.get(Language.JAVASCRIPT), 1)
        self.assertEqual(result.languages.get(Language.UNKNOWN), 1)

        # 4 & 5. Supported and unsupported file counts
        self.assertEqual(result.total_files, 3)
        self.assertEqual(result.supported_files, 2)    # python + javascript
        self.assertEqual(result.unsupported_files, 1)  # unknown (txt)

        # 6. Scan duration populated
        self.assertGreater(result.scan_duration, 0.0)

    def test_empty_repository(self) -> None:
        # 2. Empty repository
        result = self.pipeline.scan(self.root_path)

        self.assertEqual(result.total_files, 0)
        self.assertEqual(result.supported_files, 0)
        self.assertEqual(result.unsupported_files, 0)
        self.assertEqual(result.languages.get(Language.UNKNOWN), 0)

    def test_discovery_service_failure_propagation(self) -> None:
        # 7. Discovery service failure propagation
        mock_discovery = MagicMock(spec=FileDiscoveryService)
        mock_discovery.discover_files.side_effect = DiscoveryFailureError("FS read error")

        pipeline = ScannerPipeline(discovery_service=mock_discovery)

        with self.assertRaises(DiscoveryFailureError):
            pipeline.scan(self.root_path)

    def test_language_detector_failure_propagation(self) -> None:
        # 8. Language detector failure propagation
        mock_detector = MagicMock(spec=LanguageDetector)
        mock_detector.detect_files.side_effect = RuntimeError("Detector crash")

        pipeline = ScannerPipeline(language_detector=mock_detector)

        with self.assertRaises(RuntimeError):
            pipeline.scan(self.root_path)

    def test_immutable_scan_result(self) -> None:
        # 9. Immutable ScanResult
        result = self.pipeline.scan(self.root_path)
        
        # Pydantic v2 frozen model validation: trying to mutate it raises ValidationError or AttributeError
        with self.assertRaises(ValidationError_or_AttributeError()):
            result.total_files = 999  # type: ignore


def ValidationError_or_AttributeError():
    """Returns validation exceptions depending on Pydantic configuration errors."""
    return (AttributeError, TypeError, ValidationError)


if __name__ == "__main__":
    unittest.main()
