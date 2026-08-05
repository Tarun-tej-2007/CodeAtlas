"""Report Domain Exceptions Module."""


class ReportingError(Exception):
    """Base exception for all reporting subsystem errors."""
    pass


class ReportGenerationError(ReportingError):
    """Raised when report generation fails due to input validation or compilation errors."""
    pass
