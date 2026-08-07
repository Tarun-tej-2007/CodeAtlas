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
        import time
        import logging
        from app.ai.exceptions import AIContextError, PromptGenerationError

        logger = logging.getLogger(__name__)

        corr_id = kwargs.get("correlation_id") or request.metadata.extra_info.get("correlation_id") or str(uuid.uuid4())
        logger.info("[Correlation-ID: %s] Starting AI orchestration for project: %s", corr_id, request.project_id)

        started_at = datetime.now(timezone.utc)
        start_total = time.perf_counter()

        context_aggregation_ms = 0.0
        prompt_generation_ms = 0.0
        llm_execution_ms = 0.0
        recommendation_generation_ms = 0.0
        architecture_review_ms = 0.0
        persistence_ms = 0.0

        try:
            # 1. Aggregate repository context facts
            logger.info("[Correlation-ID: %s] Stage 1: Aggregating repository context facts...", corr_id)
            start_stage = time.perf_counter()
            try:
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
            except (AIContextError, AIValidationError) as e:
                logger.error("[Correlation-ID: %s] Aggregation validation failure: %s", corr_id, e)
                raise
            except Exception as e:
                logger.exception("[Correlation-ID: %s] Unexpected aggregation failure: %s", corr_id, e)
                raise AIContextError(f"Failed to compile codebase context: {e}") from e
            context_aggregation_ms = (time.perf_counter() - start_stage) * 1000.0

            # 2. Short-circuit check for empty repository context scope
            if context.files_count == 0 and not context.dependency_graph_summary:
                logger.info("[Correlation-ID: %s] No repository artifacts found; short-circuiting compilation...", corr_id)
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
                logger.info("[Correlation-ID: %s] Stage 5: Compile architecture review report...", corr_id)
                start_stage = time.perf_counter()
                review = self.architecture_reviewer.generate_review(context, analysis, ())
                architecture_review_ms = (time.perf_counter() - start_stage) * 1000.0

                # Persist results
                logger.info("[Correlation-ID: %s] Stage 6: Saving results to persistence...", corr_id)
                start_stage = time.perf_counter()
                try:
                    self.persistence.save_analysis(request.project_id, analysis)
                except AIPersistenceError:
                    raise
                except Exception as e:
                    logger.exception("[Correlation-ID: %s] Unexpected save empty analysis failure: %s", corr_id, e)
                    raise AIPersistenceError(f"Database write failure: {e}") from e
                persistence_ms = (time.perf_counter() - start_stage) * 1000.0

                total_orchestration_ms = (time.perf_counter() - start_total) * 1000.0
                logger.info("[Correlation-ID: %s] Completed AI orchestration in %.2fms", corr_id, total_orchestration_ms)

                timings = {
                    "context_aggregation_ms": context_aggregation_ms,
                    "prompt_generation_ms": prompt_generation_ms,
                    "llm_execution_ms": llm_execution_ms,
                    "recommendation_generation_ms": recommendation_generation_ms,
                    "architecture_review_ms": architecture_review_ms,
                    "persistence_ms": persistence_ms,
                    "total_orchestration_ms": total_orchestration_ms,
                }
                return AIResult(
                    project_id=request.project_id,
                    commit_id=request.commit_id,
                    analysis=analysis,
                    extra_info={"review": review, "timings": timings},
                )

            # 3. Build Prompt context payload
            logger.info("[Correlation-ID: %s] Stage 2: Prompt generation...", corr_id)
            start_stage = time.perf_counter()
            try:
                prompt_context = self.prompt_builder.build_prompt(request, context)
            except (PromptGenerationError, AIValidationError) as e:
                logger.error("[Correlation-ID: %s] Prompt builder validation failure: %s", corr_id, e)
                raise
            except Exception as e:
                logger.exception("[Correlation-ID: %s] Unexpected prompt builder failure: %s", corr_id, e)
                raise PromptGenerationError(f"Failed to build prompt context: {e}") from e
            prompt_generation_ms = (time.perf_counter() - start_stage) * 1000.0

            # 4. Invoke LLM provider
            logger.info("[Correlation-ID: %s] Stage 3: LLM execution...", corr_id)
            start_stage = time.perf_counter()
            try:
                raw_completion, usage_stats = self.llm_provider.generate_completion(request, prompt_context)
            except AIProviderError:
                raise
            except Exception as e:
                logger.exception("[Correlation-ID: %s] LLM execution provider failure: %s", corr_id, e)
                raise AIProviderError(f"LLM provider service failed: {e}") from e
            llm_execution_ms = (time.perf_counter() - start_stage) * 1000.0

            # 5. Extract and parse recommendations
            logger.info("[Correlation-ID: %s] Stage 4: Recommendations parsing...", corr_id)
            start_stage = time.perf_counter()
            try:
                recommendations = self.recommendation_generator.generate_recommendations(
                    request=request,
                    raw_completion=raw_completion,
                    prompt_context=prompt_context,
                    ai_context=context,
                )
            except AIValidationError:
                raise
            except Exception as e:
                logger.exception("[Correlation-ID: %s] Unexpected recommendation generator failure: %s", corr_id, e)
                raise AIValidationError(f"Failed to generate recommendations: {e}") from e
            recommendation_generation_ms = (time.perf_counter() - start_stage) * 1000.0

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
            logger.info("[Correlation-ID: %s] Stage 5: Compile architecture review report...", corr_id)
            start_stage = time.perf_counter()
            try:
                review = self.architecture_reviewer.generate_review(context, analysis, recommendations)
            except AIValidationError:
                raise
            except Exception as e:
                logger.exception("[Correlation-ID: %s] Unexpected reviewer failure: %s", corr_id, e)
                raise AIValidationError(f"Failed to compile report: {e}") from e
            architecture_review_ms = (time.perf_counter() - start_stage) * 1000.0

            # 8. Persist results
            logger.info("[Correlation-ID: %s] Stage 6: Saving results to persistence...", corr_id)
            start_stage = time.perf_counter()
            try:
                self.persistence.save_analysis(request.project_id, analysis)
            except AIPersistenceError:
                raise
            except Exception as e:
                logger.exception("[Correlation-ID: %s] Unexpected save analysis failure: %s", corr_id, e)
                raise AIPersistenceError(f"Database write failure: {e}") from e
            persistence_ms = (time.perf_counter() - start_stage) * 1000.0

            total_orchestration_ms = (time.perf_counter() - start_total) * 1000.0
            logger.info("[Correlation-ID: %s] Completed AI orchestration in %.2fms", corr_id, total_orchestration_ms)

            timings = {
                "context_aggregation_ms": context_aggregation_ms,
                "prompt_generation_ms": prompt_generation_ms,
                "llm_execution_ms": llm_execution_ms,
                "recommendation_generation_ms": recommendation_generation_ms,
                "architecture_review_ms": architecture_review_ms,
                "persistence_ms": persistence_ms,
                "total_orchestration_ms": total_orchestration_ms,
            }

            return AIResult(
                project_id=request.project_id,
                commit_id=request.commit_id,
                analysis=analysis,
                extra_info={"review": review, "timings": timings},
            )
        except Exception as e:
            logger.error("[Correlation-ID: %s] Orchestrator execution failure: %s", corr_id, e)
            if isinstance(e, AIError):
                raise
            raise AIError(f"Internal subsystem error: {e}") from e
