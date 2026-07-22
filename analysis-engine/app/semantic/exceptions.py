"""Semantic domain exceptions module."""


class SemanticError(Exception):
    """Base exception class for all semantic domain errors."""

    pass


class SemanticAnalysisError(SemanticError):
    """Raised when an error occurs during semantic analysis orchestration or execution."""

    pass


class SemanticModelError(SemanticError):
    """Raised when a semantic model fails validation or contains invalid mappings."""

    pass


class SemanticResolutionError(SemanticError):
    """Raised when reference resolution or scoping resolution fails."""

    pass
