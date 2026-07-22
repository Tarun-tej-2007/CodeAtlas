"""Visualization transformer module.

Converts a codebase RepositoryGraph into a renderable VisualizationGraph.
"""

from typing import Any
from app.graph import Graph as RepositoryGraph
from app.graph.enums import NodeType, EdgeType
from app.visualization.enums import EdgeKind, LayoutKind, NodeKind
from app.visualization.exceptions import TransformationError
from app.visualization.models import (
    Position,
    VisualizationEdge,
    VisualizationGraph,
    VisualizationMetadata,
    VisualizationNode,
)
from app.visualization.styles import EdgeStyle, NodeStyle


# Node type mappings from Graph NodeType to Visualization NodeKind
NODE_TYPE_MAPPING: dict[NodeType, NodeKind] = {
    NodeType.MODULE: NodeKind.MODULE,
    NodeType.CLASS: NodeKind.CLASS,
    NodeType.FUNCTION: NodeKind.FUNCTION,
    NodeType.METHOD: NodeKind.METHOD,
    NodeType.VARIABLE: NodeKind.VARIABLE,
    NodeType.PARAMETER: NodeKind.VARIABLE,
    NodeType.PROPERTY: NodeKind.VARIABLE,
    NodeType.PACKAGE: NodeKind.PACKAGE,
    NodeType.INTERFACE: NodeKind.INTERFACE,
    NodeType.ENUM: NodeKind.ENUM,
    NodeType.FILE: NodeKind.UNKNOWN,
    NodeType.PROJECT: NodeKind.UNKNOWN,
    NodeType.IMPORT: NodeKind.UNKNOWN,
    NodeType.EXPORT: NodeKind.UNKNOWN,
}

# Edge type mappings from Graph EdgeType to Visualization EdgeKind
EDGE_TYPE_MAPPING: dict[EdgeType, EdgeKind] = {
    EdgeType.CALLS: EdgeKind.CALL,
    EdgeType.IMPORTS: EdgeKind.IMPORT,
    EdgeType.EXPORTS: EdgeKind.IMPORT,
    EdgeType.DEPENDS_ON: EdgeKind.REFERENCE,
    EdgeType.REFERENCES: EdgeKind.REFERENCE,
    EdgeType.DECLARES: EdgeKind.CONTAINS,
    EdgeType.OWNS: EdgeKind.CONTAINS,
    EdgeType.CONTAINS: EdgeKind.CONTAINS,
}


class VisualizationTransformer:
    """Transformer for converting codebase graphs to visualization models."""

    def transform(self, repository_graph: RepositoryGraph) -> VisualizationGraph:
        """Transforms a RepositoryGraph into an immutable VisualizationGraph.

        Args:
            repository_graph: Input RepositoryGraph.

        Returns:
            An immutable VisualizationGraph.

        Raises:
            TransformationError: If the transformation fails.
        """
        try:
            if repository_graph is None:
                raise TransformationError("Repository graph cannot be None.")

            # Transform nodes
            viz_nodes: list[VisualizationNode] = []
            for node in repository_graph.nodes:
                try:
                    kind = NODE_TYPE_MAPPING.get(node.type, NodeKind.UNKNOWN)
                    viz_node = VisualizationNode(
                        id=node.id,
                        label=node.name,
                        kind=kind,
                        position=None,
                        style=NodeStyle(),
                        metadata=node.metadata.copy() if node.metadata else {},
                    )
                    viz_nodes.append(viz_node)
                except Exception as exc:
                    raise TransformationError(f"Failed to transform node '{node.id}': {exc}") from exc

            # Transform edges
            viz_edges: list[VisualizationEdge] = []
            for edge in repository_graph.edges:
                try:
                    kind = EDGE_TYPE_MAPPING.get(edge.type, EdgeKind.REFERENCE)
                    viz_edge = VisualizationEdge(
                        id=edge.id,
                        source=edge.source,
                        target=edge.target,
                        kind=kind,
                        style=EdgeStyle(),
                        metadata=edge.metadata.copy() if edge.metadata else {},
                    )
                    viz_edges.append(viz_edge)
                except Exception as exc:
                    raise TransformationError(f"Failed to transform edge '{edge.id}': {exc}") from exc

            # Generate Metadata
            metadata = VisualizationMetadata(
                node_count=len(viz_nodes),
                edge_count=len(viz_edges),
                group_count=0,
                layout=LayoutKind.NONE,
                graph_version="1.0",
            )

            # Return aggregate VisualizationGraph
            return VisualizationGraph(
                nodes=tuple(viz_nodes),
                edges=tuple(viz_edges),
                groups=(),
                metadata=metadata,
            )

        except TransformationError:
            raise
        except Exception as exc:
            raise TransformationError(f"Unexpected error during graph transformation: {exc}") from exc
