"""Symbol graph builder module.

Provides SymbolGraphBuilder for converting semantic AnalysisContext objects into a
structural codebase graph containing project, file, and symbol declaration hierarchy nodes.
"""

from typing import Any
from app.analyzer.models import AnalysisContext
from app.graph.builder import BaseGraphBuilder
from app.graph.enums import EdgeType, NodeType
from app.graph.exceptions import GraphBuilderError, GraphError
from app.graph.graph import Graph
from app.graph.models import GraphEdge, GraphMetadata, GraphNode
from app.parser.symbols.models import SymbolKind


SYMBOL_KIND_TO_NODE_TYPE: dict[SymbolKind, NodeType] = {
    SymbolKind.FUNCTION: NodeType.FUNCTION,
    SymbolKind.CLASS: NodeType.CLASS,
    SymbolKind.METHOD: NodeType.METHOD,
    SymbolKind.VARIABLE: NodeType.VARIABLE,
    SymbolKind.INTERFACE: NodeType.INTERFACE,
    SymbolKind.TYPE_ALIAS: NodeType.INTERFACE,
    SymbolKind.ENUM: NodeType.ENUM,
    SymbolKind.NAMESPACE: NodeType.MODULE,
    SymbolKind.UNKNOWN: NodeType.VARIABLE,
}


class SymbolGraphBuilder(BaseGraphBuilder):
    """Builder converting AnalysisContext semantic models into a structural symbol graph."""

    def __init__(self, project_name: str = "CodeAtlas") -> None:
        """Initializes SymbolGraphBuilder.

        Args:
            project_name: Name of the project or repository.
        """
        self.project_name = project_name

    def build(self, context: AnalysisContext | list[AnalysisContext] | Any) -> Graph:
        """Builds a structural Symbol Graph from one or multiple AnalysisContext objects.

        Args:
            context: Single AnalysisContext or list of AnalysisContext objects.

        Returns:
            A populated Graph container.

        Raises:
            GraphBuilderError: If context is invalid or graph building fails.
        """
        try:
            contexts: list[AnalysisContext] = []
            if isinstance(context, AnalysisContext):
                contexts = [context]
            elif isinstance(context, (list, tuple)):
                contexts = list(context)
            else:
                raise GraphBuilderError(f"Invalid context type provided to SymbolGraphBuilder: {type(context)}")

            graph = Graph(metadata=GraphMetadata(project_name=self.project_name))

            # 1. Root Project Node
            project_node_id = f"project_{self.project_name.lower().replace(' ', '_')}"
            project_node = GraphNode(
                id=project_node_id,
                type=NodeType.PROJECT,
                name=self.project_name,
            )
            graph.add_node(project_node)

            # Track added nodes and edges to prevent duplicates
            added_node_ids: set[str] = {project_node_id}
            added_edge_ids: set[str] = set()

            # 2. Process each AnalysisContext
            for ctx in contexts:
                if not ctx or not ctx.ast_document:
                    continue

                doc = ctx.ast_document
                file_node_id = f"file_{str(doc.relative_path).replace('/', '_').replace('.', '_').replace('\\', '_')}"

                # Create FILE Node
                if file_node_id not in added_node_ids:
                    file_node = GraphNode(
                        id=file_node_id,
                        type=NodeType.FILE,
                        name=doc.path.name,
                        path=doc.path,
                    )
                    graph.add_node(file_node)
                    added_node_ids.add(file_node_id)

                # Edge: PROJECT -> CONTAINS -> FILE
                contains_edge_id = f"edge_contains_{project_node_id}_{file_node_id}"
                if contains_edge_id not in added_edge_ids:
                    contains_edge = GraphEdge(
                        id=contains_edge_id,
                        source=project_node_id,
                        target=file_node_id,
                        type=EdgeType.CONTAINS,
                    )
                    graph.add_edge(contains_edge)
                    added_edge_ids.add(contains_edge_id)

                # Process Symbols in SymbolTable
                if not ctx.symbol_table or not ctx.symbol_table.symbols:
                    continue

                # First pass: Add all Symbol nodes
                for symbol in ctx.symbol_table.symbols:
                    if symbol.id not in added_node_ids:
                        node_type = SYMBOL_KIND_TO_NODE_TYPE.get(symbol.kind, NodeType.VARIABLE)
                        symbol_node = GraphNode(
                            id=symbol.id,
                            type=node_type,
                            name=symbol.name,
                            path=symbol.path,
                            line=symbol.start_line,
                        )
                        graph.add_node(symbol_node)
                        added_node_ids.add(symbol.id)

                # Second pass: Add structural ownership/declaration edges
                for symbol in ctx.symbol_table.symbols:
                    if symbol.parent_symbol_id is None or symbol.parent_symbol_id not in added_node_ids:
                        # Top-level symbol declared in FILE
                        decl_edge_id = f"edge_declares_{file_node_id}_{symbol.id}"
                        if decl_edge_id not in added_edge_ids:
                            decl_edge = GraphEdge(
                                id=decl_edge_id,
                                source=file_node_id,
                                target=symbol.id,
                                type=EdgeType.DECLARES,
                            )
                            graph.add_edge(decl_edge)
                            added_edge_ids.add(decl_edge_id)
                    else:
                        # Nested symbol declared or owned by parent symbol
                        parent_node = graph.get_node(symbol.parent_symbol_id)
                        edge_type = EdgeType.DECLARES
                        if parent_node and parent_node.type in (NodeType.FUNCTION, NodeType.METHOD):
                            edge_type = EdgeType.OWNS

                        struct_edge_id = f"edge_{edge_type.value}_{symbol.parent_symbol_id}_{symbol.id}"
                        if struct_edge_id not in added_edge_ids:
                            struct_edge = GraphEdge(
                                id=struct_edge_id,
                                source=symbol.parent_symbol_id,
                                target=symbol.id,
                                type=edge_type,
                            )
                            graph.add_edge(struct_edge)
                            added_edge_ids.add(struct_edge_id)

            return graph
        except GraphError as err:
            raise GraphBuilderError(f"Symbol graph construction failed: {err}") from err
        except GraphBuilderError:
            raise
        except Exception as err:
            raise GraphBuilderError(f"Failed to build symbol graph: {err}") from err
