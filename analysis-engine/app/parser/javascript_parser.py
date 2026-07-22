"""JavaScript Tree-sitter parser implementation."""

from typing import Any
import tree_sitter
import tree_sitter_javascript

from app.scanner.models import Language
from app.parser.base import SourceCodeParser
from app.parser.exceptions import ParserInitializationError, ParseError


class JavaScriptParser(SourceCodeParser):
    """Concrete SourceCodeParser for JavaScript using Tree-sitter."""

    def __init__(self) -> None:
        """Initializes the JavaScript Tree-sitter parser."""
        try:
            ts_lang = tree_sitter.Language(tree_sitter_javascript.language())
            self._ts_parser = tree_sitter.Parser(ts_lang)
        except Exception as err:
            raise ParserInitializationError(f"Failed to initialize JavaScript Tree-sitter parser: {err}") from err

    @property
    def parser_id(self) -> str:
        return "tree-sitter-javascript"

    @property
    def language(self) -> Language:
        return Language.JAVASCRIPT

    def parse(self, source_code: str) -> Any:
        """Parses JavaScript source code string into a Tree-sitter syntax tree.

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
            raise ParseError(f"JavaScript parsing failed: {err}") from err
