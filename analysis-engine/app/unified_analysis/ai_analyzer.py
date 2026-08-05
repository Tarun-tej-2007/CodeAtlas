"""AI Unified Analyzer Module."""

from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.unified_analysis.analyzer import UnifiedAnalysisAnalyzer
from app.unified_analysis.context_builder import UnifiedAIContextBuilder
from app.unified_analysis.engine import UnifiedAnalysisEngine
from app.unified_analysis.models import UnifiedAnalysisReport
from app.unified_analysis.prompt_templates import UnifiedAnalysisPromptTemplates


class UnifiedAIAnalysisResult(BaseModel):
    """Immutable DTO holding the UnifiedAnalysisReport and the AIResponse."""

    report: UnifiedAnalysisReport = Field(
        ..., description="The calculated aggregate unified analysis report."
    )
    ai_response: AIResponse = Field(
        ..., description="The post-processed, validated AI response."
    )

    model_config = ConfigDict(frozen=True)


class AIUnifiedAnalyzer(UnifiedAnalysisAnalyzer):
    """Coordinates unified evaluations, AI context translation, and query pipeline execution."""

    def __init__(
        self,
        engine: UnifiedAnalysisEngine,
        context_builder: UnifiedAIContextBuilder,
        prompt_templates: UnifiedAnalysisPromptTemplates,
        request_pipeline: AIRequestPipeline,
        response_processor: AIResponseProcessor,
    ) -> None:
        """Initializes the orchestrator with constructor-injected dependencies."""
        if any(
            arg is None
            for arg in (
                engine,
                context_builder,
                prompt_templates,
                request_pipeline,
                response_processor,
            )
        ):
            raise ValueError("All AIUnifiedAnalyzer dependencies must not be None.")

        self.engine = engine
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
    ) -> UnifiedAIAnalysisResult:
        """Runs the unified analysis pipeline and query execution flow."""
        if project_name is None:
            raise ValueError("project_name must not be None.")
        if not isinstance(project_name, str):
            raise TypeError("project_name must be a string.")
        if not project_name.strip():
            raise ValueError("project_name must be a non-empty string.")
        if context is None:
            raise ValueError("context must not be None.")
        if provider is None:
            raise ValueError("provider must not be None.")
        if not isinstance(provider, AIProvider):
            raise TypeError("provider must be an instance of AIProvider.")
        if model_type is None:
            raise ValueError("model_type must not be None.")
        if not isinstance(model_type, AIModelType):
            raise TypeError("model_type must be an instance of AIModelType.")
        if priority is None:
            raise ValueError("priority must not be None.")
        if not isinstance(priority, RequestPriority):
            raise TypeError("priority must be an instance of RequestPriority.")
        # 1. Execute UnifiedAnalysisEngine
        report = self.engine.analyze(project_name=project_name, context=context, **kwargs)

        # 2. Translate report into AIContext
        ai_context = self.context_builder.build_context(report)

        # 3. Ensure prompt templates are registered
        self.prompt_templates.register_all()

        # 4. Verify the template "unified_analysis_review" is available
        # This will raise an exception if not found, propagating directly
        self.prompt_templates.prompt_engine.get_template("unified_analysis_review")

        # 5. Invoke AIRequestPipeline
        raw_response = self.request_pipeline.execute(
            provider=provider,
            model_type=model_type,
            template_name="unified_analysis_review",
            context=ai_context,
            variables=variables or {},
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 6. Post-process the AI response
        processed_response = self.response_processor.process(raw_response)

        # 7. Return UnifiedAIAnalysisResult
        return UnifiedAIAnalysisResult(
            report=report,
            ai_response=processed_response,
        )
