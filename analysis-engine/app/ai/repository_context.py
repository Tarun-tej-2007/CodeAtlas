"""Repository Context Builder module.

Constructs high-level repository summary contexts from semantic results,
dependency graphs, and architectural analysis results.
"""

from typing import Dict, List, Optional
from pathlib import Path
import hashlib

from app.semantic.project_models import ProjectSemanticResult
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.graph import DependencyGraph
from app.architecture.models import ArchitectureAnalysisResult

from app.ai.enums import ContextPriority, ContextType, SummaryGranularity
from app.ai.context_builder import AIContextBuilder
from app.ai.models import ContextSection, RepositoryContext, AIContextResult


class RepositoryContextBuilder(AIContextBuilder):
    """Stateless context builder that summarizes repository properties and structures."""

    def build_context(
        self,
        repo_name: str,
        semantic_result: Optional[ProjectSemanticResult] = None,
        linked_result: Optional[LinkedSemanticResult] = None,
        graph: Optional[DependencyGraph] = None,
        arch_result: Optional[ArchitectureAnalysisResult] = None,
        *args,
        **kwargs,
    ) -> AIContextResult:
        """Constructs an AIContextResult containing a structured summary of the codebase.

        This method is stateless, thread-safe, and executes in O(V + E) time.
        """
        diagnostics: List[str] = ["Started repository context build."]

        # 1. Resolve semantic result input
        active_semantic = semantic_result
        if linked_result and linked_result.original_result:
            active_semantic = linked_result.original_result

        # Gather files and languages
        files_list: List[str] = []
        languages_set = set()
        symbol_counts: Dict[str, int] = {}

        if active_semantic:
            for path, file_obj in active_semantic.files.items():
                rel_path = Path(path).as_posix()
                files_list.append(rel_path)
                
                # Determine language from extension
                ext = path.suffix.lower()
                if ext == ".py":
                    languages_set.add("python")
                elif ext in (".js", ".jsx"):
                    languages_set.add("javascript")
                elif ext in (".ts", ".tsx"):
                    languages_set.add("typescript")
                elif ext:
                    languages_set.add(ext[1:])  # remove dot
                else:
                    languages_set.add("unknown")

                # Count symbol kinds
                for sym in file_obj.symbols:
                    kind_str = str(sym.kind).lower()
                    symbol_counts[kind_str] = symbol_counts.get(kind_str, 0) + 1

        # 2. Gather dependency graph stats
        dep_stats: Dict[str, int] = {}
        if graph:
            node_count = len(graph.nodes)
            edge_count = len(graph.edges)
            dep_stats["node_count"] = node_count
            dep_stats["edge_count"] = edge_count
            # Compute average degree (in + out degree average per node)
            dep_stats["average_degree"] = (
                int((edge_count * 2) / node_count) if node_count > 0 else 0
            )

        # 3. Gather architecture analysis summaries
        arch_stats: Dict[str, str] = {}
        if arch_result:
            arch_stats["layer_count"] = str(len(arch_result.layers))
            arch_stats["issue_count"] = str(len(arch_result.issues))
            
            # Count issues by severity
            sev_counts: Dict[str, int] = {}
            for issue in arch_result.issues:
                sev_str = str(issue.severity).lower()
                sev_counts[sev_str] = sev_counts.get(sev_str, 0) + 1
            for sev, count in sev_counts.items():
                arch_stats[f"issues_{sev}"] = str(count)

        # 4. Generate structured sections
        sections: List[ContextSection] = []

        # Overview section
        overview_lines = [
            f"Repository Name: {repo_name}",
            f"Total Analyzed Files: {len(files_list)}",
            f"Languages Discovered: {', '.join(sorted(languages_set)) if languages_set else 'None'}",
        ]
        if symbol_counts:
            overview_lines.append("\nDeclared Symbol Distribution:")
            for kind, count in sorted(symbol_counts.items()):
                overview_lines.append(f"  - {kind}: {count}")

        sections.append(
            ContextSection(
                id="repo-overview",
                title="Repository Overview & Demographics",
                content="\n".join(overview_lines),
                priority=ContextPriority.HIGH,
            )
        )

        # Graph / Dependency section
        if dep_stats:
            graph_lines = [
                "Structure Statistics:",
                f"  - Total Structural Nodes: {dep_stats['node_count']}",
                f"  - Total Dependency Connections: {dep_stats['edge_count']}",
                f"  - Average Node Connection Degree: {dep_stats['average_degree']}",
            ]
            sections.append(
                ContextSection(
                    id="repo-dependencies",
                    title="Codebase Dependency Topology Summary",
                    content="\n".join(graph_lines),
                    priority=ContextPriority.MEDIUM,
                )
            )

        # Architecture section
        if arch_stats:
            arch_lines = [
                "Layering & Architecture Rules Summary:",
                f"  - Detected Architectural Layers: {arch_stats['layer_count']}",
                f"  - Flagged Design Violations/Issues: {arch_stats['issue_count']}",
            ]
            for key, val in sorted(arch_stats.items()):
                if key.startswith("issues_"):
                    sev_name = key.split("_")[1].capitalize()
                    arch_lines.append(f"    * {sev_name} severity: {val}")

            sections.append(
                ContextSection(
                    id="repo-architecture",
                    title="Architectural Boundary & Smell Summary",
                    content="\n".join(arch_lines),
                    priority=ContextPriority.HIGH,
                )
            )

        # 5. Build RepositoryContext reference DTO
        repo_dto = RepositoryContext(
            repo_name=repo_name,
            description=f"Generated repository summary for {repo_name}.",
            file_paths=sorted(files_list),
            primary_languages=sorted(list(languages_set)),
            metadata={
                "total_symbols": str(sum(symbol_counts.values())),
                "graph_nodes": str(dep_stats.get("node_count", 0)),
                "graph_edges": str(dep_stats.get("edge_count", 0)),
            },
        )

        # Generate a deterministic stable ID for this run using MD5 hash of sections content
        sections_str = "".join(s.content for s in sections)
        run_hash = hashlib.md5(sections_str.encode("utf-8")).hexdigest()[:12]
        run_id = f"repo-context-run-{run_hash}"

        diagnostics.append(
            f"Successfully built context. Sections={len(sections)}, Files={len(files_list)}."
        )

        return AIContextResult(
            id=run_id,
            context_type=ContextType.ARCHITECTURE if arch_result else ContextType.FILE,
            granularity=SummaryGranularity.COMPACT,
            sections=sections,
            symbols=[],
            repository=repo_dto,
            diagnostics=diagnostics,
            metadata={},
        )
