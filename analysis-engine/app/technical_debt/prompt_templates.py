"""Technical Debt AI Prompt Templates module."""

from typing import List

from app.ai_service.prompts import AIPromptEngine, PromptTemplate


class TechnicalDebtPromptTemplates:
    """Class responsible for managing and registering technical debt AI prompt templates."""

    TEMPLATES: List[PromptTemplate] = [
        PromptTemplate(
            name="technical_debt_summary",
            description="Summarizes codebase technical debt statistics and aggregate effort.",
            template=(
                "Analyze the following technical debt summary for project {project_name}.\n"
                "Total Remediation Effort: {Remediation Overview}\n"
                "Debt counts by category:\n"
                "{Debt Categories}"
            ),
        ),
        PromptTemplate(
            name="technical_debt_review",
            description="Prompts a detailed review of identified technical debt items.",
            template=(
                "Perform a detailed software technical debt review for project {project_name}.\n"
                "Review context sections:\n"
                "{Summary}\n"
                "{Technical Debt Findings}\n"
                "Provide a breakdown of major code smells and design risks."
            ),
        ),
        PromptTemplate(
            name="technical_debt_recommendations",
            description="Generates actionable refactoring suggestions to resolve debt.",
            template=(
                "Provide refactoring recommendations for the technical debt identified in project {project_name}:\n"
                "{Summary}\n"
                "{Recommendations Input}\n"
                "Detail recommended clean-up tasks and mitigation plans."
            ),
        ),
        PromptTemplate(
            name="technical_debt_prioritization",
            description="Prioritizes remediation tasks based on effort and impact.",
            template=(
                "Analyze and prioritize technical debt remediation for project {project_name}:\n"
                "{Summary}\n"
                "{Technical Debt Findings}\n"
                "{Remediation Overview}\n"
                "Recommend the order of tasks to maximize cleanup ROI while minimizing effort."
            ),
        ),
    ]

    def __init__(self, prompt_engine: AIPromptEngine) -> None:
        """Initializes with dependency-injected AIPromptEngine."""
        if prompt_engine is None:
            raise ValueError("AIPromptEngine dependency must not be None.")
        self.prompt_engine = prompt_engine

    def register_all(self) -> None:
        """Registers predefined technical debt prompt templates idempotently and thread-safely."""
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
