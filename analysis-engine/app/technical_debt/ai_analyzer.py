"""AI Technical Debt Analyzer Module."""

from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.technical_debt.analyzer import TechnicalDebtAnalyzer
from app.technical_debt.context_builder import TechnicalDebtAIContextBuilder
from app.technical_debt.engine import TechnicalDebtAnalysisEngine
from app.technical_debt.models import TechnicalDebtReport
from app.technical_debt.prompt_templates import TechnicalDebtPromptTemplates
from app.technical_debt.scoring import TechnicalDebtScorer


class TechnicalDebtAIAnalysisResult(BaseModel):
    """Immutable DTO containing both the structured TechnicalDebtReport and validated AIResponse."""

    report: TechnicalDebtReport = Field(
        ..., description="The calculated codebase technical debt analysis report."
    )
    response: AIResponse = Field(
        ..., description="The validated, post-processed AI response."
    )

    model_config = ConfigDict(frozen=True)


class AITechnicalDebtAnalyzer(TechnicalDebtAnalyzer):
    """Orchestrates technical debt evaluation, weighted scoring, AI context translation, and query pipeline execution."""

    def __init__(
        self,
        analysis_engine: TechnicalDebtAnalysisEngine,
        scorer: TechnicalDebtScorer,
        context_builder: TechnicalDebtAIContextBuilder,
        prompt_templates: TechnicalDebtPromptTemplates,
        request_pipeline: AIRequestPipeline,
        response_processor: AIResponseProcessor,
    ) -> None:
        """Initializes the analyzer with dependency-injected components."""
        if any(
            arg is None
            for arg in (
                analysis_engine,
                scorer,
                context_builder,
                prompt_templates,
                request_pipeline,
                response_processor,
            )
        ):
            raise ValueError("All AITechnicalDebtAnalyzer constructor dependencies must not be None.")

        self.analysis_engine = analysis_engine
        self.scorer = scorer
        self.context_builder = context_builder
        self.prompt_templates = prompt_templates
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
    ) -> TechnicalDebtAIAnalysisResult:
        """Evaluates rules, runs scoring, builds AIContext, templates and dispatches the AI query."""
        # 1. Run TechnicalDebtAnalysisEngine (sequentially evaluates rules)
        initial_report = self.analysis_engine.analyze(
            project_name=project_name, context=context, **kwargs
        )

        # 2. Run TechnicalDebtScorer (computes weighted aggregates)
        weighted_summary = self.scorer.score(initial_report.items)

        # 3. Construct a NEW immutable TechnicalDebtReport with updated summary
        report = TechnicalDebtReport(
            project_name=initial_report.project_name,
            generated_at=initial_report.generated_at,
            items=initial_report.items,
            summary=weighted_summary,
            metadata=initial_report.metadata,
        )

        # 4. Build AIContext
        ai_context = self.context_builder.build_context(report)

        # 5. Ensure prompt templates are registered
        self.prompt_templates.register_all()

        # 6. Invoke AIRequestPipeline using the technical_debt_review template
        raw_response = self.request_pipeline.execute(
            provider=provider,
            model_type=model_type,
            template_name="technical_debt_review",
            context=ai_context,
            variables=variables or {},
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 7. Run AIResponseProcessor
        processed_response = self.response_processor.process(raw_response)

        # 8. Return TechnicalDebtAIAnalysisResult
        return TechnicalDebtAIAnalysisResult(
            report=report,
            response=processed_response,
        )
