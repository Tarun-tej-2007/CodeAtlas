"""Reference Resolution Engine module."""

import logging
from typing import Dict, List, Optional, Tuple

from app.semantic.enums import ReferenceKind
from app.semantic.models import Location, SemanticReference, SemanticSymbol
from app.semantic.scope_manager import ScopeManager
from app.semantic.symbol_table import SymbolTable

logger = logging.getLogger("analysis-engine")


class ReferenceResolver:
    """Resolves identifier references to declared symbols using lexical scope and symbol table lookups."""

    def __init__(self, scope_manager: ScopeManager, symbol_table: SymbolTable) -> None:
        """Initializes the ReferenceResolver with ScopeManager and SymbolTable dependencies.

        Args:
            scope_manager: Reusable scope manager tracking lexical scopes.
            symbol_table: Reusable symbol table storing symbols declarations.
        """
        self.scope_manager = scope_manager
        self.symbol_table = symbol_table
        self._resolved_references: List[SemanticReference] = []
        self._unresolved_references: List[Tuple[str, Location]] = []
        self._diagnostics: List[str] = []

    def resolve_reference(
        self,
        name: str,
        location: Location,
        start_scope_id: Optional[str] = None,
        reference_kind: ReferenceKind = ReferenceKind.READ,
    ) -> Optional[SemanticSymbol]:
        """Resolves an identifier reference by name to its declaring SemanticSymbol.

        Ascends the lexical scope hierarchy starting from the specified or active scope.

        Args:
            name: The identifier name to resolve.
            location: The location where the identifier usage occurred.
            start_scope_id: Optional scope ID to start the search from.
                            Defaults to the scope manager's current active scope.
            reference_kind: The kind of reference relationship (e.g. READ, CALL).

        Returns:
            The resolved SemanticSymbol, or None if the identifier cannot be resolved.
        """
        # Determine starting scope node
        if start_scope_id is not None:
            curr_scope = self.scope_manager.get_scope_by_id(start_scope_id)
            if curr_scope is None:
                msg = f"Invalid starting scope ID '{start_scope_id}' during resolution of '{name}' at line {location.start_line}."
                self._diagnostics.append(msg)
                logger.warning(msg)
                self._unresolved_references.append((name, location))
                return None
        else:
            curr_scope = self.scope_manager.get_current_scope()

        # Ascend the scope parent hierarchy
        visited_scopes = []
        curr = curr_scope
        while curr is not None:
            visited_scopes.append(curr.id)
            # Query SymbolTable for the name in the current scope level
            symbol = self.symbol_table.get_symbol_by_name_in_scope(curr.id, name)
            if symbol is not None:
                # Successfully resolved reference!
                ref = SemanticReference(
                    symbol_id=symbol.id,
                    reference_kind=reference_kind,
                    location=location,
                )
                self._resolved_references.append(ref)
                return symbol

            curr = curr.parent

        # Global fallback (if the root scope is not in the stack chain for some reason,
        # check global scope anyway)
        root_scope = self.scope_manager.get_root_scope()
        if root_scope.id not in visited_scopes:
            symbol = self.symbol_table.get_symbol_by_name_in_scope(root_scope.id, name)
            if symbol is not None:
                ref = SemanticReference(
                    symbol_id=symbol.id,
                    reference_kind=reference_kind,
                    location=location,
                )
                self._resolved_references.append(ref)
                return symbol

        # If we reach here, the reference is unresolved
        self._unresolved_references.append((name, location))
        diagnostic_msg = f"Unresolved reference to identifier '{name}' at line {location.start_line}, column {location.start_column}."
        self._diagnostics.append(diagnostic_msg)
        logger.info(diagnostic_msg)
        return None

    def get_resolved_references(self) -> List[SemanticReference]:
        """Returns the list of all successfully resolved SemanticReference objects.

        Returns:
            List of SemanticReference instances.
        """
        return list(self._resolved_references)

    def get_unresolved_references(self) -> List[Tuple[str, Location]]:
        """Returns all unresolved reference name and Location pairs.

        Returns:
            List of unresolved reference tuples.
        """
        return list(self._unresolved_references)

    def get_diagnostics(self) -> List[str]:
        """Returns generated diagnostics warnings for unresolved or invalid references.

        Returns:
            List of diagnostic strings.
        """
        return list(self._diagnostics)

    def get_references_for_symbol(self, symbol_id: str) -> List[SemanticReference]:
        """Retrieves all successfully resolved references pointing to the given symbol ID.

        Args:
            symbol_id: The target symbol identifier.

        Returns:
            List of SemanticReference instances.
        """
        return [ref for ref in self._resolved_references if ref.symbol_id == symbol_id]

    def clear(self) -> None:
        """Clears all recorded reference resolution histories and diagnostics."""
        self._resolved_references.clear()
        self._unresolved_references.clear()
        self._diagnostics.clear()
