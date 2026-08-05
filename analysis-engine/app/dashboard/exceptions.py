"""Dashboard Exceptions Module."""


class DashboardError(Exception):
    """Base exception class for all dashboard subsystem errors."""

    pass


class DashboardValidationError(DashboardError):
    """Exception raised when dashboard constraints or validations are violated."""

    pass
