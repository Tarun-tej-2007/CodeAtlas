"""Finding Analyzer Engine module.

Implements a stateless, deterministic analyzer that compiles structural code findings
from repository context, symbol context, dependency graph, and architectural results.
"""

from typing import Dict, List, Optional
import hashlib

from app.graph import DependencyGraph
from app.architecture.models import ArchitectureAnalysisResult
from app.ai.models import AIContextResult

from app.analysis.enums import AnalysisSeverity, AnalysisType
from app.analysis.analyzer import CodeAnalyzer
from app.analysis.models import (
    AnalysisFinding,
    AnalysisSummary,
    AnalysisResult,
)


class FindingAnalyzer(CodeAnalyzer):
    """Stateless engine that processes analysis inputs into code findings and summaries."""

    def _get_stable_id(self, prefix: str, content: str) -> str:
        """Helper to create a deterministic ID using SHA-256."""
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
        return f"{prefix}-{h}"

    def analyze(
        self,
        context_result: Optional[AIContextResult] = None,
        graph: Optional[DependencyGraph] = None,
        arch_result: Optional[ArchitectureAnalysisResult] = None,
        *args,
        **kwargs,
    ) -> AnalysisResult:
        """Processes AI context, graph, and architecture layers to compile code findings.

        This execution is completely deterministic, thread-safe, and stateless.
        """
        findings: List[AnalysisFinding] = []
        diagnostics: List[str] = ["Started finding analysis execution run."]

        # 1. Analyze Repository Context
        if context_result and context_result.repository:
            repo = context_result.repository
            total_files = len(repo.file_paths)
            languages = repo.primary_languages

            diagnostics.append(
                f"Processing repository context. Files={total_files}, Languages={len(languages)}."
            )

            if total_files == 0:
                fid = self._get_stable_id("finding-empty-repo", repo.repo_name)
                findings.append(
                    AnalysisFinding(
                        id=fid,
                        title="Empty Repository Structure",
                        description=f"Repository '{repo.repo_name}' contains no analyzed files.",
                        severity=AnalysisSeverity.INFO,
                        file_path="root",
                        start_line=1,
                        end_line=1,
                        rule_id="repo-empty",
                        metadata={"repo_name": repo.repo_name},
                    )
                )

            if len(languages) > 2:
                fid = self._get_stable_id(
                    "finding-multi-lang", "-".join(sorted(languages))
                )
                findings.append(
                    AnalysisFinding(
                        id=fid,
                        title="Multi-Language System Complexity",
                        description=(
                            f"Codebase incorporates {len(languages)} programming languages: "
                            f"{', '.join(sorted(languages))}."
                        ),
                        severity=AnalysisSeverity.WARNING,
                        file_path="root",
                        start_line=1,
                        end_line=1,
                        rule_id="repo-multi-language",
                        metadata={"languages": ", ".join(sorted(languages))},
                    )
                )

        # 2. Analyze Symbol Contexts
        if context_result and context_result.symbols:
            diagnostics.append(f"Analyzing {len(context_result.symbols)} symbols.")
            for sym in context_result.symbols:
                # Flag high coupling (high dependents)
                if len(sym.dependents) > 10:
                    fid = self._get_stable_id("finding-high-afferent", sym.symbol_id)
                    findings.append(
                        AnalysisFinding(
                            id=fid,
                            title="Highly Coupled Core Symbol",
                            description=(
                                f"Symbol '{sym.qualified_name}' (kind: {sym.kind}) is referenced "
                                f"by {len(sym.dependents)} dependents, suggesting a single point of failure."
                            ),
                            severity=AnalysisSeverity.WARNING,
                            file_path=sym.metadata.get("source_file", "unknown"),
                            start_line=1,
                            end_line=1,
                            rule_id="symbol-coupling-afferent",
                            metadata={
                                "symbol_id": sym.symbol_id,
                                "dependents_count": str(len(sym.dependents)),
                            },
                        )
                    )

                # Flag high dependencies (high outgoing dependencies)
                if len(sym.dependencies) > 10:
                    fid = self._get_stable_id("finding-high-efferent", sym.symbol_id)
                    findings.append(
                        AnalysisFinding(
                            id=fid,
                            title="Excessive Efferent Symbol Coupling",
                            description=(
                                f"Symbol '{sym.qualified_name}' depends on {len(sym.dependencies)} "
                                f"external symbols, indicating low cohesion."
                            ),
                            severity=AnalysisSeverity.WARNING,
                            file_path=sym.metadata.get("source_file", "unknown"),
                            start_line=1,
                            end_line=1,
                            rule_id="symbol-coupling-efferent",
                            metadata={
                                "symbol_id": sym.symbol_id,
                                "dependencies_count": str(len(sym.dependencies)),
                            },
                        )
                    )

        # 3. Analyze Dependency Relationships
        if graph:
            diagnostics.append(f"Analyzing dependency graph. Nodes={len(graph.nodes)}.")
            for node in graph.nodes:
                deg_out = len(graph.get_outgoing_target_ids(node.id))
                deg_in = len(graph.get_incoming_source_ids(node.id))
                total_deg = deg_out + deg_in
                # Node with extremely high connections
                if total_deg > 20:
                    fid = self._get_stable_id("finding-graph-hub", node.id)
                    findings.append(
                        AnalysisFinding(
                            id=fid,
                            title="High Connection Graph Hub",
                            description=(
                                f"Graph node '{node.id}' functions as a hub with degree {total_deg} "
                                f"(in={deg_in}, out={deg_out})."
                            ),
                            severity=AnalysisSeverity.WARNING,
                            file_path=node.id,
                            start_line=1,
                            end_line=1,
                            rule_id="graph-node-hub",
                            metadata={"node_id": node.id, "degree": str(total_deg)},
                        )
                    )

        # 4. Analyze Architecture issues
        if arch_result and arch_result.issues:
            diagnostics.append(f"Analyzing {len(arch_result.issues)} architectural issues.")
            for issue in arch_result.issues:
                # Convert ArchitectureIssue to AnalysisFinding
                fid = self._get_stable_id("finding-arch-issue", issue.id)
                findings.append(
                    AnalysisFinding(
                        id=fid,
                        title=issue.title,
                        description=issue.description,
                        severity=AnalysisSeverity.ERROR,
                        file_path=issue.location or "architecture",
                        start_line=1,
                        end_line=1,
                        rule_id=f"arch-{issue.category.value}",
                        metadata={
                            "arch_issue_id": issue.id,
                            "arch_category": issue.category.value,
                        },
                    )
                )

        # Sort findings lexicographically by stable ID to enforce determinism
        findings.sort(key=lambda x: x.id)

        # 5. Compile Run Summary
        severity_tallies: Dict[str, int] = {}
        for f in findings:
            sev_str = f.severity.value
            severity_tallies[sev_str] = severity_tallies.get(sev_str, 0) + 1

        summary = AnalysisSummary(
            total_findings=len(findings),
            findings_by_severity=severity_tallies,
            duration_ms=0,  # Pure functional processing has no timestamps/clocks
            metadata={},
        )

        # Generate run ID based on hash of findings
        findings_hash_str = "".join(f.id for f in findings)
        run_hash = hashlib.md5(findings_hash_str.encode("utf-8")).hexdigest()[:12]
        run_id = f"analysis-run-{run_hash}"

        diagnostics.append(
            f"Successfully compiled analysis. RunID={run_id}, Findings={len(findings)}."
        )

        return AnalysisResult(
            id=run_id,
            analysis_type=AnalysisType.DESIGN,
            summary=summary,
            findings=findings,
            recommendations=[],
            diagnostics=diagnostics,
            metadata={},
        )
