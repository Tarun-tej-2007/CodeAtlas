"""Symbol resolver module.

Provides the SymbolResolver class responsible for orchestrating intra-file symbol resolution
over an AnalysisContext.
"""

from app.analyzer.models import AnalysisContext
from app.analyzer.resolution.exceptions import ResolutionError
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.resolution.visitor import ResolutionVisitor


class SymbolResolver:
    """Orchestrates intra-file symbol resolution over AnalysisContext."""

    def __init__(self) -> None:
        """Initializes the SymbolResolver."""
        pass

    def resolve(self, context: AnalysisContext) -> ResolutionResult:
        """Resolves identifier references within a single file against in-scope declarations.

        Args:
            context: AnalysisContext containing ASTDocument and SymbolTable.

        Returns:
            An immutable ResolutionResult model.

        Raises:
            ResolutionError: If intra-file symbol resolution fails.
        """
        try:
            if not context or not context.ast_document or not context.ast_document.root:
                raise ResolutionError("Invalid or missing ASTDocument root in AnalysisContext.")

            visitor = ResolutionVisitor(
                document_path=context.ast_document.path,
                symbol_table=context.symbol_table,
            )
            visitor.visit(context.ast_document.root)

            references = visitor.references
            resolved_count = sum(1 for r in references if r.resolved)
            unresolved_count = sum(1 for r in references if not r.resolved)

            return ResolutionResult(
                references=references,
                resolved_count=resolved_count,
                unresolved_count=unresolved_count,
            )
        except ResolutionError:
            raise
        except Exception as err:
            raise ResolutionError(
                f"Failed to resolve intra-file symbols for '{context.ast_document.path}': {err}"
            ) from err
