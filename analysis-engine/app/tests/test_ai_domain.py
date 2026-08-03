"""Unit tests for the AI Context Domain Foundation."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.ai import (
    ContextType,
    ContextPriority,
    SummaryGranularity,
    AIAnalysisCategory,
    AIContextError,
    AIContextValidationError,
    AIContextModelError,
    ContextSection,
    SymbolContext,
    RepositoryContext,
    AIContextResult,
    AIContextBuilder,
)


class DummyContextBuilder(AIContextBuilder):
    """Concrete mock builder to exercise the abstract contract."""

    def __init__(self, value: str = "val") -> None:
        self.value = value

    def build_context(self, *args, **kwargs) -> AIContextResult:
        section = ContextSection(
            id="sec-1",
            title="Title",
            content=f"Content {self.value}",
            priority=ContextPriority.HIGH
        )
        return AIContextResult(
            id="run-1",
            context_type=ContextType.SYMBOL,
            granularity=SummaryGranularity.DETAILED,
            sections=[section],
            symbols=[],
            repository=None,
            diagnostics=["Build dummy context complete."]
        )


class TestAIDomainFoundation(unittest.TestCase):
    """Verifies DTO serialization, domain enums, custom exceptions, and abstract interface boundaries."""

    def test_enums(self) -> None:
        self.assertEqual(ContextType.SYMBOL, "symbol")
        self.assertEqual(ContextPriority.HIGH, "high")
        self.assertEqual(SummaryGranularity.COMPACT, "compact")
        self.assertEqual(AIAnalysisCategory.REFACTORING, "refactoring")

    def test_exceptions_hierarchy(self) -> None:
        with self.assertRaises(AIContextError):
            raise AIContextValidationError("Validation issue")
            
        with self.assertRaises(AIContextError):
            raise AIContextModelError("Model mapping issue")

    def test_model_validation_and_defaults(self) -> None:
        section = ContextSection(
            id="s1",
            title="Section Title",
            content="Hello world"
        )
        # Default priority should be MEDIUM
        self.assertEqual(section.priority, ContextPriority.MEDIUM)
        self.assertEqual(section.metadata, {})

        # Validation fails if required fields are missing
        with self.assertRaises(ValidationError):
            ContextSection(id="s2", title="Title")  # Missing 'content'

    def test_serialization(self) -> None:
        section = ContextSection(
            id="s1",
            title="Section Title",
            content="Hello world"
        )
        dump = section.model_dump()
        self.assertEqual(dump["id"], "s1")
        self.assertEqual(dump["content"], "Hello world")

        json_str = section.model_dump_json()
        self.assertIn('"id":"s1"', json_str)

    def test_immutability(self) -> None:
        section = ContextSection(
            id="s1",
            title="Section Title",
            content="Hello world"
        )
        with self.assertRaises((ValidationError, TypeError)):
            section.content = "New text"  # type: ignore

    def test_abstract_interface_contract(self) -> None:
        # Instantiating a class without implementing the abstract methods fails
        with self.assertRaises(TypeError):
            AIContextBuilder()  # type: ignore

        # Instantiating the concrete implementation works
        builder = DummyContextBuilder(value="test")
        result = builder.build_context()
        self.assertEqual(result.id, "run-1")
        self.assertEqual(result.sections[0].content, "Content test")

    def test_repeated_construction(self) -> None:
        builder = DummyContextBuilder(value="run")
        res1 = builder.build_context()
        res2 = builder.build_context()
        self.assertEqual(res1, res2)

    def test_thread_safety(self) -> None:
        builder = DummyContextBuilder(value="thread")

        def run_thread():
            return builder.build_context()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_thread) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
