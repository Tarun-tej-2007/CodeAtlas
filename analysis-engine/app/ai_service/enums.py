"""AI Service Domain Enums module.

Defines StrEnum categories for AI providers, model types, request priorities,
and response statuses.
"""

from enum import StrEnum


class AIProvider(StrEnum):
    """Supported AI model providers."""

    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AIModelType(StrEnum):
    """Abstraction tiers representing model capability classes."""

    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"


class RequestPriority(StrEnum):
    """Scheduling priority tiers for AI requests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResponseStatus(StrEnum):
    """Indicates the execution outcome of an AI request."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
