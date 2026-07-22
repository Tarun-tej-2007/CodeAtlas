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
from app.parser.models import ParsedFile, ParseResult, AnalysisResult
from app.parser.parser import (
    BaseParser,
    TreeSitterParser,
    create_treesitter_parser,
    get_treesitter_language,
)
from app.parser.registry import ParserRegistry
from app.parser.repository_parser import RepositoryParser
from app.parser.base import SourceCodeParser
from app.parser.python_parser import PythonParser
from app.parser.javascript_parser import JavaScriptParser
from app.parser.typescript_parser import TypeScriptParser
from app.parser.pipeline import ParsingPipeline

__all__ = [
    # Canonical Language Enum
    "Language",
    # Data Models
    "ParsedFile",
    "ParseResult",
    "AnalysisResult",
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
    "PythonParser",
    "JavaScriptParser",
    "TypeScriptParser",
    "ParsingPipeline",
    # Registry & Repository Parser
    "ParserRegistry",
    "RepositoryParser",
]


