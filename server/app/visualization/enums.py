"""Visualization domain enumerations module.

Defines renderer-agnostic enumeration types for visualization node kinds,
edge kinds, layout strategies, and grouping strategies.
"""

from enum import StrEnum


class NodeKind(StrEnum):
    """Represents visualization node categories."""

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    PACKAGE = "package"
    INTERFACE = "interface"
    ENUM = "enum"
    UNKNOWN = "unknown"


class EdgeKind(StrEnum):
    """Represents visualization edge categories."""

    CALL = "call"
    IMPORT = "import"
    INHERITANCE = "inheritance"
    REFERENCE = "reference"
    CONTAINS = "contains"


class LayoutKind(StrEnum):
    """Represents graph layout strategies."""

    NONE = "none"
    HIERARCHICAL = "hierarchical"
    FORCE_DIRECTED = "force_directed"
    RADIAL = "radial"
    GRID = "grid"


class GroupKind(StrEnum):
    """Represents logical visualization groups."""

    PACKAGE = "package"
    DIRECTORY = "directory"
    MODULE = "module"
    NAMESPACE = "namespace"
