"""AI Prompt Template Engine module.

Defines prompt template DTO models, custom exceptions, and the AIPromptEngine registry.
"""

import threading
from typing import Any, Dict, Mapping, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.exceptions import AIServiceError


class AIPromptTemplateError(AIServiceError):
    """Raised when prompt template registration, validation, or rendering fails."""

    pass


class PromptTemplate(BaseModel):
    """Immutable model representing a prompt template definition."""

    name: str = Field(..., min_length=1, description="Unique identifier for the prompt template.")
    description: str = Field(..., description="Brief description of the prompt template purpose.")
    template: str = Field(..., min_length=1, description="Raw format string containing template variables.")

    model_config = ConfigDict(frozen=True)


class RenderedPrompt(BaseModel):
    """Immutable DTO representing the outcome of a rendered prompt."""

    template_name: str = Field(..., description="The name of the source template utilized.")
    prompt: str = Field(..., description="The fully rendered prompt string payload.")

    model_config = ConfigDict(frozen=True)


class AIPromptEngine:
    """Thread-safe, isolated template registry and formatting engine for AI prompts."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._templates: Dict[str, PromptTemplate] = {}

    def register_template(self, template: PromptTemplate) -> None:
        """Registers a new template. Raises AIPromptTemplateError on duplicates."""
        with self._lock:
            if template.name in self._templates:
                raise AIPromptTemplateError(f"Prompt template '{template.name}' is already registered.")
            self._templates[template.name] = template

    def get_template(self, name: str) -> PromptTemplate:
        """Retrieves a registered template. Raises AIPromptTemplateError if not found."""
        with self._lock:
            tmpl = self._templates.get(name)
            if tmpl is None:
                raise AIPromptTemplateError(f"Prompt template '{name}' is not registered.")
            return tmpl

    def render(self, name: str, variables: Mapping[str, Any]) -> RenderedPrompt:
        """Renders the template with variables. Converts formatting errors to AIPromptTemplateError."""
        tmpl = self.get_template(name)
        try:
            rendered_text = tmpl.template.format(**variables)
            return RenderedPrompt(template_name=name, prompt=rendered_text)
        except KeyError as e:
            raise AIPromptTemplateError(
                f"Failed to render template '{name}': missing required variable '{e.args[0]}'."
            ) from e
        except ValueError as e:
            raise AIPromptTemplateError(f"Failed to render template '{name}': invalid format syntax ({e}).") from e
        except Exception as e:
            raise AIPromptTemplateError(f"Failed to render template '{name}': {e}") from e

    def list_templates(self) -> Tuple[PromptTemplate, ...]:
        """Returns a list of all registered templates sorted alphabetically by template name."""
        with self._lock:
            sorted_keys = sorted(self._templates.keys())
            return tuple(self._templates[k] for k in sorted_keys)

    def remove_template(self, name: str) -> None:
        """Removes a template from the engine. Raises AIPromptTemplateError if not found."""
        with self._lock:
            if name not in self._templates:
                raise AIPromptTemplateError(f"Prompt template '{name}' is not registered.")
            del self._templates[name]

    def clear(self) -> None:
        """Clears all templates from the engine registry."""
        with self._lock:
            self._templates.clear()

    def __contains__(self, name: str) -> bool:
        """Checks template existence in registry."""
        with self._lock:
            return name in self._templates

    def __len__(self) -> int:
        """Returns number of registered templates."""
        with self._lock:
            return len(self._templates)
