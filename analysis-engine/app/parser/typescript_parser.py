"""TypeScript Tree-sitter parser implementation."""

from typing import Any
import tree_sitter
import tree_sitter_typescript as ts_ts

from app.scanner.models import Language
from app.parser.base import SourceCodeParser
from app.parser.exceptions import ParserInitializationError, ParseError


class TypeScriptParser(SourceCodeParser):
    """Concrete SourceCodeParser for TypeScript using Tree-sitter."""

    def __init__(self) -> None:
        """Initializes the TypeScript Tree-sitter parser."""
        try:
            ts_lang = tree_sitter.Language(ts_ts.language_typescript())
            self._ts_parser = tree_sitter.Parser(ts_lang)
        except Exception as err:
            raise ParserInitializationError(f"Failed to initialize TypeScript Tree-sitter parser: {err}") from err

    @property
    def parser_id(self) -> str:
        return "tree-sitter-typescript"

    @property
    def language(self) -> Language:
        return Language.TYPESCRIPT

    def parse(self, source_code: str) -> Any:
        """Parses TypeScript source code string into a Tree-sitter syntax tree.

        Args:
            source_code: Raw source code string.

        Returns:
            The tree_sitter.Tree instance.

        Raises:
            ParseError: If parsing execution fails.
        """
        if source_code is None:
            raise ParseError("Source code cannot be None.")

        try:
            source_bytes = source_code.encode("utf-8")
            return self._ts_parser.parse(source_bytes)
        except Exception as err:
            raise ParseError(f"TypeScript parsing failed: {err}") from err
