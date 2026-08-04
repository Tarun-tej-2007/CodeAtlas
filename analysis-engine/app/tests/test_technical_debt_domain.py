"""Unit tests for the Technical Debt Domain Foundation layer."""

import unittest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.technical_debt import (
    TechnicalDebtCategory,
    TechnicalDebtSeverity,
    TechnicalDebtError,
    TechnicalDebtRuleError,
    TechnicalDebtItem,
    TechnicalDebtSummary,
    TechnicalDebtReport,
    TechnicalDebtAnalyzer,
)


class DummyDebtAnalyzer(TechnicalDebtAnalyzer):
    """Concrete implementation of TechnicalDebtAnalyzer interface for testing contract enforcement."""

    def analyze(self, *args, **kwargs) -> TechnicalDebtReport:
        summary = TechnicalDebtSummary(
            total_items=0,
            total_effort_minutes=0,
            items_by_category={},
            effort_by_severity={},
        )
        return TechnicalDebtReport(
            project_name="DummyProj",
            generated_at=datetime.now(timezone.utc),
            items=(),
            summary=summary,
        )


class TestTechnicalDebtDomain(unittest.TestCase):
    """Verifies domain enums, exceptions, DTO immutability, timezone asserts, and abstract contract bindings."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)

        self.item = TechnicalDebtItem(
            id="debt-123",
            category=TechnicalDebtCategory.CODE_SMELL,
            severity=TechnicalDebtSeverity.MEDIUM,
            title="Long Method Smell",
            description="Method length exceeds limit",
            effort_minutes=30,
            location_file="app/main.py",
            location_line=42,
            metadata={"rule_id": "smell-rule"},
        )
        self.summary = TechnicalDebtSummary(
            total_items=1,
            total_effort_minutes=30,
            items_by_category={TechnicalDebtCategory.CODE_SMELL: 1},
            effort_by_severity={TechnicalDebtSeverity.MEDIUM: 30},
            metadata={"run_type": "adhoc"},
        )
        self.report = TechnicalDebtReport(
            project_name="TestProj",
            generated_at=self.time_utc,
            items=(self.item,),
            summary=self.summary,
            metadata={"build_number": 105},
        )

    def test_enums(self) -> None:
        """Verifies enum categorizations and correct string values."""
        self.assertEqual(TechnicalDebtCategory.CODE_SMELL, "code_smell")
        self.assertEqual(TechnicalDebtSeverity.CRITICAL, "critical")
        self.assertEqual(len(TechnicalDebtCategory), 8)
        self.assertEqual(len(TechnicalDebtSeverity), 5)

    def test_exceptions_hierarchy(self) -> None:
        """Verifies exception subclass mappings."""
        self.assertTrue(issubclass(TechnicalDebtRuleError, TechnicalDebtError))
        self.assertTrue(issubclass(TechnicalDebtError, Exception))

        with self.assertRaises(TechnicalDebtRuleError):
            raise TechnicalDebtRuleError("Rule violation checked.")

    def test_immutable_dtos(self) -> None:
        """Verifies direct assignments on frozen Pydantic models are rejected."""
        with self.assertRaises(ValidationError):
            self.item.effort_minutes = 60  # type: ignore

        with self.assertRaises(ValidationError):
            self.report.project_name = "NewName"  # type: ignore

    def test_timezone_validation(self) -> None:
        """Verifies timezone-naive or non-UTC datetimes fail report validation."""
        naive = datetime(2026, 8, 4, 12, 0, 0)
        with self.assertRaises(ValidationError):
            TechnicalDebtReport(
                project_name="Proj",
                generated_at=naive,
                summary=self.summary,
            )

        from datetime import timedelta
        non_utc = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone(timedelta(hours=2)))
        with self.assertRaises(ValidationError):
            TechnicalDebtReport(
                project_name="Proj",
                generated_at=non_utc,
                summary=self.summary,
            )

    def test_metadata_immutability(self) -> None:
        """Verifies that metadata dictionaries are read-only views (MappingProxyType)."""
        with self.assertRaises(TypeError):
            self.item.metadata["hack"] = "value"  # type: ignore

        with self.assertRaises(TypeError):
            self.report.metadata["new_key"] = "hack"  # type: ignore

    def test_abstract_analyzer(self) -> None:
        """Verifies ABC instantiations fail but concrete subclass works."""
        with self.assertRaises(TypeError):
            TechnicalDebtAnalyzer()  # type: ignore

        analyzer = DummyDebtAnalyzer()
        res = analyzer.analyze()
        self.assertIsInstance(res, TechnicalDebtReport)
        self.assertEqual(res.project_name, "DummyProj")

    def test_deterministic_equality(self) -> None:
        """Verifies duplicate setups produce equivalent instances."""
        item2 = TechnicalDebtItem(
            id="debt-123",
            category=TechnicalDebtCategory.CODE_SMELL,
            severity=TechnicalDebtSeverity.MEDIUM,
            title="Long Method Smell",
            description="Method length exceeds limit",
            effort_minutes=30,
            location_file="app/main.py",
            location_line=42,
            metadata={"rule_id": "smell-rule"},
        )
        self.assertEqual(self.item, item2)


if __name__ == "__main__":
    unittest.main()
