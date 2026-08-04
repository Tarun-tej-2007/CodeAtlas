"""Dependency Chain Length Architecture Rule."""

import hashlib
from typing import Any, List, Set, Tuple

from app.architecture_analysis.enums import ArchitectureRuleType, ArchitectureSeverity
from app.architecture_analysis.models import ArchitectureIssue
from app.architecture_analysis.rule import ArchitectureRule
from app.graph.dependency_graph import DependencyGraph


class DependencyChainRule(ArchitectureRule):
    """Detects transitive dependency chains exceeding a configured path length threshold."""

    def __init__(
        self,
        max_chain_length: int,
        rule_id: str = "dependency-chain-rule",
        severity: ArchitectureSeverity = ArchitectureSeverity.MEDIUM,
    ) -> None:
        """Initializes the rule with a configurable maximum path length threshold."""
        if max_chain_length <= 0:
            raise ValueError("max_chain_length must be a positive integer.")
        self._max_chain_length = max_chain_length
        self._rule_id = rule_id
        self._severity = severity

    @property
    def rule_id(self) -> str:
        """Unique ID of the rule."""
        return self._rule_id

    @property
    def rule_type(self) -> ArchitectureRuleType:
        """Rule categorization: LONG_DEPENDENCY_CHAIN."""
        return ArchitectureRuleType.LONG_DEPENDENCY_CHAIN

    @property
    def severity(self) -> ArchitectureSeverity:
        """Assigned issue severity."""
        return self._severity

    @property
    def title(self) -> str:
        """Short title."""
        return "Long Dependency Chain Detected"

    @property
    def description(self) -> str:
        """Detail check description."""
        return f"A transitive dependency chain exceeds the maximum allowed length of {self._max_chain_length}."

    def evaluate(self, *args, **kwargs) -> Tuple[ArchitectureIssue, ...]:
        """Evaluates the graph and returns issues for any dependency chains exceeding threshold."""
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

        all_maximal_paths: List[List[str]] = []

        def dfs_paths(u: str, current_path: List[str], path_set: Set[str]) -> None:
            extended = False
            targets = graph.get_outgoing_target_ids(u)
            for v in targets:
                if v not in path_set:
                    extended = True
                    current_path.append(v)
                    path_set.add(v)
                    dfs_paths(v, current_path, path_set)
                    path_set.remove(v)
                    current_path.pop()

            if not extended:
                if len(current_path) > self._max_chain_length:
                    all_maximal_paths.append(list(current_path))

        # Start from every node in sorted order for determinism
        node_ids = sorted([node.id for node in graph.nodes])
        for node_id in node_ids:
            dfs_paths(node_id, [node_id], {node_id})

        # Deduplicate paths (remove any path that is a contiguous subsegment of another path)
        def is_subpath(sub: List[str], main: List[str]) -> bool:
            sub_len = len(sub)
            main_len = len(main)
            for i in range(main_len - sub_len + 1):
                if main[i : i + sub_len] == sub:
                    return True
            return False

        all_maximal_paths.sort(key=len, reverse=True)
        unique_maximal_paths: List[List[str]] = []
        for path in all_maximal_paths:
            if any(is_subpath(path, existing) for existing in unique_maximal_paths):
                continue
            unique_maximal_paths.append(path)

        # Sort lexicographically for determinism
        unique_maximal_paths.sort()

        issues = []
        for i, path in enumerate(unique_maximal_paths):
            path_str = "->".join(path)
            stable_hash = hashlib.sha256(path_str.encode("utf-8")).hexdigest()[:8]
            issue_id = f"{self._rule_id}-chain-{i}-{stable_hash}"

            issue = ArchitectureIssue(
                id=issue_id,
                rule_type=self.rule_type,
                severity=self.severity,
                title="Long Dependency Chain Detected",
                description=f"Dependency chain exceeds threshold: {path_str}",
                affected_symbols=tuple(path),
                metadata={
                    "chain_length": len(path),
                    "chain_path": path,
                    "threshold": self._max_chain_length,
                },
            )
            issues.append(issue)

        return tuple(issues)
