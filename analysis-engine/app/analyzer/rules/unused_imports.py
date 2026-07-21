"""Unused imports quality rule module.

Detects module import declarations that are never referenced in the document.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.parser.modules.models import ImportKind

from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class UnusedImportsRule(BaseRule):
    """Rule detecting imported symbols that are never referenced."""

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

        # Collect all referenced names in the document
        referenced_names: set[str] = set()

        if resolution_result:
            for ref in resolution_result.references:
                referenced_names.add(ref.name)

        if call_result:
            for call in call_result.calls:
                referenced_names.add(call.callee_name)

        if dependency_result:
            for dep in dependency_result.dependencies:
                if dep.target_id:
                    referenced_names.add(dep.target_id)

        # Also check AST document root text if resolution_result is omitted
        doc_text = doc.root.text if doc and doc.root else ""

        diag_counter = 0
        for imp in context.module_metadata.imports:
            # Side-effect imports are never unused
            if imp.kind == ImportKind.SIDE_EFFECT:
                continue

            check_name = imp.alias or imp.name
            if check_name == "*":
                continue

            # If check_name is not in referenced_names
            if check_name not in referenced_names and doc_text.count(check_name) <= 1:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_unused_import_{imp.start_line}_{check_name}_{diag_counter}",
                        severity=Severity.WARNING,
                        message=f"Unused import '{check_name}' from module '{imp.module}' at line {imp.start_line}",
                        path=doc.path,
                        line=imp.start_line,
                    )
                )

        return diagnostics
