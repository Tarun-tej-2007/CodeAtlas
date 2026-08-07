"""AI Intelligence Orchestrator Service coordinating the end-to-end review pipeline."""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

from app.ai.enums import AIAnalysisStatus
from app.ai.exceptions import AIError, AIPersistenceError, AIProviderError, AIValidationError
from app.ai.interfaces import (
    AIAnalysisPersistence,
    AIContextBuilder,
    AIOrchestrator,
    ArchitectureReviewer,
    LLMProvider,
    PromptBuilder,
    RecommendationGenerator,
)
from app.ai.models import AIAnalysis, AIResult, AIUsageStatistics, AIRequest


class AIOrchestratorService(AIOrchestrator):
    """Concrete AIOrchestrator coordinating aggregation, prompts, LLM execution, and review generation."""

    def __init__(
        self,
        context_builder: AIContextBuilder,
        prompt_builder: PromptBuilder,
        llm_provider: LLMProvider,
        recommendation_generator: RecommendationGenerator,
        architecture_reviewer: ArchitectureReviewer,
        persistence: AIAnalysisPersistence,
    ) -> None:
        """Initializes the orchestrator service with collaborative dependencies.

        Args:
            context_builder: Subsystem context aggregation builder.
            prompt_builder: Prompt context template builder.
            llm_provider: Provider-agnostic LLM executor.
            recommendation_generator: Recommendations parser engine.
            architecture_reviewer: Analysis results synthesizer.
            persistence: Analysis serialization store.
        """
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.llm_provider = llm_provider
        self.recommendation_generator = recommendation_generator
        self.architecture_reviewer = architecture_reviewer
        self.persistence = persistence

    def orchestrate_analysis(
        self,
        request: AIRequest,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
        decisions: Optional[Tuple[Any, ...]] = None,
        **kwargs: Any,
    ) -> AIResult:
        """Coordinates the end-to-end AI review pipeline with execution-scoped cache lifecycle."""
        # Fail-fast request validation
        if request is None:
            raise AIValidationError("request must not be None.")

        from app.ai.cache import execution_cache, make_hashable
        cache = execution_cache.get()

        is_outermost = False
        token = None
        if cache is None:
            token = execution_cache.set({})
            cache = execution_cache.get()
            is_outermost = True

        cache_key = None
        if cache is not None:
            cache_key = make_hashable((
                "orchestrate_analysis", request, dependency_graph, arch_result,
                governance_result, evolution_result, decisions, kwargs
            ))
            if cache_key in cache:
                return cache[cache_key]

        try:
            res = self._orchestrate_analysis_impl(
                request=request,
                dependency_graph=dependency_graph,
                arch_result=arch_result,
                governance_result=governance_result,
                evolution_result=evolution_result,
                decisions=decisions,
                **kwargs,
            )
            if cache is not None and cache_key is not None:
                cache[cache_key] = res
            return res
        finally:
            if is_outermost and token is not None:
                execution_cache.reset(token)

    def _orchestrate_analysis_impl(
        self,
        request: AIRequest,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
        decisions: Optional[Tuple[Any, ...]] = None,
        **kwargs: Any,
    ) -> AIResult:
        started_at = datetime.now(timezone.utc)

        # 1. Aggregate repository context facts
        context = self.context_builder.build_context(
            project_id=request.project_id,
            commit_id=request.commit_id,
            dependency_graph=dependency_graph,
            arch_result=arch_result,
            governance_result=governance_result,
            evolution_result=evolution_result,
            decisions=decisions,
            **kwargs,
        )

        # 2. Short-circuit check for empty repository context scope
        if context.files_count == 0 and not context.dependency_graph_summary:
            completed_at = datetime.now(timezone.utc)
            analysis = AIAnalysis(
                project_id=request.project_id,
                commit_id=request.commit_id,
                analysis_type=request.analysis_type,
                status=AIAnalysisStatus.COMPLETED,
                recommendations=(),
                statistics=AIUsageStatistics(),
                started_at=started_at,
                completed_at=completed_at,
            )

            # Generate empty review report
            review = self.architecture_reviewer.generate_review(context, analysis, ())

            # Persist results
            try:
                self.persistence.save_analysis(request.project_id, analysis)
            except Exception as e:
                raise AIPersistenceError(f"Failed to persist empty repository analysis: {e}") from e

            return AIResult(
                project_id=request.project_id,
                commit_id=request.commit_id,
                analysis=analysis,
                extra_info={"review": review},
            )

        # 3. Build Prompt context payload
        prompt_context = self.prompt_builder.build_prompt(request, context)

        # 4. Invoke LLM provider (translate infrastructure errors to AIProviderError)
        try:
            raw_completion, usage_stats = self.llm_provider.generate_completion(request, prompt_context)
        except AIProviderError:
            raise
        except Exception as e:
            raise AIProviderError(f"LLM execution failed during orchestration: {e}") from e

        # 5. Extract and parse recommendations
        recommendations = self.recommendation_generator.generate_recommendations(
            request=request,
            raw_completion=raw_completion,
            prompt_context=prompt_context,
            ai_context=context,
        )

        completed_at = datetime.now(timezone.utc)

        # 6. Formulate analysis model
        analysis = AIAnalysis(
            project_id=request.project_id,
            commit_id=request.commit_id,
            analysis_type=request.analysis_type,
            status=AIAnalysisStatus.COMPLETED,
            recommendations=recommendations,
            statistics=usage_stats,
            started_at=started_at,
            completed_at=completed_at,
        )

        # 7. Synthesize review report
        review = self.architecture_reviewer.generate_review(context, analysis, recommendations)

        # 8. Persist results (translate infrastructure errors to AIPersistenceError)
        try:
            self.persistence.save_analysis(request.project_id, analysis)
        except Exception as e:
            raise AIPersistenceError(f"Failed to save analysis run results: {e}") from e

        # 9. Return the compiled AIResult DTO
        return AIResult(
            project_id=request.project_id,
            commit_id=request.commit_id,
            analysis=analysis,
            extra_info={"review": review},
        )
