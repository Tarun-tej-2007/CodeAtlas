"""Unit tests for the AIReportAnalyzer orchestrator."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.prompts import AIPromptEngine
from app.ai_service.response_processor import AIResponseProcessor
from app.reporting import (
    ReportFormat,
    ReportSection,
    ReportGenerationError,
    ReportMetadata,
    ReportSectionContent,
    AnalysisReport,
    ReportAIContextBuilder,
    ReportingPromptTemplates,
    AIReportAnalysisResult,
    AIReportAnalyzer,
)


class TestAIReportingAnalyzer(unittest.TestCase):
    """Verifies orchestration sequence, mock delegations, templates checks, and concurrency."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)

        # Mock dependencies
        self.context_builder = MagicMock(spec=ReportAIContextBuilder)
        self.prompt_templates = MagicMock(spec=ReportingPromptTemplates)
        self.prompt_engine = MagicMock(spec=AIPromptEngine)
        self.request_pipeline = MagicMock(spec=AIRequestPipeline)
        self.response_processor = MagicMock(spec=AIResponseProcessor)

        self.analyzer = AIReportAnalyzer(
            context_builder=self.context_builder,
            prompt_templates=self.prompt_templates,
            prompt_engine=self.prompt_engine,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        self.metadata = ReportMetadata(
            project_name="OrchProj",
            generated_at=self.time_utc,
            format=ReportFormat.JSON,
        )
        self.report = AnalysisReport(
            metadata=self.metadata,
            sections={},
        )

        # Setup mock return values
        self.mock_context = MagicMock()
        self.context_builder.build_context.return_value = self.mock_context

        self.raw_ai_res = MagicMock()
        self.request_pipeline.execute.return_value = self.raw_ai_res

        self.processed_ai_res = AIResponse(
            id="res-22",
            request_id="req-22",
            text_content="AI executive summary suggestions",
            status=ResponseStatus.SUCCESS,
        )
        self.response_processor.process.return_value = self.processed_ai_res

    def test_constructor_validation(self) -> None:
        """Verifies constructor validates None inputs."""
        with self.assertRaises(ValueError):
            AIReportAnalyzer(
                context_builder=None,  # type: ignore
                prompt_templates=self.prompt_templates,
                prompt_engine=self.prompt_engine,
                request_pipeline=self.request_pipeline,
                response_processor=self.response_processor,
            )

    def test_orchestration_sequence(self) -> None:
        """Verifies correct sequential pipeline invocation execution."""
        result = self.analyzer.analyze(
            report=self.report,
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            temperature=0.7,
            max_tokens=300,
            priority=RequestPriority.HIGH,
        )

        self.assertIsInstance(result, AIReportAnalysisResult)
        self.assertEqual(result.report, self.report)
        self.assertEqual(result.ai_response, self.processed_ai_res)

        # Verify call sequences
        self.context_builder.build_context.assert_called_once_with(self.report)
        self.prompt_templates.register_all.assert_called_once()
        self.prompt_engine.get_template.assert_called_once_with("report_review")

        self.request_pipeline.execute.assert_called_once_with(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="report_review",
            context=self.mock_context,
            variables={},
            priority=RequestPriority.HIGH,
            temperature=0.7,
            max_tokens=300,
        )
        self.response_processor.process.assert_called_once_with(self.raw_ai_res)

    def test_exception_propagation(self) -> None:
        """Verifies error in execution pipeline propagates unmodified."""
        self.request_pipeline.execute.side_effect = RuntimeError("Network error")

        with self.assertRaises(RuntimeError) as ctx:
            self.analyzer.analyze(
                report=self.report,
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )
        self.assertEqual(str(ctx.exception), "Network error")

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety under parallel analyzer calls."""
        def run_analyze():
            return self.analyzer.analyze(
                report=self.report,
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(20)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.report.metadata.project_name, "OrchProj")
            self.assertEqual(res.ai_response.text_content, "AI executive summary suggestions")


if __name__ == "__main__":
    unittest.main()
