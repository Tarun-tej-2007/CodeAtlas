"""Visualization pipeline exceptions module.

Defines exceptions raised during the orchestration stages of the visualization pipeline.
"""


class VisualizationPipelineError(Exception):
    """Base exception class for all visualization pipeline errors."""

    pass


class TransformationStageError(VisualizationPipelineError):
    """Raised when the transformation stage of the pipeline fails."""

    pass


class LayoutStageError(VisualizationPipelineError):
    """Raised when the layout computing stage of the pipeline fails."""

    pass


class SerializationStageError(VisualizationPipelineError):
    """Raised when the serialization stage of the pipeline fails."""

    pass
