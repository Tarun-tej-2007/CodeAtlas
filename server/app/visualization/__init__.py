"""CodeAtlas visualization domain package.

Provides renderer-agnostic enumeration types for node kinds, edge kinds, layout strategies,
and grouping categories.
"""

from app.visualization.enums import EdgeKind, GroupKind, LayoutKind, NodeKind

__all__ = [
    "NodeKind",
    "EdgeKind",
    "LayoutKind",
    "GroupKind",
]
