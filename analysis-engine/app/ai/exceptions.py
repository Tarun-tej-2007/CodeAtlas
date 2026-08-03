"""AI Context Domain Exceptions module.

Defines custom exception hierarchy for AI context construction, model mapping,
and serialization logic.
"""


class AIContextError(Exception):
    """Base exception class for all AI context errors."""

    pass


class AIContextValidationError(AIContextError):
    """Raised when structured AI context fails boundary checks or criteria."""

    pass


class AIContextModelError(AIContextError):
    """Raised when models are instantiated with incorrect settings or missing DTO references."""

    pass
