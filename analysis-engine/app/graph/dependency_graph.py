"""Dependency graph container model module."""

from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.graph.dependency_models import DependencyMetadata, GraphEdge, GraphNode
from app.graph.exceptions import (
    DuplicateEdgeError,
    DuplicateNodeError,
    GraphValidationError,
)


class DependencyGraph(BaseModel):
    """An immutable, validated dependency graph container."""

    nodes: List[GraphNode] = Field(default_factory=list, description="List of all nodes in the graph.")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of all directed edges in the graph.")
    metadata: DependencyMetadata = Field(
        default_factory=DependencyMetadata, description="Overall graph descriptive metadata."
    )

    model_config = ConfigDict(frozen=True)

    @model_validator(mode='after')
    def _validate_and_index(self) -> 'DependencyGraph':
        """Validates graph constraints and builds read-only index lookups."""
        node_by_id: Dict[str, GraphNode] = {}
        for node in self.nodes:
            if node.id in node_by_id:
                raise DuplicateNodeError(f"Duplicate node ID detected: '{node.id}'")
            node_by_id[node.id] = node

        # Outgoing/Incoming edge mappings
        outgoing: Dict[str, List[GraphEdge]] = {node.id: [] for node in self.nodes}
        incoming: Dict[str, List[GraphEdge]] = {node.id: [] for node in self.nodes}
        seen_edges: Set[Tuple[str, str, str]] = set()

        for edge in self.edges:
            # Integrity checks
            if edge.source_id not in node_by_id:
                raise GraphValidationError(
                    f"Invalid edge source: node '{edge.source_id}' does not exist in the graph."
                )
            if edge.target_id not in node_by_id:
                raise GraphValidationError(
                    f"Invalid edge target: node '{edge.target_id}' does not exist in the graph."
                )

            # Duplicate check (source_id, target_id, type)
            edge_key = (edge.source_id, edge.target_id, edge.type.value)
            if edge_key in seen_edges:
                raise DuplicateEdgeError(
                    f"Duplicate edge detected: '{edge.source_id}' -> '{edge.target_id}' ({edge.type.value})"
                )
            seen_edges.add(edge_key)

            # Map links
            outgoing[edge.source_id].append(edge)
            incoming[edge.target_id].append(edge)

        # Set private index fields inside frozen model using object.__setattr__
        object.__setattr__(self, "_node_by_id", node_by_id)
        object.__setattr__(self, "_outgoing", {k: tuple(v) for k, v in outgoing.items()})
        object.__setattr__(self, "_incoming", {k: tuple(v) for k, v in incoming.items()})

        return self

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Exposes fast lookup of a node by its identifier.

        Args:
            node_id: Unique node identifier.

        Returns:
            The GraphNode instance, or None.
        """
        # Retrieve from private cache
        node_by_id: Dict[str, GraphNode] = getattr(self, "_node_by_id", {})
        return node_by_id.get(node_id)

    def has_node(self, node_id: str) -> bool:
        """Checks if a node ID exists in the graph.

        Args:
            node_id: Unique node identifier.

        Returns:
            True if present, False otherwise.
        """
        node_by_id: Dict[str, GraphNode] = getattr(self, "_node_by_id", {})
        return node_id in node_by_id

    def get_outgoing_edges(self, node_id: str) -> Tuple[GraphEdge, ...]:
        """Exposes outgoing edges originating from a node ID.

        Args:
            node_id: Unique node identifier.

        Returns:
            Tuple of outgoing GraphEdges.
        """
        outgoing_map: Dict[str, Tuple[GraphEdge, ...]] = getattr(self, "_outgoing", {})
        return outgoing_map.get(node_id, ())

    def get_incoming_edges(self, node_id: str) -> Tuple[GraphEdge, ...]:
        """Exposes incoming edges targeting a node ID.

        Args:
            node_id: Unique node identifier.

        Returns:
            Tuple of incoming GraphEdges.
        """
        incoming_map: Dict[str, Tuple[GraphEdge, ...]] = getattr(self, "_incoming", {})
        return incoming_map.get(node_id, ())
