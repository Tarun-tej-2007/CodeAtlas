"""Technical Debt Analysis Engine Module."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.technical_debt.analyzer import TechnicalDebtAnalyzer
from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.models import (
    TechnicalDebtItem,
    TechnicalDebtReport,
    TechnicalDebtSummary,
)
from app.technical_debt.registry import TechnicalDebtRuleRegistry


class TechnicalDebtAnalysisEngine(TechnicalDebtAnalyzer):
    """Orchestrates codebase technical debt scanning by executing registered rules."""

    def __init__(self, registry: TechnicalDebtRuleRegistry) -> None:
        """Initializes the engine with dependency-injected rule registry."""
        if registry is None:
            raise ValueError("TechnicalDebtRuleRegistry dependency must not be None.")
        self.registry = registry

    def analyze(self, *, project_name: str, context: Any, **kwargs) -> TechnicalDebtReport:
        """Executes registered rules sequentially in insertion order and compiles a report."""
        if not project_name or not project_name.strip():
            raise ValueError("project_name must be a non-empty string.")

        rules = self.registry.list_rules()
        evaluated_items: List[TechnicalDebtItem] = []

        # 1. Sequentially execute rules in registration order (exceptions propagate directly)
        for rule in rules:
            items = rule.evaluate(context, **kwargs)
            evaluated_items.extend(items)

        # 2. Compute aggregate values
        total_items = len(evaluated_items)
        total_effort = sum(item.effort_minutes for item in evaluated_items)

        items_by_category: Dict[TechnicalDebtCategory, int] = {}
        effort_by_severity: Dict[TechnicalDebtSeverity, int] = {}

        for item in evaluated_items:
            items_by_category[item.category] = items_by_category.get(item.category, 0) + 1
            effort_by_severity[item.severity] = (
                effort_by_severity.get(item.severity, 0) + item.effort_minutes
            )

        # 3. Construct TechnicalDebtSummary
        summary = TechnicalDebtSummary(
            total_items=total_items,
            total_effort_minutes=total_effort,
            items_by_category=items_by_category,
            effort_by_severity=effort_by_severity,
            metadata={"rule_count": len(rules)},
        )

        # 4. Construct TechnicalDebtReport with timezone-aware UTC datetime
        return TechnicalDebtReport(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            items=tuple(evaluated_items),
            summary=summary,
            metadata={"run_success": True},
        )
