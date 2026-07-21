"""CodeAtlas normalized AST package.

Provides neutral AST data models, builder logic, exception classes, and visitor pattern utilities.
"""

from app.parser.ast.builder import ASTBuilder
from app.parser.ast.exceptions import ASTBuilderError, ASTError
from app.parser.ast.models import ASTDocument, ASTNode
from app.parser.ast.visitor import ASTVisitor

__all__ = [
    # Data Models
    "ASTNode",
    "ASTDocument",
    # Exceptions
    "ASTError",
    "ASTBuilderError",
    # Builder
    "ASTBuilder",
    # Visitor Pattern
    "ASTVisitor",
]
