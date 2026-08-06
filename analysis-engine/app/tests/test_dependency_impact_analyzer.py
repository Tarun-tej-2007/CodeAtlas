"""Unit tests for the Dependency Impact Analyzer."""

import unittest
from typing import List

from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.incremental import (
    ChangeType,
    ChangedFile,
    DependencyImpactAnalyzer,
    IncrementalAnalysisValidationError,
)


class TestDependencyImpactAnalyzer(unittest.TestCase):
    """Verifies direct/transitive propagation, cycles termination, sorting stability, and graph validations."""

    def setUp(self) -> None:
        self.analyzer = DependencyImpactAnalyzer()

        # Define some common nodes
        self.node_a = GraphNode(id="src/a.py", name="a.py", type=DependencyNodeType.MODULE)
        self.node_b = GraphNode(id="src/b.py", name="b.py", type=DependencyNodeType.MODULE)
        self.node_c = GraphNode(id="src/c.py", name="c.py", type=DependencyNodeType.MODULE)
        self.node_sym = GraphNode(id="sym-class-a", name="MyClass", type=DependencyNodeType.CLASS)

    def test_invalid_parameters(self) -> None:
        """Verifies validation rejects invalid or None parameters."""
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.analyzer.analyze_impact(None, [])  # type: ignore

        with self.assertRaises(IncrementalAnalysisValidationError):
            self.analyzer.analyze_impact(self._build_graph([], []), None)  # type: ignore

        # Invalid changed file items
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.analyzer.analyze_impact(self._build_graph([], []), ["not_a_changed_file_dto"])  # type: ignore

    def test_no_changed_files(self) -> None:
        """Verifies empty changed files list returns empty impact set."""
        graph = self._build_graph([self.node_a], [])
        res = self.analyzer.analyze_impact(graph, [])
        self.assertEqual(len(res), 0)

    def test_single_modified_file_no_dependents(self) -> None:
        """Verifies single changed file returns only itself when no dependencies exist in graph."""
        graph = self._build_graph([self.node_a], [])
        change = ChangedFile(path="src/a.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [change])
        self.assertEqual(res, ("src/a.py",))

    def test_added_and_deleted_files(self) -> None:
        """Verifies added or deleted files are treated as impact roots even if missing from graph."""
        graph = self._build_graph([], [])
        change_add = ChangedFile(path="src/added.py", change_type=ChangeType.ADDED)
        change_del = ChangedFile(path="src/deleted.py", change_type=ChangeType.DELETED)

        res = self.analyzer.analyze_impact(graph, [change_add, change_del])
        self.assertEqual(res, ("src/added.py", "src/deleted.py"))

    def test_direct_dependency_propagation(self) -> None:
        """Verifies direct dependency propagation (B -> A: B depends on A)."""
        # Edge B imports A: src/b.py depends on src/a.py
        edge = GraphEdge(source_id="src/b.py", target_id="src/a.py", type=DependencyEdgeType.IMPORTS)
        graph = self._build_graph([self.node_a, self.node_b], [edge])

        change = ChangedFile(path="src/a.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [change])
        # Both a.py and b.py should be impacted
        self.assertEqual(res, ("src/a.py", "src/b.py"))

    def test_transitive_dependency_propagation(self) -> None:
        """Verifies transitive dependency propagation (C -> B -> A: C depends on B which depends on A)."""
        # C imports B, B imports A
        e1 = GraphEdge(source_id="src/c.py", target_id="src/b.py", type=DependencyEdgeType.IMPORTS)
        e2 = GraphEdge(source_id="src/b.py", target_id="src/a.py", type=DependencyEdgeType.IMPORTS)
        graph = self._build_graph([self.node_a, self.node_b, self.node_c], [e1, e2])

        change = ChangedFile(path="src/a.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [change])
        self.assertEqual(res, ("src/a.py", "src/b.py", "src/c.py"))

    def test_cyclic_dependency_graph(self) -> None:
        """Verifies traversal terminates safely and cleanly in cyclic dependency loops (A -> B -> A)."""
        e1 = GraphEdge(source_id="src/a.py", target_id="src/b.py", type=DependencyEdgeType.IMPORTS)
        e2 = GraphEdge(source_id="src/b.py", target_id="src/a.py", type=DependencyEdgeType.IMPORTS)
        graph = self._build_graph([self.node_a, self.node_b], [e1, e2])

        change = ChangedFile(path="src/a.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [change])
        self.assertEqual(res, ("src/a.py", "src/b.py"))

    def test_symbol_propagation(self) -> None:
        """Verifies impact propagates from module to symbol definitions and usages (b.py uses MyClass defined in a.py)."""
        # a.py -> MyClass (EXPORTS)
        # b.py -> MyClass (USAGE)
        e1 = GraphEdge(source_id="src/a.py", target_id="sym-class-a", type=DependencyEdgeType.EXPORTS)
        e2 = GraphEdge(source_id="src/b.py", target_id="sym-class-a", type=DependencyEdgeType.USAGE)
        graph = self._build_graph([self.node_a, self.node_b, self.node_sym], [e1, e2])

        change = ChangedFile(path="src/a.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [change])
        self.assertEqual(res, ("src/a.py", "src/b.py", "sym-class-a"))

    def test_duplicate_elimination_and_sorting(self) -> None:
        """Verifies output has no duplicates and is deterministically sorted."""
        # Multiple changes triggering overlapping dependencies
        e1 = GraphEdge(source_id="src/c.py", target_id="src/a.py", type=DependencyEdgeType.IMPORTS)
        e2 = GraphEdge(source_id="src/c.py", target_id="src/b.py", type=DependencyEdgeType.IMPORTS)
        graph = self._build_graph([self.node_a, self.node_b, self.node_c], [e1, e2])

        c_a = ChangedFile(path="src/a.py", change_type=ChangeType.MODIFIED)
        c_b = ChangedFile(path="src/b.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [c_a, c_b])
        # Output should be sorted: a.py, b.py, c.py
        self.assertEqual(res, ("src/a.py", "src/b.py", "src/c.py"))

    def test_large_dependency_graph(self) -> None:
        """Verifies performance under deeper chain/fanout structures."""
        nodes = [GraphNode(id=f"file_{i}.py", name=f"file_{i}", type=DependencyNodeType.MODULE) for i in range(100)]
        edges = []
        # Chain file_i depends on file_{i-1}
        for i in range(1, 100):
            edges.append(
                GraphEdge(
                    source_id=f"file_{i}.py",
                    target_id=f"file_{i-1}.py",
                    type=DependencyEdgeType.IMPORTS,
                )
            )

        graph = self._build_graph(nodes, edges)
        change = ChangedFile(path="file_0.py", change_type=ChangeType.MODIFIED)

        res = self.analyzer.analyze_impact(graph, [change])
        # Modifying file_0 should transitively impact all 100 files in the chain
        self.assertEqual(len(res), 100)
        self.assertEqual(res[0], "file_0.py")
        self.assertEqual(res[-1], "file_99.py")

    def _build_graph(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> DependencyGraph:
        """Helper to build validated DependencyGraph."""
        return DependencyGraph(nodes=nodes, edges=edges)


if __name__ == "__main__":
    unittest.main()
