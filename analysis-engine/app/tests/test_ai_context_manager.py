"""Unit tests for the AIContextManager component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.ai_service.context import (
    AIContextError,
    ContextSection,
    AIContext,
    AIContextManager,
)


class TestAIContextManager(unittest.TestCase):
    """Verifies DTO immutability, section addition/replacements/removals, duplicate traps, and thread-safe operations."""

    def setUp(self) -> None:
        self.manager = AIContextManager()
        self.sec1 = ContextSection(name="sec-1", content="Content one")
        self.sec2 = ContextSection(name="sec-2", content="Content two")
        self.sec3 = ContextSection(name="sec-3", content="Content three")

    def test_context_creation_and_ordering(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description="Integration test",
            metadata={"source": "test", "depth": 2},
            sections=[self.sec1, self.sec2]
        )

        self.assertEqual(ctx.title, "App Context")
        self.assertEqual(ctx.description, "Integration test")
        self.assertEqual(ctx.metadata["source"], "test")

        # Ordering preserved
        sections = self.manager.list_sections(ctx)
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0].name, "sec-1")
        self.assertEqual(sections[1].name, "sec-2")

    def test_duplicate_section_rejection_on_creation(self) -> None:
        duplicate_sec = ContextSection(name="sec-1", content="Duplicate content")
        with self.assertRaises(AIContextError):
            self.manager.create_context(
                title="Bad Context",
                description=None,
                metadata={},
                sections=[self.sec1, duplicate_sec]
            )

    def test_add_section_and_duplicate_rejection(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={},
            sections=[self.sec1]
        )

        # Successful addition
        ctx2 = self.manager.add_section(ctx, self.sec2)
        self.assertEqual(len(ctx2.sections), 2)
        self.assertEqual(ctx2.sections[1], self.sec2)

        # Original context should NOT be mutated
        self.assertEqual(len(ctx.sections), 1)

        # Duplicate rejection
        with self.assertRaises(AIContextError):
            self.manager.add_section(ctx2, ContextSection(name="sec-1", content="other"))

    def test_replace_section_success_and_unknown(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={},
            sections=[self.sec1, self.sec2]
        )

        # Success
        new_sec = ContextSection(name="sec-1", content="Updated Content")
        ctx2 = self.manager.replace_section(ctx, "sec-1", new_sec)
        self.assertEqual(ctx2.sections[0].content, "Updated Content")
        self.assertEqual(ctx2.sections[1].name, "sec-2")  # sec-2 unaffected

        # Replacement changing name but causing duplicate error
        dup_sec = ContextSection(name="sec-2", content="Collision")
        with self.assertRaises(AIContextError):
            self.manager.replace_section(ctx, "sec-1", dup_sec)

        # Unknown replacement
        with self.assertRaises(AIContextError):
            self.manager.replace_section(ctx, "sec-unknown", new_sec)

    def test_remove_section_success_and_unknown(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={},
            sections=[self.sec1, self.sec2]
        )

        # Success
        ctx2 = self.manager.remove_section(ctx, "sec-1")
        self.assertEqual(len(ctx2.sections), 1)
        self.assertEqual(ctx2.sections[0].name, "sec-2")

        # Unknown removal
        with self.assertRaises(AIContextError):
            self.manager.remove_section(ctx, "sec-unknown")

    def test_get_section_success_and_unknown(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={},
            sections=[self.sec1, self.sec2]
        )

        # Success
        retrieved = self.manager.get_section(ctx, "sec-2")
        self.assertEqual(retrieved, self.sec2)

        # Unknown
        with self.assertRaises(AIContextError):
            self.manager.get_section(ctx, "sec-unknown")

    def test_metadata_immutability(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={"immutable_key": "val"},
            sections=[]
        )

        # Attempting to modify metadata dictionary must raise TypeError
        with self.assertRaises(TypeError):
            ctx.metadata["immutable_key"] = "changed"  # type: ignore

    def test_context_immutability(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={},
            sections=[]
        )

        # Attempting to assign new properties must raise ValidationError or TypeError
        with self.assertRaises((ValidationError, TypeError)):
            ctx.title = "New Title"  # type: ignore

    def test_instances_isolation(self) -> None:
        manager1 = AIContextManager()
        manager2 = AIContextManager()

        # Both managers are stateless and independent
        self.assertIsNot(manager1, manager2)

    def test_concurrent_context_operations(self) -> None:
        ctx = self.manager.create_context(
            title="App Context",
            description=None,
            metadata={},
            sections=[self.sec1]
        )

        # Test operations concurrently with multiple threads
        def run_add():
            return self.manager.add_section(ctx, self.sec2)

        def run_replace():
            new_sec = ContextSection(name="sec-1", content="concurrent-replace")
            return self.manager.replace_section(ctx, "sec-1", new_sec)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures_add = [executor.submit(run_add) for _ in range(10)]
            futures_rep = [executor.submit(run_replace) for _ in range(10)]

            results_add = [f.result() for f in futures_add]
            results_rep = [f.result() for f in futures_rep]

        # Verify all operations yielded correct results safely without mutating original
        self.assertEqual(len(ctx.sections), 1)  # unchanged
        for r in results_add:
            self.assertEqual(len(r.sections), 2)
            self.assertEqual(r.sections[1].name, "sec-2")
        for r in results_rep:
            self.assertEqual(len(r.sections), 1)
            self.assertEqual(r.sections[0].content, "concurrent-replace")

    def test_deterministic_behavior(self) -> None:
        # Create same contexts repeatedly, outputs must be identical
        c1 = self.manager.create_context(
            title="Det", description=None, metadata={"k": "v"}, sections=[self.sec1, self.sec2]
        )
        c2 = self.manager.create_context(
            title="Det", description=None, metadata={"k": "v"}, sections=[self.sec1, self.sec2]
        )
        self.assertEqual(c1, c2)


if __name__ == "__main__":
    unittest.main()
