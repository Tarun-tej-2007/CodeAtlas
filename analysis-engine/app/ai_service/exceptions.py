"""AI Service Domain Exceptions module.

Defines custom exception classes for AI service configuration, requests,
provider connection issues, and response failures.
"""


class AIServiceError(Exception):
    """Base exception class for all AI Service subsystem errors."""

    pass


class AIProviderError(AIServiceError):
    """Raised when an external AI provider fails or behaves incorrectly."""

    pass


class AIRequestError(AIServiceError):
    """Raised when an AI request has invalid payloads or parameters."""

    pass


class AIResponseError(AIServiceError):
    """Raised when the response received from an AI model is invalid or cannot be parsed."""

    pass
