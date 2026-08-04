"""AI Architecture Analyzer module."""

from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIResponse
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor
from app.architecture_analysis.analyzer import ArchitectureAnalyzer
from app.architecture_analysis.context_builder import ArchitectureAIContextBuilder
from app.architecture_analysis.engine import ArchitectureRuleEngine
from app.architecture_analysis.models import ArchitectureReport
from app.architecture_analysis.prompt_templates import ArchitecturePromptTemplates


class AIArchitectureAnalysisResult(BaseModel):
    """Immutable DTO containing both the structured local report and the final AI review response."""

    architecture_report: ArchitectureReport = Field(
        ..., description="The locally generated architecture violation report."
    )
    ai_response: AIResponse = Field(
        ..., description="The validated, post-processed AI response."
    )

    model_config = ConfigDict(frozen=True)


class AIArchitectureAnalyzer(ArchitectureAnalyzer):
    """Orchestrates rule engine evaluation, AI context translation, prompt registration, and query pipeline dispatches."""

    def __init__(
        self,
        rule_engine: ArchitectureRuleEngine,
        context_builder: ArchitectureAIContextBuilder,
        prompt_templates: ArchitecturePromptTemplates,
        request_pipeline: AIRequestPipeline,
        response_processor: AIResponseProcessor,
    ) -> None:
        """Initializes the analyzer with dependency-injected services."""
        self.rule_engine = rule_engine
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
    ) -> AIArchitectureAnalysisResult:
        """Runs the rule engine, converts the report to AIContext, templates and dispatches the AI request."""
        # 1. Execute Rule Engine
        report = self.rule_engine.analyze(project_name=project_name, context=context)

        # 2. Convert to AIContext
        ai_context = self.context_builder.build_context(report)

        # 3. Ensure Templates are Registered
        self.prompt_templates.register_all()

        # 4. Execute AI Request Pipeline using 'architecture_review' template
        raw_response = self.request_pipeline.execute(
            provider=provider,
            model_type=model_type,
            template_name="architecture_review",
            context=ai_context,
            variables=variables or {},
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 5. Post-Process AI Response
        processed_response = self.response_processor.process(raw_response)

        # 6. Return Structured Integration Result
        return AIArchitectureAnalysisResult(
            architecture_report=report,
            ai_response=processed_response,
        )
