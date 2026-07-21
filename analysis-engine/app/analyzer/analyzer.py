"""Static analyzer base interface and execution pipeline module.

Provides the abstract BaseAnalyzer interface and AnalysisPipeline orchestrator with
detailed timing metrics, diagnostic aggregation, and configurable error isolation.
"""

from abc import ABC, abstractmethod
import time
from typing import Any

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

    def __init__(self, registry: AnalyzerRegistry | None = None, raise_on_error: bool = False) -> None:
        """Initializes AnalysisPipeline with an optional AnalyzerRegistry.

        Args:
            registry: Optional custom AnalyzerRegistry instance.
            raise_on_error: If True, analyzer exceptions are raised immediately as AnalyzerExecutionError.
                            If False (default), analyzer exceptions are caught and reported as ERROR Diagnostics.
        """
        self.registry = registry or AnalyzerRegistry()
        self.raise_on_error = raise_on_error

    def execute(self, context: AnalysisContext) -> AnalysisResult:
        """Executes all registered static analyzers over the provided AnalysisContext.

        Args:
            context: AnalysisContext model for the target file.

        Returns:
            An immutable AnalysisResult containing aggregated diagnostics and performance metrics.

        Raises:
            AnalyzerExecutionError: If AnalysisContext is invalid or if raise_on_error is True and an analyzer fails.
        """
        if not context or not context.ast_document:
            raise AnalyzerExecutionError("Invalid or missing AnalysisContext.")

        start_pipeline_time = time.monotonic()
        aggregated_diagnostics: list[Diagnostic] = []
        analyzer_durations: dict[str, float] = {}
        seen_diag_keys: set[tuple[str, int, str]] = set()

        analyzers = self.registry.get_all()
        for analyzer in analyzers:
            analyzer_name = analyzer.__class__.__name__
            t0 = time.monotonic()
            try:
                diagnostics = analyzer.analyze(context)
                analyzer_durations[analyzer_name] = round((time.monotonic() - t0) * 1000, 2)

                for diag in diagnostics:
                    key = (str(diag.path), diag.line, diag.message)
                    if key not in seen_diag_keys:
                        seen_diag_keys.add(key)
                        aggregated_diagnostics.append(diag)

            except Exception as err:
                analyzer_durations[analyzer_name] = round((time.monotonic() - t0) * 1000, 2)
                if self.raise_on_error:
                    raise AnalyzerExecutionError(
                        f"Analyzer '{analyzer_name}' failed during execution: {err}"
                    ) from err

                # Fault isolation: wrap individual analyzer error into diagnostic
                error_diag = Diagnostic(
                    id=f"analyzer_error_{analyzer_name}",
                    severity=Severity.ERROR,
                    message=f"Analyzer '{analyzer_name}' failed during execution: {err}",
                    path=context.ast_document.path,
                    line=1,
                )
                aggregated_diagnostics.append(error_diag)

        total_duration_ms = round((time.monotonic() - start_pipeline_time) * 1000, 2)

        # Compute metric counts
        info_count = sum(1 for d in aggregated_diagnostics if d.severity == Severity.INFO)
        warning_count = sum(1 for d in aggregated_diagnostics if d.severity == Severity.WARNING)
        error_count = sum(1 for d in aggregated_diagnostics if d.severity == Severity.ERROR)

        metrics: dict[str, Any] = {
            "total_duration_ms": total_duration_ms,
            "analyzer_durations": analyzer_durations,
            "number_of_diagnostics": len(aggregated_diagnostics),
            "total_diagnostics": len(aggregated_diagnostics),
            "info_count": info_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "symbols_count": context.symbol_table.count if context.symbol_table else 0,
            "imports_count": context.module_metadata.import_count if context.module_metadata else 0,
            "exports_count": context.module_metadata.export_count if context.module_metadata else 0,
        }

        return AnalysisResult(
            diagnostics=aggregated_diagnostics,
            metrics=metrics,
            duration_ms=total_duration_ms,
        )
