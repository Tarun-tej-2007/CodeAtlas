"""Reporting AI Prompt Templates Module."""

from typing import List

from app.ai_service.prompts import AIPromptEngine, PromptTemplate


class ReportingPromptTemplates:
    """Class responsible for managing and registering analysis reporting AI prompt templates."""

    TEMPLATES: List[PromptTemplate] = [
        PromptTemplate(
            name="report_summary",
            description="Summarizes complete analysis report details.",
            template=(
                "Summarize the analysis report for project {project_name}.\n"
                "Overview metadata:\n"
                "{Report Metadata}\n"
                "Report details:\n"
                "{Report Sections}"
            ),
        ),
        PromptTemplate(
            name="report_review",
            description="Performs an executive review of compiled sections and findings.",
            template=(
                "Perform an executive review of the report for project {project_name}.\n"
                "Report content details:\n"
                "{Report Metadata}\n"
                "{Report Sections}\n"
                "Identify primary metrics, design quality issues, and architecture risks."
            ),
        ),
        PromptTemplate(
            name="report_recommendations",
            description="Produces high-priority recommendations and remediation roadmaps.",
            template=(
                "Generate final recommendation roadmaps for project {project_name}:\n"
                "{Report Sections}\n"
                "{Recommendations Input}"
            ),
        ),
        PromptTemplate(
            name="report_executive_summary",
            description="Synthesizes a high-level executive dashboard text block.",
            template=(
                "Synthesize a high-level executive dashboard summary for project {project_name}.\n"
                "{Executive Summary Input}\n"
                "Context information:\n"
                "{Report Metadata}\n"
                "{Report Sections}"
            ),
        ),
    ]

    def __init__(self, prompt_engine: AIPromptEngine) -> None:
        """Initializes with dependency-injected AIPromptEngine."""
        if prompt_engine is None:
            raise ValueError("AIPromptEngine dependency must not be None.")
        self.prompt_engine = prompt_engine

    def register_all(self) -> None:
        """Registers predefined reporting prompt templates idempotently and thread-safely."""
        for template in self.TEMPLATES:
            try:
                # Check if template is already registered to ensure idempotency
                self.prompt_engine.get_template(template.name)
            except Exception:
                try:
                    self.prompt_engine.register_template(template)
                except Exception:
                    # Catch concurrent registration races
                    pass
