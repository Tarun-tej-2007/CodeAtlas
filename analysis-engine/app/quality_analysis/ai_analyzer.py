"""AI Quality Analyzer Module."""

from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.prompts import AIPromptEngine, PromptTemplate
from app.ai_service.response_processor import AIResponseProcessor
from app.quality_analysis.analyzer import QualityAnalyzer
from app.quality_analysis.context_builder import QualityAIContextBuilder
from app.quality_analysis.engine import QualityEvaluationEngine
from app.quality_analysis.models import QualityReport
from app.quality_analysis.scoring import QualityScorer


class QualityAIAnalysisResult(BaseModel):
    """Immutable DTO containing both the structured QualityReport and validated AIResponse."""

    quality_report: QualityReport = Field(
        ..., description="The calculated codebase quality analysis report."
    )
    ai_response: AIResponse = Field(
        ..., description="The validated, post-processed AI response."
    )

    model_config = ConfigDict(frozen=True)


class AIQualityAnalyzer(QualityAnalyzer):
    """Orchestrates quality evaluation, weighted scoring, AI context translation, and query pipeline execution."""

    def __init__(
        self,
        evaluation_engine: QualityEvaluationEngine,
        scorer: QualityScorer,
        context_builder: QualityAIContextBuilder,
        prompt_engine: AIPromptEngine,
        request_pipeline: AIRequestPipeline,
        response_processor: AIResponseProcessor,
    ) -> None:
        """Initializes the analyzer with dependency-injected components."""
        if any(
            arg is None
            for arg in (
                evaluation_engine,
                scorer,
                context_builder,
                prompt_engine,
                request_pipeline,
                response_processor,
            )
        ):
            raise ValueError("All AIQualityAnalyzer constructor dependencies must not be None.")

        self.evaluation_engine = evaluation_engine
        self.scorer = scorer
        self.context_builder = context_builder
        self.prompt_engine = prompt_engine
        self.request_pipeline = request_pipeline
        self.response_processor = response_processor

    def analyze(
        self,
        *,
        project_name: str,
        context: Any,
        provider: AIProvider,
        model_type: AIModelType,
        variables: Optional[Mapping[str, Any]] = None,
        priority: RequestPriority = RequestPriority.MEDIUM,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> QualityAIAnalysisResult:
        """Evaluates metrics, runs scoring, builds AIContext, templates and dispatches the AI query."""
        # 1. Run QualityEvaluationEngine (sequentially evaluates metrics)
        initial_report = self.evaluation_engine.analyze(
            project_name=project_name, context=context, **kwargs
        )

        # 2. Run QualityScorer (computes weighted aggregates)
        weighted_summary = self.scorer.score(initial_report.metrics)

        # Re-assemble QualityReport using the weighted summary
        report = QualityReport(
            project_name=initial_report.project_name,
            generated_at=initial_report.generated_at,
            metrics=initial_report.metrics,
            summary=weighted_summary,
            metadata=initial_report.metadata,
        )

        # 3. Build AIContext
        ai_context = self.context_builder.build_context(report)

        # 4. Ensure quality templates are registered
        self._ensure_prompt_template_registered()

        # 5. Invoke AIRequestPipeline using the quality review template
        raw_response = self.request_pipeline.execute(
            provider=provider,
            model_type=model_type,
            template_name="quality_review",
            context=ai_context,
            variables=variables or {},
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 6. Validate and post-process AIResponse
        processed_response = self.response_processor.process(raw_response)

        # 7. Return QualityAIAnalysisResult
        return QualityAIAnalysisResult(
            quality_report=report,
            ai_response=processed_response,
        )

    def _ensure_prompt_template_registered(self) -> None:
        """Guarantees that quality review template is registered in the prompt engine."""
        try:
            self.prompt_engine.get_template("quality_review")
        except Exception:
            # Register if not present
            self.prompt_engine.register_template(
                PromptTemplate(
                    name="quality_review",
                    description="Detailed quality review prompt.",
                    template=(
                        "Perform a detailed software quality review for project {project_name}.\n"
                        "Review context sections:\n"
                        "{Summary}\n"
                        "{Quality Metrics}\n"
                        "Provide actionable refactoring suggestions."
                    ),
                )
            )
