"""Unit tests for the project-level semantic models and analyzer interfaces."""

import unittest
from pathlib import Path
from pydantic import ValidationError

from app.scanner.models import Language
from app.semantic.enums import SymbolKind, VisibilityKind
from app.semantic import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ImportDeclaration,
    ExportDeclaration,
    ProjectFile,
    ProjectSemanticResult,
    ProjectSemanticAnalyzer,
)


class DummyProjectAnalyzer(ProjectSemanticAnalyzer):
    """Concrete implementation of ProjectSemanticAnalyzer interface for testing contracts."""

    def analyze_project(self, file_results):
        # Simply returns a dummy empty result to satisfy abstract contract
        return ProjectSemanticResult()


class TestProjectModels(unittest.TestCase):
    """Tests project-wide symbol modeling schema validation, nested imports, and contracts."""

    def setUp(self) -> None:
        self.loc = Location(start_line=1, start_column=0, end_line=2, end_column=10)
        self.sym_loc = SymbolLocation(file_path=Path("src/utils.py"), location=self.loc)

    def test_project_symbol_and_immutability(self) -> None:
        sym = ProjectSymbol(
            id="proj-sym-1",
            name="helper",
            qualified_name="src.utils.helper",
            kind=SymbolKind.FUNCTION,
            location=self.sym_loc,
        )

        self.assertEqual(sym.name, "helper")
        self.assertEqual(sym.location.file_path, Path("src/utils.py"))
        self.assertEqual(sym.visibility, VisibilityKind.PUBLIC)

        # Immutability validation (raises ValidationError or TypeError on change)
        with self.assertRaises((ValidationError, TypeError)):
            sym.name = "new_name"  # type: ignore

    def test_import_and_export_declarations(self) -> None:
        imp = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            local_alias="h",
            location=SymbolLocation(file_path=Path("src/main.py"), location=self.loc),
        )

        self.assertEqual(imp.imported_name, "helper")
        self.assertEqual(imp.module_specifier, "./utils")
        self.assertEqual(imp.local_alias, "h")

        exp = ExportDeclaration(
            exported_name="helper",
            local_symbol_id="proj-sym-1",
            location=self.sym_loc,
        )

        self.assertEqual(exp.exported_name, "helper")
        self.assertEqual(exp.local_symbol_id, "proj-sym-1")

    def test_project_file_and_result_aggregation(self) -> None:
        sym = ProjectSymbol(
            id="proj-sym-1",
            name="helper",
            qualified_name="src.utils.helper",
            kind=SymbolKind.FUNCTION,
            location=self.sym_loc,
        )
        proj_file = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[sym],
            imports=[],
            exports=[],
        )

        result = ProjectSemanticResult(
            files={Path("src/utils.py"): proj_file},
            cross_file_references=[],
            diagnostics=["info: project scan complete"],
        )

        self.assertEqual(len(result.files), 1)
        self.assertIn(Path("src/utils.py"), result.files)
        self.assertEqual(result.files[Path("src/utils.py")].symbols[0].id, "proj-sym-1")
        self.assertEqual(result.diagnostics, ["info: project scan complete"])

        # Serialization validation
        data = result.model_dump()
        self.assertEqual(
            data["files"][Path("src/utils.py")]["symbols"][0]["qualified_name"], "src.utils.helper"
        )

    def test_analyzer_contract_enforcement(self) -> None:
        # Verify instantiation of ProjectSemanticAnalyzer cannot be done directly
        with self.assertRaises(TypeError):
            ProjectSemanticAnalyzer()  # type: ignore

        # Verify a concrete implementation is instantiable and callable
        analyzer = DummyProjectAnalyzer()
        res = analyzer.analyze_project({})
        self.assertIsInstance(res, ProjectSemanticResult)


if __name__ == "__main__":
    unittest.main()
