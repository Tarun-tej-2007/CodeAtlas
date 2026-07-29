"""Graph cycle detection engine."""

from typing import List, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.graph.dependency_graph import DependencyGraph


class CycleResult(BaseModel):
    """Immutable result model containing detected dependency cycles."""

    cycles: List[List[str]] = Field(
        default_factory=list,
        description="Deterministic list of cycles. Each cycle is a list of node IDs starting and ending with the same node.",
    )

    model_config = ConfigDict(frozen=True)


class CycleDetector:
    """Detects cycles in a DependencyGraph using deterministic DFS traversal."""

    def __init__(self) -> None:
        pass

    def detect_cycles(self, graph: DependencyGraph) -> CycleResult:
        """Detects cycles in the given dependency graph.

        Args:
            graph: The DependencyGraph to analyze.

        Returns:
            An immutable CycleResult containing list of cycles.
        """
        visited: Set[str] = set()
        path_set: Set[str] = set()
        path: List[str] = []
        unique_cycles: Set[Tuple[str, ...]] = set()

        def dfs(u: str) -> None:
            visited.add(u)
            path_set.add(u)
            path.append(u)

            for v in graph.get_outgoing_target_ids(u):
                if v in path_set:
                    # Cycle found!
                    try:
                        idx = path.index(v)
                        cycle_nodes = path[idx:]
                        # To make the cycle representation unique, find the lexicographical minimum
                        min_node = min(cycle_nodes)
                        min_idx = cycle_nodes.index(min_node)
                        # Rotate the cycle to start with the minimum node
                        rotated = cycle_nodes[min_idx:] + cycle_nodes[:min_idx]
                        # Close the loop
                        rotated.append(min_node)
                        unique_cycles.add(tuple(rotated))
                    except ValueError:
                        pass
                elif v not in visited:
                    dfs(v)

            path.pop()
            path_set.remove(u)

        # Traverse in sorted node ID order to ensure deterministic execution pathways
        node_ids = sorted([node.id for node in graph.nodes])
        for nid in node_ids:
            if nid not in visited:
                dfs(nid)

        # Sort individual cycles by their starting node to maintain stable result output ordering
        sorted_cycles = sorted([list(c) for c in unique_cycles], key=lambda x: x[0])
        return CycleResult(cycles=sorted_cycles)
