"""Unit tests for the Architectural Risk Analyzer (CodeAtlasArchitecturalRiskAnalyzer)."""

import unittest
from datetime import datetime, timezone

from app.evolution import (
    CodeAtlasArchitecturalRiskAnalyzer,
    EvolutionTrendResult,
    EvolutionValidationError,
    RiskSeverity,
)


class TestEvolutionRiskAnalyzer(unittest.TestCase):
    """Verifies architectural degradation detection rules, scoring, severities, and validations."""

    def setUp(self) -> None:
        self.analyzer = CodeAtlasArchitecturalRiskAnalyzer()

    def test_empty_trend_history(self) -> None:
        """Verifies analyzing empty trends results in no risks reported and score 0.0."""
        trend = EvolutionTrendResult(
            coupling_trend=(),
            complexity_trend=(),
            tech_debt_trend=(),
            quality_trend=(),
            layer_stability=(),
            module_growth=(),
            summary={},
        )
        report = self.analyzer.analyze_risks(trend)
        self.assertEqual(len(report.risks), 0)
        self.assertEqual(report.overall_risk_score, 0.0)

    def test_stable_architecture(self) -> None:
        """Verifies analyzing stable architectures reports no emerging risks."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(1.0, 1.0),
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 90.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 10),
            summary={
                "coupling_trend": "stable",
                "complexity_trend": "stable",
                "tech_debt_trend": "stable",
                "quality_trend": "stable",
                "layer_stability": "stable",
                "module_growth": "stable",
            },
        )
        report = self.analyzer.analyze_risks(trend)
        self.assertEqual(len(report.risks), 0)

    def test_architectural_erosion_detection(self) -> None:
        """Verifies quality decay flags Architectural Erosion risk."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(1.0, 1.0),
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 70.0),  # Drop of 20 points
            layer_stability=(2.0, 2.0),
            module_growth=(10, 10),
            summary={"quality_trend": "decreasing"},
        )
        report = self.analyzer.analyze_risks(trend)
        self.assertEqual(len(report.risks), 1)
        risk = report.risks[0]
        self.assertEqual(risk.name, "Architectural Erosion")
        # Score should be: (90 - 70) * 5 = 100
        self.assertEqual(risk.score, 100.0)
        self.assertEqual(risk.severity, RiskSeverity.CRITICAL)

    def test_dependency_explosion_detection(self) -> None:
        """Verifies exponential module inventory growth flags Dependency Explosion."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(1.0, 1.0),
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 90.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 25),  # Growth of 15 modules
            summary={"module_growth": "increasing"},
        )
        report = self.analyzer.analyze_risks(trend)
        risk = [r for r in report.risks if r.name == "Dependency Explosion"][0]
        # Score should be: (25 - 10) * 4 = 60
        self.assertEqual(risk.score, 60.0)
        self.assertEqual(risk.severity, RiskSeverity.HIGH)

    def test_cyclic_dependency_and_coupling_growth(self) -> None:
        """Verifies rise in coupling rates flags Cyclic Dependency and Coupling growth risks."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.2, 0.8),  # Growth of 0.6
            complexity_trend=(1.0, 1.0),
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 90.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 10),
            summary={"coupling_trend": "increasing"},
        )
        report = self.analyzer.analyze_risks(trend)
        names = [r.name for r in report.risks]
        self.assertIn("Cyclic Dependency Growth", names)
        self.assertIn("Increasing Coupling", names)

        coupling_risk = [r for r in report.risks if r.name == "Increasing Coupling"][0]
        # Coupling Score: (0.8 - 0.2) * 50 = 30.0
        self.assertEqual(coupling_risk.score, 30.0)
        self.assertEqual(coupling_risk.severity, RiskSeverity.MEDIUM)

    def test_layer_degradation_detection(self) -> None:
        """Verifies drop in layer boundaries definition flags Layer Degradation."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(1.0, 1.0),
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 90.0),
            layer_stability=(5.0, 3.0),  # Drop of 2 layers
            module_growth=(10, 10),
            summary={"layer_stability": "decreasing"},
        )
        report = self.analyzer.analyze_risks(trend)
        risk = [r for r in report.risks if r.name == "Layer Degradation"][0]
        # Score: (5 - 3) * 25 = 50
        self.assertEqual(risk.score, 50.0)
        self.assertEqual(risk.severity, RiskSeverity.HIGH)

    def test_complexity_and_technical_debt_growth(self) -> None:
        """Verifies complexity rise and debt acceleration triggers respective warnings."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(10.0, 15.0),  # Rise of 5
            tech_debt_trend=(5, 12),  # Rise of 7 items
            quality_trend=(90.0, 90.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 10),
            summary={
                "complexity_trend": "increasing",
                "tech_debt_trend": "increasing",
            },
        )
        report = self.analyzer.analyze_risks(trend)
        names = [r.name for r in report.risks]
        self.assertIn("Increasing Complexity", names)
        self.assertIn("Technical Debt Acceleration", names)

        complexity_risk = [r for r in report.risks if r.name == "Increasing Complexity"][0]
        # Score: (15 - 10) * 10 = 50.0
        self.assertEqual(complexity_risk.score, 50.0)

    def test_multiple_concurrent_risks_and_hotspot(self) -> None:
        """Verifies multiple concurrent risks including Module Hotspot Concentration."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(1.0, 2.0),
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 90.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 15),
            summary={
                "complexity_trend": "increasing",
                "module_growth": "increasing",
            },
        )
        report = self.analyzer.analyze_risks(trend)
        names = [r.name for r in report.risks]
        self.assertIn("Module Hotspot Concentration", names)
        self.assertEqual(report.overall_risk_score, 75.0)  # Max score is 75 (hotspot)

    def test_deterministic_ordering(self) -> None:
        """Verifies reported risks list is strictly ordered alphabetically."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.2, 0.8),
            complexity_trend=(1.0, 2.0),
            tech_debt_trend=(5, 10),
            quality_trend=(90.0, 80.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 10),
            summary={
                "coupling_trend": "increasing",
                "complexity_trend": "increasing",
                "tech_debt_trend": "increasing",
                "quality_trend": "decreasing",
            },
        )
        report = self.analyzer.analyze_risks(trend)
        names = [r.name for r in report.risks]
        self.assertEqual(names, sorted(names))

    def test_validation_failures_on_null_input(self) -> None:
        """Verifies validator raises exception on null input parameters."""
        with self.assertRaises(EvolutionValidationError):
            self.analyzer.analyze_risks(None)  # type: ignore

    def test_validation_failures_on_inconsistent_lengths(self) -> None:
        """Verifies validator rejects timeline arrays of mismatched lengths."""
        trend = EvolutionTrendResult(
            coupling_trend=(0.3, 0.3),
            complexity_trend=(1.0, 2.0, 3.0),  # Mismatched length 3
            tech_debt_trend=(5, 5),
            quality_trend=(90.0, 90.0),
            layer_stability=(2.0, 2.0),
            module_growth=(10, 10),
            summary={},
        )
        with self.assertRaises(EvolutionValidationError):
            self.analyzer.analyze_risks(trend)


if __name__ == "__main__":
    unittest.main()
