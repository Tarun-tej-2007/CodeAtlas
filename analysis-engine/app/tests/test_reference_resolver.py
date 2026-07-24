"""Unit tests for the ReferenceResolver engine class."""

import unittest
from pathlib import Path

from app.scanner.models import Language
from app.semantic.enums import SymbolKind, ReferenceKind, ScopeKind
from app.semantic import (
    Location,
    SemanticSymbol,
    ScopeManager,
    SymbolTable,
    ReferenceResolver,
)


class TestReferenceResolver(unittest.TestCase):
    """Tests resolution flows, scopes ascents, shadowed declarations, and unresolved diagnostics."""

    def setUp(self) -> None:
        self.scope_manager = ScopeManager(root_id="global")
        self.symbol_table = SymbolTable()
        self.resolver = ReferenceResolver(
            scope_manager=self.scope_manager,
            symbol_table=self.symbol_table
        )
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)

        # 1. Register global variable "x"
        self.sym_global_x = SemanticSymbol(
            id="sym-global-x",
            name="x",
            qualified_name="global.x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="global",
        )
        self.symbol_table.register_symbol(self.sym_global_x)

        # 2. Register global function "my_func"
        self.sym_func = SemanticSymbol(
            id="sym-func",
            name="my_func",
            qualified_name="global.my_func",
            kind=SymbolKind.FUNCTION,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="global",
        )
        self.symbol_table.register_symbol(self.sym_func)

        # 3. Create nested function scope
        self.func_scope = self.scope_manager.create_scope(id="func-scope", kind=ScopeKind.FUNCTION)

    def test_successful_reference_resolution(self) -> None:
        # Successful lookup at global level
        usage_loc = Location(start_line=5, start_column=4, end_line=5, end_column=5)
        symbol = self.resolver.resolve_reference(
            name="my_func",
            location=usage_loc,
            reference_kind=ReferenceKind.CALL
        )

        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.id, "sym-func")

        # Verify recorded reference
        resolved = self.resolver.get_resolved_references()
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].symbol_id, "sym-func")
        self.assertEqual(resolved[0].reference_kind, ReferenceKind.CALL)
        self.assertEqual(resolved[0].location, usage_loc)

    def test_parent_and_global_scope_lookup(self) -> None:
        # Enter func-scope
        self.scope_manager.enter_scope(self.func_scope)

        # Resolve "x" from inside function. It should ascend to global scope.
        usage_loc = Location(start_line=10, start_column=8, end_line=10, end_column=9)
        symbol = self.resolver.resolve_reference(name="x", location=usage_loc)

        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.id, "sym-global-x")

        # Check references for symbol helper
        refs = self.resolver.get_references_for_symbol("sym-global-x")
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].location, usage_loc)

    def test_shadowed_declarations(self) -> None:
        # Define nested "x" in function scope (shadowing global "x")
        sym_local_x = SemanticSymbol(
            id="sym-local-x",
            name="x",
            qualified_name="global.my_func.x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=self.loc,
            scope_id="func-scope",
        )
        self.symbol_table.register_symbol(sym_local_x)

        # Enter func-scope
        self.scope_manager.enter_scope(self.func_scope)

        # Resolve "x" from inside function. Must resolve to local instead of global.
        usage_loc = Location(start_line=12, start_column=4, end_line=12, end_column=5)
        symbol = self.resolver.resolve_reference(name="x", location=usage_loc)

        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.id, "sym-local-x")

    def test_unresolved_references_and_diagnostics(self) -> None:
        usage_loc = Location(start_line=15, start_column=0, end_line=15, end_column=1)
        symbol = self.resolver.resolve_reference(name="y", location=usage_loc)

        # y is not registered, should return None
        self.assertIsNone(symbol)

        # Check unresolved list
        unresolved = self.resolver.get_unresolved_references()
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0], ("y", usage_loc))

        # Check diagnostics
        diagnostics = self.resolver.get_diagnostics()
        self.assertEqual(len(diagnostics), 1)
        self.assertIn("Unresolved reference to identifier 'y'", diagnostics[0])

    def test_invalid_start_scope_id(self) -> None:
        usage_loc = Location(start_line=20, start_column=0, end_line=20, end_column=2)
        symbol = self.resolver.resolve_reference(
            name="x",
            location=usage_loc,
            start_scope_id="non-existent-scope"
        )

        self.assertIsNone(symbol)
        self.assertEqual(len(self.resolver.get_diagnostics()), 1)
        self.assertEqual(len(self.resolver.get_unresolved_references()), 1)

    def test_repeated_resolutions_and_clear(self) -> None:
        usage_loc = Location(start_line=22, start_column=0, end_line=22, end_column=1)
        self.resolver.resolve_reference(name="x", location=usage_loc)
        self.resolver.resolve_reference(name="x", location=usage_loc)

        self.assertEqual(len(self.resolver.get_resolved_references()), 2)

        # Clear
        self.resolver.clear()
        self.assertEqual(len(self.resolver.get_resolved_references()), 0)
        self.assertEqual(len(self.resolver.get_unresolved_references()), 0)
        self.assertEqual(len(self.resolver.get_diagnostics()), 0)


if __name__ == "__main__":
    unittest.main()
