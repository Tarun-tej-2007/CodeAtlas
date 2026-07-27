"""Comprehensive validation and concurrency tests for the semantic linking subsystem."""

import unittest
import concurrent.futures
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
    ProjectSemanticResult,
    SemanticLinkingPipeline,
    PathResolutionCache,
)


class TestSemanticLinkingValidation(unittest.TestCase):
    """Exercises concurrency, circular loops, self-imports, cache isolations, and edge repository sizes."""

    def setUp(self) -> None:
        self.pipeline = SemanticLinkingPipeline()
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)
        self.loc_a = SymbolLocation(file_path=Path("src/a.py"), location=self.loc)
        self.loc_b = SymbolLocation(file_path=Path("src/b.py"), location=self.loc)

    def test_circular_imports_and_cyclic_references(self) -> None:
        # File A imports 'b_helper' from B, exports 'a_helper', references 'b_helper'
        sym_a = ProjectSymbol(
            id="sym-a",
            name="a_helper",
            qualified_name="src.a.a_helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_a,
        )
        exp_a = ExportDeclaration(exported_name="a_helper", local_symbol_id="sym-a", location=self.loc_a)
        imp_a = ImportDeclaration(imported_name="b_helper", module_specifier="./b", location=self.loc_a)
        ref_a = SymbolReference(name="b_helper", location=self.loc_a)

        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[sym_a],
            imports=[imp_a],
            exports=[exp_a],
            references=[ref_a]
        )

        # File B imports 'a_helper' from A, exports 'b_helper', references 'a_helper'
        sym_b = ProjectSymbol(
            id="sym-b",
            name="b_helper",
            qualified_name="src.b.b_helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_b,
        )
        exp_b = ExportDeclaration(exported_name="b_helper", local_symbol_id="sym-b", location=self.loc_b)
        imp_b = ImportDeclaration(imported_name="a_helper", module_specifier="./a", location=self.loc_b)
        ref_b = SymbolReference(name="a_helper", location=self.loc_b)

        file_b = ProjectFile(
            path=Path("src/b.py"),
            symbols=[sym_b],
            imports=[imp_b],
            exports=[exp_b],
            references=[ref_b]
        )

        project = ProjectSemanticResult(
            files={
                Path("src/a.py"): file_a,
                Path("src/b.py"): file_b
            }
        )

        linked = self.pipeline.link_project(project)

        # Confirm resolution does not block or stack overflow on circular paths
        self.assertEqual(len(linked.diagnostics), 0)
        self.assertEqual(len(linked.import_export_result.resolved_imports), 2)
        self.assertEqual(len(linked.reference_resolution_result.resolved_references), 2)

        # Confirm references resolve correctly across the cycle
        resolved_a = next(r for r in linked.reference_resolution_result.resolved_references if r.reference.name == "b_helper")
        self.assertEqual(resolved_a.target_symbol.id, "sym-b")

        resolved_b = next(r for r in linked.reference_resolution_result.resolved_references if r.reference.name == "a_helper")
        self.assertEqual(resolved_b.target_symbol.id, "sym-a")

    def test_self_imports_resolution(self) -> None:
        # File A imports its own helper (self import)
        sym_a = ProjectSymbol(
            id="sym-a",
            name="a_helper",
            qualified_name="src.a.a_helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_a,
        )
        exp_a = ExportDeclaration(exported_name="a_helper", local_symbol_id="sym-a", location=self.loc_a)
        imp_self = ImportDeclaration(imported_name="a_helper", module_specifier="./a", location=self.loc_a)
        ref_self = SymbolReference(name="a_helper", location=self.loc_a)

        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[sym_a],
            imports=[imp_self],
            exports=[exp_a],
            references=[ref_self]
        )

        project = ProjectSemanticResult(files={Path("src/a.py"): file_a})
        linked = self.pipeline.link_project(project)

        self.assertEqual(len(linked.diagnostics), 0)
        self.assertEqual(len(linked.import_export_result.resolved_imports), 1)
        self.assertEqual(len(linked.reference_resolution_result.resolved_references), 1)
        self.assertEqual(linked.reference_resolution_result.resolved_references[0].target_symbol.id, "sym-a")

    def test_empty_and_single_file_projects(self) -> None:
        # 1. Empty project
        empty_project = ProjectSemanticResult(files={})
        linked_empty = self.pipeline.link_project(empty_project)
        self.assertEqual(len(linked_empty.original_result.files), 0)
        self.assertEqual(len(linked_empty.diagnostics), 0)

        # 2. Single-file project
        sym_a = ProjectSymbol(
            id="sym-a",
            name="a_helper",
            qualified_name="src.a.a_helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_a,
        )
        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[sym_a],
            imports=[],
            exports=[],
            references=[]
        )
        single_project = ProjectSemanticResult(files={Path("src/a.py"): file_a})
        linked_single = self.pipeline.link_project(single_project)
        self.assertEqual(len(linked_single.original_result.files), 1)
        self.assertEqual(linked_single.symbol_index.get_symbol_by_id("sym-a"), sym_a)

    def test_cache_isolation_between_runs(self) -> None:
        cache = PathResolutionCache()
        
        # Resolve in first workspace scope
        cache.set(Path("src/main.py"), "./utils", Path("src/utils.py"))
        
        # Second run should construct an isolated fresh cache inside link_project
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[ImportDeclaration(imported_name="helper", module_specifier="./utils", location=self.loc_a)],
            exports=[],
            references=[]
        )
        project = ProjectSemanticResult(files={Path("src/main.py"): file_main})
        
        # The internal link_project execution handles its own cache and leaves the external cache untouched
        linked = self.pipeline.link_project(project)
        self.assertEqual(len(linked.import_export_result.resolved_imports), 0) # unresolved because utils.py is missing in project files
        self.assertEqual(cache.get(Path("src/main.py"), "./utils"), Path("src/utils.py"))

    def test_concurrent_pipeline_execution(self) -> None:
        # Verifies that running the linking pipeline across multiple threads on distinct project inputs does not raise race conditions
        def run_thread(thread_id: int) -> int:
            file_path = Path(f"src/file_{thread_id}.py")
            loc = SymbolLocation(file_path=file_path, location=self.loc)
            sym = ProjectSymbol(
                id=f"sym-{thread_id}",
                name=f"helper_{thread_id}",
                qualified_name=f"src.file_{thread_id}.helper_{thread_id}",
                kind=SymbolKind.FUNCTION,
                location=loc,
            )
            file_obj = ProjectFile(
                path=file_path,
                symbols=[sym],
                imports=[],
                exports=[],
                references=[SymbolReference(name=f"helper_{thread_id}", location=loc)]
            )
            project = ProjectSemanticResult(files={file_path: file_obj})
            res = self.pipeline.link_project(project)
            return len(res.reference_resolution_result.resolved_references)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_thread, i) for i in range(10)]
            results = [f.result() for f in futures]

        self.assertEqual(results, [1] * 10)


if __name__ == "__main__":
    unittest.main()
