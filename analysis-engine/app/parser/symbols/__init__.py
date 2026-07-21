"""CodeAtlas symbol extraction package.

Provides declaration symbol models, exception classes, symbol visitors,
and extraction engine infrastructure.
"""

from app.parser.symbols.exceptions import SymbolError, SymbolExtractionError
from app.parser.symbols.extractor import SymbolExtractor
from app.parser.symbols.models import Symbol, SymbolKind, SymbolTable
from app.parser.symbols.visitor import SymbolVisitor

__all__ = [
    # Data Models & Enums
    "SymbolKind",
    "Symbol",
    "SymbolTable",
    # Exceptions
    "SymbolError",
    "SymbolExtractionError",
    # Visitor
    "SymbolVisitor",
    # Extractor Engine
    "SymbolExtractor",
]
