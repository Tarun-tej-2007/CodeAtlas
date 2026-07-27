"""Unit tests for the SemanticLinkingPipeline orchestration flow."""

import unittest
from pathlib import Path
from pydantic import ValidationError

from app.semantic.enums import SymbolKind
from app.semantic import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ImportDeclaration,
    ExportDeclaration,
    SymbolReference,
    ProjectFile,
    ProjectSemanticResult,
    SemanticLinkingPipeline,
    LinkedSemanticResult,
)


class TestSemanticLinkingPipeline(unittest.TestCase):
    """Tests the semantic pipeline orchestration steps, diagnostics compilation, statelessness, and immutability."""

    def setUp(self) -> None:
        self.pipeline = SemanticLinkingPipeline()
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)
        self.loc_utils = SymbolLocation(file_path=Path("src/utils.py"), location=self.loc)
        self.loc_main = SymbolLocation(file_path=Path("src/main.py"), location=self.loc)

        # Build symbols
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

    def test_successful_pipeline_execution(self) -> None:
        # Define clean project setup
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
        ref_local = SymbolReference(name="local_var", location=self.loc_main)

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[self.sym_local],
            imports=[imp_helper],
            exports=[],
            references=[ref_helper, ref_local]
        )

        project_result = ProjectSemanticResult(
            files={
                Path("src/utils.py"): file_utils,
                Path("src/main.py"): file_main
            }
        )

        # Run pipeline
        linked = self.pipeline.link_project(project_result)

        # Assert correct result aggregates
        self.assertIsInstance(linked, LinkedSemanticResult)
        self.assertEqual(len(linked.diagnostics), 0)
        self.assertEqual(len(linked.import_export_result.resolved_imports), 1)
        self.assertEqual(len(linked.reference_resolution_result.resolved_references), 2)
        
        # Verify specific reference target link
        ref_helper_resolved = next(
            r for r in linked.reference_resolution_result.resolved_references if r.reference.name == "helper"
        )
        self.assertEqual(ref_helper_resolved.target_symbol.id, "sym-helper")

        # Verify immutability of LinkedSemanticResult (raises ValidationError or TypeError)
        with self.assertRaises((ValidationError, TypeError)):
            linked.diagnostics = ["injecting error"]  # type: ignore

    def test_diagnostics_aggregation_and_partial_failures(self) -> None:
        # Inconsistent export (local ID not declared in utils)
        exp_bad = ExportDeclaration(exported_name="Missing", local_symbol_id="ghost-id", location=self.loc_utils)
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[],
            imports=[],
            exports=[exp_bad],
            references=[]
        )

        # Unresolved import + unresolved local reference
        imp_bad = ImportDeclaration(
            imported_name="ghost",
            module_specifier="./missing_module",
            location=self.loc_main
        )
        ref_unresolved = SymbolReference(name="unresolved_var", location=self.loc_main)

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_bad],
            exports=[],
            references=[ref_unresolved]
        )

        project_result = ProjectSemanticResult(
            files={
                Path("src/utils.py"): file_utils,
                Path("src/main.py"): file_main
            }
        )

        linked = self.pipeline.link_project(project_result)

        # Verification of warning collection
        self.assertEqual(len(linked.diagnostics), 3)
        # 1. Index warning: inconsistent export
        self.assertTrue(any("Inconsistent export mapping" in d for d in linked.diagnostics))
        # 2. Import resolver warning: missing module
        self.assertTrue(any("Unresolved module specifier" in d for d in linked.diagnostics))
        # 3. Reference resolver warning: unresolved variable reference
        self.assertTrue(any("Unresolved reference" in d for d in linked.diagnostics))

    def test_stateless_repeated_execution(self) -> None:
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[self.sym_local],
            imports=[],
            exports=[],
            references=[SymbolReference(name="local_var", location=self.loc_main)]
        )
        project_result = ProjectSemanticResult(files={Path("src/main.py"): file_main})

        # Sweep 1
        linked1 = self.pipeline.link_project(project_result)
        # Sweep 2
        linked2 = self.pipeline.link_project(project_result)

        self.assertEqual(
            linked1.reference_resolution_result.resolved_references[0].target_symbol.id,
            linked2.reference_resolution_result.resolved_references[0].target_symbol.id,
        )


if __name__ == "__main__":
    unittest.main()
