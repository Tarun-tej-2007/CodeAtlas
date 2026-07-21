"""Symbol domain exceptions module.

Defines the exception hierarchy for symbol extraction operations in CodeAtlas.
"""


class SymbolError(Exception):
    """Base exception class for all symbol domain errors."""

    pass


class SymbolExtractionError(SymbolError):
    """Raised when extracting symbols from an ASTDocument fails."""

    pass
