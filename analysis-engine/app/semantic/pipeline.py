"""Semantic analysis pipeline coordinator."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.parser.models import ParseResult
from app.semantic.models import SemanticResult, SemanticScope
from app.semantic.scope_manager import ScopeManager
from app.semantic.symbol_table import SymbolTable
from app.semantic.reference_resolver import ReferenceResolver
from app.semantic.type_metadata import TypeMetadataExtractor


class SemanticAnalysisContext:
    """Carries the state and semantic components for a single pipeline execution run."""

    def __init__(
        self,
        scope_manager: ScopeManager,
        symbol_table: SymbolTable,
        reference_resolver: ReferenceResolver,
        type_extractor: Optional[TypeMetadataExtractor] = None,
    ) -> None:
        """Initializes the SemanticAnalysisContext.

        Args:
            scope_manager: ScopeManager instance.
            symbol_table: SymbolTable instance.
            reference_resolver: ReferenceResolver instance.
            type_extractor: Optional TypeMetadataExtractor instance.
        """
        self.scope_manager = scope_manager
        self.symbol_table = symbol_table
        self.reference_resolver = reference_resolver
        self.type_extractor = type_extractor
        self.diagnostics: List[str] = []


class SemanticAnalysisPlugin(ABC):
    """Abstract interface defining callbacks that concrete language plugins implement."""

    @abstractmethod
    def build_scopes_and_symbols(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        """Stage 1: Builds lexical scopes and registers declared symbols.

        Args:
            context: The active semantic pipeline context.
            parse_result: The parsed AST output representation.
        """
        pass

    @abstractmethod
    def resolve_references(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        """Stage 2: Resolves identifier references against symbols and scopes.

        Args:
            context: The active semantic pipeline context.
            parse_result: The parsed AST output representation.
        """
        pass

    @abstractmethod
    def extract_type_metadata(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        """Stage 3: Extracts type metadata for registered symbols.

        Args:
            context: The active semantic pipeline context.
            parse_result: The parsed AST output representation.
        """
        pass


class SemanticPipeline:
    """Coordinates and executes multi-pass semantic analysis stages in a language-agnostic manner."""

    def __init__(
        self,
        plugin: SemanticAnalysisPlugin,
        type_extractor: Optional[TypeMetadataExtractor] = None,
    ) -> None:
        """Initializes the SemanticPipeline with dependency injection.

        Args:
            plugin: Concrete SemanticAnalysisPlugin language plugin implementation.
            type_extractor: Optional TypeMetadataExtractor service.
        """
        self.plugin = plugin
        self.type_extractor = type_extractor

    def execute(self, parse_result: ParseResult) -> SemanticResult:
        """Executes the semantic analysis stages, returning aggregated results.

        This method is completely stateless between executions.

        Args:
            parse_result: The aggregated parsed codebase outputs.

        Returns:
            The resolved and compiled SemanticResult mapping symbols, references, and scopes.
        """
        # 1. Fresh context components for stateless execution
        scope_manager = ScopeManager()
        symbol_table = SymbolTable()
        reference_resolver = ReferenceResolver(scope_manager, symbol_table)

        context = SemanticAnalysisContext(
            scope_manager=scope_manager,
            symbol_table=symbol_table,
            reference_resolver=reference_resolver,
            type_extractor=self.type_extractor,
        )

        # Stage 1: Build Scopes and Symbols
        try:
            self.plugin.build_scopes_and_symbols(context, parse_result)
        except Exception as e:
            context.diagnostics.append(f"Error during scopes and symbols building: {str(e)}")

        # Stage 2: Resolve References
        try:
            self.plugin.resolve_references(context, parse_result)
        except Exception as e:
            context.diagnostics.append(f"Error during reference resolution: {str(e)}")

        # Stage 3: Type Metadata Extraction
        try:
            self.plugin.extract_type_metadata(context, parse_result)
        except Exception as e:
            context.diagnostics.append(f"Error during type metadata extraction: {str(e)}")

        # Compile ScopeNode instances to SemanticScope DTOs
        compiled_scopes: List[SemanticScope] = []
        for scope_node in scope_manager.get_all_scopes():
            compiled_scopes.append(
                SemanticScope(
                    id=scope_node.id,
                    kind=scope_node.kind,
                    parent_scope_id=scope_node.parent.id if scope_node.parent else None,
                    symbol_ids=scope_node.symbol_ids,
                )
            )

        # Collect references and diagnostics
        resolved_references = reference_resolver.get_resolved_references()
        all_diagnostics = list(reference_resolver.get_diagnostics()) + context.diagnostics

        return SemanticResult(
            symbols=list(symbol_table.iter_symbols()),
            references=resolved_references,
            scopes=compiled_scopes,
            diagnostics=all_diagnostics,
        )
