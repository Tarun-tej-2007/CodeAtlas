"""Unit integration tests for End-to-End Architecture Analysis Integration."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.models import AIResponse, AIUsage
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline
from app.scanner.models import (
    Language,
    ScanResult,
    DiscoveryResult,
    DiscoveredFile,
)
from app.parser.models import ParsedFile, ParseResult
from app.semantic import (
    SemanticResult,
    LinkedSemanticResult,
    SemanticLinkingPipeline,
    SemanticPipeline,
)
from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_builder import DependencyGraphBuilder
from app.architecture_analysis.ai_analyzer import (
    AIArchitectureAnalysisResult,
    AIArchitectureAnalyzer,
)
from app.architecture_analysis.models import ArchitectureReport, ArchitectureSummary
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.services.analysis import AnalysisService


class TestArchitectureAnalysisIntegration(unittest.TestCase):
    """End-to-end orchestration tests for integration and backward compatibility checks."""

    def setUp(self) -> None:
        # 1. Setup mock components
        self.workspace_manager = MagicMock(spec=WorkspaceManager)
        self.clone_service = MagicMock(spec=RepositoryCloneService)
        self.scanner_pipeline = MagicMock(spec=ScannerPipeline)
        self.parsing_pipeline = MagicMock(spec=ParsingPipeline)
        self.semantic_pipeline = MagicMock(spec=SemanticPipeline)
        self.linking_pipeline = MagicMock(spec=SemanticLinkingPipeline)
        self.graph_builder = MagicMock(spec=DependencyGraphBuilder)
        self.ai_analyzer = MagicMock(spec=AIArchitectureAnalyzer)

        # Config mock workspace
        self.mock_workspace = Workspace(
            id=uuid.uuid4(),
            analysis_id=uuid.uuid4(),
            path=Path("/tmp/mock-workspace"),
            created_at=datetime.now(timezone.utc),
        )
        self.workspace_manager.create_workspace.return_value = self.mock_workspace

        # Common fixtures
        self.time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
        self.project_id = uuid.uuid4()

        # Discovered & Parsed files mock return
        disc_file = DiscoveredFile(
            absolute_path=Path("/tmp/mock-workspace/main.py"),
            relative_path=Path("main.py"),
            extension=".py",
            size=100,
            language=Language.PYTHON,
        )
        self.scan_res = ScanResult(
            total_files=1,
            supported_files=1,
            unsupported_files=0,
            languages={Language.PYTHON: 1},
            discovery_result=DiscoveryResult(
                project_name="E2EProj",
                files=[disc_file],
                unsupported_files=[],
            ),
            scan_duration=0.01,
        )
        self.scanner_pipeline.scan.return_value = self.scan_res

        parsed_file = ParsedFile(
            path=Path("/tmp/mock-workspace/main.py"),
            relative_path=Path("main.py"),
            language=Language.PYTHON,
            source_code="print('e2e')",
            tree=None,
        )
        self.parse_res = ParseResult(
            files=[parsed_file],
            parsed_count=1,
            failed_count=0,
            parse_duration_ms=5.0,
        )
        self.parsing_pipeline.parse_files.return_value = self.parse_res

        # Semantic, linked, and graph mock returns
        self.sem_res = SemanticResult(symbols=[], references=[], scopes=[])
        self.semantic_pipeline.execute.return_value = self.sem_res

        from app.semantic import (
            ProjectSemanticResult,
            ProjectSymbolIndex,
            ImportExportResolutionResult,
            ReferenceResolutionResult,
        )

        self.linked_res = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={}),
            symbol_index=ProjectSymbolIndex(files={}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[]),
        )
        self.linking_pipeline.link_project.return_value = self.linked_res

        self.graph = DependencyGraph(nodes=[], edges=[])
        self.graph_builder.build_graph.return_value = self.graph

        # AI Architecture analysis return DTO
        self.arch_report = ArchitectureReport(
            project_name="E2EProj",
            generated_at=self.time,
            issues=(),
            summary=ArchitectureSummary(
                total_issues=0,
                info_count=0,
                low_count=0,
                medium_count=0,
                high_count=0,
                critical_count=0,
            ),
        )
        self.ai_response = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content="AI summary",
            status=ResponseStatus.SUCCESS,
            usage=AIUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )
        self.ai_arch_res = AIArchitectureAnalysisResult(
            architecture_report=self.arch_report, ai_response=self.ai_response
        )
        self.ai_analyzer.analyze.return_value = self.ai_arch_res

        # 2. Instantiate integration service
        self.service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            ai_analyzer=self.ai_analyzer,
        )

    def test_e2e_architecture_analysis_integration_flow(self) -> None:
        """Verifies E2E execution: Repository -> Scanner -> Parser -> Semantic -> Graph -> Engine -> AI Analyzer -> Result."""
        result = self.service.analyze_repository(
            repository_url="https://github.com/user/repo",
            project_id=self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
            variables={"rule": "check"},
            priority=RequestPriority.HIGH,
            temperature=0.1,
            max_tokens=256,
        )

        # Verify correct orchestration and execution pipelines
        self.clone_service.clone_repository.assert_called_once()
        self.scanner_pipeline.scan.assert_called_once()
        self.parsing_pipeline.parse_files.assert_called_once()
        self.semantic_pipeline.execute.assert_called_once()
        self.linking_pipeline.link_project.assert_called_once()
        self.graph_builder.build_graph.assert_called_once()

        # Analyzer assertion
        self.ai_analyzer.analyze.assert_called_once()
        self.assertEqual(result.architecture_result, self.ai_arch_res)

        # Cleanup verification
        self.workspace_manager.cleanup_workspace.assert_called_once_with(
            self.mock_workspace
        )

    def test_existing_workflow_backward_compatibility(self) -> None:
        """Verifies scanner and parser execute without errors when AI params are omitted."""
        result = self.service.analyze_repository(
            repository_url="https://github.com/user/repo",
            project_id=self.project_id,
        )

        # Assert scanner and parser executed, but AI/Semantic pipeline skipped
        self.clone_service.clone_repository.assert_called_once()
        self.scanner_pipeline.scan.assert_called_once()
        self.parsing_pipeline.parse_files.assert_called_once()
        self.semantic_pipeline.execute.assert_not_called()
        self.ai_analyzer.analyze.assert_not_called()

        # Check result
        self.assertIsNone(result.architecture_result)

    def test_failure_propagation(self) -> None:
        """Verifies any parser or scanner exception propagates correctly without blocking workspace cleanup."""
        self.parsing_pipeline.parse_files.side_effect = Exception("Parse failed catastrophically")

        with self.assertRaises(Exception) as ctx:
            self.service.analyze_repository(
                repository_url="https://github.com/user/repo",
                project_id=self.project_id,
            )

        self.assertIn("Parse failed catastrophically", str(ctx.exception))
        # Ensure cleanup still executed
        self.workspace_manager.cleanup_workspace.assert_called_once_with(
            self.mock_workspace
        )

    def test_dependency_injection_wiring(self) -> None:
        """Verifies DI mapping handles None values safely."""
        basic_service = AnalysisService()
        self.assertIsNotNone(basic_service.workspace_manager)
        self.assertIsNotNone(basic_service.clone_service)
        self.assertIsNotNone(basic_service.scanner_pipeline)
        self.assertIsNotNone(basic_service.parsing_pipeline)
        self.assertIsNone(basic_service.ai_analyzer)

    def test_deterministic_orchestration(self) -> None:
        """Verifies that duplicate runs return identical analysis outputs."""
        r1 = self.service.analyze_repository(
            repository_url="https://github.com/user/repo",
            project_id=self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )
        r2 = self.service.analyze_repository(
            repository_url="https://github.com/user/repo",
            project_id=self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )

        self.assertEqual(r1.architecture_result, r2.architecture_result)

    def test_multiple_integration_instances_isolation(self) -> None:
        """Verifies isolated states between distinct service instances."""
        service2 = AnalysisService()
        self.assertIsNot(self.service, service2)

    def test_concurrent_execution(self) -> None:
        """Verifies safe concurrent requests routing."""
        def run_integration():
            return self.service.analyze_repository(
                repository_url="https://github.com/user/repo",
                project_id=uuid.uuid4(),
                ai_provider=AIProvider.OPENAI,
                ai_model_type=AIModelType.BALANCED,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_integration) for _ in range(12)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.architecture_result, self.ai_arch_res)


if __name__ == "__main__":
    unittest.main()
