"""Quality Analysis Domain Exceptions module."""


class QualityAnalysisError(Exception):
    """Base exception class for all quality analysis domain errors."""

    pass


class QualityMetricError(QualityAnalysisError):
    """Raised when a quality metric is invalid, violates constraints, or configuration fails."""

    pass
