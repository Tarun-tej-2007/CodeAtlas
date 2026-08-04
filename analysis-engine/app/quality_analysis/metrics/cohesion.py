"""Cohesion Metrics Evaluators module."""

from typing import Any

from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.metric import QualityMetricEvaluator
from app.quality_analysis.models import QualityMetric


class AverageCohesionEvaluator(QualityMetricEvaluator):
    """Evaluates module cohesion based on the ratio of internal references to total resolved references."""

    def __init__(
        self,
        good_threshold_cohesion: float = 60.0,
        fair_threshold_cohesion: float = 40.0,
        poor_threshold_cohesion: float = 20.0,
        metric_id: str = "average-cohesion",
    ) -> None:
        """Initializes the evaluator with configurable cohesion thresholds (as percentages)."""
        if not (0.0 < poor_threshold_cohesion < fair_threshold_cohesion < good_threshold_cohesion <= 100.0):
            raise ValueError(
                "Threshold values must be positive and follow: poor < fair < good <= 100.0."
            )
        self._good_threshold = good_threshold_cohesion
        self._fair_threshold = fair_threshold_cohesion
        self._poor_threshold = poor_threshold_cohesion
        self._metric_id = metric_id

    @property
    def metric_name(self) -> str:
        return self._metric_id

    @property
    def category(self) -> MetricCategory:
        return MetricCategory.COHESION

    @property
    def description(self) -> str:
        return "Measures module cohesion based on internal file reference density ratio."

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Check if context directly holds resolved references
        resolved_references = []
        if hasattr(context, "resolved_references"):
            resolved_references = context.resolved_references or []
        else:
            # Resolve semantic context
            project_sem = context
            if hasattr(context, "semantic_context"):
                project_sem = context.semantic_context

            # Check for reference resolution result in context wrappers
            ref_res = None
            for obj in (context, project_sem):
                if hasattr(obj, "reference_resolution_result"):
                    ref_res = getattr(obj, "reference_resolution_result")
                    break
                elif hasattr(obj, "original_result") and hasattr(obj.original_result, "reference_resolution_result"):
                    ref_res = getattr(obj.original_result, "reference_resolution_result")
                    break

            if ref_res and hasattr(ref_res, "resolved_references"):
                resolved_references = ref_res.resolved_references or []

        if not resolved_references:
            # Default to maximum cohesion if no cross-file references exist
            return QualityMetric(
                name=self.metric_name,
                category=self.category,
                value=100.0,
                level=QualityLevel.EXCELLENT,
                description=self.description,
                metadata={"total_resolved_references": 0, "internal_references": 0},
            )

        total_resolved = len(resolved_references)
        internal_resolved = 0

        for ref in resolved_references:
            ref_path = None
            target_path = None

            if hasattr(ref, "reference") and hasattr(ref.reference, "location"):
                ref_path = getattr(ref.reference.location, "file_path", None)

            if hasattr(ref, "target_symbol") and hasattr(ref.target_symbol, "location"):
                target_path = getattr(ref.target_symbol.location, "file_path", None)

            if ref_path is not None and target_path is not None and ref_path == target_path:
                internal_resolved += 1

        cohesion_percentage = (internal_resolved / total_resolved) * 100.0

        # Map levels (higher cohesion percentage is better)
        if cohesion_percentage >= self._good_threshold:
            level = QualityLevel.EXCELLENT
        elif cohesion_percentage >= self._fair_threshold:
            level = QualityLevel.GOOD
        elif cohesion_percentage >= self._poor_threshold:
            level = QualityLevel.FAIR
        else:
            level = QualityLevel.POOR

        return QualityMetric(
            name=self.metric_name,
            category=self.category,
            value=cohesion_percentage,
            level=level,
            description=self.description,
            metadata={
                "total_resolved_references": total_resolved,
                "internal_references": internal_resolved,
                "good_threshold_cohesion": self._good_threshold,
                "fair_threshold_cohesion": self._fair_threshold,
                "poor_threshold_cohesion": self._poor_threshold,
            },
        )
