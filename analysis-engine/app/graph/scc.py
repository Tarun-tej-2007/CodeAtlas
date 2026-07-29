"""Strongly Connected Components (SCC) engine."""

from typing import Dict, List, Set
from pydantic import BaseModel, ConfigDict, Field

from app.graph.dependency_graph import DependencyGraph


class SCCResult(BaseModel):
    """Immutable result model containing strongly connected components."""

    components: List[List[str]] = Field(
        default_factory=list,
        description="Deterministic list of strongly connected components. Each component is a list of node IDs.",
    )

    model_config = ConfigDict(frozen=True)


class SCCEngine:
    """Computes strongly connected components (SCCs) of a DependencyGraph using Tarjan's algorithm."""

    def __init__(self) -> None:
        pass

    def compute_scc(self, graph: DependencyGraph) -> SCCResult:
        """Computes the strongly connected components of the given graph.

        Args:
            graph: The DependencyGraph to analyze.

        Returns:
            An immutable SCCResult containing components.
        """
        index_counter = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        stack: List[str] = []
        on_stack: Set[str] = set()
        sccs: List[List[str]] = []

        def strongconnect(u: str) -> None:
            nonlocal index_counter
            indices[u] = index_counter
            lowlinks[u] = index_counter
            index_counter += 1
            stack.append(u)
            on_stack.add(u)

            for edge in graph.get_outgoing_edges(u):
                v = edge.target_id
                if v not in indices:
                    strongconnect(v)
                    lowlinks[u] = min(lowlinks[u], lowlinks[v])
                elif v in on_stack:
                    lowlinks[u] = min(lowlinks[u], indices[v])

            if lowlinks[u] == indices[u]:
                component: List[str] = []
                while True:
                    v = stack.pop()
                    on_stack.remove(v)
                    component.append(v)
                    if v == u:
                        break
                # Sort component node list lexicographically for determinism
                component.sort()
                sccs.append(component)

        # Traverse in sorted node ID order to ensure deterministic execution pathways
        node_ids = sorted([node.id for node in graph.nodes])
        for nid in node_ids:
            if nid not in indices:
                strongconnect(nid)

        # Sort the overall list of components by their lexicographically smallest member
        sccs.sort(key=lambda c: c[0])
        return SCCResult(components=sccs)
