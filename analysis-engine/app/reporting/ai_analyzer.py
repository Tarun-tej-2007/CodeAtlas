"""AI Report Analyzer Module."""

from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.prompts import AIPromptEngine
from app.ai_service.response_processor import AIResponseProcessor
from app.reporting.exceptions import ReportGenerationError
from app.reporting.models import AnalysisReport
from app.reporting.context_builder import ReportAIContextBuilder
from app.reporting.prompt_templates import ReportingPromptTemplates


class AIReportAnalysisResult(BaseModel):
    """Immutable DTO holding the AnalysisReport and the AIResponse."""

    report: AnalysisReport = Field(
        ..., description="The baseline AnalysisReport used in this analysis execution."
    )
    ai_response: AIResponse = Field(
        ..., description="The post-processed, validated AI response."
    )

    model_config = ConfigDict(frozen=True)


class AIReportAnalyzer:
    """Coordinates compiling AIContext from reports, registering prompts, and dispatching queries."""

    def __init__(
        self,
        context_builder: ReportAIContextBuilder,
        prompt_templates: ReportingPromptTemplates,
        prompt_engine: AIPromptEngine,
        request_pipeline: AIRequestPipeline,
        response_processor: AIResponseProcessor,
    ) -> None:
        """Initializes the orchestrator with constructor-injected dependencies."""
        if any(
            arg is None
            for arg in (
                context_builder,
                prompt_templates,
                prompt_engine,
                request_pipeline,
                response_processor,
            )
        ):
            raise ValueError("All AIReportAnalyzer dependencies must not be None.")

        self.context_builder = context_builder
        self.prompt_templates = prompt_templates
        self.prompt_engine = prompt_engine
        self.request_pipeline = request_pipeline
        self.response_processor = response_processor

    def analyze(
        self,
        *,
        report: AnalysisReport,
        provider: AIProvider,
        model_type: AIModelType,
        variables: Optional[Mapping[str, Any]] = None,
        priority: RequestPriority = RequestPriority.MEDIUM,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AIReportAnalysisResult:
        """Executes the AI compilation, template validation, and dispatch query pipeline."""
        if report is None:
            raise ReportGenerationError("report input must not be None.")
        if not isinstance(report, AnalysisReport):
            raise ReportGenerationError("Input must be an instance of AnalysisReport.")
        if provider is None or not isinstance(provider, AIProvider):
            raise ReportGenerationError("provider must be an instance of AIProvider.")
        if model_type is None or not isinstance(model_type, AIModelType):
            raise ReportGenerationError("model_type must be an instance of AIModelType.")
        if priority is None or not isinstance(priority, RequestPriority):
            raise ReportGenerationError("priority must be an instance of RequestPriority.")

        # 1. Build AIContext
        ai_context = self.context_builder.build_context(report)

        # 2. Register prompt templates
        self.prompt_templates.register_all()

        # 3. Verify the template "report_review" is available in the engine
        try:
            self.prompt_engine.get_template("report_review")
        except Exception as err:
            raise ReportGenerationError(f"Required prompt template 'report_review' not registered: {err}")

        # 4. Invoke request pipeline
        raw_response = self.request_pipeline.execute(
            provider=provider,
            model_type=model_type,
            template_name="report_review",
            context=ai_context,
            variables=variables or {},
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 5. Process AIResponse
        processed_response = self.response_processor.process(raw_response)

        # 6. Return AIReportAnalysisResult DTO
        return AIReportAnalysisResult(
            report=report,
            ai_response=processed_response,
        )
