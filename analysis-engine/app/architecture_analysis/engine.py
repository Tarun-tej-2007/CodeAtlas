"""Architecture Rule Engine Module."""

from datetime import datetime, timezone
from typing import Any, List

from app.architecture_analysis.analyzer import ArchitectureAnalyzer
from app.architecture_analysis.enums import ArchitectureSeverity
from app.architecture_analysis.models import (
    ArchitectureIssue,
    ArchitectureReport,
    ArchitectureSummary,
)
from app.architecture_analysis.registry import ArchitectureRuleRegistry


class ArchitectureRuleEngine(ArchitectureAnalyzer):
    """Executes registered architecture rules sequentially and aggregates issues into a report."""

    def __init__(self, registry: ArchitectureRuleRegistry) -> None:
        """Initializes the engine with dependency-injected rule registry."""
        self.registry = registry

        # Verify that dependencies are actually present
        if registry is None:
            raise ValueError("ArchitectureRuleRegistry dependency must not be None.")

    def analyze(self, *, project_name: str, context: Any) -> ArchitectureReport:
        """Evaluates all registered rules against the context and compiles a report."""
        rules = self.registry.list_rules()
        accumulated_issues: List[ArchitectureIssue] = []

        # 1. Sequentially execute rules in registry order
        for rule in rules:
            issues = rule.evaluate(context)
            accumulated_issues.extend(issues)

        # 2. Automatically compute summary metrics
        total_issues = len(accumulated_issues)
        info_count = sum(1 for iss in accumulated_issues if iss.severity == ArchitectureSeverity.INFO)
        low_count = sum(1 for iss in accumulated_issues if iss.severity == ArchitectureSeverity.LOW)
        medium_count = sum(
            1 for iss in accumulated_issues if iss.severity == ArchitectureSeverity.MEDIUM
        )
        high_count = sum(1 for iss in accumulated_issues if iss.severity == ArchitectureSeverity.HIGH)
        critical_count = sum(
            1 for iss in accumulated_issues if iss.severity == ArchitectureSeverity.CRITICAL
        )

        summary = ArchitectureSummary(
            total_issues=total_issues,
            info_count=info_count,
            low_count=low_count,
            medium_count=medium_count,
            high_count=high_count,
            critical_count=critical_count,
        )

        # 3. Build and return the final report DTO
        return ArchitectureReport(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            issues=tuple(accumulated_issues),
            summary=summary,
        )
