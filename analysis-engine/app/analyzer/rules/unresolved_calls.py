"""Unresolved calls quality rule module.

Detects function, method, constructor, or static call targets that could not be resolved.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class UnresolvedCallsRule(BaseRule):
    """Rule emitting diagnostics for unresolved call targets."""

    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        doc = context.ast_document

        if not call_result or not call_result.calls:
            return diagnostics

        diag_counter = 0
        for call in call_result.calls:
            if not call.resolved:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_unresolved_call_{call.line}_{call.column}_{call.callee_name}_{diag_counter}",
                        severity=Severity.WARNING,
                        message=f"Unresolved call invocation to '{call.callee_name}' at line {call.line}",
                        path=doc.path,
                        line=call.line,
                    )
                )

        return diagnostics
