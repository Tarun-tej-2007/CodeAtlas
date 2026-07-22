"""Language detection module.

Determines the programming language of files based on their extension.
"""

import logging
from app.scanner.models import Language, DiscoveredFile, DiscoveryResult

logger = logging.getLogger("scanner")


class LanguageDetector:
    """Stateless service responsible for detecting programming language from file metadata."""

    # Map file extensions (including dot) to corresponding Language enum values
    EXTENSION_MAP: dict[str, Language] = {
        ".py": Language.PYTHON,
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".ts": Language.TYPESCRIPT,
        ".tsx": Language.TYPESCRIPT,
    }

    def detect(self, file: DiscoveredFile) -> Language:
        """Determines the programming language of a DiscoveredFile from its extension.

        Args:
            file: The DiscoveredFile model.

        Returns:
            A Language enum value.
        """
        ext = file.extension.lower() if file.extension else ""
        detected = self.EXTENSION_MAP.get(ext, Language.UNKNOWN)
        logger.debug("Detected language '%s' for file path '%s'", detected.value, file.relative_path)
        return detected

    def detect_files(self, discovery_result: DiscoveryResult) -> DiscoveryResult:
        """Processes a collection of files, returning a new DiscoveryResult with languages populated.

        Args:
            discovery_result: The source DiscoveryResult model containing DiscoveredFiles.

        Returns:
            A new DiscoveryResult instance with populated language fields.
        """
        enriched_files = []
        for file in discovery_result.files:
            lang = self.detect(file)
            # Safe copy since Pydantic models are frozen
            new_file = file.model_copy(update={"language": lang})
            enriched_files.append(new_file)

        return DiscoveryResult(files=enriched_files)
