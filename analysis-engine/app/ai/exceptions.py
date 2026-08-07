"""AI Context and Analysis exceptions module."""


class AIError(Exception):
    """Base exception class for all AI intelligence subsystem issues."""

    pass


class AIValidationError(AIError):
    """Raised when parameters, request payloads, or configurations fail validation."""

    pass


class AIProviderError(AIError):
    """Raised when interaction with external LLM platforms or providers fails."""

    pass


class AIContextError(AIError):
    """Base exception class for all AI context errors."""

    pass


class AIContextValidationError(AIContextError):
    """Raised when structured AI context fails boundary checks or criteria."""

    pass


class AIContextModelError(AIContextError):
    """Raised when models are instantiated with incorrect settings or missing DTO references."""

    pass


class AIPersistenceError(AIError):
    """Raised when saving or loading AI analysis runs to repository storage fails."""

    pass


class PromptGenerationError(AIError):
    """Raised when formatting or interpolating system prompts fails."""

    pass
