"""Unit tests for the AITechnicalDebtAnalyzer orchestrator."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.technical_debt import (
    TechnicalDebtCategory,
    TechnicalDebtSeverity,
    TechnicalDebtItem,
    TechnicalDebtSummary,
    TechnicalDebtReport,
    TechnicalDebtScorer,
    TechnicalDebtAIContextBuilder,
    TechnicalDebtAnalysisEngine,
    TechnicalDebtPromptTemplates,
    TechnicalDebtAIAnalysisResult,
    AITechnicalDebtAnalyzer,
)


class TestAITechnicalDebtAnalyzer(unittest.TestCase):
    """Verifies orchestration logic sequence, DTO re-assembly, exception propagation, and isolation."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)

        # Mock dependencies
        self.analysis_engine = MagicMock(spec=TechnicalDebtAnalysisEngine)
        self.scorer = MagicMock(spec=TechnicalDebtScorer)
        self.context_builder = MagicMock(spec=TechnicalDebtAIContextBuilder)
        self.prompt_templates = MagicMock(spec=TechnicalDebtPromptTemplates)
        self.request_pipeline = MagicMock(spec=AIRequestPipeline)
        self.response_processor = MagicMock(spec=AIResponseProcessor)

        self.analyzer = AITechnicalDebtAnalyzer(
            analysis_engine=self.analysis_engine,
            scorer=self.scorer,
            context_builder=self.context_builder,
            prompt_templates=self.prompt_templates,
            request_pipeline=self.request_pipeline,
            response_processor=self.response_processor,
        )

        # Config DTOs
        self.item = TechnicalDebtItem(
            id="debt-123",
            category=TechnicalDebtCategory.CODE_SMELL,
            severity=TechnicalDebtSeverity.MEDIUM,
            title="Smell Item",
            effort_minutes=15,
        )
        self.initial_report = TechnicalDebtReport(
            project_name="TestProj",
            generated_at=self.time_utc,
            items=(self.item,),
            summary=TechnicalDebtSummary(
                total_items=1,
                total_effort_minutes=15,
                items_by_category={TechnicalDebtCategory.CODE_SMELL: 1},
                effort_by_severity={TechnicalDebtSeverity.MEDIUM: 15},
            ),
        )
        self.weighted_summary = TechnicalDebtSummary(
            total_items=1,
            total_effort_minutes=15,
            items_by_category={TechnicalDebtCategory.CODE_SMELL: 1},
            effort_by_severity={TechnicalDebtSeverity.MEDIUM: 15},
            metadata={"weighted_overall_score": 50.0},
        )

        # Mock setups
        self.analysis_engine.analyze.return_value = self.initial_report
        self.scorer.score.return_value = self.weighted_summary

        self.mock_ai_context = MagicMock()
        self.context_builder.build_context.return_value = self.mock_ai_context

        self.raw_ai_res = MagicMock()
        self.request_pipeline.execute.return_value = self.raw_ai_res

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
            AITechnicalDebtAnalyzer(
                analysis_engine=None,  # type: ignore
                scorer=self.scorer,
                context_builder=self.context_builder,
                prompt_templates=self.prompt_templates,
                request_pipeline=self.request_pipeline,
                response_processor=self.response_processor,
            )

    def test_orchestration_sequence(self) -> None:
        """Verifies full orchestration flow and DTO re-assembly."""
        result = self.analyzer.analyze(
            project_name="TestProj",
            context="OpaqueCtx",
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            temperature=0.7,
            max_tokens=150,
            priority=RequestPriority.HIGH,
        )

        # Validate returns DTO
        self.assertIsInstance(result, TechnicalDebtAIAnalysisResult)
        self.assertEqual(result.report.summary.metadata["weighted_overall_score"], 50.0)
        self.assertEqual(result.response, self.processed_ai_res)

        # Verify steps sequency
        self.analysis_engine.analyze.assert_called_once_with(
            project_name="TestProj", context="OpaqueCtx"
        )
        self.scorer.score.assert_called_once_with((self.item,))
        self.context_builder.build_context.assert_called_once()
        self.prompt_templates.register_all.assert_called_once()

        self.request_pipeline.execute.assert_called_once_with(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="technical_debt_review",
            context=self.mock_ai_context,
            variables={},
            priority=RequestPriority.HIGH,
            temperature=0.7,
            max_tokens=150,
        )
        self.response_processor.process.assert_called_once_with(self.raw_ai_res)

    def test_exception_propagation(self) -> None:
        """Verifies engine errors bubble up cleanly without wrapping."""
        self.request_pipeline.execute.side_effect = RuntimeError("API failure")

        with self.assertRaises(RuntimeError) as ctx:
            self.analyzer.analyze(
                project_name="TestProj",
                context="Ctx",
                provider=AIProvider.OPENAI,
                model_type=AIModelType.BALANCED,
            )
        self.assertEqual(str(ctx.exception), "API failure")

    def test_deterministic_execution(self) -> None:
        """Verifies identical inputs return matching outcomes."""
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

        self.assertEqual(r1.report.summary.metadata["weighted_overall_score"], r2.report.summary.metadata["weighted_overall_score"])
        self.assertEqual(r1.response.text_content, r2.response.text_content)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety under parallel analyze pipeline execution runs."""
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
            self.assertEqual(res.report.summary.metadata["weighted_overall_score"], 50.0)
            self.assertEqual(res.response.text_content, "Review suggestion")


if __name__ == "__main__":
    unittest.main()
