"""Duplicate imports quality rule module.

Detects repeated import statements targeting the same module specifier.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class DuplicateImportsRule(BaseRule):
    """Rule detecting duplicate import statements from the same target module."""

    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        doc = context.ast_document

        if not context.module_metadata or not context.module_metadata.imports:
            return diagnostics

        seen_modules: set[str] = set()
        diag_counter = 0

        for imp in context.module_metadata.imports:
            if imp.module in seen_modules:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_duplicate_import_{imp.start_line}_{diag_counter}",
                        severity=Severity.INFO,
                        message=f"Duplicate import statement targeting module '{imp.module}' at line {imp.start_line}",
                        path=doc.path,
                        line=imp.start_line,
                    )
                )
            else:
                seen_modules.add(imp.module)

        return diagnostics
