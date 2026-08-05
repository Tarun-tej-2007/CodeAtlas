"""Unit tests for the AIUnifiedAnalyzer orchestrator."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.unified_analysis import (
    AnalysisStatus,
    UnifiedAnalysisReport,
    UnifiedAnalysisEngine,
    UnifiedAIContextBuilder,
    UnifiedAnalysisPromptTemplates,
    UnifiedAIAnalysisResult,
    AIUnifiedAnalyzer,
)


class TestAIUnifiedAnalyzer(unittest.TestCase):
    """Verifies sequential flow orchestration, mock delegations, templates checks, and concurrency."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)

        # Mock dependencies
        self.engine = MagicMock(spec=UnifiedAnalysisEngine)
        self.context_builder = MagicMock(spec=UnifiedAIContextBuilder)
        self.prompt_templates = MagicMock(spec=UnifiedAnalysisPromptTemplates)
        self.request_pipeline = MagicMock(spec=AIRequestPipeline)
        self.response_processor = MagicMock(spec=AIResponseProcessor)

        self.analyzer = AIUnifiedAnalyzer(
            engine=self.engine,
            context_builder=self.context_builder,
            prompt_templates=self.prompt_templates,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        self.report = UnifiedAnalysisReport(
            project_name="UnifiedProj",
            generated_at=self.time_utc,
            status=AnalysisStatus.SUCCESS,
        )

        # Setup mock return values
        self.engine.analyze.return_value = self.report

        self.mock_ai_context = MagicMock()
        self.context_builder.build_context.return_value = self.mock_ai_context

        # Mock prompt engine link
        self.mock_prompt_engine = MagicMock()
        self.prompt_templates.prompt_engine = self.mock_prompt_engine

        self.raw_ai_res = MagicMock()
        self.request_pipeline.execute.return_value = self.raw_ai_res

        self.processed_ai_res = AIResponse(
            id="res-11",
            request_id="req-11",
            text_content="Unified AI Sug",
            status=ResponseStatus.SUCCESS,
        )
        self.response_processor.process.return_value = self.processed_ai_res

    def test_constructor_validation(self) -> None:
        """Verifies constructor validates None inputs."""
        with self.assertRaises(ValueError):
            AIUnifiedAnalyzer(
                engine=None,  # type: ignore
                context_builder=self.context_builder,
                prompt_templates=self.prompt_templates,
                request_pipeline=self.request_pipeline,
                response_processor=self.response_processor,
            )

    def test_orchestration_sequence(self) -> None:
        """Verifies correct sequential pipeline invocation execution."""
        result = self.analyzer.analyze(
            project_name="UnifiedProj",
            context="OpaqueCtx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            temperature=0.8,
            max_tokens=200,
            priority=RequestPriority.HIGH,
        )

        self.assertIsInstance(result, UnifiedAIAnalysisResult)
        self.assertEqual(result.report, self.report)
        self.assertEqual(result.ai_response, self.processed_ai_res)

        # Verify call sequences
        self.engine.analyze.assert_called_once_with(
            project_name="UnifiedProj", context="OpaqueCtx"
        )
        self.context_builder.build_context.assert_called_once_with(self.report)
        self.prompt_templates.register_all.assert_called_once()
        self.mock_prompt_engine.get_template.assert_called_once_with("unified_analysis_review")

        self.request_pipeline.execute.assert_called_once_with(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="unified_analysis_review",
            context=self.mock_ai_context,
            variables={},
            priority=RequestPriority.HIGH,
            temperature=0.8,
            max_tokens=200,
        )
        self.response_processor.process.assert_called_once_with(self.raw_ai_res)

    def test_exception_propagation(self) -> None:
        """Verifies error in execution pipeline propagates unmodified."""
        self.request_pipeline.execute.side_effect = RuntimeError("Network error")

        with self.assertRaises(RuntimeError) as ctx:
            self.analyzer.analyze(
                project_name="Proj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )
        self.assertEqual(str(ctx.exception), "Network error")

    def test_deterministic_execution(self) -> None:
        """Verifies deterministic output returns on identical params."""
        r1 = self.analyzer.analyze(
            project_name="Proj",
            context="Ctx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
        )
        r2 = self.analyzer.analyze(
            project_name="Proj",
            context="Ctx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
        )

        self.assertEqual(r1.report, r2.report)
        self.assertEqual(r1.ai_response.text_content, r2.ai_response.text_content)

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety under parallel analyzer calls."""
        def run_analyze():
            return self.analyzer.analyze(
                project_name="Proj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(20)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.report.project_name, "UnifiedProj")
            self.assertEqual(res.ai_response.text_content, "Unified AI Sug")


if __name__ == "__main__":
    unittest.main()
