"""Graph domain enums module.

Defines NodeType and EdgeType canonical enums for the CodeAtlas graph representation,
as well as DependencyNodeType and DependencyEdgeType for the dependency graph domain.
"""

from enum import Enum, StrEnum


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


class DependencyNodeType(str, Enum):
    """Represents the semantic kind of a dependency graph node."""

    PROJECT = "project"
    PACKAGE = "package"
    MODULE = "module"
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"


class DependencyEdgeType(str, Enum):
    """Represents the semantic relationship of a dependency graph edge."""

    IMPORTS = "imports"
    EXPORTS = "exports"
    CALLS = "calls"
    INHERITANCE = "inheritance"
    IMPLEMENTATION = "implementation"
    COMPOSITION = "composition"
    USAGE = "usage"
