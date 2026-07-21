"""Duplicate exports quality rule module.

Detects repeated export declarations with the same exported identifier name.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class DuplicateExportsRule(BaseRule):
    """Rule detecting duplicate export declarations for the same identifier name."""

    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        doc = context.ast_document

        if not context.module_metadata or not context.module_metadata.exports:
            return diagnostics

        seen_exports: set[str] = set()
        diag_counter = 0

        for exp in context.module_metadata.exports:
            export_name = exp.alias or exp.name
            if export_name == "*":
                continue

            if export_name in seen_exports:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_duplicate_export_{exp.start_line}_{export_name}_{diag_counter}",
                        severity=Severity.WARNING,
                        message=f"Duplicate export declaration for '{export_name}' at line {exp.start_line}",
                        path=doc.path,
                        line=exp.start_line,
                    )
                )
            else:
                seen_exports.add(export_name)

        return diagnostics
