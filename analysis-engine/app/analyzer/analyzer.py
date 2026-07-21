"""Static analyzer base interface and execution pipeline module.

Provides the abstract BaseAnalyzer interface and AnalysisPipeline orchestrator.
"""

from abc import ABC, abstractmethod
import time

from app.analyzer.exceptions import AnalyzerExecutionError
from app.analyzer.models import (
    AnalysisContext,
    AnalysisResult,
    Diagnostic,
    Severity,
)
from app.analyzer.registry import AnalyzerRegistry


class BaseAnalyzer(ABC):
    """Abstract base class interface for static analyzers."""

    @abstractmethod
    def analyze(self, context: AnalysisContext) -> list[Diagnostic]:
        """Analyzes a single AnalysisContext and returns a list of Diagnostics.

        Args:
            context: AnalysisContext containing ASTDocument, SymbolTable, and ModuleMetadata.

        Returns:
            List of emitted Diagnostic models.

        Raises:
            AnalysisError: If static analysis pass encounters unrecoverable errors.
        """
        pass


class AnalysisPipeline:
    """Orchestrates static analysis execution across registered analyzers."""

    def __init__(self, registry: AnalyzerRegistry | None = None) -> None:
        """Initializes AnalysisPipeline with an optional AnalyzerRegistry.

        Args:
            registry: Optional custom AnalyzerRegistry instance.
        """
        self.registry = registry or AnalyzerRegistry()

    def execute(self, context: AnalysisContext) -> AnalysisResult:
        """Executes all registered static analyzers over the provided AnalysisContext.

        Args:
            context: AnalysisContext model for the target file.

        Returns:
            An immutable AnalysisResult containing aggregated diagnostics and performance metrics.

        Raises:
            AnalyzerExecutionError: If an analyzer pass fails unexpectedly during execution.
        """
        start_time = time.monotonic()
        aggregated_diagnostics: list[Diagnostic] = []

        analyzers = self.registry.get_all()
        for analyzer in analyzers:
            try:
                diagnostics = analyzer.analyze(context)
                aggregated_diagnostics.extend(diagnostics)
            except Exception as err:
                raise AnalyzerExecutionError(
                    f"Analyzer '{analyzer.__class__.__name__}' failed during execution: {err}"
                ) from err

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        # Calculate diagnostic severity metrics
        info_count = sum(1 for d in aggregated_diagnostics if d.severity == Severity.INFO)
        warning_count = sum(1 for d in aggregated_diagnostics if d.severity == Severity.WARNING)
        error_count = sum(1 for d in aggregated_diagnostics if d.severity == Severity.ERROR)

        metrics = {
            "total_diagnostics": len(aggregated_diagnostics),
            "info_count": info_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "symbols_count": context.symbol_table.count,
            "imports_count": context.module_metadata.import_count,
            "exports_count": context.module_metadata.export_count,
        }

        return AnalysisResult(
            diagnostics=aggregated_diagnostics,
            metrics=metrics,
            duration_ms=duration_ms,
        )
