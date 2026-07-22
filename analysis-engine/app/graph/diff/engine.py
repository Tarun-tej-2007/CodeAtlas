"""Graph diff engine module.

Computes changes between two RepositoryGraph instances.
"""

from app.graph.graph import Graph
from app.graph.diff.exceptions import InvalidGraphComparison
from app.graph.diff.models import (
    EdgeAdded,
    EdgeRemoved,
    EdgeUpdated,
    GraphDiff,
    NodeAdded,
    NodeRemoved,
    NodeUpdated,
)


class GraphDiffEngine:
    """Computes the difference between two codebase graphs and returns a GraphDiff."""

    @staticmethod
    def diff(old_graph: Graph, new_graph: Graph) -> GraphDiff:
        """Compares old_graph and new_graph, returns a sorted GraphDiff change set.

        Args:
            old_graph: Old state of the codebase Graph.
            new_graph: New state of the codebase Graph.

        Returns:
            A GraphDiff object describing the changes.

        Raises:
            InvalidGraphComparison: If either graph is invalid or comparison cannot be performed.
        """
        if old_graph is None or new_graph is None:
            raise InvalidGraphComparison("Input graphs for diff comparison cannot be None.")

        if not isinstance(old_graph, Graph) or not isinstance(new_graph, Graph):
            raise InvalidGraphComparison("Inputs must be instances of Graph.")

        # 1. Compare Nodes
        old_nodes = {node.id: node for node in old_graph.nodes}
        new_nodes = {node.id: node for node in new_graph.nodes}

        nodes_added: list[NodeAdded] = []
        nodes_removed: list[NodeRemoved] = []
        nodes_updated: list[NodeUpdated] = []

        # Find added and updated nodes
        for node_id, new_node in new_nodes.items():
            if node_id not in old_nodes:
                nodes_added.append(NodeAdded(id=node_id, node=new_node))
            else:
                old_node = old_nodes[node_id]
                if old_node != new_node:
                    nodes_updated.append(NodeUpdated(id=node_id, old_node=old_node, new_node=new_node))

        # Find removed nodes
        for node_id, old_node in old_nodes.items():
            if node_id not in new_nodes:
                nodes_removed.append(NodeRemoved(id=node_id, node=old_node))

        # 2. Compare Edges
        old_edges = {edge.id: edge for edge in old_graph.edges}
        new_edges = {edge.id: edge for edge in new_graph.edges}

        edges_added: list[EdgeAdded] = []
        edges_removed: list[EdgeRemoved] = []
        edges_updated: list[EdgeUpdated] = []

        # Find added and updated edges
        for edge_id, new_edge in new_edges.items():
            if edge_id not in old_edges:
                edges_added.append(EdgeAdded(id=edge_id, edge=new_edge))
            else:
                old_edge = old_edges[edge_id]
                if old_edge != new_edge:
                    edges_updated.append(EdgeUpdated(id=edge_id, old_edge=old_edge, new_edge=new_edge))

        # Find removed edges
        for edge_id, old_edge in old_edges.items():
            if edge_id not in new_edges:
                edges_removed.append(EdgeRemoved(id=edge_id, edge=old_edge))

        # Sort changes deterministically by ID to ensure stable comparisons
        nodes_added.sort(key=lambda x: x.id)
        nodes_removed.sort(key=lambda x: x.id)
        nodes_updated.sort(key=lambda x: x.id)
        edges_added.sort(key=lambda x: x.id)
        edges_removed.sort(key=lambda x: x.id)
        edges_updated.sort(key=lambda x: x.id)

        return GraphDiff(
            nodes_added=tuple(nodes_added),
            nodes_removed=tuple(nodes_removed),
            nodes_updated=tuple(nodes_updated),
            edges_added=tuple(edges_added),
            edges_removed=tuple(edges_removed),
            edges_updated=tuple(edges_updated),
        )
