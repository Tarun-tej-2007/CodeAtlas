"""Scope management module.

Provides the Scope class for managing lexical scope hierarchies, symbol declarations,
lexical shadowing, and nested scope resolution.
"""

from typing import Self
from app.parser.symbols import Symbol


class Scope:
    """Manages lexical symbol declarations and parent scope resolution chains."""

    def __init__(self, kind: str = "global", parent: Self | None = None) -> None:
        """Initializes a Scope instance.

        Args:
            kind: Kind of scope ('global', 'function', 'class', 'block').
            parent: Optional parent Scope instance.
        """
        self.kind = kind
        self.parent = parent
        self.symbols: dict[str, Symbol] = {}

    def declare(self, symbol: Symbol) -> None:
        """Registers a declaration symbol in the current scope frame.

        Args:
            symbol: Symbol instance to register.
        """
        self.symbols[symbol.name] = symbol

    def resolve(self, name: str) -> Symbol | None:
        """Resolves an identifier name against the scope chain.

        Supports lexical shadowing by prioritizing local scope declarations
        before delegating to parent scopes.

        Args:
            name: Identifier name string.

        Returns:
            The resolved Symbol if found in the scope chain, None otherwise.
        """
        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.resolve(name)

        return None

    def create_child(self, kind: str) -> Self:
        """Creates a new child Scope frame nested under the current scope.

        Args:
            kind: Kind of child scope ('function', 'class', 'block').

        Returns:
            A new Scope instance referencing self as parent.
        """
        return self.__class__(kind=kind, parent=self)
