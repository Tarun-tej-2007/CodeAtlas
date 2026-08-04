"""Complexity Metrics Evaluators module."""

from typing import Any, Dict

from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.metric import QualityMetricEvaluator
from app.quality_analysis.models import QualityMetric


class AverageNestingDepthEvaluator(QualityMetricEvaluator):
    """Evaluates codebase complexity based on the average lexical nesting depth of scopes."""

    def __init__(
        self,
        good_threshold_depth: float = 2.0,
        fair_threshold_depth: float = 3.5,
        poor_threshold_depth: float = 5.0,
        metric_id: str = "average-nesting-depth",
    ) -> None:
        """Initializes the evaluator with configurable depth thresholds."""
        if not (0.0 < good_threshold_depth < fair_threshold_depth < poor_threshold_depth):
            raise ValueError(
                "Threshold values must be positive and follow: good < fair < poor."
            )
        self._good_threshold = good_threshold_depth
        self._fair_threshold = fair_threshold_depth
        self._poor_threshold = poor_threshold_depth
        self._metric_id = metric_id

    @property
    def metric_name(self) -> str:
        return self._metric_id

    @property
    def category(self) -> MetricCategory:
        return MetricCategory.COMPLEXITY

    @property
    def description(self) -> str:
        return "Measures software complexity based on the average lexical nesting depth of scopes."

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Resolve semantic scopes
        project_sem = context
        if hasattr(context, "semantic_context"):
            project_sem = context.semantic_context

        if hasattr(project_sem, "original_result"):
            project_sem = project_sem.original_result

        scopes = []
        if hasattr(project_sem, "scopes"):
            scopes = getattr(project_sem, "scopes", []) or []
        elif hasattr(project_sem, "_scopes"):
            scopes = getattr(project_sem, "_scopes", []) or []
        elif hasattr(context, "scopes"):
            scopes = getattr(context, "scopes", []) or []

        if not scopes:
            return QualityMetric(
                name=self.metric_name,
                category=self.category,
                value=0.0,
                level=QualityLevel.EXCELLENT,
                description=self.description,
                metadata={"total_scopes": 0},
            )

        # 1. Map scopes by ID
        parent_map: Dict[str, str] = {}
        for scope in scopes:
            scope_id = getattr(scope, "id", None)
            parent_id = getattr(scope, "parent_scope_id", None)
            if parent_id is None and hasattr(scope, "parent") and scope.parent:
                parent_id = getattr(scope.parent, "id", None)
            if scope_id:
                parent_map[scope_id] = parent_id

        # 2. Compute depth for each scope deterministically (cycle detection protected)
        total_depth = 0.0
        for scope_id in parent_map:
            depth = 0
            visited = {scope_id}
            curr_id = parent_map[scope_id]
            while curr_id and curr_id in parent_map:
                if curr_id in visited:
                    # Prevent cycle infinite loops
                    break
                visited.add(curr_id)
                depth += 1
                curr_id = parent_map[curr_id]
            total_depth += depth

        total_scopes = len(parent_map)
        avg_depth = total_depth / total_scopes

        # Map levels (lower depth is less complex / better)
        if avg_depth <= self._good_threshold:
            level = QualityLevel.EXCELLENT
        elif avg_depth <= self._fair_threshold:
            level = QualityLevel.GOOD
        elif avg_depth <= self._poor_threshold:
            level = QualityLevel.FAIR
        else:
            level = QualityLevel.POOR

        return QualityMetric(
            name=self.metric_name,
            category=self.category,
            value=avg_depth,
            level=level,
            description=self.description,
            metadata={
                "total_scopes": total_scopes,
                "good_threshold_depth": self._good_threshold,
                "fair_threshold_depth": self._fair_threshold,
                "poor_threshold_depth": self._poor_threshold,
            },
        )
