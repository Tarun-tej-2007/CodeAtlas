"""Architecture Analysis Domain Exceptions."""


class ArchitectureAnalysisError(Exception):
    """Base exception for all architecture analysis domain errors."""

    pass


class ArchitectureRuleError(ArchitectureAnalysisError):
    """Exception raised when an architecture rule is violated or fails configuration."""

    pass
