"""CodeAtlas intra-file call analysis package.

Provides call reference models, exception classes, CallVisitor, and CallAnalyzer infrastructure.
"""

from app.analyzer.calls.analyzer import CallAnalyzer
from app.analyzer.calls.exceptions import CallAnalysisError, CallError
from app.analyzer.calls.models import CallAnalysisResult, CallKind, CallReference
from app.analyzer.calls.visitor import CallVisitor

__all__ = [
    # Enums & Domain Models
    "CallKind",
    "CallReference",
    "CallAnalysisResult",
    # Exceptions
    "CallError",
    "CallAnalysisError",
    # Visitor & Analyzer
    "CallVisitor",
    "CallAnalyzer",
]
