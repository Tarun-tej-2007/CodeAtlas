"""Dependency graph builder module."""

from pathlib import Path
from typing import Dict, List, Set, Tuple

from app.semantic import SymbolKind
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.graph.dependency_models import DependencyMetadata, GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.enums import DependencyEdgeType, DependencyNodeType


class DependencyGraphBuilder:
    """Transforms a LinkedSemanticResult into a validated structural DependencyGraph."""

    def __init__(self) -> None:
        pass

    def _map_symbol_kind(self, kind: SymbolKind) -> DependencyNodeType:
        """Maps a semantic SymbolKind to its corresponding DependencyNodeType."""
        mapping = {
            SymbolKind.CLASS: DependencyNodeType.CLASS,
            SymbolKind.INTERFACE: DependencyNodeType.INTERFACE,
            SymbolKind.ENUM: DependencyNodeType.ENUM,
            SymbolKind.FUNCTION: DependencyNodeType.FUNCTION,
            SymbolKind.METHOD: DependencyNodeType.METHOD,
            SymbolKind.VARIABLE: DependencyNodeType.VARIABLE,
            SymbolKind.MODULE: DependencyNodeType.MODULE,
            SymbolKind.NAMESPACE: DependencyNodeType.MODULE,
        }
        return mapping.get(kind, DependencyNodeType.VARIABLE)

    def build_graph(self, linked_result: LinkedSemanticResult) -> DependencyGraph:
        """Transforms a LinkedSemanticResult into a DependencyGraph.

        Args:
            linked_result: The completed semantic linking context result.

        Returns:
            A verified read-only DependencyGraph.
        """
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        seen_nodes: Set[str] = set()
        seen_edges: Set[Tuple[str, str, str]] = set()

        files = linked_result.original_result.files

        # 1. Generate nodes for files (modules) and their symbols
        for file_path, project_file in files.items():
            # Add MODULE node
            file_id = str(file_path)
            if file_id not in seen_nodes:
                seen_nodes.add(file_id)
                nodes.append(
                    GraphNode(
                        id=file_id,
                        name=file_path.name,
                        type=DependencyNodeType.MODULE,
                        metadata={"path": file_id},
                    )
                )

            # Add symbol nodes
            for symbol in project_file.symbols:
                if symbol.id not in seen_nodes:
                    seen_nodes.add(symbol.id)
                    nodes.append(
                        GraphNode(
                            id=symbol.id,
                            name=symbol.name,
                            type=self._map_symbol_kind(symbol.kind),
                            metadata={"qualified_name": symbol.qualified_name},
                        )
                    )

        # 2. Generate IMPORTS edges from resolved imports
        for resolved_imp in linked_result.import_export_result.resolved_imports:
            source_id = str(resolved_imp.import_declaration.location.file_path)
            target_id = str(resolved_imp.target_file)
            edge_key = (source_id, target_id, DependencyEdgeType.IMPORTS.value)

            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append(
                    GraphEdge(
                        source_id=source_id,
                        target_id=target_id,
                        type=DependencyEdgeType.IMPORTS,
                    )
                )

        # 3. Generate EXPORTS edges from module export declarations
        for file_path, project_file in files.items():
            source_id = str(file_path)
            for export in project_file.exports:
                if export.local_symbol_id:
                    target_id = export.local_symbol_id
                    edge_key = (source_id, target_id, DependencyEdgeType.EXPORTS.value)

                    # Verify target node exists to prevent validation errors
                    if target_id in seen_nodes and edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(
                            GraphEdge(
                                source_id=source_id,
                                target_id=target_id,
                                type=DependencyEdgeType.EXPORTS,
                            )
                        )

        # 4. Generate USAGE edges from resolved cross-file reference usages
        for resolved_ref in linked_result.reference_resolution_result.resolved_references:
            source_id = str(resolved_ref.reference.location.file_path)
            target_id = resolved_ref.target_symbol.id
            edge_key = (source_id, target_id, DependencyEdgeType.USAGE.value)

            if target_id in seen_nodes and edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append(
                    GraphEdge(
                        source_id=source_id,
                        target_id=target_id,
                        type=DependencyEdgeType.USAGE,
                    )
                )

        # 5. Generate descriptive metadata
        metadata = DependencyMetadata(
            description="Structural Dependency Graph Builder Output",
            version="1.0.0",
            attributes={
                "total_files": len(files),
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "diagnostics_count": len(linked_result.diagnostics),
            },
        )

        return DependencyGraph(nodes=nodes, edges=edges, metadata=metadata)
