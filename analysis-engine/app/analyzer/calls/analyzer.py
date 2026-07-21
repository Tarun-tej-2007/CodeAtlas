"""Call analyzer module.

Provides the CallAnalyzer class responsible for extracting intra-file call references
and caller-callee invocation relationships from an AnalysisContext.
"""

from app.analyzer.models import AnalysisContext
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.calls.exceptions import CallAnalysisError
from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.calls.visitor import CallVisitor


class CallAnalyzer:
    """Analyzes intra-file call invocations within an AnalysisContext."""

    def __init__(self) -> None:
        """Initializes the CallAnalyzer."""
        pass

    def analyze(
        self,
        context: AnalysisContext,
        resolution_result: ResolutionResult | None = None,
    ) -> CallAnalysisResult:
        """Analyzes an AnalysisContext and extracts call invocation references.

        Args:
            context: AnalysisContext containing ASTDocument and SymbolTable.
            resolution_result: Optional ResolutionResult containing resolved intra-file references.

        Returns:
            An immutable CallAnalysisResult model.

        Raises:
            CallAnalysisError: If call detection or analysis fails.
        """
        try:
            if not context or not context.ast_document or not context.ast_document.root:
                raise CallAnalysisError("Invalid or missing ASTDocument root in AnalysisContext.")

            visitor = CallVisitor(
                document_path=context.ast_document.path,
                symbol_table=context.symbol_table,
                resolution_result=resolution_result,
            )
            visitor.visit(context.ast_document.root)

            calls = visitor.calls
            resolved_calls = sum(1 for c in calls if c.resolved)
            unresolved_calls = sum(1 for c in calls if not c.resolved)

            return CallAnalysisResult(
                calls=calls,
                call_count=len(calls),
                resolved_calls=resolved_calls,
                unresolved_calls=unresolved_calls,
            )
        except CallAnalysisError:
            raise
        except Exception as err:
            raise CallAnalysisError(
                f"Failed to analyze call invocations for '{context.ast_document.path}': {err}"
            ) from err
