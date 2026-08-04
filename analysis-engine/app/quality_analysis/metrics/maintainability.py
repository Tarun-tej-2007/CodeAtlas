"""Maintainability Metrics Evaluators module."""

from typing import Any, Optional

from app.quality_analysis.enums import MetricCategory, QualityLevel
from app.quality_analysis.metric import QualityMetricEvaluator
from app.quality_analysis.models import QualityMetric


class AverageFileSizeEvaluator(QualityMetricEvaluator):
    """Evaluates codebase maintainability based on average discovered file size (in bytes)."""

    def __init__(
        self,
        good_threshold_bytes: int = 50 * 1024,
        fair_threshold_bytes: int = 150 * 1024,
        poor_threshold_bytes: int = 500 * 1024,
        metric_id: str = "average-file-size",
    ) -> None:
        """Initializes the evaluator with configurable size thresholds."""
        if not (0 < good_threshold_bytes < fair_threshold_bytes < poor_threshold_bytes):
            raise ValueError(
                "Threshold values must be positive and follow: good < fair < poor."
            )
        self._good_threshold = good_threshold_bytes
        self._fair_threshold = fair_threshold_bytes
        self._poor_threshold = poor_threshold_bytes
        self._metric_id = metric_id

    @property
    def metric_name(self) -> str:
        return self._metric_id

    @property
    def category(self) -> MetricCategory:
        return MetricCategory.MAINTAINABILITY

    @property
    def description(self) -> str:
        return "Measures software maintainability based on the average size (in bytes) of files."

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Resolve scan result files list
        scan_result = context
        if hasattr(context, "scan_result"):
            scan_result = context.scan_result

        # Locate files list
        files = []
        if hasattr(scan_result, "discovery_result") and hasattr(
            scan_result.discovery_result, "files"
        ):
            files = scan_result.discovery_result.files or []
        elif hasattr(scan_result, "files"):
            files = scan_result.files or []

        if not files:
            # If no files found, default to excellent
            return QualityMetric(
                name=self.metric_name,
                category=self.category,
                value=0.0,
                level=QualityLevel.EXCELLENT,
                description=self.description,
                metadata={"total_files": 0},
            )

        total_size = sum(getattr(f, "size", 0) for f in files)
        avg_size = total_size / len(files)

        # Map quality level based on average size
        if avg_size <= self._good_threshold:
            level = QualityLevel.EXCELLENT
        elif avg_size <= self._fair_threshold:
            level = QualityLevel.GOOD
        elif avg_size <= self._poor_threshold:
            level = QualityLevel.FAIR
        else:
            level = QualityLevel.POOR

        return QualityMetric(
            name=self.metric_name,
            category=self.category,
            value=avg_size,
            level=level,
            description=self.description,
            metadata={
                "total_files": len(files),
                "total_size_bytes": total_size,
                "good_threshold_bytes": self._good_threshold,
                "fair_threshold_bytes": self._fair_threshold,
                "poor_threshold_bytes": self._poor_threshold,
            },
        )


class SymbolDensityEvaluator(QualityMetricEvaluator):
    """Evaluates codebase maintainability based on average symbol density per file."""

    def __init__(
        self,
        good_threshold_density: float = 15.0,
        fair_threshold_density: float = 35.0,
        poor_threshold_density: float = 75.0,
        metric_id: str = "symbol-density",
    ) -> None:
        """Initializes the evaluator with configurable density thresholds."""
        if not (0.0 < good_threshold_density < fair_threshold_density < poor_threshold_density):
            raise ValueError(
                "Threshold values must be positive and follow: good < fair < poor."
            )
        self._good_threshold = good_threshold_density
        self._fair_threshold = fair_threshold_density
        self._poor_threshold = poor_threshold_density
        self._metric_id = metric_id

    @property
    def metric_name(self) -> str:
        return self._metric_id

    @property
    def category(self) -> MetricCategory:
        return MetricCategory.MAINTAINABILITY

    @property
    def description(self) -> str:
        return "Measures codebase maintainability based on the average symbol density per file."

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Resolve semantic files mapping
        project_sem = context
        if hasattr(context, "semantic_context"):
            # Resolve from architecture context wrapper
            project_sem = context.semantic_context

        # Check for LinkedSemanticResult structure
        if hasattr(project_sem, "original_result"):
            project_sem = project_sem.original_result

        files_map = {}
        if hasattr(project_sem, "files"):
            files_map = project_sem.files or {}

        if not files_map:
            return QualityMetric(
                name=self.metric_name,
                category=self.category,
                value=0.0,
                level=QualityLevel.EXCELLENT,
                description=self.description,
                metadata={"total_files": 0},
            )

        total_symbols = sum(len(getattr(f, "symbols", []) or []) for f in files_map.values())
        avg_density = total_symbols / len(files_map)

        if avg_density <= self._good_threshold:
            level = QualityLevel.EXCELLENT
        elif avg_density <= self._fair_threshold:
            level = QualityLevel.GOOD
        elif avg_density <= self._poor_threshold:
            level = QualityLevel.FAIR
        else:
            level = QualityLevel.POOR

        return QualityMetric(
            name=self.metric_name,
            category=self.category,
            value=avg_density,
            level=level,
            description=self.description,
            metadata={
                "total_files": len(files_map),
                "total_symbols": total_symbols,
                "good_threshold_density": self._good_threshold,
                "fair_threshold_density": self._fair_threshold,
                "poor_threshold_density": self._poor_threshold,
            },
        )
