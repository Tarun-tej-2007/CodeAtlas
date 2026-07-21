"""Quality rules exceptions module.

Defines the exception hierarchy for the Quality Rules Engine in CodeAtlas.
"""


class RuleError(Exception):
    """Base exception class for all quality rule errors."""

    pass


class RuleEngineError(RuleError):
    """Raised when rule evaluation or engine execution fails."""

    pass
