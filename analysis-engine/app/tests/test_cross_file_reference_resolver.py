"""Unit tests for the CrossFileReferenceResolver."""

import unittest
from pathlib import Path

from app.semantic.enums import SymbolKind
from app.semantic import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ImportDeclaration,
    ExportDeclaration,
    SymbolReference,
    ProjectFile,
    ProjectSymbolIndex,
    ImportExportResolver,
    CrossFileReferenceResolver,
)


class TestCrossFileReferenceResolver(unittest.TestCase):
    """Tests cross-file referencing, alias dereferencing, local resolution fallbacks, and diagnostics."""

    def setUp(self) -> None:
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)
        self.loc_utils = SymbolLocation(file_path=Path("src/utils.py"), location=self.loc)
        self.loc_main = SymbolLocation(file_path=Path("src/main.py"), location=self.loc)

        # Dependencies
        self.import_resolver = ImportExportResolver()

        # 1. Define utility symbols
        self.sym_helper = ProjectSymbol(
            id="sym-helper",
            name="helper",
            qualified_name="src.utils.helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_utils,
        )

        self.sym_local = ProjectSymbol(
            id="sym-local",
            name="local_var",
            qualified_name="src.main.local_var",
            kind=SymbolKind.VARIABLE,
            location=self.loc_main,
        )

    def test_successful_cross_file_reference_resolution(self) -> None:
        # File A (src/utils.py): exports helper
        exp_helper = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper],
            imports=[],
            exports=[exp_helper],
            references=[]
        )

        # File B (src/main.py): imports helper from "./utils"
        imp_helper = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            location=self.loc_main
        )
        # B references "helper" (imported) and "local_var" (declared locally)
        ref_helper = SymbolReference(name="helper", location=self.loc_main)
        ref_local = SymbolReference(name="local_var", location=self.loc_main)

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[self.sym_local],
            imports=[imp_helper],
            exports=[],
            references=[ref_helper, ref_local]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }

        # Index and resolve references
        index = ProjectSymbolIndex(project)
        resolver = CrossFileReferenceResolver(index, self.import_resolver)
        result = resolver.resolve_project_references(project)

        # Assertions
        self.assertEqual(len(result.resolved_references), 2)
        self.assertEqual(len(result.unresolved_references), 0)
        self.assertEqual(len(result.diagnostics), 0)

        # Find helper resolved reference
        resolved_helper = next(r for r in result.resolved_references if r.reference.name == "helper")
        self.assertEqual(resolved_helper.target_symbol.id, "sym-helper")

        # Find local resolved reference
        resolved_local = next(r for r in result.resolved_references if r.reference.name == "local_var")
        self.assertEqual(resolved_local.target_symbol.id, "sym-local")

    def test_alias_reference_resolution(self) -> None:
        # File A exports helper
        exp_helper = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper],
            imports=[],
            exports=[exp_helper],
            references=[]
        )

        # File B imports helper as 'h' and references 'h'
        imp_alias = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            local_alias="h",
            location=self.loc_main
        )
        ref_alias = SymbolReference(name="h", location=self.loc_main)

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_alias],
            exports=[],
            references=[ref_alias]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }

        index = ProjectSymbolIndex(project)
        resolver = CrossFileReferenceResolver(index, self.import_resolver)
        result = resolver.resolve_project_references(project)

        # Verification
        self.assertEqual(len(result.resolved_references), 1)
        resolved = result.resolved_references[0]
        self.assertEqual(resolved.reference.name, "h")
        self.assertEqual(resolved.target_symbol.id, "sym-helper")

    def test_unresolved_references(self) -> None:
        # File A empty
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[],
            imports=[],
            exports=[],
            references=[]
        )

        # File B contains a reference to non-existent 'ghost' symbol
        ref_ghost = SymbolReference(name="ghost", location=self.loc_main)
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[],
            exports=[],
            references=[ref_ghost]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }

        index = ProjectSymbolIndex(project)
        resolver = CrossFileReferenceResolver(index, self.import_resolver)
        result = resolver.resolve_project_references(project)

        # Verification
        self.assertEqual(len(result.resolved_references), 0)
        self.assertEqual(len(result.unresolved_references), 1)
        self.assertEqual(result.unresolved_references[0].name, "ghost")
        self.assertEqual(len(result.diagnostics), 1)
        self.assertIn("Unresolved reference to name 'ghost'", result.diagnostics[0])

    def test_ambiguous_references(self) -> None:
        # File A declares two local symbols named 'conflict' (e.g. shadowed blocks or inner functions)
        sym_conflict1 = ProjectSymbol(
            id="sym-c1",
            name="conflict",
            qualified_name="src.main.conflict1",
            kind=SymbolKind.VARIABLE,
            location=self.loc_main,
        )
        sym_conflict2 = ProjectSymbol(
            id="sym-c2",
            name="conflict",
            qualified_name="src.main.conflict2",
            kind=SymbolKind.FUNCTION,
            location=self.loc_main,
        )

        ref_conflict = SymbolReference(name="conflict", location=self.loc_main)

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[sym_conflict1, sym_conflict2],
            imports=[],
            exports=[],
            references=[ref_conflict]
        )

        project = {
            Path("src/main.py"): file_main
        }

        index = ProjectSymbolIndex(project)
        resolver = CrossFileReferenceResolver(index, self.import_resolver)
        result = resolver.resolve_project_references(project)

        # Verification
        self.assertEqual(len(result.resolved_references), 0)
        self.assertEqual(len(result.unresolved_references), 1)
        self.assertEqual(len(result.diagnostics), 1)
        self.assertIn("Ambiguous local reference to name 'conflict'", result.diagnostics[0])

    def test_resolver_statelessness_and_repeated_executions(self) -> None:
        # Verify multiple sweeps do not leak states
        exp_helper = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper],
            imports=[],
            exports=[exp_helper],
            references=[]
        )
        imp_helper = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            location=self.loc_main
        )
        ref_helper = SymbolReference(name="helper", location=self.loc_main)
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_helper],
            exports=[],
            references=[ref_helper]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }

        index = ProjectSymbolIndex(project)
        resolver = CrossFileReferenceResolver(index, self.import_resolver)

        res1 = resolver.resolve_project_references(project)
        res2 = resolver.resolve_project_references(project)

        self.assertEqual(len(res1.resolved_references), 1)
        self.assertEqual(len(res2.resolved_references), 1)
        self.assertEqual(res1.resolved_references[0].target_symbol.id, res2.resolved_references[0].target_symbol.id)


if __name__ == "__main__":
    unittest.main()
