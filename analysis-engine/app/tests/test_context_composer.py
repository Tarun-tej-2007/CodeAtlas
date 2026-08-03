"""Unit tests for the AI Context Composer."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.ai.enums import ContextPriority, ContextType, SummaryGranularity
from app.ai.models import ContextSection, SymbolContext, RepositoryContext, AIContextResult
from app.ai.context_composer import AIContextComposer


class TestAIContextComposer(unittest.TestCase):
    """Verifies context merging, priority ordering, duplicate deduplication, and thread safety."""

    def setUp(self) -> None:
        self.composer = AIContextComposer()

    def test_empty_inputs(self) -> None:
        res = self.composer.compose(repo_result=None, symbol_result=None)
        self.assertEqual(res.sections, [])
        self.assertEqual(res.symbols, [])
        self.assertEqual(res.repository, None)

    def test_repository_only_context(self) -> None:
        repo_dto = RepositoryContext(repo_name="my-repo", file_paths=[], primary_languages=[])
        sec = ContextSection(id="s-repo", title="Repo", content="Content", priority=ContextPriority.MEDIUM)
        repo_res = AIContextResult(
            id="r1",
            context_type=ContextType.FILE,
            granularity=SummaryGranularity.COMPACT,
            sections=[sec],
            symbols=[],
            repository=repo_dto,
            diagnostics=["Repo diagnostics"]
        )

        res = self.composer.compose(repo_result=repo_res)
        self.assertEqual(res.repository.repo_name, "my-repo")
        self.assertEqual(len(res.sections), 1)
        self.assertEqual(res.sections[0].id, "s-repo")

    def test_symbol_only_context(self) -> None:
        sym = SymbolContext(symbol_id="sym-1", qualified_name="math.add", kind="function", definition_summary="...")
        sec = ContextSection(id="s-sym", title="Sym", content="Content", priority=ContextPriority.HIGH)
        symbol_res = AIContextResult(
            id="s1",
            context_type=ContextType.SYMBOL,
            granularity=SummaryGranularity.DETAILED,
            sections=[sec],
            symbols=[sym],
            repository=None,
            diagnostics=["Sym diagnostics"]
        )

        res = self.composer.compose(symbol_result=symbol_res)
        self.assertEqual(len(res.symbols), 1)
        self.assertEqual(res.symbols[0].symbol_id, "sym-1")
        self.assertEqual(len(res.sections), 1)
        self.assertEqual(res.sections[0].id, "s-sym")

    def test_combined_context_and_priority_ordering(self) -> None:
        # Define sections with different priorities
        sec_low = ContextSection(id="sec-low", title="Low", content="L", priority=ContextPriority.LOW)
        sec_high = ContextSection(id="sec-high", title="High", content="H", priority=ContextPriority.HIGH)
        sec_crit = ContextSection(id="sec-crit", title="Crit", content="C", priority=ContextPriority.CRITICAL)
        sec_med = ContextSection(id="sec-med", title="Med", content="M", priority=ContextPriority.MEDIUM)

        repo_res = AIContextResult(
            id="r1", context_type=ContextType.FILE, sections=[sec_low, sec_high], symbols=[], repository=None
        )
        symbol_res = AIContextResult(
            id="s1", context_type=ContextType.SYMBOL, sections=[sec_crit, sec_med], symbols=[], repository=None
        )

        res = self.composer.compose(repo_result=repo_res, symbol_result=symbol_res)

        self.assertEqual(len(res.sections), 4)
        # Check order: Critical, High, Medium, Low
        self.assertEqual(res.sections[0].id, "sec-crit")
        self.assertEqual(res.sections[1].id, "sec-high")
        self.assertEqual(res.sections[2].id, "sec-med")
        self.assertEqual(res.sections[3].id, "sec-low")

    def test_duplicate_section_removal_and_priority_win(self) -> None:
        # Duplicate section ID 'sec-dup', but one has MEDIUM and the other has CRITICAL priority
        sec_dup_med = ContextSection(id="sec-dup", title="Duplicate", content="Med content", priority=ContextPriority.MEDIUM)
        sec_dup_crit = ContextSection(id="sec-dup", title="Duplicate", content="Crit content", priority=ContextPriority.CRITICAL)

        repo_res = AIContextResult(
            id="r1", context_type=ContextType.FILE, sections=[sec_dup_med], symbols=[], repository=None
        )
        symbol_res = AIContextResult(
            id="s1", context_type=ContextType.SYMBOL, sections=[sec_dup_crit], symbols=[], repository=None
        )

        res = self.composer.compose(repo_result=repo_res, symbol_result=symbol_res)

        # Deduplication should leave exactly 1 section
        self.assertEqual(len(res.sections), 1)
        self.assertEqual(res.sections[0].id, "sec-dup")
        # Higher priority (CRITICAL) must win, retaining its content
        self.assertEqual(res.sections[0].priority, ContextPriority.CRITICAL)
        self.assertEqual(res.sections[0].content, "Crit content")

    def test_serialization(self) -> None:
        sec = ContextSection(id="s1", title="Title", content="Content", priority=ContextPriority.MEDIUM)
        repo_res = AIContextResult(
            id="r1", context_type=ContextType.FILE, sections=[sec], symbols=[], repository=None
        )
        res = self.composer.compose(repo_result=repo_res)

        dump = res.model_dump()
        self.assertIn("composed-context-run", dump["id"])

        json_str = res.model_dump_json()
        self.assertIn('"id":"s1"', json_str)

    def test_repeated_execution_and_determinism(self) -> None:
        sec = ContextSection(id="s1", title="Title", content="Content", priority=ContextPriority.MEDIUM)
        repo_res = AIContextResult(
            id="r1", context_type=ContextType.FILE, sections=[sec], symbols=[], repository=None
        )

        res1 = self.composer.compose(repo_result=repo_res)
        res2 = self.composer.compose(repo_result=repo_res)

        self.assertEqual(res1.id, res2.id)
        self.assertEqual(res1, res2)

    def test_thread_safety_and_concurrency(self) -> None:
        sec = ContextSection(id="s1", title="Title", content="Content", priority=ContextPriority.MEDIUM)
        repo_res = AIContextResult(
            id="r1", context_type=ContextType.FILE, sections=[sec], symbols=[], repository=None
        )

        def run_compose():
            return self.composer.compose(repo_result=repo_res)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_compose) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results:
            self.assertEqual(r, first)


if __name__ == "__main__":
    unittest.main()
