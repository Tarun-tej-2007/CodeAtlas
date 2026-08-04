"""Quality Evaluation Engine Module."""

from datetime import datetime, timezone
from typing import Any, List

from app.quality_analysis.analyzer import QualityAnalyzer
from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.models import (
    QualityMetric,
    QualityReport,
    QualitySummary,
)
from app.quality_analysis.registry import QualityMetricRegistry


class QualityEvaluationEngine(QualityAnalyzer):
    """Orchestrates software quality evaluation by running registered metric evaluators."""

    def __init__(self, registry: QualityMetricRegistry) -> None:
        """Initializes the engine with dependency-injected metric registry."""
        if registry is None:
            raise ValueError("QualityMetricRegistry dependency must not be None.")
        self.registry = registry

    def analyze(self, *, project_name: str, context: Any, **kwargs) -> QualityReport:
        """Evaluates all registered metrics against the context and compiles a report."""
        if not project_name or not project_name.strip():
            raise ValueError("project_name must be a non-empty string.")
        evaluators = self.registry.list_metrics()
        evaluated_metrics: List[QualityMetric] = []

        # 1. Sequentially execute evaluators in registration order (exceptions propagate directly)
        for evaluator in evaluators:
            metric = evaluator.evaluate(context, **kwargs)
            evaluated_metrics.append(metric)

        # 2. Compute category segmented averages
        category_totals = {}
        category_counts = {}
        for m in evaluated_metrics:
            category_totals[m.category] = category_totals.get(m.category, 0.0) + m.value
            category_counts[m.category] = category_counts.get(m.category, 0) + 1

        metrics_by_category = {
            cat: (category_totals[cat] / category_counts[cat])
            for cat in category_totals
        }

        # 3. Compute overall score (average of all metric values)
        overall_score = (
            (sum(m.value for m in evaluated_metrics) / len(evaluated_metrics))
            if evaluated_metrics
            else 0.0
        )
        overall_level = self._determine_quality_level(overall_score)

        # 4. Construct immutable QualitySummary
        summary = QualitySummary(
            overall_score=overall_score,
            overall_level=overall_level,
            metrics_by_category=metrics_by_category,
        )

        # 5. Compile final QualityReport DTO with timezone-aware UTC datetime
        return QualityReport(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            metrics=tuple(evaluated_metrics),
            summary=summary,
        )

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Deterministically evaluates a quality rating level classification based on overall score."""
        if score >= 90.0:
            return QualityLevel.EXCELLENT
        elif score >= 75.0:
            return QualityLevel.GOOD
        elif score >= 50.0:
            return QualityLevel.FAIR
        elif score >= 25.0:
            return QualityLevel.POOR
        return QualityLevel.CRITICAL
