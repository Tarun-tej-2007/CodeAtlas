"""Call graph builder module."""

from typing import List, Set, Tuple

from app.semantic import SymbolKind
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.semantic.project_models import Location
from app.graph.dependency_models import DependencyMetadata, GraphEdge
from app.graph.dependency_graph import DependencyGraph
from app.graph.enums import DependencyEdgeType


class CallGraphBuilder:
    """Enriches an existing DependencyGraph with behavioural CALLS edges."""

    def __init__(self) -> None:
        pass

    def _encloses(self, parent: Location, child: Location) -> bool:
        """Determines if the parent coordinate range fully encloses the child range."""
        if parent.start_line > child.start_line:
            return False
        if parent.start_line == child.start_line and parent.start_column > child.start_column:
            return False
        if parent.end_line < child.end_line:
            return False
        if parent.end_line == child.end_line and parent.end_column < child.end_column:
            return False
        return True

    def build_call_graph(
        self, graph: DependencyGraph, linked_result: LinkedSemanticResult
    ) -> DependencyGraph:
        """Enriches the given dependency graph with CALLS edges from semantic references.

        Args:
            graph: The existing structural DependencyGraph.
            linked_result: The semantic linking pipeline result.

        Returns:
            A new enriched DependencyGraph containing call relationship edges.
        """
        # Deduplication and tracking sets
        seen_edges: Set[Tuple[str, str, str]] = {
            (edge.source_id, edge.target_id, edge.type.value) for edge in graph.edges
        }
        new_calls_edges: List[GraphEdge] = []

        files = linked_result.original_result.files

        for resolved_ref in linked_result.reference_resolution_result.resolved_references:
            callee = resolved_ref.target_symbol

            # Only function-to-function, method-to-method, and mixed calls are supported
            if callee.kind not in (SymbolKind.FUNCTION, SymbolKind.METHOD):
                continue

            ref_file_path = resolved_ref.reference.location.file_path
            project_file = files.get(ref_file_path)
            if not project_file:
                continue

            # Find enclosing caller symbols in the same file
            ref_loc = resolved_ref.reference.location.location
            candidates = []
            for sym in project_file.symbols:
                if sym.kind in (SymbolKind.FUNCTION, SymbolKind.METHOD):
                    if self._encloses(sym.location.location, ref_loc):
                        candidates.append(sym)

            if not candidates:
                continue

            # Find the deepest candidate (smallest line/col span)
            caller = min(
                candidates,
                key=lambda c: (
                    c.location.location.end_line - c.location.location.start_line,
                    c.location.location.end_column - c.location.location.start_column,
                ),
            )

            # Check if both caller and callee nodes exist in the graph
            if graph.has_node(caller.id) and graph.has_node(callee.id):
                edge_key = (caller.id, callee.id, DependencyEdgeType.CALLS.value)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    new_calls_edges.append(
                        GraphEdge(
                            source_id=caller.id,
                            target_id=callee.id,
                            type=DependencyEdgeType.CALLS,
                        )
                    )

        # Ensure deterministic output ordering by sorting new call edges
        new_calls_edges.sort(key=lambda e: (e.source_id, e.target_id))

        # Combine existing and calls edges
        enriched_edges = list(graph.edges) + new_calls_edges

        # Enrich metadata
        orig_attrs = graph.metadata.attributes
        new_attrs = dict(orig_attrs) if orig_attrs else {}
        new_attrs["calls_edges_count"] = len(new_calls_edges)
        new_attrs["total_edges"] = len(enriched_edges)

        metadata = DependencyMetadata(
            description=graph.metadata.description,
            version=graph.metadata.version,
            attributes=new_attrs,
        )

        return DependencyGraph(nodes=graph.nodes, edges=enriched_edges, metadata=metadata)
