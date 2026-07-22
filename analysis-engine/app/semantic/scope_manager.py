"""LEXICAL scope manager module coordinating scope tracking and queries."""

from typing import Dict, List, Optional

from app.semantic.enums import ScopeKind
from app.semantic.exceptions import SemanticResolutionError, SemanticModelError
from app.semantic.models import Location
from app.semantic.scope import ScopeNode


class ScopeManager:
    """Manages the lifecycle, tracking, stack, and query lookups of lexical scopes."""

    def __init__(self, root_id: str = "global", root_kind: ScopeKind = ScopeKind.GLOBAL) -> None:
        """Initializes a ScopeManager starting with a root global scope.

        Args:
            root_id: Unique identifier for the root scope.
            root_kind: ScopeKind for the root scope.
        """
        self.root = ScopeNode(id=root_id, kind=root_kind)
        self.current_scope = self.root
        self.stack: List[ScopeNode] = [self.root]
        self.scopes_map: Dict[str, ScopeNode] = {root_id: self.root}

    def get_root_scope(self) -> ScopeNode:
        """Returns the root scope node.

        Returns:
            The root ScopeNode instance.
        """
        return self.root

    def get_current_scope(self) -> ScopeNode:
        """Returns the active ScopeNode.

        Returns:
            The current active ScopeNode.
        """
        return self.current_scope

    def create_scope(
        self,
        id: str,
        kind: ScopeKind,
        location: Optional[Location] = None,
        metadata: Optional[dict] = None,
    ) -> ScopeNode:
        """Creates a new nested ScopeNode as a child of the current active scope.

        Args:
            id: Unique identifier for the new scope.
            kind: ScopeKind classification.
            location: Optional location coordinates range.
            metadata: Optional extensible metadata dictionary.

        Returns:
            The newly created ScopeNode.

        Raises:
            SemanticModelError: If a scope with the given ID is already registered.
        """
        if id in self.scopes_map:
            raise SemanticModelError(f"Scope with ID '{id}' is already registered.")

        new_scope = ScopeNode(
            id=id,
            kind=kind,
            parent=self.current_scope,
            location=location,
            metadata=metadata,
        )
        self.scopes_map[id] = new_scope
        return new_scope

    def enter_scope(self, scope: ScopeNode) -> None:
        """Enters the specified ScopeNode, pushing it onto the tracking stack.

        Args:
            scope: The ScopeNode to enter.

        Raises:
            SemanticResolutionError: If entering a scope that is not registered.
        """
        if scope.id not in self.scopes_map:
            raise SemanticResolutionError(f"Cannot enter unregistered scope '{scope.id}'.")

        self.stack.append(scope)
        self.current_scope = scope

    def exit_scope(self) -> None:
        """Exits the current active scope, popping the tracking stack back to the parent.

        Raises:
            SemanticResolutionError: If attempting to exit the root scope (empty stack transit).
        """
        if len(self.stack) <= 1:
            raise SemanticResolutionError("Cannot exit the root scope (scope stack bottom reached).")

        self.stack.pop()
        self.current_scope = self.stack[-1]

    def register_symbol(self, symbol_id: str) -> None:
        """Registers a symbol identifier into the current active scope.

        Args:
            symbol_id: Deterministic identifier of the symbol.
        """
        self.current_scope.add_symbol(symbol_id)

    def lookup_symbol_scope(self, symbol_id: str) -> Optional[ScopeNode]:
        """Resolves the nearest declaring lexical scope for a symbol ID, scanning up to the root.

        Args:
            symbol_id: The symbol identifier to lookup.

        Returns:
            The declaring ScopeNode, or None if not declared in current stack resolution.
        """
        curr: Optional[ScopeNode] = self.current_scope
        while curr:
            if symbol_id in curr.symbol_ids:
                return curr
            curr = curr.parent
        return None

    def get_scope_by_id(self, scope_id: str) -> Optional[ScopeNode]:
        """Looks up a scope instance by its ID.

        Args:
            scope_id: Unique scope identifier.

        Returns:
            The matching ScopeNode, or None.
        """
        return self.scopes_map.get(scope_id)

    def get_parent_scopes(self, scope_id: str) -> List[ScopeNode]:
        """Retrieves the list of enclosing parent scopes for a scope ID, from immediate parent to root.

        Args:
            scope_id: Unique scope identifier.

        Returns:
            A list of enclosing ScopeNodes.
        """
        scope = self.scopes_map.get(scope_id)
        if not scope:
            return []
        parents = []
        curr = scope.parent
        while curr:
            parents.append(curr)
            curr = curr.parent
        return parents

    def get_child_scopes(self, scope_id: str) -> List[ScopeNode]:
        """Retrieves all immediate children of a given scope.

        Args:
            scope_id: Unique scope identifier.

        Returns:
            A list of immediate child ScopeNodes.
        """
        scope = self.scopes_map.get(scope_id)
        return scope.children if scope else []

    def get_all_scopes(self) -> List[ScopeNode]:
        """Returns all registered scopes managed by this manager.

        Returns:
            A list of all ScopeNode instances.
        """
        return list(self.scopes_map.values())
