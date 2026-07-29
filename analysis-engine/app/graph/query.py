"""Graph query engine module."""

from typing import List, Optional, Tuple

from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.traversal import GraphTraversal


class DependencyGraphQuery:
    """Stateless query engine over a DependencyGraph."""

    def __init__(self) -> None:
        self._traversal = GraphTraversal()

    def get_node(self, graph: DependencyGraph, node_id: str) -> Optional[GraphNode]:
        """Look up a node by its unique identifier."""
        return graph.get_node(node_id)

    def has_node(self, graph: DependencyGraph, node_id: str) -> bool:
        """Check if a node ID exists in the graph."""
        return graph.has_node(node_id)

    def get_outgoing_edges(self, graph: DependencyGraph, node_id: str) -> Tuple[GraphEdge, ...]:
        """Retrieve outgoing edges originating from the specified node."""
        return graph.get_outgoing_edges(node_id)

    def get_incoming_edges(self, graph: DependencyGraph, node_id: str) -> Tuple[GraphEdge, ...]:
        """Retrieve incoming edges targeting the specified node."""
        return graph.get_incoming_edges(node_id)

    def get_neighbours(self, graph: DependencyGraph, node_id: str) -> List[GraphNode]:
        """Retrieve all immediate outgoing neighbour nodes of the specified node ID, sorted lexicographically by ID."""
        if not graph.has_node(node_id):
            return []

        target_ids = sorted(list({edge.target_id for edge in graph.get_outgoing_edges(node_id)}))
        neighbours = []
        for tid in target_ids:
            node = graph.get_node(tid)
            if node:
                neighbours.append(node)
        return neighbours

    def get_reachable_nodes(self, graph: DependencyGraph, start_node_id: str) -> List[str]:
        """Compute the list of all node IDs reachable from the start node, sorted lexicographically."""
        if not graph.has_node(start_node_id):
            return []

        visited = set(self._traversal.bfs(graph, start_node_id))
        return sorted(list(visited))

    def shortest_path(self, graph: DependencyGraph, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find the shortest unweighted path from source to target using BFS.

        Args:
            graph: The DependencyGraph to search.
            source_id: Starting node ID.
            target_id: Destination node ID.

        Returns:
            List of node IDs forming the shortest path from source to target (inclusive),
            or None if no path exists.
        """
        if not graph.has_node(source_id) or not graph.has_node(target_id):
            return None

        if source_id == target_id:
            return [source_id]

        visited = {source_id}
        queue = [[source_id]]

        while queue:
            path = queue.pop(0)
            current = path[-1]

            if current == target_id:
                return path

            # Sort targets lexicographically to ensure deterministic path selection
            targets = sorted([edge.target_id for edge in graph.get_outgoing_edges(current)])
            for target in targets:
                if target not in visited:
                    visited.add(target)
                    new_path = list(path) + [target]
                    queue.append(new_path)

        return None
