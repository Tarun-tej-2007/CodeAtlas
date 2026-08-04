"""Unit tests for the AI Analysis Domain Foundation."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.analysis import (
    AnalysisType,
    AnalysisSeverity,
    RecommendationStatus,
    AnalysisTrigger,
    AnalysisError,
    AnalysisValidationError,
    AnalysisExecutionError,
    AnalysisFinding,
    AnalysisRecommendation,
    AnalysisSummary,
    AnalysisResult,
    CodeAnalyzer,
)


class DummyAnalyzer(CodeAnalyzer):
    """Concrete mock analyzer to exercise the abstract contract."""

    def __init__(self, run_id: str = "run-1") -> None:
        self.run_id = run_id

    def analyze(self, *args, **kwargs) -> AnalysisResult:
        summary = AnalysisSummary(
            total_findings=1,
            findings_by_severity={"warning": 1},
            duration_ms=45,
            metadata={}
        )
        finding = AnalysisFinding(
            id="f-1",
            title="Smell",
            description="Bad class",
            severity=AnalysisSeverity.WARNING,
            file_path="src/main.py",
            start_line=10,
            end_line=12,
            metadata={}
        )
        recommendation = AnalysisRecommendation(
            id="r-1",
            finding_id="f-1",
            remediation="Refactor the class",
            status=RecommendationStatus.OPEN,
            metadata={}
        )
        return AnalysisResult(
            id=self.run_id,
            analysis_type=AnalysisType.CODE_QUALITY,
            summary=summary,
            findings=[finding],
            recommendations=[recommendation],
            diagnostics=["Dummy run complete."]
        )


class TestAnalysisDomainFoundation(unittest.TestCase):
    """Verifies DTO serialization, domain enums, custom exceptions, and abstract interface boundaries."""

    def test_enums(self) -> None:
        self.assertEqual(AnalysisType.CODE_QUALITY, "code_quality")
        self.assertEqual(AnalysisSeverity.CRITICAL, "critical")
        self.assertEqual(RecommendationStatus.OPEN, "open")
        self.assertEqual(AnalysisTrigger.MANUAL, "manual")

    def test_exceptions_hierarchy(self) -> None:
        with self.assertRaises(AnalysisError):
            raise AnalysisValidationError("Validation issue")
            
        with self.assertRaises(AnalysisError):
            raise AnalysisExecutionError("Execution issue")

    def test_model_validation_and_defaults(self) -> None:
        finding = AnalysisFinding(
            id="f-1",
            title="Smell",
            description="Bad class",
            severity=AnalysisSeverity.WARNING,
            file_path="src/main.py",
            start_line=10,
            end_line=12
        )
        self.assertEqual(finding.rule_id, None)
        self.assertEqual(finding.metadata, {})

        # Validation fails if line constraint values are invalid (start_line < 1)
        with self.assertRaises(ValidationError):
            AnalysisFinding(
                id="f-1",
                title="Smell",
                description="Bad class",
                severity=AnalysisSeverity.WARNING,
                file_path="src/main.py",
                start_line=0,
                end_line=12
            )

    def test_serialization(self) -> None:
        finding = AnalysisFinding(
            id="f-1",
            title="Smell",
            description="Bad class",
            severity=AnalysisSeverity.WARNING,
            file_path="src/main.py",
            start_line=10,
            end_line=12
        )
        dump = finding.model_dump()
        self.assertEqual(dump["id"], "f-1")
        self.assertEqual(dump["file_path"], "src/main.py")

        json_str = finding.model_dump_json()
        self.assertIn('"id":"f-1"', json_str)

    def test_immutability(self) -> None:
        finding = AnalysisFinding(
            id="f-1",
            title="Smell",
            description="Bad class",
            severity=AnalysisSeverity.WARNING,
            file_path="src/main.py",
            start_line=10,
            end_line=12
        )
        with self.assertRaises((ValidationError, TypeError)):
            finding.title = "New Title"  # type: ignore

    def test_abstract_interface_contract(self) -> None:
        # Instantiating a class without implementing the abstract methods fails
        with self.assertRaises(TypeError):
            CodeAnalyzer()  # type: ignore

        # Instantiating the concrete implementation works
        analyzer = DummyAnalyzer(run_id="run-test")
        result = analyzer.analyze()
        self.assertEqual(result.id, "run-test")
        self.assertEqual(result.findings[0].id, "f-1")

    def test_repeated_construction(self) -> None:
        analyzer = DummyAnalyzer(run_id="run-repeat")
        res1 = analyzer.analyze()
        res2 = analyzer.analyze()
        self.assertEqual(res1, res2)

    def test_thread_safety(self) -> None:
        analyzer = DummyAnalyzer(run_id="run-thread")

        def run_thread():
            return analyzer.analyze()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_thread) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
