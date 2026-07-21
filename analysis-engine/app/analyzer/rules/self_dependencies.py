"""Self-dependency quality rule module.

Detects self-referencing dependency relationships, excluding valid recursive calls.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyKind, DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class SelfDependencyRule(BaseRule):
    """Rule emitting diagnostics for non-call self-dependency relationships."""

    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        doc = context.ast_document

        if not dependency_result or not dependency_result.dependencies:
            return diagnostics

        diag_counter = 0
        for dep in dependency_result.dependencies:
            # Exclude valid recursive calls (source_id == target_id with kind == DependencyKind.CALL)
            if dep.kind == DependencyKind.CALL:
                continue

            if dep.source_id and dep.target_id and dep.source_id == dep.target_id:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_self_dependency_{dep.line}_{diag_counter}",
                        severity=Severity.WARNING,
                        message=f"Self-dependency detected for symbol '{dep.source_id}' at line {dep.line}",
                        path=doc.path,
                        line=dep.line,
                    )
                )

        return diagnostics
