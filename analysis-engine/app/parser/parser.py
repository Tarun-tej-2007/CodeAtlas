"""Base parser interface and Tree-sitter initialization module.

Defines the abstract BaseParser interface and helper functions for instantiating
and initializing language-specific Tree-sitter parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import tree_sitter
import tree_sitter_javascript as ts_js
import tree_sitter_typescript as ts_ts

from app.parser.exceptions import ParserInitializationError, UnsupportedLanguageError
from app.parser.language import Language
from app.parser.models import ParsedFile


class BaseParser(ABC):
    """Abstract base class interface for language-specific code parsers."""

    @abstractmethod
    def parse_file(self, file_path: Path, repository_root: Path) -> ParsedFile:
        """Parses a single source file and returns a ParsedFile domain model.

        Args:
            file_path: Absolute path to the source file.
            repository_root: Absolute path to the repository root directory.

        Returns:
            An immutable ParsedFile domain model containing the AST tree.

        Raises:
            ParseFailureError: If file reading or parsing fails.
        """
        pass


def create_treesitter_parser(language: Language) -> tree_sitter.Parser:
    """Initializes and returns a Tree-sitter parser configured for the specified Language.

    Args:
        language: Canonical Language enum member.

    Returns:
        Configured tree_sitter.Parser instance.

    Raises:
        ParserInitializationError: If Tree-sitter grammar loading or parser creation fails.
        UnsupportedLanguageError: If the specified language is not supported by Tree-sitter.
    """
    try:
        if language == Language.JAVASCRIPT:
            ts_lang = tree_sitter.Language(ts_js.language())
        elif language == Language.TYPESCRIPT:
            ts_lang = tree_sitter.Language(ts_ts.language_typescript())
        else:
            raise UnsupportedLanguageError(f"Unsupported language for Tree-sitter parser: '{language}'")

        return tree_sitter.Parser(ts_lang)
    except (UnsupportedLanguageError, ParserInitializationError):
        raise
    except Exception as err:
        raise ParserInitializationError(
            f"Failed to initialize Tree-sitter parser for language '{language}': {err}"
        ) from err
