"""Dashboard AI Analyzer Module."""

from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.dashboard.exceptions import DashboardValidationError
from app.dashboard.models import DashboardModel
from app.dashboard.engine import DashboardAggregationEngine
from app.dashboard.context_builder import DashboardAIContextBuilder
from app.dashboard.prompt_templates import DashboardPromptTemplates


class AIDashboardAnalysisResult(BaseModel):
    """Immutable DTO holding the compiled DashboardModel and the AIResponse."""

    dashboard: DashboardModel = Field(
        ..., description="The baseline DashboardModel compiled and reviewed in this workflow."
    )
    ai_response: AIResponse = Field(
        ..., description="The post-processed, validated AI response."
    )

    model_config = ConfigDict(frozen=True)


class AIDashboardAnalyzer:
    """Orchestrates aggregating dashboard widget data and executing AI dashboard reviews."""

    def __init__(
        self,
        dashboard_engine: DashboardAggregationEngine,
        context_builder: DashboardAIContextBuilder,
        prompt_templates: DashboardPromptTemplates,
        request_pipeline: AIRequestPipeline,
        response_processor: AIResponseProcessor,
    ) -> None:
        """Initializes the orchestrator with constructor-injected dependencies."""
        if any(
            arg is None
            for arg in (
                dashboard_engine,
                context_builder,
                prompt_templates,
                request_pipeline,
                response_processor,
            )
        ):
            raise ValueError("All AIDashboardAnalyzer dependencies must not be None.")

        self.dashboard_engine = dashboard_engine
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
    ) -> AIDashboardAnalysisResult:
        """Runs the complete dashboard aggregation, templates registration, and review dispatch sequence."""
        if project_name is None or not project_name.strip():
            raise DashboardValidationError("project_name must be a non-empty string.")
        if context is None:
            raise DashboardValidationError("context must not be None.")
        if provider is None or not isinstance(provider, AIProvider):
            raise DashboardValidationError("provider must be an instance of AIProvider.")
        if model_type is None or not isinstance(model_type, AIModelType):
            raise DashboardValidationError("model_type must be an instance of AIModelType.")
        if priority is None or not isinstance(priority, RequestPriority):
            raise DashboardValidationError("priority must be an instance of RequestPriority.")

        # 1. Aggregate / Compile DashboardModel
        # Supports both "aggregate" and "compile" names flexibly
        compile_fn = getattr(self.dashboard_engine, "compile", None) or getattr(
            self.dashboard_engine, "aggregate", None
        )
        if compile_fn is None:
            raise DashboardValidationError("dashboard_engine lacks compile or aggregate method.")

        dashboard = compile_fn(project_name=project_name, context=context)

        # 2. Build AIContext
        ai_context = self.context_builder.build_context(dashboard)

        # 3. Register templates
        self.prompt_templates.register_all()

        # 4. Verify "dashboard_review" exists in prompt engine
        try:
            self.prompt_templates.prompt_engine.get_template("dashboard_review")
        except Exception as err:
            raise DashboardValidationError(f"Required prompt template 'dashboard_review' not registered: {err}")

        # 5. Execute AI Request Pipeline
        raw_response = self.request_pipeline.execute(
            provider=provider,
            model_type=model_type,
            template_name="dashboard_review",
            context=ai_context,
            variables=variables or {},
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 6. Process response
        processed_response = self.response_processor.process(raw_response)

        # 7. Return AIDashboardAnalysisResult
        return AIDashboardAnalysisResult(
            dashboard=dashboard,
            ai_response=processed_response,
        )
