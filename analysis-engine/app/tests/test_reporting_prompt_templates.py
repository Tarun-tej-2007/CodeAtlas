"""Unit tests for the Reporting AI Prompt Templates."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.prompts import AIPromptEngine, AIPromptTemplateError
from app.reporting import ReportingPromptTemplates


class TestReportingPromptTemplates(unittest.TestCase):
    """Verifies template registration idempotency, lookups, rendering, and concurrency."""

    def setUp(self) -> None:
        self.engine = AIPromptEngine()
        self.templates = ReportingPromptTemplates(self.engine)

    def test_constructor_validation(self) -> None:
        """Verifies constructor rejects None prompt engine."""
        with self.assertRaises(ValueError):
            ReportingPromptTemplates(None)  # type: ignore

    def test_registration_and_idempotency(self) -> None:
        """Verifies templates register correctly, allow duplicate calls without error, and preserve names."""
        self.assertEqual(len(self.engine.list_templates()), 0)

        # Register first time
        self.templates.register_all()
        listed1 = self.engine.list_templates()
        self.assertEqual(len(listed1), 4)

        names = [t.name for t in listed1]
        self.assertIn("report_summary", names)
        self.assertIn("report_review", names)
        self.assertIn("report_recommendations", names)
        self.assertIn("report_executive_summary", names)

        # Re-register (idempotency check)
        self.templates.register_all()
        listed2 = self.engine.list_templates()
        self.assertEqual(len(listed1), len(listed2))

    def test_template_rendering(self) -> None:
        """Verifies that templates compile and render parameters properly."""
        self.templates.register_all()

        res = self.engine.render(
            "report_summary",
            {
                "project_name": "Atlas",
                "Report Metadata": "Metadata fields",
                "Report Sections": "Detailed body content",
            },
        )
        self.assertIn("Atlas", res.prompt)
        self.assertIn("Metadata fields", res.prompt)

        # Confirm missing variable errors out
        with self.assertRaises(AIPromptTemplateError):
            self.engine.render("report_summary", {"project_name": "Ghost"})

    def test_concurrent_registration(self) -> None:
        """Verifies thread-safety during concurrent registration runs."""
        engine = AIPromptEngine()
        templates = ReportingPromptTemplates(engine)

        def run_register():
            templates.register_all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_register) for _ in range(25)]
            for f in futures:
                f.result()

        self.assertEqual(len(engine.list_templates()), 4)


if __name__ == "__main__":
    unittest.main()
