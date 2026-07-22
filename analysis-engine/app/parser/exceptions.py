"""Parser domain exceptions module.

Defines the exception hierarchy for source code parsing operations in CodeAtlas.
"""


class ParserError(Exception):
    """Base exception class for all source code parsing errors."""

    pass


class UnsupportedLanguageError(ParserError):
    """Raised when encountering an unsupported programming language."""

    pass


class ParserInitializationError(ParserError):
    """Raised when initializing or loading Tree-sitter language grammars fails."""

    pass


class ParseFailureError(ParserError):
    """Raised when parsing a source file fails due to I/O or syntax errors."""

    pass


class ParseError(ParserError):
    """Raised when parsing source code fails due to syntax or structural errors."""

    pass

