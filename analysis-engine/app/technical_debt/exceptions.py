"""Technical Debt Domain Exceptions module."""


class TechnicalDebtError(Exception):
    """Base exception class for all technical debt domain errors."""

    pass


class TechnicalDebtRuleError(TechnicalDebtError):
    """Raised when a technical debt rule constraint or validation fails."""

    pass
