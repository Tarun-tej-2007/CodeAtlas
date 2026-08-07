"""Unit and integration tests for AI Architecture Intelligence Performance Optimization layer."""

import contextvars
import threading
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
    AIMetadata,
    AIOrchestratorService,
    AIProvider,
    AIRequest,
    AIResult,
    AIUsageStatistics,
    AIValidationError,
    ArchitectureReviewService,
    PromptBuilderService,
    RecommendationGeneratorService,
)
from app.ai.cache import execution_cache, make_hashable
from app.ai.interfaces import AIAnalysisPersistence, LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLMProvider to monitor invocation counts."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate_completion(self, request: AIRequest, prompt) -> tuple:
        self.call_count += 1
        stats = AIUsageStatistics(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        return "[]", stats


class TestAIPerformance(unittest.TestCase):
    """Verifies ContextVar execution-scoped cache lookup, hits/misses, thread/task isolation, and lifecycle resets."""

    def setUp(self) -> None:
        # Reset the ContextVar execution_cache before each test runs
        execution_cache.set(None)

        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"
        self.time_utc = datetime.now(timezone.utc)

        self.request = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            metadata=AIMetadata(
                author="Perf Tester",
                created_at=self.time_utc,
                provider=AIProvider.MOCK,
                model_name="mock-model",
            ),
        )

        # Mock collaborators
        self.mock_persistence = MagicMock(spec=AIAnalysisPersistence)
        self.llm_provider = MockLLMProvider()

        self.context_builder = AIContextAggregationService()
        self.prompt_builder = PromptBuilderService()
        self.recommendation_generator = RecommendationGeneratorService()
        self.architecture_reviewer = ArchitectureReviewService()

        self.orchestrator = AIOrchestratorService(
            context_builder=self.context_builder,
            prompt_builder=self.prompt_builder,
            llm_provider=self.llm_provider,
            recommendation_generator=self.recommendation_generator,
            architecture_reviewer=self.architecture_reviewer,
            persistence=self.mock_persistence,
        )

    def tearDown(self) -> None:
        execution_cache.set(None)

    def test_make_hashable_deterministic(self) -> None:
        """Verifies make_hashable utility creates identical keys for structurally equal payloads."""
        d1 = {"a": [1, 2, {"b": 3}], "c": "d"}
        d2 = {"c": "d", "a": [1, 2, {"b": 3}]}  # different key order

        h1 = make_hashable(d1)
        h2 = make_hashable(d2)

        self.assertEqual(h1, h2)
        # Verify hashable types are returned
        cache_dict = {h1: "success"}
        self.assertEqual(cache_dict[h2], "success")

    def test_cache_hits_within_lifecycle_scope(self) -> None:
        """Verifies duplicate invocations yield cached results when execution context cache is active."""
        # Activate cache
        token = execution_cache.set({})
        try:
            # Build context first time
            ctx1 = self.context_builder.build_context(self.project_id, self.commit_id)
            # Build context second time
            ctx2 = self.context_builder.build_context(self.project_id, self.commit_id)

            # Assert same instance/reference is returned
            self.assertIs(ctx1, ctx2)

            # Check prompt builder caching
            prompt1 = self.prompt_builder.build_prompt(self.request, ctx1)
            prompt2 = self.prompt_builder.build_prompt(self.request, ctx1)
            self.assertIs(prompt1, prompt2)
        finally:
            execution_cache.reset(token)

    def test_cache_misses_for_different_inputs(self) -> None:
        """Verifies that different inputs cause cache misses."""
        token = execution_cache.set({})
        try:
            ctx1 = self.context_builder.build_context(self.project_id, self.commit_id)
            ctx2 = self.context_builder.build_context(self.project_id, "different-commit")

            self.assertIsNot(ctx1, ctx2)
        finally:
            execution_cache.reset(token)

    def test_context_var_task_isolation(self) -> None:
        """Verifies that execution context caches do not leak between different ContextVar contexts."""
        ctx_var_1 = contextvars.copy_context()
        ctx_var_2 = contextvars.copy_context()

        # Run action in first context to seed the cache
        def run_in_1():
            token = execution_cache.set({})
            res = self.context_builder.build_context(self.project_id, self.commit_id)
            return res, execution_cache.get()

        # Run action in second context which starts with empty cache
        def run_in_2():
            token = execution_cache.set({})
            res = self.context_builder.build_context(self.project_id, self.commit_id)
            return res, execution_cache.get()

        res1, cache1 = ctx_var_1.run(run_in_1)
        res2, cache2 = ctx_var_2.run(run_in_2)

        # They should return newly compiled contexts rather than sharing the reference across ContextVar bounds
        self.assertIsNot(res1, res2)

    def test_thread_isolation(self) -> None:
        """Verifies concurrent threads executing analyses do not cross-leak cache values."""
        results = []
        errors = []

        def worker():
            try:
                # Running orchestrator will manage cache lifecycle locally to this thread
                res = self.orchestrator.orchestrate_analysis(self.request)
                results.append(res)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Thread errors occurred: {errors}")
        self.assertEqual(len(results), 3)
        # Ensure separate threads created distinct result objects
        self.assertIsNot(results[0], results[1])
        self.assertIsNot(results[1], results[2])

    def test_cache_lifecycle_cleanup_after_successful_run(self) -> None:
        """Verifies that the ContextVar is completely reset to None after orchestrator finishes."""
        self.assertEqual(execution_cache.get(), None)

        res = self.orchestrator.orchestrate_analysis(self.request)

        # After execution completes, cache must be reset to None
        self.assertEqual(execution_cache.get(), None)

    def test_cache_lifecycle_cleanup_after_exceptions(self) -> None:
        """Verifies that the cache is cleaned up even if orchestrator run raises an exception."""
        # Cause the context builder to raise validation failure
        bad_request = None

        with self.assertRaises(AIValidationError):
            self.orchestrator.orchestrate_analysis(bad_request)

        # ContextVar must still be reset to None
        self.assertEqual(execution_cache.get(), None)

    def test_repeated_orchestration_reuse(self) -> None:
        """Verifies orchestrator reuse. Duplicate orchestrator calls return cached objects."""
        from app.graph.dependency_graph import DependencyGraph
        from app.graph.dependency_models import GraphNode
        from app.graph.enums import DependencyNodeType

        dep_graph = DependencyGraph(
            nodes=[GraphNode(id="src/app.py", name="app", type=DependencyNodeType.MODULE)]
        )

        # In a single outer execution context
        token = execution_cache.set({})
        try:
            res1 = self.orchestrator.orchestrate_analysis(self.request, dependency_graph=dep_graph)
            res2 = self.orchestrator.orchestrate_analysis(self.request, dependency_graph=dep_graph)

            self.assertIs(res1, res2)
            # Verify LLM provider call count remains exactly 1!
            self.assertEqual(self.llm_provider.call_count, 1)
        finally:
            execution_cache.reset(token)


if __name__ == "__main__":
    unittest.main()
