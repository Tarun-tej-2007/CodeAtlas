"""Unit tests for Technical Debt Scoring."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.technical_debt import (
    TechnicalDebtCategory,
    TechnicalDebtSeverity,
    TechnicalDebtItem,
    TechnicalDebtSummary,
    TechnicalDebtScorer,
)


class TestTechnicalDebtScoring(unittest.TestCase):
    """Verifies default/custom weights, aggregates split counts, invalid configurations rejection, and thread safety."""

    def setUp(self) -> None:
        self.item_smell = TechnicalDebtItem(
            id="smell-1",
            category=TechnicalDebtCategory.CODE_SMELL,
            severity=TechnicalDebtSeverity.MEDIUM,
            title="Smell Item",
            effort_minutes=10,
        )
        self.item_dup = TechnicalDebtItem(
            id="dup-1",
            category=TechnicalDebtCategory.DUPLICATION,
            severity=TechnicalDebtSeverity.HIGH,
            title="Dup Item",
            effort_minutes=30,
        )
        self.item_dead = TechnicalDebtItem(
            id="dead-1",
            category=TechnicalDebtCategory.DEAD_CODE,
            severity=TechnicalDebtSeverity.HIGH,
            title="Dead Item",
            effort_minutes=15,
        )

        self.items = [self.item_smell, self.item_dup, self.item_dead]
        self.scorer = TechnicalDebtScorer()

    def test_empty_findings(self) -> None:
        """Verifies aggregates default on empty findings."""
        summary = self.scorer.score([])
        self.assertEqual(summary.total_items, 0)
        self.assertEqual(summary.total_effort_minutes, 0)
        self.assertEqual(summary.metadata["weighted_overall_score"], 0.0)

    def test_type_safety_checking(self) -> None:
        """Verifies collection rejects non-DTO element types."""
        with self.assertRaises(TypeError):
            self.scorer.score([self.item_smell, "invalid-type"])  # type: ignore

    def test_invalid_weights_rejection(self) -> None:
        """Verifies constructor rejects negative weight values."""
        with self.assertRaises(ValueError):
            TechnicalDebtScorer(
                severity_weights={
                    TechnicalDebtSeverity.MEDIUM: -2.5,
                }
            )

    def test_default_weights_scoring(self) -> None:
        """Verifies correct calculation under default weights configuration."""
        summary = self.scorer.score(self.items)

        # Total items and effort sum
        self.assertEqual(summary.total_items, 3)
        self.assertEqual(summary.total_effort_minutes, 55)

        # Counts by category
        self.assertEqual(summary.items_by_category[TechnicalDebtCategory.CODE_SMELL], 1)
        self.assertEqual(summary.items_by_category[TechnicalDebtCategory.DUPLICATION], 1)
        self.assertEqual(summary.items_by_category[TechnicalDebtCategory.DEAD_CODE], 1)

        # Effort by severity
        self.assertEqual(summary.effort_by_severity[TechnicalDebtSeverity.MEDIUM], 10)
        self.assertEqual(summary.effort_by_severity[TechnicalDebtSeverity.HIGH], 45)

        # Weighted overall score calculation (MEDIUM: 5.0, HIGH: 10.0)
        # Expected: (1 * 5.0) + (2 * 10.0) = 25.0
        self.assertEqual(summary.metadata["weighted_overall_score"], 25.0)

    def test_custom_weights_scoring(self) -> None:
        """Verifies custom weights config translates to customized aggregate values."""
        custom_scorer = TechnicalDebtScorer(
            severity_weights={
                TechnicalDebtSeverity.INFO: 0.5,
                TechnicalDebtSeverity.LOW: 1.0,
                TechnicalDebtSeverity.MEDIUM: 2.0,
                TechnicalDebtSeverity.HIGH: 4.0,
                TechnicalDebtSeverity.CRITICAL: 8.0,
            }
        )
        summary = custom_scorer.score(self.items)

        # Weighted overall score calculation (MEDIUM: 2.0, HIGH: 4.0)
        # Expected: (1 * 2.0) + (2 * 4.0) = 10.0
        self.assertEqual(summary.metadata["weighted_overall_score"], 10.0)

    def test_deterministic_execution(self) -> None:
        """Verifies scoring identical collections yields equal results."""
        s1 = self.scorer.score(self.items)
        s2 = self.scorer.score(self.items)

        self.assertEqual(s1.total_items, s2.total_items)
        self.assertEqual(s1.total_effort_minutes, s2.total_effort_minutes)
        self.assertEqual(s1.metadata["weighted_overall_score"], s2.metadata["weighted_overall_score"])

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety under parallel score execution requests."""
        def run_score():
            return self.scorer.score(self.items)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_score) for _ in range(50)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.metadata["weighted_overall_score"], 25.0)
            self.assertEqual(res.total_effort_minutes, 55)


if __name__ == "__main__":
    unittest.main()
