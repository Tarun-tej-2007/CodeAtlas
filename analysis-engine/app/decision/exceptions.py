"""Domain-specific exceptions for Architecture Decision Intelligence."""


class DecisionError(Exception):
    """Base exception for all architecture decision subsystem issues."""

    pass


class DecisionValidationError(DecisionError):
    """Raised when decision configurations or relationship definitions fail validation."""

    pass


class DecisionPersistenceError(DecisionError):
    """Raised when decision storage repository operations fail."""

    pass


class DecisionTraceabilityError(DecisionError):
    """Raised when parsing, mapping, or tracking code-to-decision links fails."""

    pass
