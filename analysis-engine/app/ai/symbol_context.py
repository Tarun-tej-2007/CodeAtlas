"""Symbol Context Builder module.

Constructs AI-ready contexts for codebase symbols, resolving dependencies,
exports, layer assignments, and call relationships.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import hashlib

from app.semantic.project_models import ProjectSymbol
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.graph import DependencyGraph
from app.graph.enums import DependencyEdgeType
from app.architecture.models import ArchitectureAnalysisResult

from app.ai.enums import ContextPriority, ContextType, SummaryGranularity
from app.ai.context_builder import AIContextBuilder
from app.ai.models import ContextSection, SymbolContext, AIContextResult


class SymbolContextBuilder(AIContextBuilder):
    """Stateless builder that constructs detailed context for individual or all codebase symbols."""

    def build_context(
        self,
        target_symbol_id: Optional[str] = None,
        linked_result: Optional[LinkedSemanticResult] = None,
        graph: Optional[DependencyGraph] = None,
        arch_result: Optional[ArchitectureAnalysisResult] = None,
        *args,
        **kwargs,
    ) -> AIContextResult:
        """Constructs an AIContextResult containing a structured summary of symbols.

        This method is stateless, thread-safe, and executes in O(V + E) time.
        """
        diagnostics: List[str] = ["Started symbol context build."]

        # 1. Resolve symbols to process
        symbols_to_process: List[ProjectSymbol] = []
        if linked_result and linked_result.symbol_index:
            if target_symbol_id:
                sym = linked_result.symbol_index.get_symbol_by_id(target_symbol_id)
                if sym:
                    symbols_to_process.append(sym)
                else:
                    diagnostics.append(f"Target symbol ID '{target_symbol_id}' not found in index.")
            else:
                # Process all registered symbols
                for file_path, file_symbols in linked_result.symbol_index._by_file.items():
                    symbols_to_process.extend(file_symbols)

        # 2. Build lookup cache maps in O(V + E) to ensure O(1) matching during iteration
        exported_ids: Set[str] = set()
        if linked_result and linked_result.symbol_index:
            exported_ids = {
                sym.id for sym in linked_result.symbol_index.get_exported_symbols()
            }

        # Imports lookup map
        import_usages: Dict[str, List[str]] = {}
        if linked_result and linked_result.import_export_result:
            for ri in linked_result.import_export_result.resolved_imports:
                target_id = ri.target_symbol.id
                importing_file = Path(ri.import_declaration.location.file_path).as_posix()
                if target_id not in import_usages:
                    import_usages[target_id] = []
                import_usages[target_id].append(importing_file)

        # Graph dependencies and calls maps
        usages_in: Dict[str, List[str]] = {}
        usages_out: Dict[str, List[str]] = {}
        calls_in: Dict[str, List[str]] = {}
        calls_out: Dict[str, List[str]] = {}

        if graph:
            for edge in graph.edges:
                src = edge.source_id
                tgt = edge.target_id
                if edge.type == DependencyEdgeType.CALLS:
                    calls_out.setdefault(src, []).append(tgt)
                    calls_in.setdefault(tgt, []).append(src)
                else:
                    usages_out.setdefault(src, []).append(tgt)
                    usages_in.setdefault(tgt, []).append(src)

        # Architectural layer mapping
        node_to_layer: Dict[str, str] = {}
        if arch_result:
            for layer in arch_result.layers:
                for node_id in layer.node_ids:
                    node_to_layer[node_id] = layer.id

        # Architectural issues/diagnostics mapping
        symbol_diagnostics: Dict[str, List[str]] = {}
        if arch_result:
            for issue in arch_result.issues:
                if issue.location:
                    symbol_diagnostics.setdefault(issue.location, []).append(
                        f"[{issue.severity.upper()}] {issue.title}: {issue.description}"
                    )

        # 3. Process matching symbols
        symbol_contexts: List[SymbolContext] = []
        sections: List[ContextSection] = []

        for symbol in symbols_to_process:
            sid = symbol.id

            # Gather incoming and outgoing links
            deps_out = list(set(usages_out.get(sid, [])))
            deps_in = list(set(usages_in.get(sid, [])))
            c_out = list(set(calls_out.get(sid, [])))
            c_in = list(set(calls_in.get(sid, [])))

            # Export/Import details
            is_exported = sid in exported_ids
            imp_files = import_usages.get(sid, [])

            # Layer assignment
            layer_id = node_to_layer.get(sid, "none")

            # Diagnostics
            issues_list = symbol_diagnostics.get(sid, [])

            # Definition summary
            start_l = symbol.location.location.start_line
            start_c = symbol.location.location.start_column
            end_l = symbol.location.location.end_line
            end_c = symbol.location.location.end_column
            def_range = f"L{start_l}:{start_c}-L{end_l}:{end_c}"

            def_summary = (
                f"Symbol '{symbol.name}' (kind: {symbol.kind.value}) defined in "
                f"'{Path(symbol.location.file_path).as_posix()}' at range {def_range}."
            )

            # Metadata tags
            metadata = {
                "name": symbol.name,
                "source_file": Path(symbol.location.file_path).as_posix(),
                "source_location": def_range,
                "exported_status": "true" if is_exported else "false",
                "imported_usages": ", ".join(sorted(imp_files)),
                "calls_in": ", ".join(sorted(c_in)),
                "calls_out": ", ".join(sorted(c_out)),
                "architecture_layer": layer_id,
                "diagnostics": "; ".join(issues_list),
            }

            # Combine all dependencies (usages + calls)
            all_dependencies = sorted(list(set(deps_out + c_out)))
            all_dependents = sorted(list(set(deps_in + c_in)))

            sym_context = SymbolContext(
                symbol_id=sid,
                qualified_name=symbol.qualified_name,
                kind=symbol.kind.value,
                definition_summary=def_summary,
                dependencies=all_dependencies,
                dependents=all_dependents,
                metadata=metadata,
            )
            symbol_contexts.append(sym_context)

            # Generate descriptive text paragraph section
            sec_lines = [
                f"Symbol Qualified Path: {symbol.qualified_name}",
                f"Kind: {symbol.kind.value}",
                f"Location: {metadata['source_file']} ({def_range})",
                f"Architectural Layer: {layer_id}",
                f"Exported: {metadata['exported_status']}",
            ]
            if imp_files:
                sec_lines.append(f"Imported by files: {', '.join(sorted(imp_files))}")
            if all_dependencies:
                sec_lines.append(f"Outgoing Dependencies: {', '.join(all_dependencies)}")
            if all_dependents:
                sec_lines.append(f"Incoming Dependents: {', '.join(all_dependents)}")
            if issues_list:
                sec_lines.append(f"Structural Warnings/Diagnostics:\n  - " + "\n  - ".join(issues_list))

            sections.append(
                ContextSection(
                    id=f"symbol-context-{sid}",
                    title=f"Symbol Context: {symbol.qualified_name}",
                    content="\n".join(sec_lines),
                    priority=ContextPriority.HIGH if is_exported else ContextPriority.MEDIUM,
                )
            )

        # Sort results deterministically by symbol qualified name
        symbol_contexts.sort(key=lambda x: x.qualified_name)
        sections.sort(key=lambda x: x.id)

        # Generate a deterministic stable ID for this run using MD5 hash of sections content
        sections_str = "".join(s.content for s in sections)
        run_hash = hashlib.md5(sections_str.encode("utf-8")).hexdigest()[:12]
        run_id = f"symbol-context-run-{run_hash}"

        diagnostics.append(
            f"Successfully built symbol context. Processed={len(symbol_contexts)} symbols."
        )

        return AIContextResult(
            id=run_id,
            context_type=ContextType.SYMBOL,
            granularity=SummaryGranularity.DETAILED,
            sections=sections,
            symbols=symbol_contexts,
            repository=None,
            diagnostics=diagnostics,
            metadata={},
        )
