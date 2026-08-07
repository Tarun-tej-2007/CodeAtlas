"""Integration and unit tests for the AI intelligence production hardening layer."""

import logging
import unittest
import uuid
from datetime import datetime, timezone
from typing import Generator, Optional
from unittest.mock import MagicMock

from app.ai import (
    AIAnalysis,
    AIAnalysisStatus,
    AIAnalysisType,
    AIContext,
    AIContextAggregationService,
    AIError,
    AIMetadata,
    AIOrchestratorService,
    AIProvider,
    AIRequest,
    AIResult,
    AIUsageStatistics,
    AIValidationError,
    AIPersistenceError,
    AIProviderError,
    ArchitectureReviewService,
    PromptBuilderService,
    RecommendationGeneratorService,
)
from app.ai.cache import execution_cache
from app.ai.interfaces import AIAnalysisPersistence, LLMProvider
from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphNode
from app.graph.enums import DependencyNodeType


class CapturingHandler(logging.Handler):
    """Logging handler to capture formatted messages for assertion checks."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class TestAIHardening(unittest.TestCase):
    """Verifies correlation ID tracing, structured logging, timing metrics, and exception mappings."""

    def setUp(self) -> None:
        # Reset the ContextVar execution_cache before each test runs
        execution_cache.set(None)

        self.project_id = uuid.uuid4()
        self.commit_id = "commit-xyz-987"
        self.correlation_id = f"corr-{uuid.uuid4()}"
        self.time_utc = datetime.now(timezone.utc)

        self.metadata = AIMetadata(
            author="Harden Tester",
            created_at=self.time_utc,
            provider=AIProvider.MOCK,
            model_name="mock-model",
            extra_info={"correlation_id": self.correlation_id},
        )
        self.request = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.SECURITY_REVIEW,
            metadata=self.metadata,
        )

        # Build dummy non-empty dependency graph to bypass short-circuiting
        self.dep_graph = DependencyGraph(
            nodes=[GraphNode(id="src/main.py", name="main", type=DependencyNodeType.MODULE)]
        )

        # Mock collaborators
        self.mock_persistence = MagicMock(spec=AIAnalysisPersistence)
        self.mock_llm = MagicMock(spec=LLMProvider)

        # Set up LLM mock returns
        self.mock_llm.generate_completion.return_value = (
            "[]",
            AIUsageStatistics(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

        self.context_builder = AIContextAggregationService()
        self.prompt_builder = PromptBuilderService()
        self.recommendation_generator = RecommendationGeneratorService()
        self.architecture_reviewer = ArchitectureReviewService()

        self.orchestrator = AIOrchestratorService(
            context_builder=self.context_builder,
            prompt_builder=self.prompt_builder,
            llm_provider=self.mock_llm,
            recommendation_generator=self.recommendation_generator,
            architecture_reviewer=self.architecture_reviewer,
            persistence=self.mock_persistence,
        )

        # Hook logger to capture messages
        self.logger = logging.getLogger("app.ai.ai_orchestrator")
        self.logger.setLevel(logging.INFO)
        self.handler = CapturingHandler()
        self.logger.addHandler(self.handler)

    def tearDown(self) -> None:
        self.logger.removeHandler(self.handler)
        execution_cache.set(None)

    def test_correlation_id_propagation_and_logging(self) -> None:
        """Verifies correlation ID prefixing in logs during orchestration pipeline."""
        res = self.orchestrator.orchestrate_analysis(self.request, dependency_graph=self.dep_graph)

        self.assertIsNotNone(res)
        log_messages = [r.getMessage() for r in self.handler.records]
        
        # Verify that all logs contain the Correlation-ID prefix
        self.assertTrue(len(log_messages) > 0)
        for msg in log_messages:
            self.assertIn(f"[Correlation-ID: {self.correlation_id}]", msg)

    def test_timing_metrics_generation_and_persistence(self) -> None:
        """Verifies that execution duration metrics are computed and persisted in extra_info."""
        res = self.orchestrator.orchestrate_analysis(self.request, dependency_graph=self.dep_graph)

        timings = res.extra_info.get("timings")
        self.assertIsNotNone(timings)
        
        # Verify that all requested timing categories are present
        required_keys = (
            "context_aggregation_ms",
            "prompt_generation_ms",
            "llm_execution_ms",
            "recommendation_generation_ms",
            "architecture_review_ms",
            "persistence_ms",
            "total_orchestration_ms",
        )
        for key in required_keys:
            self.assertIn(key, timings)
            self.assertIsInstance(timings[key], float)
            self.assertTrue(timings[key] >= 0.0)

    def test_exception_translation_on_provider_failures(self) -> None:
        """Verifies that arbitrary LLM execution errors are translated to AIProviderError."""
        self.mock_llm.generate_completion.side_effect = RuntimeError("API rate limit exceeded")

        with self.assertRaises(AIProviderError):
            self.orchestrator.orchestrate_analysis(self.request, dependency_graph=self.dep_graph)

    def test_exception_translation_on_persistence_failures(self) -> None:
        """Verifies that storage write failures are translated to AIPersistenceError."""
        self.mock_persistence.save_analysis.side_effect = OSError("Disk full")

        with self.assertRaises(AIPersistenceError):
            self.orchestrator.orchestrate_analysis(self.request, dependency_graph=self.dep_graph)

    def test_unexpected_exception_mapping_to_ai_error(self) -> None:
        """Verifies unexpected errors are mapped to generic AIError to prevent infrastructure leaks."""
        # Force a generic exception in context builder
        mock_context_builder = MagicMock()
        mock_context_builder.build_context.side_effect = TypeError("Invalid parameter type mapping")

        broken_orchestrator = AIOrchestratorService(
            context_builder=mock_context_builder,
            prompt_builder=self.prompt_builder,
            llm_provider=self.mock_llm,
            recommendation_generator=self.recommendation_generator,
            architecture_reviewer=self.architecture_reviewer,
            persistence=self.mock_persistence,
        )

        with self.assertRaises(AIError) as context:
            broken_orchestrator.orchestrate_analysis(self.request)

        # Original infrastructure TypeError details should be wrapped/shielded
        self.assertNotIn("TypeError", str(context.exception))

    def test_context_var_cleanup_on_failures(self) -> None:
        """Verifies that ContextVar cache is cleaned up even when provider or persistence calls fail."""
        self.mock_llm.generate_completion.side_effect = RuntimeError("Network timeout")

        with self.assertRaises(AIProviderError):
            self.orchestrator.orchestrate_analysis(self.request, dependency_graph=self.dep_graph)

        # ContextVar must still be reset to None
        self.assertIsNone(execution_cache.get())


if __name__ == "__main__":
    unittest.main()
