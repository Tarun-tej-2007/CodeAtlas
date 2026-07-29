"""Graph traversal algorithms module."""

from typing import Generator, List, Set

from app.graph.dependency_graph import DependencyGraph


class GraphTraversal:
    """Provides stateless BFS and DFS traversal generators over a DependencyGraph."""

    def __init__(self) -> None:
        pass

    def bfs(self, graph: DependencyGraph, start_node_id: str) -> Generator[str, None, None]:
        """Performs a breadth-first search traversal starting from start_node_id.

        Args:
            graph: The DependencyGraph to traverse.
            start_node_id: The node identifier to start traversal from.

        Yields:
            Node identifiers in BFS order.
        """
        if not graph.has_node(start_node_id):
            return

        visited = {start_node_id}
        queue = [start_node_id]

        while queue:
            current = queue.pop(0)
            yield current

            # Sort targets lexicographically to guarantee deterministic execution
            targets = sorted([edge.target_id for edge in graph.get_outgoing_edges(current)])
            for target in targets:
                if target not in visited:
                    visited.add(target)
                    queue.append(target)

    def dfs(self, graph: DependencyGraph, start_node_id: str) -> Generator[str, None, None]:
        """Performs a depth-first search traversal starting from start_node_id.

        Args:
            graph: The DependencyGraph to traverse.
            start_node_id: The node identifier to start traversal from.

        Yields:
            Node identifiers in DFS order.
        """
        if not graph.has_node(start_node_id):
            return

        visited: Set[str] = set()
        stack = [start_node_id]

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                yield current

                # Push to stack in reverse sorted order so they are popped in sorted order
                targets = sorted([edge.target_id for edge in graph.get_outgoing_edges(current)], reverse=True)
                for target in targets:
                    if target not in visited:
                        stack.append(target)
