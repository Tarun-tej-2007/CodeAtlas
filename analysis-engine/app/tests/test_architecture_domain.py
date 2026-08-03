"""Unit tests for the Architecture Analysis Domain package."""

import unittest
from pydantic import ValidationError

from app.architecture import (
    AnalysisCategory,
    ArchitectureAnalysisResult,
    ArchitectureAnalyzer,
    ArchitectureError,
    ArchitectureIssue,
    ArchitectureLayer,
    ArchitectureMetric,
    ArchitectureModelError,
    ArchitectureValidationError,
    ArchitectureAnalysisError,
    LayerType,
    SeverityLevel,
    CouplingType,
    ArchitectureSmellType,
)


class TestArchitectureDomain(unittest.TestCase):
    """Verifies enums, models instantiation, serialization, immutability, and exception definitions."""

    def test_enums(self) -> None:
        # Check some canonical enum mappings
        self.assertEqual(LayerType.PRESENTATION, "presentation")
        self.assertEqual(LayerType.DOMAIN, "domain")
        self.assertEqual(LayerType.INFRASTRUCTURE, "infrastructure")

        self.assertEqual(ArchitectureSmellType.CYCLIC_DEPENDENCY, "cyclic_dependency")
        self.assertEqual(ArchitectureSmellType.GOD_COMPONENT, "god_component")

        self.assertEqual(CouplingType.AFFERENT, "afferent")
        self.assertEqual(CouplingType.EFFERENT, "efferent")

        self.assertEqual(SeverityLevel.ERROR, "error")
        self.assertEqual(SeverityLevel.CRITICAL, "critical")

        self.assertEqual(AnalysisCategory.LAYERING, "layering")
        self.assertEqual(AnalysisCategory.SMELL, "smell")

    def test_exceptions_hierarchy(self) -> None:
        self.assertTrue(issubclass(ArchitectureAnalysisError, ArchitectureError))
        self.assertTrue(issubclass(ArchitectureModelError, ArchitectureError))
        self.assertTrue(issubclass(ArchitectureValidationError, ArchitectureError))

    def test_model_defaults_and_validation(self) -> None:
        # 1. ArchitectureIssue
        issue = ArchitectureIssue(
            id="issue-0",
            title="Layer Violation",
            description="Presentation directly imports Infrastructure layer.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Introduce Application/Service boundary.",
        )
        self.assertEqual(issue.id, "issue-0")
        self.assertEqual(issue.location, None)
        self.assertEqual(issue.metadata, {})

        # Validation error (missing required fields)
        with self.assertRaises(ValidationError):
            ArchitectureIssue(id="issue-1", title="Incomplete")

        # 2. ArchitectureLayer
        layer = ArchitectureLayer(
            id="domain-layer",
            name="Domain Layer",
            layer_type=LayerType.DOMAIN,
        )
        self.assertEqual(layer.id, "domain-layer")
        self.assertEqual(layer.node_ids, [])
        self.assertEqual(layer.metadata, {})

        # 3. ArchitectureMetric
        metric = ArchitectureMetric(
            name="Instability",
            value=0.75,
            unit="dimensionless",
            description="Ratio of efferent coupling to total coupling.",
        )
        self.assertEqual(metric.name, "Instability")
        self.assertEqual(metric.value, 0.75)
        self.assertEqual(metric.metadata, {})

        # 4. ArchitectureAnalysisResult
        result = ArchitectureAnalysisResult(
            issues=[issue],
            layers=[layer],
            metrics=[metric],
            diagnostics=["Run completed successfully."]
        )
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(len(result.layers), 1)
        self.assertEqual(len(result.metrics), 1)
        self.assertEqual(result.diagnostics, ["Run completed successfully."])
        self.assertEqual(result.metadata, {})

    def test_serialization_and_dump(self) -> None:
        issue = ArchitectureIssue(
            id="issue-0",
            title="Layer Violation",
            description="Presentation directly imports Infrastructure layer.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Introduce Application/Service boundary.",
            metadata={"source": "analyzer-v1"}
        )
        # model_dump() verification
        dump = issue.model_dump()
        self.assertEqual(dump["id"], "issue-0")
        self.assertEqual(dump["metadata"]["source"], "analyzer-v1")
        self.assertEqual(dump["severity"], SeverityLevel.ERROR)

        # model_dump_json() serialization verification
        json_str = issue.model_dump_json()
        self.assertIn('"id":"issue-0"', json_str)
        self.assertIn('"severity":"error"', json_str)

    def test_immutability(self) -> None:
        issue = ArchitectureIssue(
            id="issue-0",
            title="Layer Violation",
            description="Presentation directly imports Infrastructure layer.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Introduce Application/Service boundary.",
        )
        # Assignment to a field should raise ValidationError or TypeError under frozen ConfigDict
        with self.assertRaises((ValidationError, TypeError)):
            issue.title = "New Title"  # type: ignore

    def test_equality(self) -> None:
        issue1 = ArchitectureIssue(
            id="issue-0",
            title="Layer Violation",
            description="Presentation directly imports Infrastructure layer.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Introduce Application/Service boundary.",
        )
        issue2 = ArchitectureIssue(
            id="issue-0",
            title="Layer Violation",
            description="Presentation directly imports Infrastructure layer.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Introduce Application/Service boundary.",
        )
        self.assertEqual(issue1, issue2)

        issue3 = ArchitectureIssue(
            id="issue-diff",
            title="Layer Violation",
            description="Presentation directly imports Infrastructure layer.",
            severity=SeverityLevel.ERROR,
            category=AnalysisCategory.LAYERING,
            recommendation="Introduce Application/Service boundary.",
        )
        self.assertNotEqual(issue1, issue3)

    def test_analyzer_interface_contract(self) -> None:
        # Abstract class cannot be instantiated directly
        with self.assertRaises(TypeError):
            ArchitectureAnalyzer()  # type: ignore

        # Ensure a subclass implementing analyze works
        class MockAnalyzer(ArchitectureAnalyzer):
            def analyze(self, graph) -> ArchitectureAnalysisResult:
                return ArchitectureAnalysisResult(diagnostics=["Mock diagnostics"])

        analyzer = MockAnalyzer()
        res = analyzer.analyze(None)
        self.assertEqual(res.diagnostics, ["Mock diagnostics"])


if __name__ == "__main__":
    unittest.main()
