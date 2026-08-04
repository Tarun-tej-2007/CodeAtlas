"""Unit tests for the AIArchitectureAnalyzer component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.context import AIContext
from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.models import AIResponse, AIUsage
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.architecture_analysis import (
    ArchitectureRuleEngine,
    ArchitectureAIContextBuilder,
    ArchitecturePromptTemplates,
    ArchitectureReport,
    ArchitectureSummary,
    AIArchitectureAnalysisResult,
    AIArchitectureAnalyzer,
)
from app.architecture_analysis.exceptions import ArchitectureRuleError


class TestAIArchitectureAnalyzer(unittest.TestCase):
    """Verifies orchestration pipeline routing, mock delegations, exception propagation, and thread safety."""

    def setUp(self) -> None:
        self.rule_engine = MagicMock(spec=ArchitectureRuleEngine)
        self.context_builder = MagicMock(spec=ArchitectureAIContextBuilder)
        self.prompt_templates = MagicMock(spec=ArchitecturePromptTemplates)
        self.request_pipeline = MagicMock(spec=AIRequestPipeline)
        self.response_processor = MagicMock(spec=AIResponseProcessor)

        self.analyzer = AIArchitectureAnalyzer(
            rule_engine=self.rule_engine,
            context_builder=self.context_builder,
            prompt_templates=self.prompt_templates,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        # Common fixtures
        self.time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
        self.summary = ArchitectureSummary(
            total_issues=0,
            info_count=0,
            low_count=0,
            medium_count=0,
            high_count=0,
            critical_count=0,
        )
        self.report = ArchitectureReport(
            project_name="IntegrationProj",
            generated_at=self.time,
            issues=(),
            summary=self.summary,
        )
        self.ai_context = AIContext(
            title="Analysis Context",
            description="Testing context",
            metadata={},
            sections=(),
        )
        self.raw_response = AIResponse(
            id="resp-raw",
            request_id="req-raw",
            text_content="Raw analysis completion text",
            status=ResponseStatus.SUCCESS,
            usage=AIUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )
        self.processed_response = AIResponse(
            id="resp-processed",
            request_id="req-raw",
            text_content="Processed analysis completion text",
            status=ResponseStatus.SUCCESS,
            usage=AIUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )

    def test_successful_orchestration_flow(self) -> None:
        """Verifies full execution pipeline from rule engine to response processor."""
        # Arrange mock behaviors
        self.rule_engine.analyze.return_value = self.report
        self.context_builder.build_context.return_value = self.ai_context
        self.request_pipeline.execute.return_value = self.raw_response
        self.response_processor.process.return_value = self.processed_response

        # Act
        result = self.analyzer.analyze(
            project_name="IntegrationProj",
            context="OpaqueCtx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            variables={"mode": "strict"},
            priority=RequestPriority.HIGH,
            temperature=0.5,
            max_tokens=400,
        )

        # Assert delegation occurred
        self.rule_engine.analyze.assert_called_once_with(
            project_name="IntegrationProj", context="OpaqueCtx"
        )
        self.context_builder.build_context.assert_called_once_with(self.report)
        self.prompt_templates.register_all.assert_called_once()
        self.request_pipeline.execute.assert_called_once_with(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="architecture_review",
            context=self.ai_context,
            variables={"mode": "strict"},
            priority=RequestPriority.HIGH,
            temperature=0.5,
            max_tokens=400,
        )
        self.response_processor.process.assert_called_once_with(self.raw_response)

        # Verify output DTO
        self.assertIsInstance(result, AIArchitectureAnalysisResult)
        self.assertEqual(result.architecture_report, self.report)
        self.assertEqual(result.ai_response, self.processed_response)

    def test_exception_propagation(self) -> None:
        """Verifies exceptions raised by downstream rule engine propagate directly."""
        self.rule_engine.analyze.side_effect = ArchitectureRuleError("Failed to trace code")

        with self.assertRaises(ArchitectureRuleError):
            self.analyzer.analyze(
                project_name="FailProj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.FAST,
            )

    def test_multiple_analyzer_instances_isolation(self) -> None:
        """Verifies multiple analyzer instances do not share state."""
        analyzer2 = AIArchitectureAnalyzer(
            rule_engine=MagicMock(spec=ArchitectureRuleEngine),
            context_builder=MagicMock(spec=ArchitectureAIContextBuilder),
            prompt_templates=MagicMock(spec=ArchitecturePromptTemplates),
            request_pipeline=MagicMock(spec=AIRequestPipeline),
            response_processor=MagicMock(spec=AIResponseProcessor),
        )
        self.assertIsNot(self.analyzer, analyzer2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe execution when analyzer is invoked concurrently."""
        self.rule_engine.analyze.return_value = self.report
        self.context_builder.build_context.return_value = self.ai_context
        self.request_pipeline.execute.return_value = self.raw_response
        self.response_processor.process.return_value = self.processed_response

        def run_analyzer():
            return self.analyzer.analyze(
                project_name="ConcurrentProj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.FAST,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyzer) for _ in range(15)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.architecture_report, self.report)
            self.assertEqual(r.ai_response, self.processed_response)

    def test_deterministic_orchestration(self) -> None:
        """Verifies that identical inputs yield equivalent analysis result DTOs."""
        self.rule_engine.analyze.return_value = self.report
        self.context_builder.build_context.return_value = self.ai_context
        self.request_pipeline.execute.return_value = self.raw_response
        self.response_processor.process.return_value = self.processed_response

        r1 = self.analyzer.analyze(
            project_name="DetProj",
            context="Ctx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.FAST,
        )
        r2 = self.analyzer.analyze(
            project_name="DetProj",
            context="Ctx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.FAST,
        )

        self.assertEqual(r1.architecture_report, r2.architecture_report)
        self.assertEqual(r1.ai_response, r2.ai_response)


if __name__ == "__main__":
    unittest.main()
