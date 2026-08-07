"""Unit tests for the AIOrchestratorService component."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai import (
    AIAnalysis,
    AIAnalysisStatus,
    AIAnalysisType,
    AIContext,
    AIMetadata,
    AIOrchestratorService,
    AIProvider,
    AIProviderError,
    AIRecommendation,
    AIRequest,
    AIResult,
    AIUsageStatistics,
    AIValidationError,
    AIPersistenceError,
    PromptContext,
    ArchitectureReview,
    RefactoringRoadmap,
)
from app.ai.interfaces import (
    AIAnalysisPersistence,
    AIContextBuilder,
    ArchitectureReviewer,
    LLMProvider,
    PromptBuilder,
    RecommendationGenerator,
)


class TestAIOrchestrator(unittest.TestCase):
    """Verifies end-to-end AI review pipeline orchestration and error handling."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)

        # Mocks for collaborate interfaces
        self.context_builder = MagicMock(spec=AIContextBuilder)
        self.prompt_builder = MagicMock(spec=PromptBuilder)
        self.llm_provider = MagicMock(spec=LLMProvider)
        self.recommendation_generator = MagicMock(spec=RecommendationGenerator)
        self.architecture_reviewer = MagicMock(spec=ArchitectureReviewer)
        self.persistence = MagicMock(spec=AIAnalysisPersistence)

        # Orchestrator instantiation
        self.service = AIOrchestratorService(
            context_builder=self.context_builder,
            prompt_builder=self.prompt_builder,
            llm_provider=self.llm_provider,
            recommendation_generator=self.recommendation_generator,
            architecture_reviewer=self.architecture_reviewer,
            persistence=self.persistence,
        )

        self.metadata = AIMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            provider=AIProvider.MOCK,
            model_name="mock-model",
            temperature=0.0,
            extra_info={},
        )
        self.request = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            metadata=self.metadata,
        )

    def test_invalid_parameters(self) -> None:
        """Verifies fail-fast validation on missing request input."""
        with self.assertRaises(AIValidationError):
            self.service.orchestrate_analysis(None)

    def test_empty_repository_workflow(self) -> None:
        """Verifies that an empty repository aggregates context but short-circuits without LLM invocation."""
        empty_ctx = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=0,
            dependency_graph_summary=None,
        )
        self.context_builder.build_context.return_value = empty_ctx

        # Empty review mock return
        empty_review = ArchitectureReview(
            project_id=self.project_id,
            commit_id=self.commit_id,
            executive_summary="Empty executive summary",
            roadmap=RefactoringRoadmap(estimated_workload="low"),
        )
        self.architecture_reviewer.generate_review.return_value = empty_review

        # Execute orchestration
        res = self.service.orchestrate_analysis(self.request)

        # Verification checks
        self.assertIsInstance(res, AIResult)
        self.assertEqual(res.analysis.status, AIAnalysisStatus.COMPLETED)
        self.assertEqual(res.analysis.recommendations, ())

        # Ensure LLM provider was never called
        self.llm_provider.generate_completion.assert_not_called()

        # Ensure persistence save was triggered
        self.persistence.save_analysis.assert_called_once()

    def test_successful_orchestration_flow(self) -> None:
        """Verifies end-to-end orchestration success path and intermediate component mappings."""
        # Setup aggregation context
        rich_ctx = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=10,
            dependency_graph_summary="Node: a.py",
        )
        self.context_builder.build_context.return_value = rich_ctx

        # Setup prompt builder output
        prompt_ctx = PromptContext(system_prompt="System", user_prompt="User")
        self.prompt_builder.build_prompt.return_value = prompt_ctx

        # Setup LLM execution output
        stats = AIUsageStatistics(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        self.llm_provider.generate_completion.return_value = ("Raw Completion text", stats)

        # Setup recommendations output
        recs = (
            AIRecommendation(
                title="R1",
                description="Desc 1",
                category="architecture",
                priority="high",
            ),
        )
        self.recommendation_generator.generate_recommendations.return_value = recs

        # Setup review output
        review = ArchitectureReview(
            project_id=self.project_id,
            commit_id=self.commit_id,
            executive_summary="Rich review summary",
            roadmap=RefactoringRoadmap(estimated_workload="medium"),
        )
        self.architecture_reviewer.generate_review.return_value = review

        # Run orchestration
        res = self.service.orchestrate_analysis(self.request)

        # Verify pipeline execution sequence and persistence save
        self.context_builder.build_context.assert_called_once()
        self.prompt_builder.build_prompt.assert_called_once_with(self.request, rich_ctx)
        self.llm_provider.generate_completion.assert_called_once_with(self.request, prompt_ctx)
        self.recommendation_generator.generate_recommendations.assert_called_once()
        self.architecture_reviewer.generate_review.assert_called_once()
        self.persistence.save_analysis.assert_called_once_with(self.project_id, res.analysis)

        # Verify results
        self.assertEqual(res.analysis.recommendations, recs)
        self.assertEqual(res.analysis.statistics.total_tokens, 150)
        self.assertEqual(res.extra_info["review"], review)

    def test_exception_translation_llm_failure(self) -> None:
        """Verifies that generic LLM exceptions are translated to AIProviderError."""
        rich_ctx = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=10,
            dependency_graph_summary="Node: a.py",
        )
        self.context_builder.build_context.return_value = rich_ctx

        prompt_ctx = PromptContext(system_prompt="System", user_prompt="User")
        self.prompt_builder.build_prompt.return_value = prompt_ctx

        # Simulate connection error or API outage
        self.llm_provider.generate_completion.side_effect = RuntimeError("Outage")

        with self.assertRaises(AIProviderError):
            self.service.orchestrate_analysis(self.request)

    def test_exception_translation_persistence_failure(self) -> None:
        """Verifies that storage exceptions are translated to AIPersistenceError."""
        rich_ctx = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=10,
            dependency_graph_summary="Node: a.py",
        )
        self.context_builder.build_context.return_value = rich_ctx

        prompt_ctx = PromptContext(system_prompt="System", user_prompt="User")
        self.prompt_builder.build_prompt.return_value = prompt_ctx

        self.llm_provider.generate_completion.return_value = ("Text", AIUsageStatistics())
        self.recommendation_generator.generate_recommendations.return_value = ()
        self.architecture_reviewer.generate_review.return_value = ArchitectureReview(
            project_id=self.project_id,
            commit_id=self.commit_id,
            executive_summary="Summary",
            roadmap=RefactoringRoadmap(estimated_workload="low"),
        )

        # Simulate storage backend error
        self.persistence.save_analysis.side_effect = IOError("Database write timeout")

        with self.assertRaises(AIPersistenceError):
            self.service.orchestrate_analysis(self.request)


if __name__ == "__main__":
    unittest.main()
