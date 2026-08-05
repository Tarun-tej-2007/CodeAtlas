"""Unit tests for the AIDashboardAnalyzer orchestrator."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.prompts import AIPromptEngine
from app.ai_service.response_processor import AIResponseProcessor
from app.dashboard import (
    DashboardStatus,
    DashboardWidgetType,
    DashboardMetadata,
    DashboardModel,
    DashboardWidget,
    DashboardAggregationEngine,
    DashboardAIContextBuilder,
    DashboardPromptTemplates,
    AIDashboardAnalysisResult,
    AIDashboardAnalyzer,
    DashboardValidationError,
)


class TestAIDashboardAnalyzer(unittest.TestCase):
    """Verifies orchestration sequence, prompt checks, validation restrictions, and concurrent runs."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)

        # Mock dependencies
        self.dashboard_engine = MagicMock(spec=DashboardAggregationEngine)
        self.context_builder = MagicMock(spec=DashboardAIContextBuilder)
        self.prompt_templates = MagicMock(spec=DashboardPromptTemplates)
        self.prompt_engine = MagicMock(spec=AIPromptEngine)
        self.request_pipeline = MagicMock(spec=AIRequestPipeline)
        self.response_processor = MagicMock(spec=AIResponseProcessor)

        # Connect prompt engine mock into template dependencies
        self.prompt_templates.prompt_engine = self.prompt_engine

        self.analyzer = AIDashboardAnalyzer(
            dashboard_engine=self.dashboard_engine,
            context_builder=self.context_builder,
            prompt_templates=self.prompt_templates,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        self.metadata = DashboardMetadata(
            project_name="AIOrchProj",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
        )
        self.dashboard = DashboardModel(
            metadata=self.metadata,
            widgets={},
        )

        # Setup mock return values
        self.dashboard_engine.compile.return_value = self.dashboard
        
        self.mock_context = MagicMock()
        self.context_builder.build_context.return_value = self.mock_context

        self.raw_ai_res = MagicMock()
        self.request_pipeline.execute.return_value = self.raw_ai_res

        self.processed_ai_res = AIResponse(
            id="res-dashboard-5",
            request_id="req-dashboard-5",
            text_content="AI dashboard metrics suggestions",
            status=ResponseStatus.SUCCESS,
        )
        self.response_processor.process.return_value = self.processed_ai_res

    def test_constructor_validation(self) -> None:
        """Verifies constructor validates None inputs."""
        with self.assertRaises(ValueError):
            AIDashboardAnalyzer(
                dashboard_engine=None,  # type: ignore
                context_builder=self.context_builder,
                prompt_templates=self.prompt_templates,
                request_pipeline=self.request_pipeline,
                response_processor=self.response_processor,
            )

    def test_orchestration_sequence(self) -> None:
        """Verifies correct sequential pipeline invocation execution."""
        result = self.analyzer.analyze(
            project_name="AIOrchProj",
            context="DummyContext",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            temperature=0.7,
            max_tokens=400,
            priority=RequestPriority.HIGH,
        )

        self.assertIsInstance(result, AIDashboardAnalysisResult)
        self.assertEqual(result.dashboard, self.dashboard)
        self.assertEqual(result.ai_response, self.processed_ai_res)

        # Verify call sequences
        self.dashboard_engine.compile.assert_called_once_with(
            project_name="AIOrchProj", context="DummyContext"
        )
        self.context_builder.build_context.assert_called_once_with(self.dashboard)
        self.prompt_templates.register_all.assert_called_once()
        self.prompt_engine.get_template.assert_called_once_with("dashboard_review")

        self.request_pipeline.execute.assert_called_once_with(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="dashboard_review",
            context=self.mock_context,
            variables={},
            priority=RequestPriority.HIGH,
            temperature=0.7,
            max_tokens=400,
        )
        self.response_processor.process.assert_called_once_with(self.raw_ai_res)

    def test_exception_propagation(self) -> None:
        """Verifies error in execution pipeline propagates unmodified."""
        self.request_pipeline.execute.side_effect = RuntimeError("Network timeout")

        with self.assertRaises(RuntimeError) as ctx:
            self.analyzer.analyze(
                project_name="AIOrchProj",
                context="DummyContext",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )
        self.assertEqual(str(ctx.exception), "Network timeout")

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety under parallel analyzer calls."""
        def run_analyze():
            return self.analyzer.analyze(
                project_name="AIOrchProj",
                context="DummyContext",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.dashboard.metadata.project_name, "AIOrchProj")
            self.assertEqual(res.ai_response.text_content, "AI dashboard metrics suggestions")


if __name__ == "__main__":
    unittest.main()
