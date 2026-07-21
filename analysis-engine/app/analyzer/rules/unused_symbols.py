"""Unused symbols quality rule module.

Detects local variables, functions, and methods declared in a file that are never referenced.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.base import BaseRule


class UnusedSymbolsRule(BaseRule):
    """Rule detecting declared local variables, functions, or methods that are never referenced."""

    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        doc = context.ast_document

        # Collect exported names to avoid flagging exported top-level symbols
        exported_names: set[str] = set()
        if context.module_metadata:
            for exp in context.module_metadata.exports:
                exported_names.add(exp.name)

        # Collect referenced symbol IDs and names
        referenced_symbol_ids: set[str] = set()
        referenced_names: set[str] = set()

        if resolution_result:
            for ref in resolution_result.references:
                if ref.resolved and ref.resolved_symbol_id:
                    referenced_symbol_ids.add(ref.resolved_symbol_id)
                referenced_names.add(ref.name)

        if call_result:
            for call in call_result.calls:
                if call.resolved and call.callee_symbol_id:
                    referenced_symbol_ids.add(call.callee_symbol_id)
                referenced_names.add(call.callee_name)

        if dependency_result:
            for dep in dependency_result.dependencies:
                if dep.resolved and dep.target_id:
                    referenced_symbol_ids.add(dep.target_id)

        # Evaluate each symbol in SymbolTable
        diag_counter = 0
        for symbol in context.symbol_table.symbols:
            # Skip exported symbols or main entrypoints
            if symbol.name in exported_names or symbol.name == "main":
                continue

            # Check if symbol ID or name is referenced
            if symbol.id not in referenced_symbol_ids and symbol.name not in referenced_names:
                diag_counter += 1
                diagnostics.append(
                    Diagnostic(
                        id=f"rule_unused_symbol_{symbol.start_line}_{symbol.name}_{diag_counter}",
                        severity=Severity.WARNING,
                        message=f"Unused {symbol.kind.value} declaration '{symbol.name}' at line {symbol.start_line}",
                        path=doc.path,
                        line=symbol.start_line,
                    )
                )

        return diagnostics
