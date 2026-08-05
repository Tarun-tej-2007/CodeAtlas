"""Dashboard AI Prompt Templates Module."""

from typing import List

from app.ai_service.prompts import AIPromptEngine, PromptTemplate


class DashboardPromptTemplates:
    """Class responsible for managing and registering dashboard AI prompt templates."""

    TEMPLATES: List[PromptTemplate] = [
        PromptTemplate(
            name="dashboard_summary",
            description="Summarizes complete dashboard layout details.",
            template=(
                "Summarize the dashboard cards and widgets for project {project_name}.\n"
                "Overview metadata:\n"
                "{Dashboard Overview}\n"
                "Widget contents details:\n"
                "{Dashboard Widgets}"
            ),
        ),
        PromptTemplate(
            name="dashboard_review",
            description="Performs an executive review of dashboard metrics and findings.",
            template=(
                "Perform an executive review of the dashboard widgets for project {project_name}.\n"
                "Widget details:\n"
                "{Dashboard Overview}\n"
                "{Dashboard Widgets}\n"
                "Identify primary metrics, trends, and quality issues."
            ),
        ),
        PromptTemplate(
            name="dashboard_recommendations",
            description="Produces dashboard optimization and remediation roadmaps.",
            template=(
                "Generate final recommendation roadmaps for project {project_name}:\n"
                "{Dashboard Widgets}\n"
                "{Dashboard Recommendations}"
            ),
        ),
        PromptTemplate(
            name="dashboard_executive_summary",
            description="Synthesizes a high-level executive dashboard summary.",
            template=(
                "Synthesize a high-level executive dashboard summary for project {project_name}.\n"
                "Context information:\n"
                "{Dashboard Overview}\n"
                "{Dashboard Widgets}"
            ),
        ),
    ]

    def __init__(self, prompt_engine: AIPromptEngine) -> None:
        """Initializes with dependency-injected AIPromptEngine."""
        if prompt_engine is None:
            raise ValueError("AIPromptEngine dependency must not be None.")
        self.prompt_engine = prompt_engine

    def register_all(self) -> None:
        """Registers predefined dashboard prompt templates idempotently and thread-safely."""
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
