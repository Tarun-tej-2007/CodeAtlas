"""Graph domain enums module.

Defines NodeType and EdgeType canonical enums for the CodeAtlas graph representation.
"""

from enum import StrEnum


class NodeType(StrEnum):
    """Canonical node types in the CodeAtlas codebase graph."""

    MODULE = "module"
    PACKAGE = "package"
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    PARAMETER = "parameter"
    PROPERTY = "property"
    IMPORT = "import"
    EXPORT = "export"
    FILE = "file"
    PROJECT = "project"


class EdgeType(StrEnum):
    """Canonical edge relationship types in the CodeAtlas codebase graph."""

    CALLS = "calls"
    DEPENDS_ON = "depends_on"
    IMPORTS = "imports"
    EXPORTS = "exports"
    DECLARES = "declares"
    OWNS = "owns"
    CONTAINS = "contains"
    REFERENCES = "references"
