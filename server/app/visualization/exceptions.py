"""Visualization exceptions module.

Defines the exception hierarchy for visualization domain errors, graph transformation,
serialization, layout, and validation failures.
"""


class VisualizationError(Exception):
    """Base exception class for all visualization subsystem errors."""

    pass


class InvalidVisualizationGraph(VisualizationError):
    """Raised when a visualization graph is structurally invalid."""

    pass


class TransformationError(VisualizationError):
    """Raised when converting a RepositoryGraph into a VisualizationGraph fails."""

    pass


class SerializationError(VisualizationError):
    """Raised when visualization graph serialization or deserialization fails."""

    pass


class LayoutError(VisualizationError):
    """Raised when spatial layout calculation fails."""

    pass


class VisualizationValidationError(VisualizationError):
    """Raised when visualization-specific validation rules fail."""

    pass
