"""CodeAtlas parser domain package.

Provides abstractions, data models, exception classes, language definitions,
and registry infrastructure for source code parsing.
"""

from app.parser.exceptions import (
    ParseFailureError,
    ParserError,
    ParserInitializationError,
    UnsupportedLanguageError,
)
from app.parser.language import Language
from app.parser.models import ParsedFile, ParseResult
from app.parser.parser import BaseParser, create_treesitter_parser
from app.parser.registry import ParserRegistry

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
    # Parser Base Interface & Helper
    "BaseParser",
    "create_treesitter_parser",
    # Parser Registry
    "ParserRegistry",
]
