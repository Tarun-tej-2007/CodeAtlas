"""Repository parser module.

Provides the RepositoryParser class for orchestrating multi-file parsing
over a ScanResult produced by the codebase Scanner.
"""

import time
from app.parser.exceptions import ParseFailureError, UnsupportedLanguageError
from app.parser.language import Language
from app.parser.models import ParsedFile, ParseResult
from app.parser.parser import TreeSitterParser
from app.parser.registry import ParserRegistry
from app.scanner.models import ScanResult


class RepositoryParser:
    """Orchestrates source code parsing for all files discovered in a ScanResult."""

    def __init__(self, registry: ParserRegistry | None = None) -> None:
        """Initializes RepositoryParser with a ParserRegistry instance.

        If no registry is provided, a default registry pre-loaded with
        JavaScript and TypeScript TreeSitterParsers is initialized.

        Args:
            registry: Optional custom ParserRegistry instance.
        """
        if registry is not None:
            self.registry = registry
        else:
            self.registry = ParserRegistry()
            self._register_default_parsers()

    def _register_default_parsers(self) -> None:
        """Helper to register standard JavaScript and TypeScript parsers."""
        self.registry.register(
            Language.JAVASCRIPT, TreeSitterParser(Language.JAVASCRIPT)
        )
        self.registry.register(
            Language.TYPESCRIPT, TreeSitterParser(Language.TYPESCRIPT)
        )

    def parse(self, scan_result: ScanResult) -> ParseResult:
        """Parses all supported source files in the provided ScanResult.

        Args:
            scan_result: ScanResult object containing discovered file metadata and repository root.

        Returns:
            ParseResult containing successfully parsed ParsedFile objects and statistics.
        """
        start_time = time.monotonic()

        parsed_files: list[ParsedFile] = []
        parsed_count = 0
        failed_count = 0

        for file_meta in scan_result.files:
            # Resolve canonical Language enum from file metadata or extension
            try:
                if file_meta.language:
                    lang = Language.from_str(file_meta.language)
                else:
                    lang = Language.from_str(file_meta.extension)

                parser = self.registry.get(lang)
                parsed_file = parser.parse_file(
                    file_path=file_meta.path,
                    repository_root=scan_result.repository_root,
                )
                parsed_files.append(parsed_file)
                parsed_count += 1
            except (UnsupportedLanguageError, ParseFailureError, Exception):
                failed_count += 1
                continue

        parse_duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        return ParseResult(
            files=parsed_files,
            parsed_count=parsed_count,
            failed_count=failed_count,
            parse_duration_ms=parse_duration_ms,
        )

    def parse_repository(self, scan_result: ScanResult) -> ParseResult:
        """Alias for parse() to maintain API flexibility."""
        return self.parse(scan_result)
