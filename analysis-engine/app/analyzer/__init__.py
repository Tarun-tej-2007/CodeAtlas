"""CodeAtlas static analysis foundation package.

Provides domain models, BaseAnalyzer interface, AnalyzerRegistry, AnalysisPipeline,
and exception classes for orchestrating static code analysis.
"""

from app.analyzer.analyzer import AnalysisPipeline, BaseAnalyzer
from app.analyzer.exceptions import AnalysisError, AnalyzerExecutionError
from app.analyzer.models import (
    AnalysisContext,
    AnalysisResult,
    Diagnostic,
    Severity,
)
from app.analyzer.registry import AnalyzerRegistry

__all__ = [
    # Enums & Domain Models
    "Severity",
    "Diagnostic",
    "AnalysisContext",
    "AnalysisResult",
    # Exceptions
    "AnalysisError",
    "AnalyzerExecutionError",
    # Base Analyzer & Pipeline
    "BaseAnalyzer",
    "AnalysisPipeline",
    # Registry
    "AnalyzerRegistry",
]
