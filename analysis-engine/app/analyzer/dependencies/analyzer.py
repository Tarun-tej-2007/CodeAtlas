"""Dependency analyzer module.

Provides the DependencyAnalyzer class responsible for orchestrating intra-file
symbol and module dependency relationship extraction over an AnalysisContext.
"""

from app.analyzer.calls import CallAnalyzer, CallAnalysisResult
from app.analyzer.dependencies.builder import DependencyBuilder
from app.analyzer.dependencies.exceptions import DependencyAnalysisError
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext
from app.analyzer.resolution import SymbolResolver, ResolutionResult


class DependencyAnalyzer:
    """Orchestrates dependency relationship extraction over AnalysisContext."""

    def __init__(self) -> None:
        """Initializes the DependencyAnalyzer."""
        pass

    def analyze(
        self,
        context: AnalysisContext,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> DependencyResult:
        """Analyzes AnalysisContext and builds deduplicated symbol and module dependencies.

        Args:
            context: AnalysisContext containing ASTDocument, SymbolTable, and ModuleMetadata.
            resolution_result: Optional ResolutionResult model.
            call_result: Optional CallAnalysisResult model.

        Returns:
            An immutable DependencyResult model.

        Raises:
            DependencyAnalysisError: If dependency analysis fails.
        """
        try:
            if not context or not context.ast_document:
                raise DependencyAnalysisError("Invalid or missing ASTDocument in AnalysisContext.")

            # Resolve symbols if resolution_result not provided
            if resolution_result is None:
                resolution_result = SymbolResolver().resolve(context)

            # Analyze calls if call_result not provided
            if call_result is None:
                call_result = CallAnalyzer().analyze(context, resolution_result=resolution_result)

            builder = DependencyBuilder()
            return builder.build(
                context=context,
                resolution_result=resolution_result,
                call_result=call_result,
            )
        except DependencyAnalysisError:
            raise
        except Exception as err:
            raise DependencyAnalysisError(
                f"Failed to analyze dependencies for '{context.ast_document.path}': {err}"
            ) from err
