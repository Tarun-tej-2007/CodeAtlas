"""AI Context Manager module.

Defines immutable context DTO models, custom exceptions, and the AIContextManager component.
"""

from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ai_service.exceptions import AIServiceError


class AIContextError(AIServiceError):
    """Raised when context creation, lookup, or modification fails."""

    pass


class ContextSection(BaseModel):
    """Immutable section of structured context."""

    name: str = Field(..., min_length=1, description="Unique identifier for the section.")
    content: str = Field(..., description="The context content string payload.")

    model_config = ConfigDict(frozen=True)


class AIContext(BaseModel):
    """Immutable context mapping metadata and context sections."""

    title: str = Field(..., min_length=1, description="Title identifier of the context.")
    description: Optional[str] = Field(default=None, description="Optional high-level description.")
    metadata: Mapping[str, Any] = Field(default_factory=dict, description="Immutable metadata configuration map.")
    sections: Tuple[ContextSection, ...] = Field(default_factory=tuple, description="Sorted list of sections.")

    model_config = ConfigDict(frozen=True)

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Wraps dictionaries inside MappingProxyType to enforce read-only runtime immutability."""
        return MappingProxyType(dict(v))


class AIContextManager:
    """Stateless manager for assembling and modifying immutable AIContext aggregates."""

    def create_context(
        self,
        title: str,
        description: Optional[str],
        metadata: Mapping[str, Any],
        sections: Iterable[ContextSection],
    ) -> AIContext:
        """Assembles a new immutable AIContext. Ensures unique section names."""
        sections_tuple = tuple(sections)
        seen = set()
        for sec in sections_tuple:
            if sec.name in seen:
                raise AIContextError(
                    f"Duplicate section name '{sec.name}' discovered during context creation."
                )
            seen.add(sec.name)

        return AIContext(
            title=title,
            description=description,
            metadata=metadata,
            sections=sections_tuple,
        )

    def add_section(self, context: AIContext, section: ContextSection) -> AIContext:
        """Adds a section to a context. Raises AIContextError if duplicate."""
        if any(sec.name == section.name for sec in context.sections):
            raise AIContextError(f"Section name '{section.name}' already exists in context.")

        new_sections = context.sections + (section,)
        return AIContext(
            title=context.title,
            description=context.description,
            metadata=context.metadata,
            sections=new_sections,
        )

    def replace_section(
        self, context: AIContext, section_name: str, replacement: ContextSection
    ) -> AIContext:
        """Replaces a section in the context. Raises AIContextError if section_name is not found."""
        if replacement.name != section_name:
            if any(sec.name == replacement.name for sec in context.sections):
                raise AIContextError(
                    f"Cannot replace with section name '{replacement.name}' as it already exists."
                )

        new_sections = []
        replaced = False
        for sec in context.sections:
            if sec.name == section_name:
                new_sections.append(replacement)
                replaced = True
            else:
                new_sections.append(sec)

        if not replaced:
            raise AIContextError(f"Section '{section_name}' not found in context for replacement.")

        return AIContext(
            title=context.title,
            description=context.description,
            metadata=context.metadata,
            sections=tuple(new_sections),
        )

    def remove_section(self, context: AIContext, section_name: str) -> AIContext:
        """Removes a section from the context. Raises AIContextError if section_name is not found."""
        new_sections = []
        removed = False
        for sec in context.sections:
            if sec.name == section_name:
                removed = True
            else:
                new_sections.append(sec)

        if not removed:
            raise AIContextError(f"Section '{section_name}' not found in context for removal.")

        return AIContext(
            title=context.title,
            description=context.description,
            metadata=context.metadata,
            sections=tuple(new_sections),
        )

    def get_section(self, context: AIContext, section_name: str) -> ContextSection:
        """Retrieves a section by name. Raises AIContextError if not found."""
        for sec in context.sections:
            if sec.name == section_name:
                return sec
        raise AIContextError(f"Section '{section_name}' not found in context.")

    def list_sections(self, context: AIContext) -> Tuple[ContextSection, ...]:
        """Returns the tuple of sections preserved in order."""
        return context.sections
