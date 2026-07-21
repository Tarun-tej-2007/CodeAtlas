"""CodeAtlas module import/export analysis package.

Provides import/export symbol models, exception classes, module visitor,
and module analyzer infrastructure.
"""

from app.parser.modules.analyzer import ModuleAnalyzer
from app.parser.modules.exceptions import ModuleAnalysisError, ModuleError
from app.parser.modules.models import (
    ExportKind,
    ExportSymbol,
    ImportKind,
    ImportSymbol,
    ModuleMetadata,
)
from app.parser.modules.visitor import ModuleVisitor

__all__ = [
    # Enums & Data Models
    "ImportKind",
    "ExportKind",
    "ImportSymbol",
    "ExportSymbol",
    "ModuleMetadata",
    # Exceptions
    "ModuleError",
    "ModuleAnalysisError",
    # Visitor
    "ModuleVisitor",
    # Analyzer Engine
    "ModuleAnalyzer",
]
