"""Architecture Semantic Context Adapter module."""

from typing import Any, Optional, Tuple

from app.semantic.models import SemanticReference, SemanticScope, SemanticSymbol


class ArchitectureSemanticContext:
    """Read-only adapter wrapping semantic analysis outputs for architectural rules."""

    def __init__(self, semantic_result: Any) -> None:
        """Initializes the adapter by extracting and indexing symbols, references, and scopes."""
        if hasattr(semantic_result, "original_result"):
            # Parse Project-level LinkedSemanticResult structure
            files = getattr(semantic_result.original_result, "files", {}) or {}
            self._symbols = []
            for file_obj in files.values():
                self._symbols.extend(getattr(file_obj, "symbols", []) or [])

            ref_res = getattr(semantic_result, "reference_resolution_result", None)
            resolved_refs = getattr(ref_res, "resolved_references", []) or []
            self._references = [r.reference for r in resolved_refs if hasattr(r, "reference")]
            self._scopes = []
        elif any(hasattr(semantic_result, attr) for attr in ("symbols", "references", "scopes")):
            # Parse file-level SemanticResult structure
            self._symbols = getattr(semantic_result, "symbols", []) or []
            self._references = getattr(semantic_result, "references", []) or []
            self._scopes = getattr(semantic_result, "scopes", []) or []
        else:
            raise ValueError("Object does not appear to be a valid semantic analysis output model.")

        # Build lookup tables for O(1) reads
        self._symbols_by_id = {sym.id: sym for sym in self._symbols if hasattr(sym, "id")}
        self._symbols_by_qn = {
            sym.qualified_name: sym for sym in self._symbols if hasattr(sym, "qualified_name")
        }
        self._scopes_by_id = {scope.id: scope for scope in self._scopes if hasattr(scope, "id")}

        # Group references by symbol_id for faster index query lookups
        self._refs_by_sym = {}
        for ref in self._references:
            sym_id = getattr(ref, "symbol_id", None)
            if sym_id is None and hasattr(ref, "name"):
                # Handle SymbolReference by mapping its name to registered symbol ID
                target_sym = self.get_symbol_by_qualified_name(ref.name)
                if not target_sym:
                    # Fallback to simple name lookup
                    target_sym = next((s for s in self._symbols if getattr(s, "name", None) == ref.name), None)
                if target_sym:
                    sym_id = getattr(target_sym, "id", None)

            if sym_id is not None:
                if sym_id not in self._refs_by_sym:
                    self._refs_by_sym[sym_id] = []
                self._refs_by_sym[sym_id].append(ref)
        self._refs_by_sym = {k: tuple(v) for k, v in self._refs_by_sym.items()}

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
