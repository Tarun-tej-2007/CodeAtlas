"""Scanner pipeline module orchestrating file discovery and language detection."""

import logging
import time
from pathlib import Path

from app.scanner.exceptions import (
    DiscoveryFailureError,
    DiscoveryRootNotFoundError,
    InvalidDiscoveryRootError,
)
from app.scanner.discovery import FileDiscoveryService
from app.scanner.language_detector import LanguageDetector
from app.scanner.models import Language, ScanResult

logger = logging.getLogger("scanner")


class ScannerPipeline:
    """Orchestrates file discovery and language classification into a ScanResult."""

    def __init__(
        self,
        discovery_service: FileDiscoveryService | None = None,
        language_detector: LanguageDetector | None = None,
    ) -> None:
        """Initializes the ScannerPipeline with injected services.

        Args:
            discovery_service: Optional FileDiscoveryService override.
            language_detector: Optional LanguageDetector override.
        """
        self.discovery_service = discovery_service or FileDiscoveryService()
        self.language_detector = language_detector or LanguageDetector()

    def scan(self, repository_root: Path | str) -> ScanResult:
        """Scans the target repository recursively to discover files and classify their languages.

        Args:
            repository_root: Root path of the codebase.

        Returns:
            A ScanResult containing discovery data, language stats, and duration.

        Raises:
            DiscoveryRootNotFoundError: If repository_root does not exist.
            InvalidDiscoveryRootError: If repository_root is not a directory.
            DiscoveryFailureError: If traversal fails.
        """
        # 1. Validate repository root
        try:
            resolved_path = Path(repository_root).resolve()
        except Exception as err:
            raise InvalidDiscoveryRootError(f"Failed to resolve path '{repository_root}': {err}") from err

        if not resolved_path.exists():
            raise DiscoveryRootNotFoundError(f"Repository root directory does not exist: {resolved_path}")

        if not resolved_path.is_dir():
            raise InvalidDiscoveryRootError(f"Repository root path is not a directory: {resolved_path}")

        # Measure scan duration
        start_time = time.monotonic()

        # 2. Execute FileDiscoveryService
        discovery_result = self.discovery_service.discover_files(resolved_path)

        # 3. Execute LanguageDetector
        enriched_result = self.language_detector.detect_files(discovery_result)

        # 4 & 5. Produce language statistics and file counts
        total_files = len(enriched_result.files)
        supported_files = 0
        unsupported_files = 0
        language_counts: dict[Language, int] = {lang: 0 for lang in Language}

        for file in enriched_result.files:
            lang = file.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
            if lang == Language.UNKNOWN:
                unsupported_files += 1
            else:
                supported_files += 1

        scan_duration = time.monotonic() - start_time

        # 7. Return ScanResult
        return ScanResult(
            repository_root=resolved_path,
            discovery_result=enriched_result,
            total_files=total_files,
            supported_files=supported_files,
            unsupported_files=unsupported_files,
            languages=language_counts,
            scan_duration=scan_duration,
        )
