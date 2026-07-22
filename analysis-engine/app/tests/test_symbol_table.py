"""Unit tests for the SymbolTable engine class."""

import unittest
from pathlib import Path

from app.scanner.models import Language
from app.semantic.enums import SymbolKind, VisibilityKind
from app.semantic.exceptions import SemanticModelError
from app.semantic import (
    Location,
    SemanticSymbol,
    SymbolTable,
)


class TestSymbolTable(unittest.TestCase):
    """Tests registration rules, lookups, scope queries, shadowing, and unregistration index cleanups."""

    def setUp(self) -> None:
        self.table = SymbolTable()
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)

        # Build some semantic symbols
        self.sym_global = SemanticSymbol(
            id="sym-global",
            name="x",
            qualified_name="global.x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="global-scope",
        )

        self.sym_nested = SemanticSymbol(
            id="sym-nested",
            name="x",  # Shadowing: same name as sym_global
            qualified_name="global.func.x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="function-scope",
        )

        self.sym_class = SemanticSymbol(
            id="sym-class",
            name="MyClass",
            qualified_name="global.MyClass",
            kind=SymbolKind.CLASS,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="global-scope",
        )

        self.sym_method = SemanticSymbol(
            id="sym-method",
            name="my_method",
            qualified_name="global.MyClass.my_method",
            kind=SymbolKind.METHOD,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="class-scope",
            parent_symbol_id="sym-class",
        )

    def test_successful_registration_and_lookup(self) -> None:
        # successful registration
        self.table.register_symbol(self.sym_global)
        
        # lookup by ID
        self.assertEqual(self.table.get_symbol("sym-global"), self.sym_global)
        # contains_symbol()
        self.assertTrue(self.table.contains_symbol("sym-global"))
        self.assertFalse(self.table.contains_symbol("non-existent"))

        # lookup by qualified name
        self.assertEqual(self.table.get_symbol_by_qualified_name("global.x"), self.sym_global)

    def test_duplicate_registration_rejection(self) -> None:
        self.table.register_symbol(self.sym_global)

        # 1. Duplicate ID rejection
        dup_id_sym = SemanticSymbol(
            id="sym-global",  # Collision
            name="y",
            qualified_name="global.y",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="global-scope",
        )
        with self.assertRaises(SemanticModelError):
            self.table.register_symbol(dup_id_sym)

        # 2. Duplicate name within the same scope rejection
        dup_name_sym = SemanticSymbol(
            id="sym-another",
            name="x",  # Collision in scope 'global-scope'
            qualified_name="global.another_x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="global-scope",
        )
        with self.assertRaises(SemanticModelError):
            self.table.register_symbol(dup_name_sym)

    def test_shadowing_allowed_across_nested_scopes(self) -> None:
        # shadowing is allowed
        self.table.register_symbol(self.sym_global)
        self.table.register_symbol(self.sym_nested)  # registered in 'function-scope'

        self.assertEqual(self.table.get_symbol("sym-global"), self.sym_global)
        self.assertEqual(self.table.get_symbol("sym-nested"), self.sym_nested)

    def test_scope_queries(self) -> None:
        # scope queries
        self.table.register_symbol(self.sym_global)
        self.table.register_symbol(self.sym_class)

        global_symbols = self.table.get_symbols_in_scope("global-scope")
        self.assertEqual(len(global_symbols), 2)
        self.assertIn(self.sym_global, global_symbols)
        self.assertIn(self.sym_class, global_symbols)

    def test_parent_child_ownership(self) -> None:
        # parent-child ownership
        self.table.register_symbol(self.sym_class)
        self.table.register_symbol(self.sym_method)

        # get child symbols
        children = self.table.get_child_symbols("sym-class")
        self.assertEqual(children, [self.sym_method])

        # get parent symbol
        self.assertEqual(self.table.get_parent_symbol("sym-method"), self.sym_class)
        self.assertIsNone(self.table.get_parent_symbol("sym-class"))

    def test_iteration(self) -> None:
        # iteration
        self.table.register_symbol(self.sym_global)
        self.table.register_symbol(self.sym_class)

        symbols = list(self.table.iter_symbols())
        self.assertEqual(len(symbols), 2)
        self.assertIn(self.sym_global, symbols)
        self.assertIn(self.sym_class, symbols)

    def test_unregister_and_cleanup_indexes(self) -> None:
        self.table.register_symbol(self.sym_class)
        self.table.register_symbol(self.sym_method)

        # Unregister parent
        self.table.unregister_symbol("sym-class")
        self.assertFalse(self.table.contains_symbol("sym-class"))
        
        # Verify index cleanup
        self.assertIsNone(self.table.get_symbol_by_qualified_name("global.MyClass"))
        self.assertEqual(self.table.get_symbols_in_scope("global-scope"), [])
        self.assertIsNone(self.table.get_parent_symbol("sym-method"))

        # Unregistering non-existent symbol raises error
        with self.assertRaises(SemanticModelError):
            self.table.unregister_symbol("sym-class")


if __name__ == "__main__":
    unittest.main()
