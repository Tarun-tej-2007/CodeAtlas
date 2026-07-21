"""Graph container module.

Provides the Graph class for O(1) node/edge lookups, indexing, and deterministic traversals.
"""

from typing import Any
from app.graph.enums import EdgeType
from app.graph.exceptions import GraphError
from app.graph.models import GraphEdge, GraphMetadata, GraphNode


class Graph:
    """Canonical graph container managing O(1) indexed GraphNode and GraphEdge collections."""

    def __init__(self, metadata: GraphMetadata | None = None) -> None:
        """Initializes a Graph container with optional metadata.

        Args:
            metadata: GraphMetadata instance (defaults to generic project metadata if omitted).
        """
        self.metadata = metadata or GraphMetadata(project_name="CodeAtlas")
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._out_edges: dict[str, list[GraphEdge]] = {}
        self._in_edges: dict[str, list[GraphEdge]] = {}

    def add_node(self, node: GraphNode) -> None:
        """Adds a GraphNode to the graph container.

        Args:
            node: GraphNode model instance.

        Raises:
            GraphError: If a node with the same ID is already present in the graph.
        """
        if node.id in self._nodes:
            raise GraphError(f"Duplicate node ID '{node.id}' already exists in graph.")

        self._nodes[node.id] = node
        self._out_edges[node.id] = []
        self._in_edges[node.id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        """Adds a GraphEdge to the graph container.

        Args:
            edge: GraphEdge model instance.

        Raises:
            GraphError: If edge ID exists or if source/target node IDs are not present in graph.
        """
        if edge.id in self._edges:
            raise GraphError(f"Duplicate edge ID '{edge.id}' already exists in graph.")

        if edge.source not in self._nodes:
            raise GraphError(f"Cannot add edge '{edge.id}': Source node '{edge.source}' not found in graph.")

        if edge.target not in self._nodes:
            raise GraphError(f"Cannot add edge '{edge.id}': Target node '{edge.target}' not found in graph.")

        self._edges[edge.id] = edge
        self._out_edges[edge.source].append(edge)
        self._in_edges[edge.target].append(edge)

    def get_node(self, node_id: str) -> GraphNode | None:
        """Retrieves a node by its ID.

        Args:
            node_id: Node unique identifier string.

        Returns:
            GraphNode instance if present, None otherwise.
        """
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        """Retrieves an edge by its ID.

        Args:
            edge_id: Edge unique identifier string.

        Returns:
            GraphEdge instance if present, None otherwise.
        """
        return self._edges.get(edge_id)

    def get_edges(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        edge_type: EdgeType | None = None,
    ) -> list[GraphEdge]:
        """Queries edges filtered by source node ID, target node ID, and/or edge relationship type.

        Args:
            source_id: Optional source node ID filter.
            target_id: Optional target node ID filter.
            edge_type: Optional EdgeType filter.

        Returns:
            Filtered list of GraphEdge instances in deterministic insertion order.
        """
        if source_id is not None and source_id in self._out_edges:
            candidates = self._out_edges[source_id]
        elif target_id is not None and target_id in self._in_edges:
            candidates = self._in_edges[target_id]
        else:
            candidates = list(self._edges.values())

        filtered: list[GraphEdge] = []
        for edge in candidates:
            if source_id is not None and edge.source != source_id:
                continue
            if target_id is not None and edge.target != target_id:
                continue
            if edge_type is not None and edge.type != edge_type:
                continue
            filtered.append(edge)

        return filtered

    def node_count(self) -> int:
        """Returns total node count."""
        return len(self._nodes)

    def edge_count(self) -> int:
        """Returns total edge count."""
        return len(self._edges)

    @property
    def nodes(self) -> list[GraphNode]:
        """Returns list of all nodes in deterministic insertion order."""
        return list(self._nodes.values())

    @property
    def edges(self) -> list[GraphEdge]:
        """Returns list of all edges in deterministic insertion order."""
        return list(self._edges.values())
