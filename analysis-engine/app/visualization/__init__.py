"""CodeAtlas visualization engine package.

Provides enums, style models, domain models, exceptions, transformer, and serializer
for renderer-agnostic codebase codebase visualization.
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
from app.visualization.serializer import VisualizationSerializer
from app.visualization.styles import EdgeStyle, GroupStyle, NodeStyle
from app.visualization.transformers import VisualizationTransformer

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
    # Transformers
    "VisualizationTransformer",
    # Serializers
    "VisualizationSerializer",
]
