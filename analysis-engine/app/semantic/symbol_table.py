"""Semantic Symbol Table Engine."""

from typing import Dict, Iterator, List, Optional, Tuple

from app.semantic.exceptions import SemanticModelError
from app.semantic.models import SemanticSymbol


class SymbolTable:
    """Manages semantic symbols declarations, duplicate detection, and provides fast indexes."""

    def __init__(self) -> None:
        """Initializes an empty SymbolTable with optimized lookups."""
        # Primary storage: symbol_id -> SemanticSymbol
        self._symbols: Dict[str, SemanticSymbol] = {}
        
        # Index: qualified_name -> SemanticSymbol
        self._by_qualified_name: Dict[str, SemanticSymbol] = {}
        
        # Index: scope_id -> list of symbol_ids
        self._by_scope: Dict[str, List[str]] = {}
        
        # Index: parent_symbol_id -> list of symbol_ids
        self._by_parent: Dict[str, List[str]] = {}
        
        # Duplicate detector index: (scope_id, name) -> symbol_id
        # scope_id can be None (representing global or unplaced declarations)
        self._scope_name_index: Dict[Tuple[Optional[str], str], str] = {}

    def register_symbol(self, symbol: SemanticSymbol) -> None:
        """Registers a symbol into the table and builds indexes.

        Args:
            symbol: The SemanticSymbol instance to register.

        Raises:
            SemanticModelError: If symbol ID already exists, or a duplicate declaration
                                exists in the same lexical scope block.
        """
        # 1. Unique symbol ID validation
        if symbol.id in self._symbols:
            raise SemanticModelError(f"Symbol ID '{symbol.id}' is already registered.")

        # 2. Duplicate detection within the same lexical scope
        scope_key = (symbol.scope_id, symbol.name)
        if scope_key in self._scope_name_index:
            raise SemanticModelError(
                f"Duplicate declaration of symbol name '{symbol.name}' in scope '{symbol.scope_id}'."
            )

        # 3. Add to primary storage
        self._symbols[symbol.id] = symbol
        self._scope_name_index[scope_key] = symbol.id

        # 4. Qualified name index
        if symbol.qualified_name:
            self._by_qualified_name[symbol.qualified_name] = symbol

        # 5. Scope index
        if symbol.scope_id is not None:
            if symbol.scope_id not in self._by_scope:
                self._by_scope[symbol.scope_id] = []
            self._by_scope[symbol.scope_id].append(symbol.id)

        # 6. Parent-child index
        if symbol.parent_symbol_id is not None:
            if symbol.parent_symbol_id not in self._by_parent:
                self._by_parent[symbol.parent_symbol_id] = []
            self._by_parent[symbol.parent_symbol_id].append(symbol.id)

    def unregister_symbol(self, symbol_id: str) -> None:
        """Unregisters a symbol from the table, cleaning up all internal indexes.

        Args:
            symbol_id: Unique identifier of the symbol.

        Raises:
            SemanticModelError: If the symbol ID is not found.
        """
        if symbol_id not in self._symbols:
            raise SemanticModelError(f"Symbol ID '{symbol_id}' not found in the symbol table.")

        symbol = self._symbols[symbol_id]

        # Cleanup indexes
        self._scope_name_index.pop((symbol.scope_id, symbol.name), None)
        self._by_qualified_name.pop(symbol.qualified_name, None)

        if symbol.scope_id is not None and symbol.scope_id in self._by_scope:
            self._by_scope[symbol.scope_id].remove(symbol_id)
            if not self._by_scope[symbol.scope_id]:
                self._by_scope.pop(symbol.scope_id)

        if symbol.parent_symbol_id is not None and symbol.parent_symbol_id in self._by_parent:
            self._by_parent[symbol.parent_symbol_id].remove(symbol_id)
            if not self._by_parent[symbol.parent_symbol_id]:
                self._by_parent.pop(symbol.parent_symbol_id)

        # Remove from primary storage
        self._symbols.pop(symbol_id)

    def get_symbol(self, symbol_id: str) -> Optional[SemanticSymbol]:
        """Retrieves a symbol by its ID.

        Args:
            symbol_id: Unique symbol identifier.

        Returns:
            The SemanticSymbol instance, or None.
        """
        return self._symbols.get(symbol_id)

    def get_symbol_by_name_in_scope(self, scope_id: Optional[str], name: str) -> Optional[SemanticSymbol]:
        """Retrieves a symbol by its name within a specific scope.

        Args:
            scope_id: Lexical scope identifier.
            name: Name identifier of the symbol.

        Returns:
            The SemanticSymbol instance, or None.
        """
        symbol_id = self._scope_name_index.get((scope_id, name))
        if symbol_id:
            return self.get_symbol(symbol_id)
        return None

    def get_symbol_by_qualified_name(self, qualified_name: str) -> Optional[SemanticSymbol]:
        """Retrieves a symbol by its qualified name.

        Args:
            qualified_name: Fully qualified module name of the symbol.

        Returns:
            The SemanticSymbol instance, or None.
        """
        return self._by_qualified_name.get(qualified_name)

    def get_symbols_in_scope(self, scope_id: str) -> List[SemanticSymbol]:
        """Retrieves all symbols declared directly inside a given scope.

        Args:
            scope_id: Lexical scope identifier.

        Returns:
            A list of SemanticSymbols in the scope.
        """
        symbol_ids = self._by_scope.get(scope_id, [])
        return [self._symbols[sid] for sid in symbol_ids]

    def get_child_symbols(self, parent_symbol_id: str) -> List[SemanticSymbol]:
        """Retrieves all child symbols owned by a parent symbol.

        Args:
            parent_symbol_id: Enclosing container symbol identifier.

        Returns:
            A list of child SemanticSymbols.
        """
        symbol_ids = self._by_parent.get(parent_symbol_id, [])
        return [self._symbols[sid] for sid in symbol_ids]

    def get_parent_symbol(self, symbol_id: str) -> Optional[SemanticSymbol]:
        """Retrieves the parent container symbol of a given symbol.

        Args:
            symbol_id: Unique symbol identifier.

        Returns:
            The parent SemanticSymbol, or None.
        """
        symbol = self._symbols.get(symbol_id)
        if symbol and symbol.parent_symbol_id:
            return self._symbols.get(symbol.parent_symbol_id)
        return None

    def contains_symbol(self, symbol_id: str) -> bool:
        """Checks if a symbol with the given ID is present.

        Args:
            symbol_id: Unique symbol identifier.

        Returns:
            True if present, False otherwise.
        """
        return symbol_id in self._symbols

    def iter_symbols(self) -> Iterator[SemanticSymbol]:
        """Returns an iterator over all registered symbols.

        Returns:
            An Iterator of SemanticSymbol instances.
        """
        return iter(self._symbols.values())
