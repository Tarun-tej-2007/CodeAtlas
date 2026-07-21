"""AST visitor pattern module.

Provides the generic ASTVisitor class for depth-first, pre-order traversal
over normalized ASTNode hierarchies.
"""

from app.parser.ast.models import ASTNode


class ASTVisitor:
    """Generic base class implementing the visitor pattern over normalized ASTNode trees."""

    def visit(self, node: ASTNode) -> None:
        """Performs depth-first pre-order traversal starting at the given node.

        Args:
            node: The root or subtree ASTNode to visit.
        """
        self.visit_node(node)
        for child in node.children:
            self.visit(child)

    def visit_node(self, node: ASTNode) -> None:
        """Hook method invoked for each ASTNode visited.

        Subclasses override this method to perform node type inspection or symbol extraction.

        Args:
            node: The current ASTNode being visited.
        """
        pass
