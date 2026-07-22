"""CodeAtlas parser domain package.

Provides abstractions, data models, exception classes, language definitions,
and registry infrastructure for source code parsing.
"""

from app.parser.exceptions import (
    ParseFailureError,
    ParserError,
    ParserInitializationError,
    UnsupportedLanguageError,
    ParseError,
)
from app.parser.language import Language
from app.parser.models import ParsedFile, ParseResult
from app.parser.parser import (
    BaseParser,
    TreeSitterParser,
    create_treesitter_parser,
    get_treesitter_language,
)
from app.parser.registry import ParserRegistry
from app.parser.repository_parser import RepositoryParser
from app.parser.base import SourceCodeParser

__all__ = [
    # Canonical Language Enum
    "Language",
    # Data Models
    "ParsedFile",
    "ParseResult",
    # Exceptions
    "ParserError",
    "UnsupportedLanguageError",
    "ParserInitializationError",
    "ParseFailureError",
    "ParseError",
    # Parser Base Interface, Implementations & Helpers
    "BaseParser",
    "TreeSitterParser",
    "create_treesitter_parser",
    "get_treesitter_language",
    "SourceCodeParser",
    # Registry & Repository Parser
    "ParserRegistry",
    "RepositoryParser",
]


