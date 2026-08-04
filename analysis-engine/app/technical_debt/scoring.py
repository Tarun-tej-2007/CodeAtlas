"""Technical Debt Scoring and Aggregation Module."""

from typing import Any, Dict, Iterable, Mapping, Optional

from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.models import TechnicalDebtItem, TechnicalDebtSummary


class TechnicalDebtScorer:
    """Computes technical debt summaries and weighted scores from collections of findings."""

    DEFAULT_WEIGHTS: Mapping[TechnicalDebtSeverity, float] = {
        TechnicalDebtSeverity.INFO: 1.0,
        TechnicalDebtSeverity.LOW: 2.0,
        TechnicalDebtSeverity.MEDIUM: 5.0,
        TechnicalDebtSeverity.HIGH: 10.0,
        TechnicalDebtSeverity.CRITICAL: 20.0,
    }

    def __init__(
        self,
        severity_weights: Optional[Mapping[TechnicalDebtSeverity, float]] = None,
    ) -> None:
        """Initializes the scorer with configurable or default severity weights."""
        if severity_weights is not None:
            if any(w < 0.0 for w in severity_weights.values()):
                raise ValueError("Severity weights must be non-negative values.")
            self._weights = dict(severity_weights)
        else:
            self._weights = dict(self.DEFAULT_WEIGHTS)

    def score(self, items: Iterable[TechnicalDebtItem]) -> TechnicalDebtSummary:
        """Aggregates technical debt items and calculates categories, effort sums, and weighted scores."""
        items_list = list(items)
        if any(not isinstance(item, TechnicalDebtItem) for item in items_list):
            raise TypeError("All items in the collection must be instances of TechnicalDebtItem.")

        if not items_list:
            return TechnicalDebtSummary(
                total_items=0,
                total_effort_minutes=0,
                items_by_category={},
                effort_by_severity={},
                metadata={"weighted_overall_score": 0.0, "severity_weights": self._weights},
            )

        # 1. Basic aggregates
        total_items = len(items_list)
        total_effort = sum(item.effort_minutes for item in items_list)

        items_by_category: Dict[TechnicalDebtCategory, int] = {}
        effort_by_severity: Dict[TechnicalDebtSeverity, int] = {}
        severity_counts: Dict[TechnicalDebtSeverity, int] = {}

        for item in items_list:
            items_by_category[item.category] = items_by_category.get(item.category, 0) + 1
            effort_by_severity[item.severity] = (
                effort_by_severity.get(item.severity, 0) + item.effort_minutes
            )
            severity_counts[item.severity] = severity_counts.get(item.severity, 0) + 1

        # 2. Compute weighted overall score based on severity counts
        weighted_score = sum(
            count * self._weights.get(sev, 1.0)
            for sev, count in severity_counts.items()
        )

        # 3. Compile deterministic metadata mappings
        metadata = {
            "weighted_overall_score": float(weighted_score),
            "severity_counts": {k.value: v for k, v in severity_counts.items()},
            "severity_weights": {k.value: v for k, v in self._weights.items()},
        }

        return TechnicalDebtSummary(
            total_items=total_items,
            total_effort_minutes=total_effort,
            items_by_category=items_by_category,
            effort_by_severity=effort_by_severity,
            metadata=metadata,
        )
