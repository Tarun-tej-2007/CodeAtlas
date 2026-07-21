"""Base parser interface and Tree-sitter initialization module.

Defines the abstract BaseParser interface, concrete TreeSitterParser class,
cached grammar loading, and helper functions for instantiating Tree-sitter parsers.
"""

from abc import ABC, abstractmethod
import functools
from pathlib import Path
import tree_sitter
import tree_sitter_javascript as ts_js
import tree_sitter_typescript as ts_ts

from app.parser.exceptions import (
    ParseFailureError,
    ParserInitializationError,
    UnsupportedLanguageError,
)
from app.parser.language import Language
from app.parser.models import ParsedFile


@functools.lru_cache(maxsize=16)
def get_treesitter_language(language: Language) -> tree_sitter.Language:
    """Retrieves and caches native Tree-sitter Language instances per Language enum.

    Args:
        language: Canonical Language enum member.

    Returns:
        Cached tree_sitter.Language instance.

    Raises:
        UnsupportedLanguageError: If the specified language is not supported.
        ParserInitializationError: If loading grammar fails.
    """
    try:
        if language == Language.JAVASCRIPT:
            return tree_sitter.Language(ts_js.language())
        elif language == Language.TYPESCRIPT:
            return tree_sitter.Language(ts_ts.language_typescript())
        else:
            raise UnsupportedLanguageError(
                f"Unsupported language for Tree-sitter parser: '{language}'"
            )
    except UnsupportedLanguageError:
        raise
    except Exception as err:
        raise ParserInitializationError(
            f"Failed to load Tree-sitter grammar for language '{language}': {err}"
        ) from err


def create_treesitter_parser(language: Language) -> tree_sitter.Parser:
    """Initializes and returns a Tree-sitter parser configured for the specified Language.

    Args:
        language: Canonical Language enum member.

    Returns:
        Configured tree_sitter.Parser instance.

    Raises:
        ParserInitializationError: If Tree-sitter grammar loading or parser creation fails.
        UnsupportedLanguageError: If the specified language is not supported.
    """
    ts_lang = get_treesitter_language(language)
    return tree_sitter.Parser(ts_lang)


class BaseParser(ABC):
    """Abstract base class interface for language-specific code parsers."""

    @abstractmethod
    def parse_file(self, file_path: Path, repository_root: Path) -> ParsedFile:
        """Parses a single source file and returns a ParsedFile domain model."""
        pass


class TreeSitterParser(BaseParser):
    """Concrete implementation of BaseParser using Tree-sitter."""

    def __init__(self, language: Language) -> None:
        """Initializes the TreeSitterParser for a specific language.

        Args:
            language: Canonical Language enum member.

        Raises:
            ParserInitializationError: If Tree-sitter initialization fails.
            UnsupportedLanguageError: If the language is unsupported.
        """
        self.language = language
        self._ts_parser = create_treesitter_parser(language)

    def parse_file(self, file_path: Path, repository_root: Path) -> ParsedFile:
        """Reads and parses a source file into a ParsedFile model.

        Args:
            file_path: Absolute path to the source file.
            repository_root: Absolute path to the repository root directory.

        Returns:
            An immutable ParsedFile domain model containing the Tree-sitter AST.

        Raises:
            ParseFailureError: If reading or parsing the file fails.
        """
        try:
            source_bytes = file_path.read_bytes()
        except PermissionError as err:
            raise ParseFailureError(
                f"Permission denied reading file '{file_path}': {err}"
            ) from err
        except (FileNotFoundError, OSError) as err:
            raise ParseFailureError(
                f"Failed to read file '{file_path}': {err}"
            ) from err

        try:
            tree = self._ts_parser.parse(source_bytes)
            source_code = source_bytes.decode("utf-8", errors="replace")
            relative_path = file_path.relative_to(repository_root)
        except Exception as err:
            raise ParseFailureError(
                f"Failed to parse source file '{file_path}': {err}"
            ) from err

        return ParsedFile(
            path=file_path,
            relative_path=relative_path,
            language=self.language,
            source_code=source_code,
            tree=tree,
        )
