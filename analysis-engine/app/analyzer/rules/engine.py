"""Rule engine module.

Provides the RuleEngine class responsible for executing quality rules over
semantic analysis results and producing standardized diagnostics.
"""

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic
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
    """Orchestrates quality rule execution and diagnostic aggregation."""

    def __init__(self, registry: RuleRegistry | None = None) -> None:
        """Initializes RuleEngine with a RuleRegistry instance.

        If no registry is provided, a default registry pre-loaded with all standard
        quality rules is initialized.

        Args:
            registry: Optional custom RuleRegistry instance.
        """
        if registry is not None:
            self.registry = registry
        else:
            self.registry = RuleRegistry()
            self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Helper to register built-in static quality rules."""
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
        """Executes all registered quality rules and aggregates diagnostics.

        Args:
            context: AnalysisContext for the document.
            dependency_result: Optional DependencyResult.
            resolution_result: Optional ResolutionResult.
            call_result: Optional CallAnalysisResult.

        Returns:
            List of aggregated Diagnostic objects.

        Raises:
            RuleEngineError: If rule execution fails.
        """
        try:
            if not context or not context.ast_document:
                raise RuleEngineError("Invalid or missing ASTDocument in AnalysisContext.")

            aggregated_diagnostics: list[Diagnostic] = []

            for rule in self.registry.get_all():
                rule_diagnostics = rule.evaluate(
                    context=context,
                    dependency_result=dependency_result,
                    resolution_result=resolution_result,
                    call_result=call_result,
                )
                aggregated_diagnostics.extend(rule_diagnostics)

            return aggregated_diagnostics
        except RuleEngineError:
            raise
        except Exception as err:
            raise RuleEngineError(
                f"Failed to execute quality rules for '{context.ast_document.path}': {err}"
            ) from err
