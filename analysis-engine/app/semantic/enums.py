"""Semantic domain enums module."""

from enum import StrEnum


class SymbolKind(StrEnum):
    """Supported kinds of semantic symbols in CodeAtlas."""

    CLASS = "class"
    INTERFACE = "interface"
    METHOD = "method"
    FUNCTION = "function"
    VARIABLE = "variable"
    PARAMETER = "parameter"
    MODULE = "module"
    NAMESPACE = "namespace"
    PROPERTY = "property"
    CONSTRUCTOR = "constructor"
    ENUM = "enum"
    ENUM_MEMBER = "enum_member"
    TYPE_ALIAS = "type_alias"
    UNKNOWN = "unknown"


class ScopeKind(StrEnum):
    """Kinds of semantic lexical scopes in CodeAtlas."""

    GLOBAL = "global"
    MODULE = "module"
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    METHOD = "method"
    BLOCK = "block"
    NAMESPACE = "namespace"
    UNKNOWN = "unknown"


class ReferenceKind(StrEnum):
    """Kinds of cross-reference relationships between symbols."""

    CALL = "call"
    READ = "read"
    WRITE = "write"
    INSTANTIATE = "instantiate"
    INHERIT = "inherit"
    IMPLEMENT = "implement"
    IMPORT = "import"
    UNKNOWN = "unknown"


class VisibilityKind(StrEnum):
    """Visibility scope kinds for semantic declarations."""

    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    INTERNAL = "internal"
    PACKAGE = "package"
    UNKNOWN = "unknown"
