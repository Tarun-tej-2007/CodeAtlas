"""AI Context Lookup Cache module.

Implements an execution-scoped lookup cache that indexes symbols, import/export
maps, graph connections, and architectural layers to optimize context builders.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path

from app.semantic.linking_pipeline import LinkedSemanticResult
from app.graph import DependencyGraph
from app.graph.enums import DependencyEdgeType
from app.architecture.models import ArchitectureAnalysisResult


class ContextLookupCache:
    """Execution-scoped, immutable-after-init lookup cache.

    Avoids repeated indexing passes across multiple context builders.
    """

    def __init__(
        self,
        linked_result: Optional[LinkedSemanticResult] = None,
        graph: Optional[DependencyGraph] = None,
        arch_result: Optional[ArchitectureAnalysisResult] = None,
    ) -> None:
        """Indexes all relevant structures in a single O(V + E) pass."""
        self.files_list: List[str] = []
        self.languages: Set[str] = set()
        self.symbol_counts: Dict[str, int] = {}
        
        # Graph node/edge stats
        self.graph_node_count: int = len(graph.nodes) if graph else 0
        self.graph_edge_count: int = len(graph.edges) if graph else 0

        # 1. Pre-index Project Files and languages
        active_semantic = linked_result.original_result if linked_result else None
        if active_semantic:
            for path, file_obj in active_semantic.files.items():
                rel_path = Path(path).as_posix()
                self.files_list.append(rel_path)

                ext = path.suffix.lower()
                if ext == ".py":
                    self.languages.add("python")
                elif ext in (".js", ".jsx"):
                    self.languages.add("javascript")
                elif ext in (".ts", ".tsx"):
                    self.languages.add("typescript")
                elif ext:
                    self.languages.add(ext[1:])
                else:
                    self.languages.add("unknown")

                # Count symbol kinds
                for sym in file_obj.symbols:
                    kind_str = str(sym.kind).lower()
                    self.symbol_counts[kind_str] = self.symbol_counts.get(kind_str, 0) + 1

        # 2. Pre-index exported symbols
        self.exported_ids: Set[str] = set()
        if linked_result and linked_result.symbol_index:
            self.exported_ids = {
                sym.id for sym in linked_result.symbol_index.get_exported_symbols()
            }

        # 3. Pre-index imports usage maps
        self.import_usages: Dict[str, List[str]] = {}
        if linked_result and linked_result.import_export_result:
            for ri in linked_result.import_export_result.resolved_imports:
                target_id = ri.target_symbol.id
                importing_file = Path(ri.import_declaration.location.file_path).as_posix()
                if target_id not in self.import_usages:
                    self.import_usages[target_id] = []
                self.import_usages[target_id].append(importing_file)

        # 4. Pre-index graph relationships
        self.usages_in: Dict[str, List[str]] = {}
        self.usages_out: Dict[str, List[str]] = {}
        self.calls_in: Dict[str, List[str]] = {}
        self.calls_out: Dict[str, List[str]] = {}

        if graph:
            for edge in graph.edges:
                src = edge.source_id
                tgt = edge.target_id
                if edge.type == DependencyEdgeType.CALLS:
                    self.calls_out.setdefault(src, []).append(tgt)
                    self.calls_in.setdefault(tgt, []).append(src)
                else:
                    self.usages_out.setdefault(src, []).append(tgt)
                    self.usages_in.setdefault(tgt, []).append(src)

        # 5. Pre-index architecture layers
        self.node_to_layer: Dict[str, str] = {}
        if arch_result:
            for layer in arch_result.layers:
                for node_id in layer.node_ids:
                    self.node_to_layer[node_id] = layer.id

        # 6. Pre-index architecture diagnostics
        self.symbol_diagnostics: Dict[str, List[str]] = {}
        if arch_result:
            for issue in arch_result.issues:
                if issue.location:
                    self.symbol_diagnostics.setdefault(issue.location, []).append(
                        f"[{issue.severity.upper()}] {issue.title}: {issue.description}"
                    )
