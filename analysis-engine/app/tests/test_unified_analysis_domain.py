"""Unit tests for the Unified Analysis domain layer."""

import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from app.unified_analysis import (
    AnalysisStatus,
    UnifiedAnalysisError,
    UnifiedAnalysisAggregationError,
    UnifiedAnalysisReport,
    UnifiedAnalysisAnalyzer,
)


class DummyAnalyzer(UnifiedAnalysisAnalyzer):
    """Concrete implementation of the UnifiedAnalysisAnalyzer for testing purposes."""

    def analyze(self, *, project_name: str, context: str, **kwargs) -> UnifiedAnalysisReport:
        return UnifiedAnalysisReport(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            status=AnalysisStatus.SUCCESS,
            metadata={"source": context},
        )


class TestUnifiedAnalysisDomain(unittest.TestCase):
    """Verifies DTO immutability, enums validation, and domain exception patterns."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.report = UnifiedAnalysisReport(
            project_name="UnifiedProj",
            generated_at=self.time_utc,
            status=AnalysisStatus.SUCCESS,
            metadata={"test_key": "test_val"},
        )

    def test_enum_values(self) -> None:
        """Verifies enum value mappings."""
        self.assertEqual(AnalysisStatus.PENDING.value, "pending")
        self.assertEqual(AnalysisStatus.RUNNING.value, "running")
        self.assertEqual(AnalysisStatus.SUCCESS.value, "success")
        self.assertEqual(AnalysisStatus.FAILED.value, "failed")

    def test_exception_hierarchy(self) -> None:
        """Verifies custom domain exception inherits base error."""
        err = UnifiedAnalysisAggregationError("Aggregation failed")
        self.assertIsInstance(err, UnifiedAnalysisError)

    def test_immutable_dto_properties(self) -> None:
        """Verifies UnifiedAnalysisReport is read-only at runtime."""
        with self.assertRaises(ValidationErrorInheritor if hasattr(self, "ValidationErrorInheritor") else Exception):
            self.report.project_name = "NewName"  # type: ignore

    def test_project_name_validation(self) -> None:
        """Verifies project_name cannot be empty or whitespace-only."""
        with self.assertRaises(ValueError):
            UnifiedAnalysisReport(
                project_name="   ",
                generated_at=self.time_utc,
                status=AnalysisStatus.SUCCESS,
            )

    def test_timezone_aware_utc_timestamp(self) -> None:
        """Verifies generated_at validator rejects naive or non-UTC datetimes."""
        naive_dt = datetime.now()
        with self.assertRaises(ValueError):
            UnifiedAnalysisReport(
                project_name="Proj",
                generated_at=naive_dt,
                status=AnalysisStatus.SUCCESS,
            )

        eastern_dt = datetime.now(timezone.utc).astimezone()
        if eastern_dt.tzinfo != timezone.utc:
            with self.assertRaises(ValueError):
                UnifiedAnalysisReport(
                    project_name="Proj",
                    generated_at=eastern_dt,
                    status=AnalysisStatus.SUCCESS,
                )

    def test_mapping_proxy_type_metadata(self) -> None:
        """Verifies metadata is frozen as a MappingProxyType."""
        self.assertIsInstance(self.report.metadata, MappingProxyType)
        with self.assertRaises(TypeError):
            self.report.metadata["new_key"] = "val"  # type: ignore

    def test_deterministic_equality(self) -> None:
        """Verifies that two reports with matching fields share equality."""
        r1 = UnifiedAnalysisReport(
            project_name="ProjA",
            generated_at=self.time_utc,
            status=AnalysisStatus.SUCCESS,
            metadata={"k": "v"},
        )
        r2 = UnifiedAnalysisReport(
            project_name="ProjA",
            generated_at=self.time_utc,
            status=AnalysisStatus.SUCCESS,
            metadata={"k": "v"},
        )
        self.assertEqual(r1, r2)

    def test_analyzer_abstract_contract(self) -> None:
        """Verifies abstract base analyzer registration and invocation contract."""
        analyzer = DummyAnalyzer()
        res = analyzer.analyze(project_name="TestDummy", context="LocalCtx")

        self.assertIsInstance(res, UnifiedAnalysisReport)
        self.assertEqual(res.project_name, "TestDummy")
        self.assertEqual(res.metadata["source"], "LocalCtx")


if __name__ == "__main__":
    unittest.main()
