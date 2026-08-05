"""Unit tests for the Unified Analysis Engine orchestration."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.unified_analysis import (
    AnalysisStatus,
    UnifiedAnalysisContributor,
    UnifiedAnalysisRegistry,
    UnifiedAnalysisEngine,
    UnifiedAnalysisReport,
)


class DummyContributor(UnifiedAnalysisContributor):
    """Mock contributor implementation for testing engine flow executions."""

    def __init__(self, name: str, category: str = "general", output: Any = "success") -> None:
        self._name = name
        self._category = category
        self._output = output

    @property
    def contributor_name(self) -> str:
        return self._name

    @property
    def contributor_type(self) -> str:
        return self._category

    def contribute(self, context: Any, **kwargs) -> Any:
        return self._output


class TestUnifiedAnalysisEngine(unittest.TestCase):
    """Verifies sequential contributor execution, output aggregation, and exception propagation."""

    def setUp(self) -> None:
        self.registry = UnifiedAnalysisRegistry()
        self.engine = UnifiedAnalysisEngine(self.registry)

    def test_constructor_validation(self) -> None:
        """Verifies engine rejects None registry injection."""
        with self.assertRaises(ValueError):
            UnifiedAnalysisEngine(None)  # type: ignore

    def test_empty_registry_execution(self) -> None:
        """Verifies report is generated when no contributors are registered."""
        report = self.engine.analyze(project_name="EmptyProj", context="Ctx")
        self.assertIsInstance(report, UnifiedAnalysisReport)
        self.assertEqual(report.project_name, "EmptyProj")
        self.assertEqual(report.status, AnalysisStatus.SUCCESS)
        self.assertIsNone(report.scan_result)
        self.assertIsNone(report.parse_result)
        self.assertIsNone(report.architecture_result)
        self.assertIsNone(report.quality_result)
        self.assertIsNone(report.technical_debt_result)
        self.assertEqual(len(report.metadata), 0)

    def test_single_contributor_execution(self) -> None:
        """Verifies mapping a single contributor output correctly."""
        c = DummyContributor(name="scan-contrib", category="scan", output={"files": 5})
        self.registry.register(c)

        report = self.engine.analyze(project_name="SingleProj", context="Ctx")
        self.assertEqual(report.scan_result, {"files": 5})
        self.assertIsNone(report.parse_result)

    def test_multiple_contributors_execution_and_order(self) -> None:
        """Verifies executing multiple contributors in correct registration order."""
        c_scan = DummyContributor(name="scan-contrib", category="scan", output="scan-output")
        c_parse = DummyContributor(name="parse-contrib", category="parse", output="parse-output")
        c_arch = DummyContributor(name="arch-contrib", category="architecture", output="arch-output")
        c_qual = DummyContributor(name="qual-contrib", category="quality", output="qual-output")
        c_tech = DummyContributor(name="tech-contrib", category="technical_debt", output="tech-output")
        c_ext = DummyContributor(name="ext-contrib", category="custom_metadata", output="custom-output")

        self.registry.register(c_scan)
        self.registry.register(c_parse)
        self.registry.register(c_arch)
        self.registry.register(c_qual)
        self.registry.register(c_tech)
        self.registry.register(c_ext)

        report = self.engine.analyze(project_name="MultiProj", context="Ctx")

        self.assertEqual(report.scan_result, "scan-output")
        self.assertEqual(report.parse_result, "parse-output")
        self.assertEqual(report.architecture_result, "arch-output")
        self.assertEqual(report.quality_result, "qual-output")
        self.assertEqual(report.technical_debt_result, "tech-output")
        self.assertEqual(report.metadata["custom_metadata"], "custom-output")

    def test_context_forwarding_and_kwargs(self) -> None:
        """Verifies context and custom kwargs pass unmodified to contributors."""
        invoked_args = {}

        class ContextSpyContributor(UnifiedAnalysisContributor):
            @property
            def contributor_name(self) -> str:
                return "spy"

            @property
            def contributor_type(self) -> str:
                return "quality"

            def contribute(self, context: Any, **kwargs) -> Any:
                invoked_args["context"] = context
                invoked_args["extra"] = kwargs.get("extra")
                return "spy-result"

        self.registry.register(ContextSpyContributor())
        self.engine.analyze(project_name="SpyProj", context="SharedCtx", extra="secret")

        self.assertEqual(invoked_args["context"], "SharedCtx")
        self.assertEqual(invoked_args["extra"], "secret")

    def test_exception_propagation(self) -> None:
        """Verifies contributor errors propagate directly without wrapper nesting."""
        class CrashContributor(UnifiedAnalysisContributor):
            @property
            def contributor_name(self) -> str:
                return "crash"

            @property
            def contributor_type(self) -> str:
                return "scan"

            def contribute(self, context: Any, **kwargs) -> Any:
                raise RuntimeError("Contributor crashed")

        self.registry.register(CrashContributor())

        with self.assertRaises(RuntimeError) as ctx:
            self.engine.analyze(project_name="CrashProj", context="Ctx")
        self.assertEqual(str(ctx.exception), "Contributor crashed")

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety under parallel engine executions."""
        c = DummyContributor(name="scan-c", category="scan", output="val")
        self.registry.register(c)

        def run_analyze():
            return self.engine.analyze(project_name="ParallelProj", context="Ctx")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(30)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.scan_result, "val")
            self.assertEqual(res.project_name, "ParallelProj")


if __name__ == "__main__":
    unittest.main()
