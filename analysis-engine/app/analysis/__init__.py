"""CodeAtlas AI Code Analysis package.

Establishes core StrEnums, custom exceptions, immutable DTO models, and abstract
pipeline interfaces for codebase analysis.
"""

from app.analysis.enums import (
    AnalysisType,
    AnalysisSeverity,
    RecommendationStatus,
    AnalysisTrigger,
)
from app.analysis.exceptions import (
    AnalysisError,
    AnalysisValidationError,
    AnalysisExecutionError,
)
from app.analysis.models import (
    AnalysisFinding,
    AnalysisRecommendation,
    AnalysisSummary,
    AnalysisResult,
)
from app.analysis.analyzer import CodeAnalyzer
from app.analysis.finding_analyzer import FindingAnalyzer

__all__ = [
    # Enums
    "AnalysisType",
    "AnalysisSeverity",
    "RecommendationStatus",
    "AnalysisTrigger",
    # Exceptions
    "AnalysisError",
    "AnalysisValidationError",
    "AnalysisExecutionError",
    # Models
    "AnalysisFinding",
    "AnalysisRecommendation",
    "AnalysisSummary",
    "AnalysisResult",
    # Analyzer Interface
    "CodeAnalyzer",
    # Finding Analyzer
    "FindingAnalyzer",
]
