"""Parsing pipeline orchestrator module."""

import logging
import time
from typing import List

from app.scanner.models import DiscoveredFile
from app.parser.models import ParsedFile, ParseResult
from app.plugins import PluginRegistry, PythonPlugin, JavaScriptPlugin, TypeScriptPlugin
from app.plugins.exceptions import PluginNotFoundError
from app.parser.exceptions import ParseError, ParserInitializationError

logger = logging.getLogger("analysis-engine")


class ParsingPipeline:
    """Orchestrates parsing of multiple discovered source files into AST syntax trees."""

    def __init__(self, registry: PluginRegistry | None = None) -> None:
        """Initializes the ParsingPipeline with a PluginRegistry.

        If no registry is provided, a default registry is created and
        populated with Python, JavaScript, and TypeScript plugins.
        """
        if registry is None:
            registry = PluginRegistry()
            registry.register(PythonPlugin())
            registry.register(JavaScriptPlugin())
            registry.register(TypeScriptPlugin())
        self.registry = registry

    def parse_files(self, files: List[DiscoveredFile]) -> ParseResult:
        """Parses a collection of discovered files, aggregating results and handling edge cases.

        Continues parsing remaining files when encountering unsupported languages,
        ParseErrors, or initialization errors.

        Args:
            files: List of discovered file metadata models.

        Returns:
            A ParseResult containing successfully parsed files and performance metrics.
        """
        start_time = time.monotonic()
        parsed_files: List[ParsedFile] = []
        failed_count = 0

        for discovered_file in files:
            # Skip unknown languages immediately as failed/unsupported
            if discovered_file.language == discovered_file.language.UNKNOWN:
                logger.warning("Unsupported language or file without extension: %s", discovered_file.absolute_path)
                failed_count += 1
                continue

            try:
                # 1. Resolve appropriate LanguagePlugin
                plugin = self.registry.get_plugin(discovered_file.language)
                
                # 2. Obtain parser
                parser = plugin.get_parser()
                
                # 3. Read source code
                try:
                    source_code = discovered_file.absolute_path.read_text(encoding="utf-8", errors="replace")
                except Exception as read_err:
                    logger.error(
                        "Failed to read file contents at '%s': %s",
                        discovered_file.absolute_path,
                        read_err,
                        exc_info=True
                    )
                    failed_count += 1
                    continue

                # 4. Parse source code
                tree = parser.parse(source_code)
                
                # 5. Build ParsedFile
                parsed_file = ParsedFile(
                    path=discovered_file.absolute_path,
                    relative_path=discovered_file.relative_path,
                    language=discovered_file.language,
                    source_code=source_code,
                    tree=tree
                )
                parsed_files.append(parsed_file)

            except (PluginNotFoundError, ParserInitializationError, ParseError) as err:
                logger.error(
                    "Error parsing file '%s': %s",
                    discovered_file.absolute_path,
                    err,
                    exc_info=True
                )
                failed_count += 1
            except Exception as unexpected_err:
                logger.error(
                    "Unexpected failure parsing file '%s': %s",
                    discovered_file.absolute_path,
                    unexpected_err,
                    exc_info=True
                )
                failed_count += 1

        duration_ms = (time.monotonic() - start_time) * 1000.0

        return ParseResult(
            files=parsed_files,
            parsed_count=len(parsed_files),
            failed_count=failed_count,
            parse_duration_ms=duration_ms
        )
