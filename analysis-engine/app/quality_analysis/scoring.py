"""Quality Scoring and Aggregation Module."""

from typing import Any, Dict, Iterable, Mapping, Optional

from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.models import QualityMetric, QualitySummary


class QualityScorer:
    """Computes category-weighted quality scores and ratings from QualityMetric collections."""

    def __init__(
        self,
        category_weights: Optional[Mapping[MetricCategory, float]] = None,
    ) -> None:
        """Initializes the scorer with configurable category weights."""
        if category_weights is not None:
            if any(w < 0.0 for w in category_weights.values()):
                raise ValueError("Category weights must be non-negative values.")
            self._weights = dict(category_weights)
        else:
            self._weights = {}

    def score(self, metrics: Iterable[QualityMetric]) -> QualitySummary:
        """Aggregates metrics and calculates the weighted category and overall scores."""
        metrics_list = list(metrics)
        if any(not isinstance(m, QualityMetric) for m in metrics_list):
            raise TypeError("All items in metrics collection must be instances of QualityMetric.")
        if not metrics_list:
            return QualitySummary(
                overall_score=0.0,
                overall_level=QualityLevel.CRITICAL,
                metrics_by_category={},
                metadata={"total_metrics": 0},
            )

        # 1. Compute simple averages for each category
        category_totals: Dict[MetricCategory, float] = {}
        category_counts: Dict[MetricCategory, int] = {}
        for m in metrics_list:
            category_totals[m.category] = category_totals.get(m.category, 0.0) + m.value
            category_counts[m.category] = category_counts.get(m.category, 0) + 1

        category_averages: Dict[MetricCategory, float] = {
            cat: (category_totals[cat] / category_counts[cat])
            for cat in category_totals
        }

        # 2. Compute weighted overall score based on category averages
        weighted_sum = 0.0
        total_weight = 0.0

        for cat, avg_val in category_averages.items():
            # Use configured weight or default to 1.0
            weight = self._weights.get(cat, 1.0)
            weighted_sum += avg_val * weight
            total_weight += weight

        overall_score = (weighted_sum / total_weight) if total_weight > 0.0 else 0.0
        overall_level = self._determine_quality_level(overall_score)

        return QualitySummary(
            overall_score=overall_score,
            overall_level=overall_level,
            metrics_by_category=category_averages,
            metadata={
                "total_metrics": len(metrics_list),
                "category_weights": self._weights,
            },
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
