"""Architecture AI Prompt Templates module."""

from typing import List

from app.ai_service.prompts import AIPromptTemplateError, AIPromptEngine, PromptTemplate


class ArchitecturePromptTemplates:
    """Class responsible for managing and registering architecture-related AI prompt templates."""

    # Pre-defined, generic architecture templates
    TEMPLATES: List[PromptTemplate] = [
        PromptTemplate(
            name="architecture_summary",
            description="Summarizes high-level architectural metrics and counts.",
            template=(
                "Analyze the following architectural summary for project {project_name}.\n"
                "Total Issues: {total_issues}\n"
                "Severity Counts:\n"
                "  INFO: {info_count}\n"
                "  LOW: {low_count}\n"
                "  MEDIUM: {medium_count}\n"
                "  HIGH: {high_count}\n"
                "  CRITICAL: {critical_count}"
            ),
        ),
        PromptTemplate(
            name="architecture_review",
            description="Prompts a detailed review of identified architectural violations.",
            template=(
                "Perform a detailed architectural review for project {project_name}.\n"
                "Review context sections:\n"
                "{Summary}\n"
                "{Architecture Issues}\n"
                "Provide a breakdown of major risks and violations."
            ),
        ),
        PromptTemplate(
            name="architecture_recommendations",
            description="Generates refactoring recommendations and mitigation plans.",
            template=(
                "Provide refactoring recommendations for the following issues identified in project {project_name}:\n"
                "{Summary}\n"
                "{Recommendations Input}\n"
                "Detail recommended structural edits and migration plans."
            ),
        ),
        PromptTemplate(
            name="dependency_analysis",
            description="Analyzes structural dependency graph cycles and long chains.",
            template=(
                "Analyze the dependency graph structure and violations for project {project_name}:\n"
                "{Summary}\n"
                "{Dependency Analysis}\n"
                "Focus on resolving circular dependencies and long transit chains."
            ),
        ),
    ]

    def __init__(self, prompt_engine: AIPromptEngine) -> None:
        """Initializes the prompt template manager with dependency-injected AIPromptEngine."""
        if prompt_engine is None:
            raise ValueError("AIPromptEngine dependency must not be None.")
        self.prompt_engine = prompt_engine

    def register_all(self) -> None:
        """Registers all predefined architecture templates with the prompt engine.

        Guarantees idempotency and safe concurrent execution.
        """
        for tmpl in self.TEMPLATES:
            # Check contains to skip if already registered
            if tmpl.name not in self.prompt_engine:
                try:
                    self.prompt_engine.register_template(tmpl)
                except AIPromptTemplateError:
                    # In case of concurrent registration race condition, safely catch and ignore duplicate error
                    pass
