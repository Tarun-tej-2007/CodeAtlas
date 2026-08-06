"""Domain-specific exceptions for Architecture Governance."""


class GovernanceError(Exception):
    """Base exception for all architecture governance domain issues."""

    pass


class GovernanceValidationError(GovernanceError):
    """Raised when governance entities fail validation rules."""

    pass


class GovernancePersistenceError(GovernanceError):
    """Raised when repository storage query or write operations encounter errors."""

    pass


class PolicyEvaluationError(GovernanceError):
    """Raised when evaluating policy rules fails during runtime execution."""

    pass
