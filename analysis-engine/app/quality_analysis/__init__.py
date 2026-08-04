"""CodeAtlas Quality Analysis domain package."""

from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.exceptions import QualityAnalysisError, QualityMetricError
from app.quality_analysis.models import QualityMetric, QualitySummary, QualityReport
from app.quality_analysis.analyzer import QualityAnalyzer
from app.quality_analysis.metric import QualityMetricEvaluator
from app.quality_analysis.registry import QualityMetricRegistry
from app.quality_analysis.engine import QualityEvaluationEngine
from app.quality_analysis.metrics.maintainability import (
    AverageFileSizeEvaluator,
    SymbolDensityEvaluator,
)
from app.quality_analysis.metrics.coupling import AverageCouplingEvaluator
from app.quality_analysis.metrics.cohesion import AverageCohesionEvaluator
from app.quality_analysis.metrics.complexity import AverageNestingDepthEvaluator
from app.quality_analysis.scoring import QualityScorer
from app.quality_analysis.context_builder import QualityAIContextBuilder
from app.quality_analysis.ai_analyzer import QualityAIAnalysisResult, AIQualityAnalyzer

__all__ = [
    "MetricCategory",
    "QualityLevel",
    "QualityAnalysisError",
    "QualityMetricError",
    "QualityMetric",
    "QualitySummary",
    "QualityReport",
    "QualityAnalyzer",
    "QualityMetricEvaluator",
    "QualityMetricRegistry",
    "QualityEvaluationEngine",
    "AverageFileSizeEvaluator",
    "SymbolDensityEvaluator",
    "AverageCouplingEvaluator",
    "AverageCohesionEvaluator",
    "AverageNestingDepthEvaluator",
    "QualityScorer",
    "QualityAIContextBuilder",
    "QualityAIAnalysisResult",
    "AIQualityAnalyzer",
]
