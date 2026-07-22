"""Lexical scope tree node module."""

from typing import Any, Dict, List, Optional

from app.semantic.enums import ScopeKind
from app.semantic.models import Location


class ScopeNode:
    """Represents a node in the lexical scope hierarchy of a codebase."""

    def __init__(
        self,
        id: str,
        kind: ScopeKind,
        parent: Optional["ScopeNode"] = None,
        location: Optional[Location] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes a ScopeNode.

        Args:
            id: Unique identifier for this scope.
            kind: The ScopeKind classification of this lexical scope block.
            parent: The enclosing parent ScopeNode, if any.
            location: Optional source code coordinate location range.
            metadata: Optional extensible metadata dictionary.
        """
        self.id = id
        self.kind = kind
        self.parent = parent
        self.children: List["ScopeNode"] = []
        self.symbol_ids: List[str] = []
        self.location = location
        self.metadata = metadata or {}

        if parent is not None:
            parent.children.append(self)

    def add_symbol(self, symbol_id: str) -> None:
        """Registers a declared symbol ID declared directly within this scope.

        Args:
            symbol_id: The unique identifier of the symbol.
        """
        if symbol_id not in self.symbol_ids:
            self.symbol_ids.append(symbol_id)
