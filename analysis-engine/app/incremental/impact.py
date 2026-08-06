"""Dependency Impact Analyzer Module."""

from typing import Iterable, List, Set, Tuple

from app.graph.dependency_graph import DependencyGraph
from app.incremental.enums import ChangeType
from app.incremental.exceptions import IncrementalAnalysisValidationError
from app.incremental.models import ChangedFile


class DependencyImpactAnalyzer:
    """Analyzer determining the minimal set of files and symbols requiring reanalysis after changes."""

    def analyze_impact(
        self, graph: DependencyGraph, changed_files: Iterable[ChangedFile]
    ) -> Tuple[str, ...]:
        """Calculates direct and transitive dependency impact from changed files over the dependency graph.

        Args:
            graph: The immutable validated DependencyGraph.
            changed_files: Collection of ChangedFile changes to analyze.

        Returns:
            An immutable, sorted, duplicate-free tuple of impacted node IDs (files/symbols).

        Raises:
            IncrementalAnalysisValidationError if parameters are invalid.
        """
        if graph is None:
            raise IncrementalAnalysisValidationError("graph must not be None.")
        if not isinstance(graph, DependencyGraph):
            raise IncrementalAnalysisValidationError("graph must be an instance of DependencyGraph.")
        if changed_files is None:
            raise IncrementalAnalysisValidationError("changed_files must not be None.")

        # Set of all impacted nodes
        impacted: Set[str] = set()
        queue: List[str] = []

        # 1. Identify initial impact roots from changed files
        for changed_file in changed_files:
            if not isinstance(changed_file, ChangedFile):
                raise IncrementalAnalysisValidationError("All changed_files items must be ChangedFile instances.")

            if changed_file.change_type in (ChangeType.ADDED, ChangeType.MODIFIED, ChangeType.DELETED):
                path_str = changed_file.path.replace("\\", "/")
                impacted.add(path_str)

                if graph.has_node(path_str):
                    queue.append(path_str)

        # 2. Transitive BFS traversal propagating impact along dependency edges
        # Safe against cyclic graphs using the 'impacted' set to guard visited status
        from app.graph.enums import DependencyEdgeType

        while queue:
            current = queue.pop(0)

            # A. Traverse outgoing edges: if current exports another node, that node is impacted
            for out_edge in graph.get_outgoing_edges(current):
                if out_edge.type == DependencyEdgeType.EXPORTS:
                    target_id = out_edge.target_id
                    if target_id not in impacted:
                        impacted.add(target_id)
                        queue.append(target_id)

            # B. Traverse incoming edges: if another node depends on current (non-exports), it is impacted
            for in_edge in graph.get_incoming_edges(current):
                if in_edge.type != DependencyEdgeType.EXPORTS:
                    source_id = in_edge.source_id
                    if source_id not in impacted:
                        impacted.add(source_id)
                        queue.append(source_id)

        # Return sorted list of impacted node IDs to guarantee output determinism
        return tuple(sorted(list(impacted)))
