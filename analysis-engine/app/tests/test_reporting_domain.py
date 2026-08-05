"""Unit tests for the Analysis Reporting Domain foundation."""

import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType

from app.reporting import (
    ReportFormat,
    ReportSection,
    ReportingError,
    ReportGenerationError,
    ReportSectionContent,
    ReportMetadata,
    AnalysisReport,
    ReportGenerator,
)


class DummyGenerator(ReportGenerator):
    """Concrete implementation for testing interface contract definition."""

    def generate(self, *, project_name: str, context: dict, format: ReportFormat, **kwargs) -> AnalysisReport:
        meta = ReportMetadata(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            format=format,
        )
        return AnalysisReport(metadata=meta, sections={})


class TestReportingDomain(unittest.TestCase):
    """Verifies DTO immutability, timezone constraints, mapping proxy freezes, and exceptions."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.section_content = ReportSectionContent(
            section=ReportSection.SUMMARY,
            title="Overview Section",
            content="Aggregate metrics review",
            metadata={"source": "scan-pipeline", "score": 9.5},
        )
        self.metadata = ReportMetadata(
            project_name="CodeAtlasReporting",
            generated_at=self.time_utc,
            format=ReportFormat.JSON,
            extra_info={"engine": "v2", "dry_run": False},
        )
        self.report = AnalysisReport(
            metadata=self.metadata,
            sections={ReportSection.SUMMARY: self.section_content},
        )

    def test_enum_values(self) -> None:
        """Verifies report enums values."""
        self.assertEqual(ReportFormat.JSON.value, "json")
        self.assertEqual(ReportSection.SUMMARY.value, "summary")

    def test_exception_hierarchy(self) -> None:
        """Verifies exception classes derive from ReportingError."""
        self.assertTrue(issubclass(ReportGenerationError, ReportingError))
        with self.assertRaises(ReportingError):
            raise ReportGenerationError("Failed to build markdown report layout.")

    def test_immutable_dto_properties(self) -> None:
        """Verifies Pydantic DTO instances are frozen and reject edits/mutations."""
        with self.assertRaises(ValidationError := Exception):
            # Attempt direct mutation
            self.metadata.project_name = "NewName"  # type: ignore

        with self.assertRaises(ValidationError):
            self.section_content.title = "Empty Title"  # type: ignore

    def test_project_name_validation(self) -> None:
        """Verifies empty or whitespace project names are rejected."""
        with self.assertRaises(ValueError):
            ReportMetadata(
                project_name="   ",
                generated_at=self.time_utc,
                format=ReportFormat.JSON,
            )

    def test_utc_timezone_awareness(self) -> None:
        """Verifies datetime timestamps reject naive or non-UTC values."""
        naive_time = datetime(2026, 8, 5, 12, 0, 0)
        with self.assertRaises(ValueError):
            ReportMetadata(
                project_name="FailProj",
                generated_at=naive_time,
                format=ReportFormat.JSON,
            )

    def test_mapping_proxy_protection(self) -> None:
        """Verifies nested dictionary maps are cast into read-only MappingProxyType views."""
        self.assertIsInstance(self.metadata.extra_info, MappingProxyType)
        self.assertIsInstance(self.section_content.metadata, MappingProxyType)
        self.assertIsInstance(self.report.sections, MappingProxyType)

        # Confirm mutation throws runtime error
        with self.assertRaises(TypeError):
            self.metadata.extra_info["new_key"] = "hack"  # type: ignore

    def test_abstract_interface_enforcement(self) -> None:
        """Verifies the base ReportGenerator cannot be instantiated directly and forces override."""
        with self.assertRaises(TypeError):
            ReportGenerator()  # type: ignore

        # Verify subclass instantiates and executes
        gen = DummyGenerator()
        res = gen.generate(
            project_name="DummyProj",
            context={},
            format=ReportFormat.MARKDOWN,
        )
        self.assertEqual(res.metadata.project_name, "DummyProj")

    def test_deterministic_equality(self) -> None:
        """Verifies DTO equivalence is value-deterministic."""
        meta1 = ReportMetadata(
            project_name="MatchProj",
            generated_at=self.time_utc,
            format=ReportFormat.HTML,
        )
        meta2 = ReportMetadata(
            project_name="MatchProj",
            generated_at=self.time_utc,
            format=ReportFormat.HTML,
        )
        self.assertEqual(meta1, meta2)


if __name__ == "__main__":
    unittest.main()
