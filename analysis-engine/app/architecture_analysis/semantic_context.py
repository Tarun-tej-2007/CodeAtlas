"""Architecture Semantic Context Adapter module."""

from typing import Any, Optional, Tuple

from app.semantic.models import SemanticReference, SemanticScope, SemanticSymbol


class ArchitectureSemanticContext:
    """Read-only adapter wrapping semantic analysis outputs for architectural rules."""

    def __init__(self, semantic_result: Any) -> None:
        """Initializes the adapter by extracting and indexing symbols, references, and scopes."""
        if not any(hasattr(semantic_result, attr) for attr in ("symbols", "references", "scopes")):
            raise ValueError("Object does not appear to be a valid semantic analysis output model.")

        self._symbols = getattr(semantic_result, "symbols", []) or []
        self._references = getattr(semantic_result, "references", []) or []
        self._scopes = getattr(semantic_result, "scopes", []) or []

        # Local read-only dictionaries for fast O(1) indexed lookups
        self._symbols_by_id = {sym.id: sym for sym in self._symbols}
        self._symbols_by_qn = {sym.qualified_name: sym for sym in self._symbols}
        self._scopes_by_id = {scope.id: scope for scope in self._scopes}

        refs_by_sym = {}
        for ref in self._references:
            if ref.symbol_id not in refs_by_sym:
                refs_by_sym[ref.symbol_id] = []
            refs_by_sym[ref.symbol_id].append(ref)
        self._refs_by_sym = {k: tuple(v) for k, v in refs_by_sym.items()}

    def get_symbol_by_id(self, symbol_id: str) -> Optional[SemanticSymbol]:
        """Looks up a declared semantic symbol by its identifier."""
        return self._symbols_by_id.get(symbol_id)

    def get_symbol_by_qualified_name(self, qualified_name: str) -> Optional[SemanticSymbol]:
        """Looks up a declared semantic symbol by its qualified name."""
        return self._symbols_by_qn.get(qualified_name)

    def get_references_for_symbol(self, symbol_id: str) -> Tuple[SemanticReference, ...]:
        """Finds all usages or references targeting a specific symbol ID."""
        return self._refs_by_sym.get(symbol_id, ())

    def get_scope_by_id(self, scope_id: str) -> Optional[SemanticScope]:
        """Looks up a lexical/symbolic scope by its identifier."""
        return self._scopes_by_id.get(scope_id)

    def list_all_symbols(self) -> Tuple[SemanticSymbol, ...]:
        """Lists all symbols mapped in the semantic context."""
        return tuple(self._symbols)

    def list_all_references(self) -> Tuple[SemanticReference, ...]:
        """Lists all references mapped in the semantic context."""
        return tuple(self._references)

    def list_all_scopes(self) -> Tuple[SemanticScope, ...]:
        """Lists all scopes mapped in the semantic context."""
        return tuple(self._scopes)
