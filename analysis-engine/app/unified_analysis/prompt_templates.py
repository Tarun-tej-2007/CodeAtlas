"""Unified AI Prompt Templates Module."""

from typing import List

from app.ai_service.prompts import AIPromptEngine, PromptTemplate


class UnifiedAnalysisPromptTemplates:
    """Class responsible for managing and registering unified analysis AI prompt templates."""

    TEMPLATES: List[PromptTemplate] = [
        PromptTemplate(
            name="unified_analysis_summary",
            description="Summarizes complete repository scan, parse, quality, and architectural results.",
            template=(
                "Generate a summary for project {project_name}.\n"
                "Overview context:\n"
                "{Repository Summary}\n"
                "Subsystem metrics:\n"
                "{Scan Results}\n"
                "{Parse Results}\n"
                "{Quality Analysis}"
            ),
        ),
        PromptTemplate(
            name="unified_analysis_review",
            description="Performs an E2E technical health and architecture review of the codebase.",
            template=(
                "Perform a unified health review of project {project_name}.\n"
                "Inputs:\n"
                "{Repository Summary}\n"
                "{Architecture Analysis}\n"
                "{Technical Debt Analysis}\n"
                "Outline code health issues and critical architecture bottlenecks."
            ),
        ),
        PromptTemplate(
            name="unified_analysis_recommendations",
            description="Produces actionable refactoring roadmap recommendations.",
            template=(
                "Generate refactoring roadmap recommendations for project {project_name}:\n"
                "{Repository Summary}\n"
                "{Recommendations Input}\n"
                "{Technical Debt Analysis}\n"
                "Detail remediation steps, mitigation plans, and cleanup roadmaps."
            ),
        ),
        PromptTemplate(
            name="unified_analysis_executive_summary",
            description="Provides a high-level executive summary of project quality and debt.",
            template=(
                "Compile an executive dashboard summary for project {project_name}:\n"
                "Details:\n"
                "{Repository Summary}\n"
                "{Scan Results}\n"
                "{Architecture Analysis}\n"
                "{Quality Analysis}\n"
                "{Technical Debt Analysis}\n"
                "{Metadata}"
            ),
        ),
    ]

    def __init__(self, prompt_engine: AIPromptEngine) -> None:
        """Initializes with dependency-injected AIPromptEngine."""
        if prompt_engine is None:
            raise ValueError("AIPromptEngine dependency must not be None.")
        self.prompt_engine = prompt_engine

    def register_all(self) -> None:
        """Registers predefined unified analysis prompt templates idempotently and thread-safely."""
        for template in self.TEMPLATES:
            try:
                # Check if template is already registered to ensure idempotency
                self.prompt_engine.get_template(template.name)
            except Exception:
                try:
                    self.prompt_engine.register_template(template)
                except Exception:
                    # Catch potential concurrent registration race wins by other threads
                    pass
