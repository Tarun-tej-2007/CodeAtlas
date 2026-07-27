"""Unit tests for the ProjectSymbolIndex class."""

import unittest
from pathlib import Path

from app.scanner.models import Language
from app.semantic.enums import SymbolKind
from app.semantic.exceptions import SemanticModelError
from app.semantic import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ExportDeclaration,
    ProjectFile,
    ProjectSymbolIndex,
)


class TestProjectSymbolIndex(unittest.TestCase):
    """Tests project-wide symbol indexing keys, duplicate IDs, simple name mappings, and exported lookups."""

    def setUp(self) -> None:
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)
        self.loc_a = SymbolLocation(file_path=Path("src/a.py"), location=self.loc)
        self.loc_b = SymbolLocation(file_path=Path("src/b.py"), location=self.loc)

        # Build dummy symbols
        self.sym_class = ProjectSymbol(
            id="sym-class-a",
            name="MyClass",
            qualified_name="src.a.MyClass",
            kind=SymbolKind.CLASS,
            location=self.loc_a,
        )

        self.sym_method = ProjectSymbol(
            id="sym-method-a",
            name="run",
            qualified_name="src.a.MyClass.run",
            kind=SymbolKind.METHOD,
            location=self.loc_a,
            parent_symbol_id="sym-class-a",
        )

        # Duplicate simple name but different ID/qualified name
        self.sym_shadowed = ProjectSymbol(
            id="sym-method-shadow",
            name="run",
            qualified_name="src.b.run",
            kind=SymbolKind.FUNCTION,
            location=self.loc_b,
        )

    def test_successful_indexing_and_lookups(self) -> None:
        exp = ExportDeclaration(exported_name="MyClass", local_symbol_id="sym-class-a", location=self.loc_a)

        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[self.sym_class, self.sym_method],
            imports=[],
            exports=[exp]
        )
        file_b = ProjectFile(
            path=Path("src/b.py"),
            symbols=[self.sym_shadowed],
            imports=[],
            exports=[]
        )

        project = {
            Path("src/a.py"): file_a,
            Path("src/b.py"): file_b
        }

        # Index construction
        index = ProjectSymbolIndex(project)

        # 1. get_symbol_by_id
        self.assertEqual(index.get_symbol_by_id("sym-class-a"), self.sym_class)
        self.assertEqual(index.get_symbol_by_id("sym-method-shadow"), self.sym_shadowed)
        self.assertIsNone(index.get_symbol_by_id("non-existent"))

        # 2. has_symbol
        self.assertTrue(index.has_symbol("sym-class-a"))
        self.assertFalse(index.has_symbol("non-existent"))

        # 3. get_symbol_by_qualified_name
        self.assertEqual(index.get_symbol_by_qualified_name("src.a.MyClass"), self.sym_class)
        self.assertEqual(index.get_symbol_by_qualified_name("src.b.run"), self.sym_shadowed)

        # 4. get_symbol_by_name (simple name lookup returning list)
        run_symbols = index.get_symbol_by_name("run")
        self.assertEqual(len(run_symbols), 2)
        self.assertIn(self.sym_method, run_symbols)
        self.assertIn(self.sym_shadowed, run_symbols)

        # 5. get_symbols_in_file
        symbols_in_a = index.get_symbols_in_file(Path("src/a.py"))
        self.assertEqual(len(symbols_in_a), 2)
        self.assertIn(self.sym_class, symbols_in_a)
        self.assertIn(self.sym_method, symbols_in_a)

        # 6. get_exported_symbols
        exported = index.get_exported_symbols()
        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0].id, "sym-class-a")

        # Diagnostics check (should be empty for clean index)
        self.assertEqual(len(index.diagnostics), 0)

    def test_duplicate_symbol_id_raises_error(self) -> None:
        sym_dup = ProjectSymbol(
            id="sym-class-a",  # Collision
            name="AnotherClass",
            qualified_name="src.b.AnotherClass",
            kind=SymbolKind.CLASS,
            location=self.loc_b,
        )

        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[self.sym_class],
            imports=[],
            exports=[]
        )
        file_b = ProjectFile(
            path=Path("src/b.py"),
            symbols=[sym_dup],
            imports=[],
            exports=[]
        )

        project = {
            Path("src/a.py"): file_a,
            Path("src/b.py"): file_b
        }

        with self.assertRaises(SemanticModelError):
            ProjectSymbolIndex(project)

    def test_duplicate_qualified_name_records_diagnostic(self) -> None:
        sym_dup_qname = ProjectSymbol(
            id="sym-dup-id",
            name="MyClass",
            qualified_name="src.a.MyClass",  # Duplicate qname
            kind=SymbolKind.CLASS,
            location=self.loc_b,
        )

        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[self.sym_class],
            imports=[],
            exports=[]
        )
        file_b = ProjectFile(
            path=Path("src/b.py"),
            symbols=[sym_dup_qname],
            imports=[],
            exports=[]
        )

        project = {
            Path("src/a.py"): file_a,
            Path("src/b.py"): file_b
        }

        index = ProjectSymbolIndex(project)
        self.assertEqual(len(index.diagnostics), 1)
        self.assertIn("Duplicate qualified name", index.diagnostics[0])

    def test_inconsistent_exported_symbol_mapping(self) -> None:
        # Export referencing local_symbol_id that does not exist in symbols
        exp_bad = ExportDeclaration(exported_name="MissingSymbol", local_symbol_id="ghost-id", location=self.loc_a)

        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[self.sym_class],
            imports=[],
            exports=[exp_bad]
        )

        project = {
            Path("src/a.py"): file_a
        }

        index = ProjectSymbolIndex(project)
        self.assertEqual(len(index.diagnostics), 1)
        self.assertIn("Inconsistent export mapping", index.diagnostics[0])
        self.assertEqual(len(index.get_exported_symbols()), 0)


if __name__ == "__main__":
    unittest.main()
