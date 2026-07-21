"""CodeAtlas visualization domain package.

Provides renderer-agnostic enumeration types for node kinds, edge kinds, layout strategies,
and grouping categories.
"""

from app.visualization.enums import EdgeKind, GroupKind, LayoutKind, NodeKind
from app.visualization.exceptions import (
    InvalidVisualizationGraph,
    LayoutError,
    SerializationError,
    TransformationError,
    VisualizationError,
    VisualizationValidationError,
)
from app.visualization.models import (
    Position,
    VisualizationEdge,
    VisualizationGraph,
    VisualizationGroup,
    VisualizationMetadata,
    VisualizationNode,
)
from app.visualization.styles import EdgeStyle, GroupStyle, NodeStyle

__all__ = [
    # Enums
    "NodeKind",
    "EdgeKind",
    "LayoutKind",
    "GroupKind",
    # Styles
    "NodeStyle",
    "EdgeStyle",
    "GroupStyle",
    # Models
    "Position",
    "VisualizationNode",
    "VisualizationEdge",
    "VisualizationGroup",
    "VisualizationMetadata",
    "VisualizationGraph",
    # Exceptions
    "VisualizationError",
    "InvalidVisualizationGraph",
    "TransformationError",
    "SerializationError",
    "LayoutError",
    "VisualizationValidationError",
]



