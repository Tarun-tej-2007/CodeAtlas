"""Graph query filters module.

Provides reusable helper functions for filtering lists of GraphNode and GraphEdge objects.
"""

from pathlib import Path
from typing import Any
from app.graph.enums import EdgeType, NodeType
from app.graph.models import GraphEdge, GraphNode


def filter_nodes(
    nodes: list[GraphNode],
    node_type: NodeType | None = None,
    name: str | None = None,
    path: Path | str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> list[GraphNode]:
    """Filters a list of GraphNode objects based on criteria.

    Args:
        nodes: List of GraphNode objects to filter.
        node_type: Optional NodeType filter.
        name: Optional name filter.
        path: Optional Path or path string filter.
        metadata_filters: Optional dictionary of key/value metadata matches.

    Returns:
        Filtered list of GraphNode objects in deterministic order.
    """
    filtered: list[GraphNode] = []
    target_path = str(path) if path is not None else None

    for node in nodes:
        if node_type is not None and node.type != node_type:
            continue
        if name is not None and node.name != name:
            continue
        if target_path is not None and (node.path is None or str(node.path) != target_path):
            continue
        if metadata_filters:
            match = True
            for k, v in metadata_filters.items():
                if k not in node.metadata or node.metadata[k] != v:
                    match = False
                    break
            if not match:
                continue

        filtered.append(node)

    return filtered


def filter_edges(
    edges: list[GraphEdge],
    edge_type: EdgeType | None = None,
    source: str | None = None,
    target: str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> list[GraphEdge]:
    """Filters a list of GraphEdge objects based on criteria.

    Args:
        edges: List of GraphEdge objects to filter.
        edge_type: Optional EdgeType filter.
        source: Optional source node ID filter.
        target: Optional target node ID filter.
        metadata_filters: Optional dictionary of key/value metadata matches.

    Returns:
        Filtered list of GraphEdge objects in deterministic order.
    """
    filtered: list[GraphEdge] = []

    for edge in edges:
        if edge_type is not None and edge.type != edge_type:
            continue
        if source is not None and edge.source != source:
            continue
        if target is not None and edge.target != target:
            continue
        if metadata_filters:
            match = True
            for k, v in metadata_filters.items():
                if k not in edge.metadata or edge.metadata[k] != v:
                    match = False
                    break
            if not match:
                continue

        filtered.append(edge)

    return filtered
