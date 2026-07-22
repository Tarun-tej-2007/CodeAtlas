"""Hierarchical graph layout engine module.

Provides HierarchicalLayoutEngine for computing level-based DAG visualization layouts.
"""

from typing import Any
from app.visualization.enums import LayoutKind
from app.visualization.layouts.base import BaseLayoutEngine
from app.visualization.layouts.constants import (
    DEFAULT_HORIZONTAL_SPACING,
    DEFAULT_VERTICAL_SPACING,
)
from app.visualization.layouts.exceptions import (
    CyclicLayoutError,
    InvalidLayoutGraph,
    LayoutEngineError,
)
from app.visualization.models import (
    Position,
    VisualizationGraph,
    VisualizationMetadata,
    VisualizationNode,
)


class HierarchicalLayoutEngine(BaseLayoutEngine):
    """Layout engine that assigns deterministic coordinates to nodes in a tree or DAG."""

    def __init__(
        self,
        horizontal_spacing: float = DEFAULT_HORIZONTAL_SPACING,
        vertical_spacing: float = DEFAULT_VERTICAL_SPACING,
    ) -> None:
        """Initializes HierarchicalLayoutEngine.

        Args:
            horizontal_spacing: Horizontal distance between sibling nodes.
            vertical_spacing: Vertical distance between levels.
        """
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing

    def layout(self, graph: VisualizationGraph) -> VisualizationGraph:
        """Computes hierarchical node coordinates for a VisualizationGraph DAG.

        Args:
            graph: Input VisualizationGraph container (must remain unmodified).

        Returns:
            A new VisualizationGraph instance with assigned positions.

        Raises:
            LayoutEngineError: If layout computation fails due to cycles, invalid nodes, or errors.
        """
        try:
            if graph is None:
                raise InvalidLayoutGraph("Input graph cannot be None.")

            if not graph.nodes:
                # Empty graph: return copy directly
                return VisualizationGraph(
                    nodes=(),
                    edges=graph.edges,
                    groups=graph.groups,
                    metadata=VisualizationMetadata(
                        node_count=0,
                        edge_count=len(graph.edges),
                        group_count=len(graph.groups),
                        layout=LayoutKind.NONE,
                    ),
                )

            # Node ID sets
            node_ids = {n.id for n in graph.nodes}
            if len(node_ids) != len(graph.nodes):
                raise InvalidLayoutGraph("Graph contains nodes with duplicate IDs.")

            # Validate edge endpoints
            adj_out: dict[str, list[str]] = {n_id: [] for n_id in node_ids}
            in_degrees: dict[str, int] = {n_id: 0 for n_id in node_ids}

            for edge in graph.edges:
                if edge.source not in node_ids:
                    raise InvalidLayoutGraph(f"Edge '{edge.id}' has missing source node '{edge.source}'.")
                if edge.target not in node_ids:
                    raise InvalidLayoutGraph(f"Edge '{edge.id}' has missing target node '{edge.target}'.")

                adj_out[edge.source].append(edge.target)
                in_degrees[edge.target] += 1

            # Kahn's Algorithm for Topological Sort & Cycle Detection
            top_order: list[str] = []
            # Deterministic initial queue by sorting keys
            queue = [n_id for n_id, deg in sorted(in_degrees.items()) if deg == 0]
            temp_in_degrees = in_degrees.copy()

            while queue:
                # Deterministic pop to keep topological order stable
                curr = queue.pop(0)
                top_order.append(curr)

                for neighbor in sorted(adj_out[curr]):
                    temp_in_degrees[neighbor] -= 1
                    if temp_in_degrees[neighbor] == 0:
                        queue.append(neighbor)

            if len(top_order) < len(graph.nodes):
                raise CyclicLayoutError("Layout failed: Cycle detected in the visualization hierarchy.")

            # Level propagation using topological order
            levels = {n_id: 0 for n_id in node_ids}
            for u in top_order:
                for v in sorted(adj_out[u]):
                    levels[v] = max(levels[v], levels[u] + 1)

            # Group nodes by level
            level_groups: dict[int, list[str]] = {}
            for n_id, level in sorted(levels.items()):
                level_groups.setdefault(level, []).append(n_id)

            # Assign positions
            positions: dict[str, Position] = {}
            for level in sorted(level_groups.keys()):
                # Sort sibling nodes deterministically
                siblings = sorted(level_groups[level])
                for idx, n_id in enumerate(siblings):
                    x = idx * self.horizontal_spacing
                    y = level * self.vertical_spacing
                    positions[n_id] = Position(x=x, y=y)

            # Construct new VisualizationNodes with updated positions
            new_nodes = []
            for node in graph.nodes:
                new_node = VisualizationNode(
                    id=node.id,
                    label=node.label,
                    kind=node.kind,
                    position=positions[node.id],
                    style=node.style,
                    metadata=node.metadata.copy() if node.metadata else {},
                )
                new_nodes.append(new_node)

            # Return aggregate VisualizationGraph with layout metadata
            new_meta = VisualizationMetadata(
                node_count=len(new_nodes),
                edge_count=len(graph.edges),
                group_count=len(graph.groups),
                layout=LayoutKind.HIERARCHICAL,
                graph_version=graph.metadata.graph_version,
            )

            return VisualizationGraph(
                nodes=tuple(new_nodes),
                edges=graph.edges,
                groups=graph.groups,
                metadata=new_meta,
            )

        except (InvalidLayoutGraph, CyclicLayoutError):
            raise
        except Exception as exc:
            raise LayoutEngineError(f"Unexpected error during layout calculation: {exc}") from exc
