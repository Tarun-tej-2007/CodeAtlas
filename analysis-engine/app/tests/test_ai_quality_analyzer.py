"""Unit tests for the AIQualityAnalyzer orchestrator."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.prompts import AIPromptEngine
from app.ai_service.response_processor import AIResponseProcessor
from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetric,
    QualityReport,
    QualitySummary,
    QualityScorer,
    QualityAIContextBuilder,
    QualityEvaluationEngine,
    QualityAIAnalysisResult,
    AIQualityAnalyzer,
)


class TestAIQualityAnalyzer(unittest.TestCase):
    """Verifies orchestration logic sequence, exception bubble up, thread-safety, and isolation."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)

        # Mock dependencies
        self.evaluation_engine = MagicMock(spec=QualityEvaluationEngine)
        self.scorer = MagicMock(spec=QualityScorer)
        self.context_builder = MagicMock(spec=QualityAIContextBuilder)
        self.prompt_engine = MagicMock(spec=AIPromptEngine)
        self.request_pipeline = MagicMock(spec=AIRequestPipeline)
        self.response_processor = MagicMock(spec=AIResponseProcessor)

        self.analyzer = AIQualityAnalyzer(
            evaluation_engine=self.evaluation_engine,
            scorer=self.scorer,
            context_builder=self.context_builder,
            prompt_engine=self.prompt_engine,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        # Config stubs
        self.metric = QualityMetric(
            name="avg-file-size",
            category=MetricCategory.MAINTAINABILITY,
            value=80.0,
            level=QualityLevel.GOOD,
        )
        self.initial_report = QualityReport(
            project_name="TestProj",
            generated_at=self.time_utc,
            metrics=(self.metric,),
            summary=QualitySummary(overall_score=80.0, overall_level=QualityLevel.GOOD),
        )
        self.weighted_summary = QualitySummary(
            overall_score=85.0,
            overall_level=QualityLevel.GOOD,
            metrics_by_category={MetricCategory.MAINTAINABILITY: 85.0},
        )

        # Setup mock behavior
        self.evaluation_engine.analyze.return_value = self.initial_report
        self.scorer.score.return_value = self.weighted_summary

        self.mock_ai_context = MagicMock()
        self.context_builder.build_context.return_value = self.mock_ai_context

        self.raw_ai_res = MagicMock()
        self.request_pipeline.execute.return_value = self.raw_ai_res

        from app.ai_service.enums import ResponseStatus
        self.processed_ai_res = AIResponse(
            id="resp-123",
            request_id="req-123",
            text_content="Review suggestion",
            status=ResponseStatus.SUCCESS,
        )
        self.response_processor.process.return_value = self.processed_ai_res

    def test_constructor_validation(self) -> None:
        """Verifies constructor raises ValueError if any dependency is None."""
        with self.assertRaises(ValueError):
            AIQualityAnalyzer(
                evaluation_engine=None,  # type: ignore
                scorer=self.scorer,
                context_builder=self.context_builder,
                prompt_engine=self.prompt_engine,
                request_pipeline=self.request_pipeline,
                response_processor=self.response_processor,
            )

    def test_orchestration_sequence(self) -> None:
        """Verifies full sequential pipeline orchestration calls."""
        # Act
        result = self.analyzer.analyze(
            project_name="TestProj",
            context="OpaqueCtx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            temperature=0.7,
            max_tokens=150,
            priority=RequestPriority.HIGH,
        )

        # Assert correct result aggregates
        self.assertIsInstance(result, QualityAIAnalysisResult)
        self.assertEqual(result.quality_report.summary.overall_score, 85.0)  # weighted summary applied
        self.assertEqual(result.ai_response, self.processed_ai_res)

        # Verify steps sequence and delegations
        self.evaluation_engine.analyze.assert_called_once_with(
            project_name="TestProj", context="OpaqueCtx"
        )
        self.scorer.score.assert_called_once_with((self.metric,))
        self.context_builder.build_context.assert_called_once()
        self.prompt_engine.get_template.assert_called_once_with("quality_review")

        self.request_pipeline.execute.assert_called_once_with(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="quality_review",
            context=self.mock_ai_context,
            variables={},
            priority=RequestPriority.HIGH,
            temperature=0.7,
            max_tokens=150,
        )
        self.response_processor.process.assert_called_once_with(self.raw_ai_res)

    def test_exception_propagation(self) -> None:
        """Verifies errors raised inside pipelines bubble up cleanly."""
        self.request_pipeline.execute.side_effect = RuntimeError("Network error")

        with self.assertRaises(RuntimeError) as ctx:
            self.analyzer.analyze(
                project_name="TestProj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )
        self.assertEqual(str(ctx.exception), "Network error")

    def test_deterministic_execution(self) -> None:
        """Verifies identical inputs return matching orchestrator outcomes."""
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

        self.assertEqual(r1.quality_report.summary.overall_score, r2.quality_report.summary.overall_score)
        self.assertEqual(r1.ai_response.text_content, r2.ai_response.text_content)

    def test_instance_isolation(self) -> None:
        """Verifies separate analyzer instances maintain independent dependencies."""
        eval2 = MagicMock()
        analyzer2 = AIQualityAnalyzer(
            evaluation_engine=eval2,
            scorer=self.scorer,
            context_builder=self.context_builder,
            prompt_engine=self.prompt_engine,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        eval2.analyze.return_value = self.initial_report

        _ = analyzer2.analyze(
            project_name="Proj",
            context="Ctx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
        )
        eval2.analyze.assert_called_once()
        self.evaluation_engine.analyze.assert_not_called()

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety under parallel orchestration analyze runs."""
        def run_analyze():
            return self.analyzer.analyze(
                project_name="Proj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.quality_report.summary.overall_score, 85.0)
            self.assertEqual(res.ai_response.text_content, "Review suggestion")


if __name__ == "__main__":
    unittest.main()
