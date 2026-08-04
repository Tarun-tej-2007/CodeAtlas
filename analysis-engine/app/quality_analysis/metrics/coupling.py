"""Coupling Metrics Evaluators module."""

from typing import Any

from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.metric import QualityMetricEvaluator
from app.quality_analysis.models import QualityMetric


class AverageCouplingEvaluator(QualityMetricEvaluator):
    """Evaluates average coupling connections per node across the dependency graph."""

    def __init__(
        self,
        good_threshold_coupling: float = 2.0,
        fair_threshold_coupling: float = 5.0,
        poor_threshold_coupling: float = 10.0,
        metric_id: str = "average-coupling",
    ) -> None:
        """Initializes the evaluator with configurable coupling thresholds."""
        if not (0.0 < good_threshold_coupling < fair_threshold_coupling < poor_threshold_coupling):
            raise ValueError(
                "Threshold values must be positive and follow: good < fair < poor."
            )
        self._good_threshold = good_threshold_coupling
        self._fair_threshold = fair_threshold_coupling
        self._poor_threshold = poor_threshold_coupling
        self._metric_id = metric_id

    @property
    def metric_name(self) -> str:
        return self._metric_id

    @property
    def category(self) -> MetricCategory:
        return MetricCategory.COUPLING

    @property
    def description(self) -> str:
        return "Measures software coupling based on the average directed connection edges per node in the graph."

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Resolve dependency graph
        graph = context
        if hasattr(context, "graph"):
            graph = context.graph

        nodes = getattr(graph, "nodes", []) or []
        edges = getattr(graph, "edges", []) or []

        if not nodes:
            return QualityMetric(
                name=self.metric_name,
                category=self.category,
                value=0.0,
                level=QualityLevel.EXCELLENT,
                description=self.description,
                metadata={"total_nodes": 0, "total_edges": 0},
            )

        total_nodes = len(nodes)
        total_edges = len(edges)
        avg_coupling = total_edges / total_nodes

        # Map levels (lower coupling is better)
        if avg_coupling <= self._good_threshold:
            level = QualityLevel.EXCELLENT
        elif avg_coupling <= self._fair_threshold:
            level = QualityLevel.GOOD
        elif avg_coupling <= self._poor_threshold:
            level = QualityLevel.FAIR
        else:
            level = QualityLevel.POOR

        return QualityMetric(
            name=self.metric_name,
            category=self.category,
            value=avg_coupling,
            level=level,
            description=self.description,
            metadata={
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "good_threshold_coupling": self._good_threshold,
                "fair_threshold_coupling": self._fair_threshold,
                "poor_threshold_coupling": self._poor_threshold,
            },
        )
