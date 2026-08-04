"""Unit tests for the concrete dependency graph rules."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.architecture_analysis import (
    ArchitectureSeverity,
    ArchitectureRuleRegistry,
    CircularDependencyRule,
    DependencyChainRule,
)
from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphNode, GraphEdge
from app.graph.enums import DependencyNodeType, DependencyEdgeType


def make_test_graph(nodes_list: list[str], edges_list: list[tuple[str, str]]) -> DependencyGraph:
    """Helper to create a DependencyGraph with target node IDs and edges."""
    nodes = [
        GraphNode(id=nid, name=nid, type=DependencyNodeType.MODULE)
        for nid in nodes_list
    ]
    edges = [
        GraphEdge(source_id=src, target_id=tgt, type=DependencyEdgeType.IMPORTS)
        for src, tgt in edges_list
    ]
    return DependencyGraph(nodes=nodes, edges=edges)


class TestDependencyGraphRules(unittest.TestCase):
    """Verifies cycle loops, long dependency paths, configurable limits, and registry compatibility."""

    def test_circular_dependency_no_cycles(self) -> None:
        """Verifies CircularDependencyRule on a DAG (no cycles)."""
        rule = CircularDependencyRule()
        # A -> B -> C
        graph = make_test_graph(["A", "B", "C"], [("A", "B"), ("B", "C")])

        issues = rule.evaluate(graph)
        self.assertEqual(len(issues), 0)

    def test_circular_dependency_single_cycle(self) -> None:
        """Verifies circular rule detects a single cycle."""
        rule = CircularDependencyRule(severity=ArchitectureSeverity.CRITICAL)
        # A -> B -> A
        graph = make_test_graph(["A", "B"], [("A", "B"), ("B", "A")])

        issues = rule.evaluate(graph)
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.severity, ArchitectureSeverity.CRITICAL)
        # Involved unique symbols are A and B
        self.assertEqual(set(issue.affected_symbols), {"A", "B"})
        self.assertEqual(issue.metadata["cycle_length"], 2)
        # Verify closed path starting and ending with the same node
        self.assertEqual(issue.metadata["cycle_path"][0], issue.metadata["cycle_path"][-1])

    def test_circular_dependency_multiple_cycles(self) -> None:
        """Verifies circular rule detects multiple independent cycles."""
        rule = CircularDependencyRule()
        # Cycle 1: A -> B -> A
        # Cycle 2: C -> D -> C
        graph = make_test_graph(
            ["A", "B", "C", "D"],
            [("A", "B"), ("B", "A"), ("C", "D"), ("D", "C")]
        )

        issues = rule.evaluate(graph)
        self.assertEqual(len(issues), 2)

        # Deterministic issue IDs/ordering checks
        ids = [issue.id for issue in issues]
        self.assertEqual(len(set(ids)), 2)  # unique IDs

    def test_dependency_chain_no_long_chains(self) -> None:
        """Verifies DependencyChainRule doesn't flag paths under the threshold."""
        # Threshold: 3 (max chain length allowed is 3 nodes)
        rule = DependencyChainRule(max_chain_length=3)
        # A -> B -> C (length 3)
        graph = make_test_graph(["A", "B", "C"], [("A", "B"), ("B", "C")])

        issues = rule.evaluate(graph)
        self.assertEqual(len(issues), 0)

    def test_dependency_chain_long_chain_detected(self) -> None:
        """Verifies DependencyChainRule flags paths exceeding threshold."""
        rule = DependencyChainRule(max_chain_length=2, severity=ArchitectureSeverity.HIGH)
        # A -> B -> C (length 3, threshold 2)
        graph = make_test_graph(["A", "B", "C"], [("A", "B"), ("B", "C")])

        issues = rule.evaluate(graph)
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.severity, ArchitectureSeverity.HIGH)
        self.assertEqual(issue.affected_symbols, ("A", "B", "C"))
        self.assertEqual(issue.metadata["chain_length"], 3)
        self.assertEqual(issue.metadata["threshold"], 2)

    def test_configurable_threshold_on_dependency_chain(self) -> None:
        """Verifies constructor-injected thresholds affect long dependency chains evaluation."""
        # A -> B -> C -> D -> E (length 5)
        graph = make_test_graph(
            ["A", "B", "C", "D", "E"],
            [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")]
        )

        # Threshold 5 -> No issues
        rule_5 = DependencyChainRule(max_chain_length=5)
        self.assertEqual(len(rule_5.evaluate(graph)), 0)

        # Threshold 4 -> 1 issue of length 5
        rule_4 = DependencyChainRule(max_chain_length=4)
        issues = rule_4.evaluate(graph)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].metadata["chain_length"], 5)

    def test_registry_compatibility(self) -> None:
        """Verifies concrete graph rules can be registered in ArchitectureRuleRegistry."""
        registry = ArchitectureRuleRegistry()
        rule_cycle = CircularDependencyRule()
        rule_chain = DependencyChainRule(max_chain_length=4)

        registry.register(rule_cycle)
        registry.register(rule_chain)

        self.assertEqual(len(registry), 2)
        self.assertTrue(registry.contains(rule_cycle.rule_id))
        self.assertTrue(registry.contains(rule_chain.rule_id))

    def test_deterministic_issue_ordering(self) -> None:
        """Verifies identical inputs return matching deterministic issue sequences."""
        rule = DependencyChainRule(max_chain_length=2)
        graph = make_test_graph(
            ["A", "B", "C", "D", "E"],
            [("A", "B"), ("B", "C"), ("D", "E")]
        )
        # Paths exceeding length 2:
        # 1. A -> B -> C (length 3)
        # 2. D -> E is length 2, under threshold -> not reported

        issues1 = rule.evaluate(graph)
        issues2 = rule.evaluate(graph)

        self.assertEqual(issues1, issues2)
        self.assertEqual(len(issues1), 1)
        self.assertEqual(issues1[0].affected_symbols, ("A", "B", "C"))

    def test_concurrent_execution(self) -> None:
        """Verifies that rule evaluation is thread-safe and stateless."""
        rule_cycle = CircularDependencyRule()
        rule_chain = DependencyChainRule(max_chain_length=2)
        # Create a simple cycle graph for cycle detection, and a separate graph for chain detection
        graph_cycle = make_test_graph(
            ["A", "B", "C"],
            [("A", "B"), ("B", "C"), ("C", "A")]
        )
        graph_chain = make_test_graph(
            ["A", "B", "C"],
            [("A", "B"), ("B", "C")]
        )

        def run_cycle():
            return rule_cycle.evaluate(graph_cycle)

        def run_chain():
            return rule_chain.evaluate(graph_chain)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures_cycle = [executor.submit(run_cycle) for _ in range(15)]
            futures_chain = [executor.submit(run_chain) for _ in range(15)]

            results_cycle = [f.result() for f in futures_cycle]
            results_chain = [f.result() for f in futures_chain]

        for r in results_cycle:
            self.assertEqual(len(r), 1)
            self.assertEqual(set(r[0].affected_symbols), {"A", "B", "C"})

        for r in results_chain:
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0].affected_symbols, ("A", "B", "C"))


if __name__ == "__main__":
    unittest.main()
