"""Circular Dependency Architecture Rule."""

import hashlib
from typing import Any, Tuple

from app.architecture_analysis.enums import ArchitectureRuleType, ArchitectureSeverity
from app.architecture_analysis.models import ArchitectureIssue
from app.architecture_analysis.rule import ArchitectureRule
from app.graph.cycle_detector import CycleDetector
from app.graph.dependency_graph import DependencyGraph


class CircularDependencyRule(ArchitectureRule):
    """Detects dependency cycles in the codebase graph structure."""

    def __init__(
        self,
        rule_id: str = "circular-dependency-rule",
        severity: ArchitectureSeverity = ArchitectureSeverity.HIGH,
    ) -> None:
        """Initializes the rule with a custom ID, severity, and cycle detector."""
        self._rule_id = rule_id
        self._severity = severity
        self._detector = CycleDetector()

    @property
    def rule_id(self) -> str:
        """Unique ID of the rule."""
        return self._rule_id

    @property
    def rule_type(self) -> ArchitectureRuleType:
        """Rule categorization: CIRCULAR_DEPENDENCY."""
        return ArchitectureRuleType.CIRCULAR_DEPENDENCY

    @property
    def severity(self) -> ArchitectureSeverity:
        """Assigned issue severity."""
        return self._severity

    @property
    def title(self) -> str:
        """Short title."""
        return "Circular Dependency Detected"

    @property
    def description(self) -> str:
        """Detail check description."""
        return "A closed loop of dependencies exists between modules, violating layering principles."

    def evaluate(self, *args, **kwargs) -> Tuple[ArchitectureIssue, ...]:
        """Evaluates the graph and returns issues for any cycles found."""
        context = args[0] if args else kwargs.get("context")
        if context is None:
            return ()

        # Resolve DependencyGraph from context
        graph = context
        if not isinstance(graph, DependencyGraph):
            if hasattr(context, "graph") and isinstance(context.graph, DependencyGraph):
                graph = context.graph
            else:
                return ()

        cycle_result = self._detector.detect_cycles(graph)
        issues = []

        for i, cycle in enumerate(cycle_result.cycles):
            # Generate deterministic stable issue id
            cycle_str = "->".join(cycle)
            stable_hash = hashlib.sha256(cycle_str.encode("utf-8")).hexdigest()[:8]
            issue_id = f"{self._rule_id}-cycle-{i}-{stable_hash}"

            # Affected symbols are nodes in the cycle (excluding the closing duplicate node)
            involved = tuple(cycle[:-1])

            issue = ArchitectureIssue(
                id=issue_id,
                rule_type=self.rule_type,
                severity=self.severity,
                title="Circular Dependency Detected",
                description=f"Circular dependency path: {cycle_str}",
                affected_symbols=involved,
                metadata={
                    "cycle_length": len(involved),
                    "cycle_path": cycle,
                },
            )
            issues.append(issue)

        return tuple(issues)
