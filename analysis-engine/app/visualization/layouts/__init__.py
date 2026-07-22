"""Visualization layouts package.

Provides BaseLayoutEngine and concrete hierarchical layout engines for visualization graphs.
"""

from app.visualization.layouts.base import BaseLayoutEngine
from app.visualization.layouts.constants import (
    DEFAULT_HORIZONTAL_SPACING,
    DEFAULT_VERTICAL_SPACING,
    DEFAULT_NODE_HEIGHT,
    DEFAULT_NODE_WIDTH,
)
from app.visualization.layouts.exceptions import (
    CyclicLayoutError,
    InvalidLayoutGraph,
    LayoutEngineError,
    UnsupportedLayoutError,
)
from app.visualization.layouts.hierarchical import HierarchicalLayoutEngine

__all__ = [
    # Base layout
    "BaseLayoutEngine",
    # Hierarchical Layout
    "HierarchicalLayoutEngine",
    # Constants
    "DEFAULT_HORIZONTAL_SPACING",
    "DEFAULT_VERTICAL_SPACING",
    "DEFAULT_NODE_WIDTH",
    "DEFAULT_NODE_HEIGHT",
    # Exceptions
    "LayoutEngineError",
    "InvalidLayoutGraph",
    "CyclicLayoutError",
    "UnsupportedLayoutError",
]
