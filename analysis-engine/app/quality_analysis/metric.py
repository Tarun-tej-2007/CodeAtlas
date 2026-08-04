"""Quality Metric Evaluator interface."""

from abc import ABC, abstractmethod
from typing import Any

from app.quality_analysis.enums import MetricCategory
from app.quality_analysis.models import QualityMetric


class QualityMetricEvaluator(ABC):
    """Abstract Base Class defining the contract for all codebase quality metric evaluators."""

    @property
    @abstractmethod
    def metric_name(self) -> str:
        """Returns the unique identifier name of the metric."""
        pass

    @property
    @abstractmethod
    def category(self) -> MetricCategory:
        """Returns the MetricCategory category this evaluator targets."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Returns a brief explanation of what this quality metric measures."""
        pass

    @abstractmethod
    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        """Evaluates the quality metric constraints against the provided context.

        Args:
            context: The codebase context (e.g. AST, graph, semantic index).

        Returns:
            The computed QualityMetric DTO.
        """
        pass
