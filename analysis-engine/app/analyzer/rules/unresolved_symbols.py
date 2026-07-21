"""Unresolved symbols quality rule module.

Detects identifier references in a document that could not be resolved to any in-scope symbol declaration.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class UnresolvedSymbolsRule(BaseRule):
    """Rule emitting diagnostics for unresolved symbol references."""

    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        doc = context.ast_document

        if not resolution_result or not resolution_result.references:
            return diagnostics

        diag_counter = 0
        for ref in resolution_result.references:
            if not ref.resolved:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_unresolved_symbol_{ref.line}_{ref.column}_{ref.name}_{diag_counter}",
                        severity=Severity.ERROR,
                        message=f"Unresolved symbol reference '{ref.name}' at line {ref.line}",
                        path=doc.path,
                        line=ref.line,
                    )
                )

        return diagnostics
