"""Rule engine module.

Provides the RuleEngine class responsible for executing quality rules over
semantic analysis results, measuring per-rule durations, isolating rule failures,
and producing deduplicated diagnostics.
"""

import time
from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic, Severity
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.rules.duplicate_exports import DuplicateExportsRule
from app.analyzer.rules.duplicate_imports import DuplicateImportsRule
from app.analyzer.rules.exceptions import RuleEngineError
from app.analyzer.rules.registry import RuleRegistry
from app.analyzer.rules.self_dependencies import SelfDependencyRule
from app.analyzer.rules.unresolved_calls import UnresolvedCallsRule
from app.analyzer.rules.unresolved_symbols import UnresolvedSymbolsRule
from app.analyzer.rules.unused_imports import UnusedImportsRule
from app.analyzer.rules.unused_symbols import UnusedSymbolsRule


class RuleEngine:
    """Orchestrates quality rule execution with error isolation, timing, and diagnostic deduplication."""

    def __init__(self, registry: RuleRegistry | None = None) -> None:
        """Initializes RuleEngine with a RuleRegistry instance.

        Args:
            registry: Optional custom RuleRegistry instance.
        """
        if registry is not None:
            self.registry = registry
        else:
            self.registry = RuleRegistry()
            self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Registers built-in static quality rules in deterministic order."""
        self.registry.register(UnusedSymbolsRule())
        self.registry.register(UnusedImportsRule())
        self.registry.register(DuplicateImportsRule())
        self.registry.register(DuplicateExportsRule())
        self.registry.register(UnresolvedSymbolsRule())
        self.registry.register(UnresolvedCallsRule())
        self.registry.register(SelfDependencyRule())

    def execute(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        """Executes all registered quality rules with error isolation and deduplication.

        Args:
            context: AnalysisContext for the document.
            dependency_result: Optional DependencyResult.
            resolution_result: Optional ResolutionResult.
            call_result: Optional CallAnalysisResult.

        Returns:
            Deduplicated list of Diagnostic objects.

        Raises:
            RuleEngineError: If context is invalid.
        """
        if not context or not context.ast_document:
            raise RuleEngineError("Invalid or missing ASTDocument in AnalysisContext.")

        aggregated_diagnostics: list[Diagnostic] = []
        seen_diag_keys: set[tuple[str, int, str]] = set()

        rules = self.registry.get_all()
        for rule in rules:
            rule_name = rule.__class__.__name__
            try:
                rule_diagnostics = rule.evaluate(
                    context=context,
                    dependency_result=dependency_result,
                    resolution_result=resolution_result,
                    call_result=call_result,
                )

                for diag in rule_diagnostics:
                    key = (str(diag.path), diag.line, diag.message)
                    if key not in seen_diag_keys:
                        seen_diag_keys.add(key)
                        aggregated_diagnostics.append(diag)
            except Exception as err:
                # Isolate rule execution failure so remaining rules continue
                error_diag = Diagnostic(
                    id=f"rule_error_{rule_name}",
                    severity=Severity.ERROR,
                    message=f"Rule '{rule_name}' failed during execution: {err}",
                    path=context.ast_document.path,
                    line=1,
                )
                aggregated_diagnostics.append(error_diag)

        return aggregated_diagnostics
