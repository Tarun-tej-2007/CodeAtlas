"""Graph query engine module.

Provides GraphQueryEngine for high-level O(1) and O(out_degree) querying and traversal
over a CodeAtlas Graph instance.
"""

from typing import Any
from app.graph.enums import EdgeType, NodeType
from app.graph.graph import Graph
from app.graph.models import GraphEdge, GraphNode
from app.graph.query.exceptions import GraphQueryError
from app.graph.query.filters import filter_edges, filter_nodes


class GraphQueryEngine:
    """High-level query engine providing O(1) and adjacency traversal APIs over a Graph container."""

    def __init__(self, graph: Graph) -> None:
        """Initializes GraphQueryEngine with a Graph instance.

        Args:
            graph: Canonical Graph container instance.

        Raises:
            GraphQueryError: If graph is None or invalid.
        """
        if not isinstance(graph, Graph):
            raise GraphQueryError(f"Invalid graph instance provided to GraphQueryEngine: {type(graph)}")
        self.graph = graph

    # ====================================================
    # NODE QUERIES
    # ====================================================

    def get_node(self, node_id: str) -> GraphNode:
        """Retrieves a GraphNode by ID.

        Args:
            node_id: Node unique identifier string.

        Returns:
            GraphNode model.

        Raises:
            GraphQueryError: If node_id is missing or not found in graph.
        """
        if not node_id:
            raise GraphQueryError("node_id must be a non-empty string.")
        node = self.graph.get_node(node_id)
        if node is None:
            raise GraphQueryError(f"Node '{node_id}' not found in graph.")
        return node

    def get_nodes(self) -> list[GraphNode]:
        """Returns all graph nodes in deterministic insertion order."""
        return self.graph.nodes

    def get_nodes_by_type(self, node_type: NodeType) -> list[GraphNode]:
        """Returns all graph nodes matching the specified NodeType."""
        return filter_nodes(self.graph.nodes, node_type=node_type)

    def find_node_by_name(self, name: str) -> GraphNode | None:
        """Finds the first graph node matching the specified entity name."""
        matches = filter_nodes(self.graph.nodes, name=name)
        return matches[0] if matches else None

    def find_nodes_by_name(self, name: str) -> list[GraphNode]:
        """Finds all graph nodes matching the specified entity name."""
        return filter_nodes(self.graph.nodes, name=name)

    # ====================================================
    # EDGE QUERIES
    # ====================================================

    def get_edges(self) -> list[GraphEdge]:
        """Returns all graph edges in deterministic insertion order."""
        return self.graph.edges

    def get_edges_by_type(self, edge_type: EdgeType) -> list[GraphEdge]:
        """Returns all graph edges matching the specified EdgeType."""
        return filter_edges(self.graph.edges, edge_type=edge_type)

    def get_outgoing_edges(self, node_id: str) -> list[GraphEdge]:
        """Returns all outgoing edges from node_id in O(out_degree) time.

        Raises:
            GraphQueryError: If node_id is not found in graph.
        """
        self.get_node(node_id)  # Validate node existence
        return self.graph.get_edges(source_id=node_id)

    def get_incoming_edges(self, node_id: str) -> list[GraphEdge]:
        """Returns all incoming edges to node_id in O(in_degree) time.

        Raises:
            GraphQueryError: If node_id is not found in graph.
        """
        self.get_node(node_id)  # Validate node existence
        return self.graph.get_edges(target_id=node_id)

    # ====================================================
    # TRAVERSAL
    # ====================================================

    def successors(self, node_id: str) -> list[GraphNode]:
        """Returns target nodes of all outgoing edges from node_id."""
        out_edges = self.get_outgoing_edges(node_id)
        visited_ids: set[str] = set()
        result: list[GraphNode] = []
        for edge in out_edges:
            if edge.target not in visited_ids:
                visited_ids.add(edge.target)
                target_node = self.graph.get_node(edge.target)
                if target_node:
                    result.append(target_node)
        return result

    def predecessors(self, node_id: str) -> list[GraphNode]:
        """Returns source nodes of all incoming edges to node_id."""
        in_edges = self.get_incoming_edges(node_id)
        visited_ids: set[str] = set()
        result: list[GraphNode] = []
        for edge in in_edges:
            if edge.source not in visited_ids:
                visited_ids.add(edge.source)
                source_node = self.graph.get_node(edge.source)
                if source_node:
                    result.append(source_node)
        return result

    def neighbors(self, node_id: str) -> list[GraphNode]:
        """Returns all adjacent nodes (predecessors and successors) without duplicates."""
        visited_ids: set[str] = set()
        result: list[GraphNode] = []
        for node in self.predecessors(node_id) + self.successors(node_id):
            if node.id not in visited_ids:
                visited_ids.add(node.id)
                result.append(node)
        return result

    def parents(self, node_id: str) -> list[GraphNode]:
        """Returns nodes pointing to node_id via CONTAINS, DECLARES, or OWNS edges."""
        in_edges = self.get_incoming_edges(node_id)
        struct_types = (EdgeType.CONTAINS, EdgeType.DECLARES, EdgeType.OWNS)
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in in_edges:
            if edge.type in struct_types and edge.source not in visited_ids:
                visited_ids.add(edge.source)
                source_node = self.graph.get_node(edge.source)
                if source_node:
                    result.append(source_node)
        return result

    def children(self, node_id: str) -> list[GraphNode]:
        """Returns nodes pointed to by node_id via CONTAINS, DECLARES, or OWNS edges."""
        out_edges = self.get_outgoing_edges(node_id)
        struct_types = (EdgeType.CONTAINS, EdgeType.DECLARES, EdgeType.OWNS)
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in out_edges:
            if edge.type in struct_types and edge.target not in visited_ids:
                visited_ids.add(edge.target)
                target_node = self.graph.get_node(edge.target)
                if target_node:
                    result.append(target_node)
        return result

    # ====================================================
    # STRUCTURAL HELPERS
    # ====================================================

    def get_file_symbols(self, file_node_id: str) -> list[GraphNode]:
        """Returns all symbol nodes declared directly or recursively in the specified file."""
        return [
            child for child in self.children(file_node_id)
            if child.type not in (NodeType.FILE, NodeType.PROJECT)
        ]

    def get_module_symbols(self, module_node_id: str) -> list[GraphNode]:
        """Returns symbol nodes declared in the specified module."""
        return self.children(module_node_id)

    def get_class_members(self, class_node_id: str) -> list[GraphNode]:
        """Returns member nodes (methods, properties, etc.) declared in the specified class."""
        return [
            child for child in self.children(class_node_id)
            if child.type in (NodeType.METHOD, NodeType.PROPERTY, NodeType.VARIABLE, NodeType.FUNCTION)
        ]

    def get_function_parameters(self, function_node_id: str) -> list[GraphNode]:
        """Returns parameter nodes owned by the specified function or method."""
        return [
            child for child in self.children(function_node_id)
            if child.type == NodeType.PARAMETER
        ]

    # ====================================================
    # BEHAVIORAL HELPERS
    # ====================================================

    def get_callers(self, symbol_id: str) -> list[GraphNode]:
        """Returns caller nodes that invoke symbol_id via CALLS edges."""
        in_edges = self.get_incoming_edges(symbol_id)
        call_edges = [e for e in in_edges if e.type == EdgeType.CALLS]
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in call_edges:
            if edge.source not in visited_ids:
                visited_ids.add(edge.source)
                caller = self.graph.get_node(edge.source)
                if caller:
                    result.append(caller)
        return result

    def get_callees(self, symbol_id: str) -> list[GraphNode]:
        """Returns callee nodes invoked by symbol_id via CALLS edges."""
        out_edges = self.get_outgoing_edges(symbol_id)
        call_edges = [e for e in out_edges if e.type == EdgeType.CALLS]
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in call_edges:
            if edge.target not in visited_ids:
                visited_ids.add(edge.target)
                callee = self.graph.get_node(edge.target)
                if callee:
                    result.append(callee)
        return result

    # ====================================================
    # DEPENDENCY HELPERS
    # ====================================================

    def get_imports(self, module_id: str) -> list[GraphNode]:
        """Returns target nodes/modules imported by module_id via IMPORTS edges."""
        out_edges = self.get_outgoing_edges(module_id)
        import_edges = [e for e in out_edges if e.type == EdgeType.IMPORTS]
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in import_edges:
            if edge.target not in visited_ids:
                visited_ids.add(edge.target)
                imp_node = self.graph.get_node(edge.target)
                if imp_node:
                    result.append(imp_node)
        return result

    def get_exports(self, module_id: str) -> list[GraphNode]:
        """Returns target nodes exported by module_id via EXPORTS edges."""
        out_edges = self.get_outgoing_edges(module_id)
        export_edges = [e for e in out_edges if e.type == EdgeType.EXPORTS]
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in export_edges:
            if edge.target not in visited_ids:
                visited_ids.add(edge.target)
                exp_node = self.graph.get_node(edge.target)
                if exp_node:
                    result.append(exp_node)
        return result

    def get_dependencies(self, module_id: str) -> list[GraphNode]:
        """Returns target nodes/modules depended on by module_id via DEPENDS_ON or IMPORTS edges."""
        out_edges = self.get_outgoing_edges(module_id)
        dep_edges = [e for e in out_edges if e.type in (EdgeType.DEPENDS_ON, EdgeType.IMPORTS)]
        result: list[GraphNode] = []
        visited_ids: set[str] = set()

        for edge in dep_edges:
            if edge.target not in visited_ids:
                visited_ids.add(edge.target)
                target_node = self.graph.get_node(edge.target)
                if target_node:
                    result.append(target_node)
        return result
