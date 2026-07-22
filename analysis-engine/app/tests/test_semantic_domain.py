"""Unit tests for the Semantic domain models, enums, and exceptions."""

import unittest
from pathlib import Path
from pydantic import ValidationError

from app.scanner.models import Language
from app.semantic import (
    SymbolKind,
    ScopeKind,
    ReferenceKind,
    VisibilityKind,
    Location,
    SemanticSymbol,
    SemanticReference,
    SemanticScope,
    SemanticResult,
    SemanticError,
    SemanticAnalysisError,
    SemanticModelError,
    SemanticResolutionError,
)


class TestSemanticDomain(unittest.TestCase):
    """Tests properties, schemas, serialization, and constraints of the semantic domain."""

    def test_semantic_enums(self) -> None:
        # Verify enum values are consistent
        self.assertEqual(SymbolKind.CLASS, "class")
        self.assertEqual(ScopeKind.FUNCTION, "function")
        self.assertEqual(ReferenceKind.CALL, "call")
        self.assertEqual(VisibilityKind.PUBLIC, "public")

    def test_location_validation(self) -> None:
        # Successful validation
        loc = Location(start_line=1, start_column=0, end_line=2, end_column=10)
        self.assertEqual(loc.start_line, 1)

        # Failure validation (negative coordinates)
        with self.assertRaises(ValidationError):
            Location(start_line=0, start_column=0, end_line=1, end_column=10)

    def test_semantic_symbol_defaults_and_immutability(self) -> None:
        loc = Location(start_line=10, start_column=5, end_line=10, end_column=20)
        symbol = SemanticSymbol(
            id="symbol-1",
            name="my_func",
            qualified_name="module.my_func",
            kind=SymbolKind.FUNCTION,
            language=Language.PYTHON,
            file_path=Path("/app/src/module.py"),
            location=loc,
        )

        # Verify defaults
        self.assertEqual(symbol.visibility, VisibilityKind.PUBLIC)
        self.assertEqual(symbol.metadata, {})
        self.assertIsNone(symbol.parent_symbol_id)

        # Verify immutability (frozen BaseModel raises ValidationError or TypeError)
        with self.assertRaises((ValidationError, TypeError)):
            symbol.name = "new_name"  # type: ignore

    def test_semantic_result_serialization(self) -> None:
        loc = Location(start_line=5, start_column=0, end_line=5, end_column=10)
        symbol = SemanticSymbol(
            id="sym-id",
            name="MyClass",
            qualified_name="MyClass",
            kind=SymbolKind.CLASS,
            language=Language.TYPESCRIPT,
            file_path=Path("main.ts"),
            location=loc,
        )
        ref = SemanticReference(
            symbol_id="sym-id",
            reference_kind=ReferenceKind.INSTANTIATE,
            location=loc,
        )
        scope = SemanticScope(
            id="scope-id",
            kind=ScopeKind.CLASS,
            symbol_ids=["sym-id"],
        )

        result = SemanticResult(
            symbols=[symbol],
            references=[ref],
            scopes=[scope],
            diagnostics=["warning: type mismatch"],
        )

        # Dump to dictionary and verify contents
        dumped = result.model_dump()
        self.assertEqual(len(dumped["symbols"]), 1)
        self.assertEqual(dumped["symbols"][0]["name"], "MyClass")
        self.assertEqual(dumped["references"][0]["reference_kind"], "instantiate")
        self.assertEqual(dumped["scopes"][0]["symbol_ids"], ["sym-id"])
        self.assertEqual(dumped["diagnostics"], ["warning: type mismatch"])

    def test_exceptions_hierarchy(self) -> None:
        self.assertTrue(issubclass(SemanticAnalysisError, SemanticError))
        self.assertTrue(issubclass(SemanticModelError, SemanticError))
        self.assertTrue(issubclass(SemanticResolutionError, SemanticError))


if __name__ == "__main__":
    unittest.main()
