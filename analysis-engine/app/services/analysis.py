"""Analysis service module coordinating workspace, cloning, and scanning."""

import logging
import uuid

from app.workspace.manager import WorkspaceManager
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.scanner.models import ScanResult
from app.parser.pipeline import ParsingPipeline
from app.parser.models import AnalysisResult

from typing import Any, Mapping, Optional
from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.semantic import SemanticPipeline, SemanticLinkingPipeline
from app.semantic.project_models import ProjectSemanticResult, ProjectFile, ProjectSymbol, SymbolLocation, SymbolReference
from app.graph.dependency_builder import DependencyGraphBuilder
from app.architecture_analysis import ArchitectureSemanticContext
from app.architecture_analysis.ai_analyzer import AIArchitectureAnalyzer

logger = logging.getLogger("analysis-engine")


class CombinedArchitectureContext:
    """Holds both the DependencyGraph and the ArchitectureSemanticContext for rule evaluation."""

    def __init__(self, graph: Any, semantic_context: Any) -> None:
        self.graph = graph
        self.semantic_context = semantic_context


class AnalysisService:
    """Orchestrates codebase static analysis by preparing workspaces, acquiring code, scanning, and parsing."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager | None = None,
        clone_service: RepositoryCloneService | None = None,
        scanner_pipeline: ScannerPipeline | None = None,
        parsing_pipeline: ParsingPipeline | None = None,
        semantic_pipeline: SemanticPipeline | None = None,
        linking_pipeline: SemanticLinkingPipeline | None = None,
        graph_builder: DependencyGraphBuilder | None = None,
        ai_analyzer: AIArchitectureAnalyzer | None = None,
        technical_debt_analyzer: Any = None,
    ) -> None:
        """Initializes the AnalysisService with injected sub-services.

        Args:
            workspace_manager: Optional WorkspaceManager override.
            clone_service: Optional RepositoryCloneService override.
            scanner_pipeline: Optional ScannerPipeline override.
            parsing_pipeline: Optional ParsingPipeline override.
            semantic_pipeline: Optional SemanticPipeline override.
            linking_pipeline: Optional SemanticLinkingPipeline override.
            graph_builder: Optional DependencyGraphBuilder override.
            ai_analyzer: Optional AIArchitectureAnalyzer override.
            technical_debt_analyzer: Optional TechnicalDebtAnalysisEngine or AITechnicalDebtAnalyzer override.
        """
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.clone_service = clone_service or RepositoryCloneService()
        self.scanner_pipeline = scanner_pipeline or ScannerPipeline()
        self.parsing_pipeline = parsing_pipeline or ParsingPipeline()
        self.semantic_pipeline = semantic_pipeline
        self.linking_pipeline = linking_pipeline
        self.graph_builder = graph_builder
        self.ai_analyzer = ai_analyzer
        self.technical_debt_analyzer = technical_debt_analyzer

    def analyze_repository(
        self,
        repository_url: str,
        project_id: uuid.UUID,
        *,
        ai_provider: Optional[AIProvider] = None,
        ai_model_type: Optional[AIModelType] = None,
        variables: Optional[Mapping[str, Any]] = None,
        priority: RequestPriority = RequestPriority.MEDIUM,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AnalysisResult:
        """Runs the static analysis and parsing pipeline on the given repository URL.

        1. Creates an isolated workspace.
        2. Clones or copies the repository files.
        3. Scans the workspace to discover files and identify languages.
        4. Parses discovered files.
        5. Runs semantic analysis, graph linking, rule evaluations and AI analysis if provider is specified.
        6. Guarantees workspace cleanup (if configured to delete).

        Args:
            repository_url: Local path or remote Git URL.
            project_id: Project identifier to isolate the workspace.
            ai_provider: AI Provider to use for architecture analysis.
            ai_model_type: AI Model Type to use.
            variables: Variables map for prompts.
            priority: Request priority.
            temperature: Sampling temperature.
            max_tokens: Max completion tokens limit.

        Returns:
            The aggregated AnalysisResult containing scan, parse and optional architecture outputs.
        """
        workspace = self.workspace_manager.create_workspace(analysis_id=project_id)
        
        try:
            self.clone_service.clone_repository(source=repository_url, workspace=workspace)
            scan_result = self.scanner_pipeline.scan(repository_root=workspace.path)
            
            # Execute parsing pipeline
            discovered_files = scan_result.discovery_result.files
            parse_result = self.parsing_pipeline.parse_files(discovered_files)

            architecture_result = None
            technical_debt_result = None

            run_architecture = bool(ai_provider and ai_model_type and self.ai_analyzer)
            run_tech_debt = self.technical_debt_analyzer is not None

            if run_architecture or run_tech_debt:
                # 1. Semantic Analysis
                file_semantics = {}
                for parsed_file in parse_result.files:
                    if self.semantic_pipeline:
                        sem_res = self.semantic_pipeline.execute(parsed_file)
                        
                        proj_symbols = [
                            ProjectSymbol(
                                id=s.id,
                                name=s.name,
                                qualified_name=s.qualified_name,
                                kind=s.kind,
                                location=SymbolLocation(file_path=parsed_file.relative_path, location=s.location),
                                metadata=s.metadata or {},
                            )
                            for s in sem_res.symbols
                        ]
                        
                        proj_references = []
                        for ref in sem_res.references:
                            sym_name = next(
                                (s.name for s in sem_res.symbols if s.id == ref.symbol_id), "unknown"
                            )
                            proj_references.append(
                                SymbolReference(
                                    name=sym_name,
                                    location=SymbolLocation(file_path=parsed_file.relative_path, location=ref.location),
                                )
                            )
                        
                        file_semantics[parsed_file.relative_path] = ProjectFile(
                            path=parsed_file.relative_path,
                            symbols=proj_symbols,
                            imports=[],
                            exports=[],
                            references=proj_references,
                        )

                project_sem = ProjectSemanticResult(files=file_semantics)

                # 2. Semantic Linking
                linked_sem = None
                if self.linking_pipeline:
                    linked_sem = self.linking_pipeline.link_project(project_sem)

                # 3. Dependency Graph Construction
                graph = None
                if self.graph_builder and linked_sem:
                    graph = self.graph_builder.build_graph(linked_sem)

                # 4. Context Combination
                sem_context = ArchitectureSemanticContext(linked_sem) if linked_sem else None
                combined_context = CombinedArchitectureContext(
                    graph=graph, semantic_context=sem_context
                )

                # Define Wrapper Context for Technical Debt rule resolution
                class CombinedTechnicalDebtContext:
                    def __init__(self, graph: Any, linked_sem: Any) -> None:
                        self.graph = graph
                        self.original_result = getattr(linked_sem, "original_result", None)
                        self.reference_resolution_result = getattr(linked_sem, "reference_resolution_result", None)
                        self.files = getattr(self.original_result, "files", {}) if self.original_result else {}
                        self.resolved_references = getattr(self.reference_resolution_result, "resolved_references", []) if self.reference_resolution_result else []

                td_context = CombinedTechnicalDebtContext(graph, linked_sem)

                # 5. Execute AI Architecture Analyzer (runs rule engine & request pipeline)
                if run_architecture:
                    architecture_result = self.ai_analyzer.analyze(
                        project_name=str(project_id),
                        context=combined_context,
                        provider=ai_provider,
                        model_type=ai_model_type,
                        variables=variables,
                        priority=priority,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                # 6. Execute Technical Debt Analyzer or Engine
                if run_tech_debt:
                    from app.technical_debt.ai_analyzer import AITechnicalDebtAnalyzer
                    if isinstance(self.technical_debt_analyzer, AITechnicalDebtAnalyzer):
                        if ai_provider and ai_model_type:
                            technical_debt_result = self.technical_debt_analyzer.analyze(
                                project_name=str(project_id),
                                context=td_context,
                                provider=ai_provider,
                                model_type=ai_model_type,
                                variables=variables,
                                priority=priority,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            )
                        else:
                            technical_debt_result = self.technical_debt_analyzer.analysis_engine.analyze(
                                project_name=str(project_id),
                                context=td_context,
                            )
                    else:
                        technical_debt_result = self.technical_debt_analyzer.analyze(
                            project_name=str(project_id),
                            context=td_context,
                        )
            
            return AnalysisResult(
                scan_result=scan_result,
                parse_result=parse_result,
                architecture_result=architecture_result,
                technical_debt_result=technical_debt_result,
            )
        finally:
            try:
                self.workspace_manager.cleanup_workspace(workspace)
            except Exception as cleanup_err:
                logger.error(
                    "Failed to clean up workspace at '%s' after analysis: %s",
                    workspace.path,
                    cleanup_err,
                    exc_info=True,
                )
                # We log the cleanup failure but do not raise it,
                # ensuring the original exception (if any) or result propagates untouched.

