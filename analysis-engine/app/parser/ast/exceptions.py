"""AST domain exceptions module.

Defines the exception hierarchy for normalized AST building and traversal in CodeAtlas.
"""


class ASTError(Exception):
    """Base exception class for all normalized AST errors."""

    pass


class ASTBuilderError(ASTError):
    """Raised when constructing a normalized ASTNode or ASTDocument fails."""

    pass
