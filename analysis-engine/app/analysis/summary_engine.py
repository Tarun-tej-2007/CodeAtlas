"""AI Analysis Summary Engine module.

Implements a stateless, extensible engine that calculates code finding aggregations,
severities, and custom metadata metrics for analysis run summaries.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json

from app.analysis.models import AnalysisSummary, AnalysisResult


class SummaryMetricCalculator(ABC):
    """Abstract interface for contributing specific metrics to the analysis summary."""

    @abstractmethod
    def calculate(self, result: AnalysisResult) -> Dict[str, str]:
        """Calculates custom summary metrics, returning them as string key-value pairs."""
        pass


# --- Concrete Metric Calculators ---


class SeverityAggregator(SummaryMetricCalculator):
    """Calculates finding counts grouped by severity."""

    def calculate(self, result: AnalysisResult) -> Dict[str, str]:
        tallies: Dict[str, int] = {}
        for f in result.findings:
            sev = f.severity.value
            tallies[sev] = tallies.get(sev, 0) + 1
        return {"findings_by_severity": json.dumps(tallies)}


class RecommendationCounter(SummaryMetricCalculator):
    """Calculates total recommendations count."""

    def calculate(self, result: AnalysisResult) -> Dict[str, str]:
        return {"total_recommendations": str(len(result.recommendations))}


class UniqueFileCounter(SummaryMetricCalculator):
    """Calculates number of unique files affected by findings."""

    def calculate(self, result: AnalysisResult) -> Dict[str, str]:
        affected = {f.file_path for f in result.findings if f.file_path}
        return {"unique_files_affected": str(len(affected))}


# --- Summary Engine Core ---


class SummaryEngine:
    """Stateless aggregator that calculates summary statistics for codebase analysis runs."""

    def __init__(self, calculators: Optional[List[SummaryMetricCalculator]] = None) -> None:
        """Initializes the engine with custom or default calculators."""
        self.calculators = calculators if calculators is not None else self._get_default_calculators()

    def _get_default_calculators(self) -> List[SummaryMetricCalculator]:
        return [
            SeverityAggregator(),
            RecommendationCounter(),
            UniqueFileCounter(),
        ]

    def summarize(self, result: AnalysisResult) -> AnalysisResult:
        """Calculates and populates summary statistics for an AnalysisResult.

        Returns a new immutable AnalysisResult with the populated summary.
        """
        diagnostics = list(result.diagnostics)
        diagnostics.append("Started summary aggregation phase.")

        # 1. Base counts
        total_findings = len(result.findings)

        # Build initial severity mapping
        findings_by_severity: Dict[str, int] = {}
        for f in result.findings:
            sev_str = f.severity.value
            findings_by_severity[sev_str] = findings_by_severity.get(sev_str, 0) + 1

        # 2. Gather metrics from registered calculators
        composed_metadata = dict(result.summary.metadata)
        for calculator in self.calculators:
            metrics = calculator.calculate(result)
            composed_metadata.update(metrics)

        summary = AnalysisSummary(
            total_findings=total_findings,
            findings_by_severity=findings_by_severity,
            duration_ms=result.summary.duration_ms,
            metadata=composed_metadata,
        )

        diagnostics.append(
            f"Successfully compiled summary. TotalFindings={total_findings}, SeverityGroups={len(findings_by_severity)}."
        )

        # Return a new immutable AnalysisResult
        return AnalysisResult(
            id=result.id,
            analysis_type=result.analysis_type,
            summary=summary,
            findings=result.findings,
            recommendations=result.recommendations,
            diagnostics=diagnostics,
            metadata=result.metadata,
        )
