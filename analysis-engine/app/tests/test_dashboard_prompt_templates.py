"""Unit tests for the Dashboard AI Prompt Templates."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.prompts import AIPromptEngine, AIPromptTemplateError
from app.dashboard import DashboardPromptTemplates


class TestDashboardPromptTemplates(unittest.TestCase):
    """Verifies template registration idempotency, duplicate protection, rendering, and concurrency."""

    def setUp(self) -> None:
        self.engine = AIPromptEngine()
        self.templates = DashboardPromptTemplates(self.engine)

    def test_constructor_validation(self) -> None:
        """Verifies constructor rejects None prompt engine."""
        with self.assertRaises(ValueError):
            DashboardPromptTemplates(None)  # type: ignore

    def test_registration_and_idempotency(self) -> None:
        """Verifies templates register correctly, allow duplicate calls without error, and preserve names."""
        self.assertEqual(len(self.engine.list_templates()), 0)

        # Register first time
        self.templates.register_all()
        listed1 = self.engine.list_templates()
        self.assertEqual(len(listed1), 4)

        names = [t.name for t in listed1]
        self.assertIn("dashboard_summary", names)
        self.assertIn("dashboard_review", names)
        self.assertIn("dashboard_recommendations", names)
        self.assertIn("dashboard_executive_summary", names)

        # Re-register (idempotency check)
        self.templates.register_all()
        listed2 = self.engine.list_templates()
        self.assertEqual(len(listed1), len(listed2))

    def test_template_rendering(self) -> None:
        """Verifies that templates compile and render parameters properly."""
        self.templates.register_all()

        res = self.engine.render(
            "dashboard_summary",
            {
                "project_name": "ProjectX",
                "Dashboard Overview": "General dashboard metadata info",
                "Dashboard Widgets": "Visual layout widget card details",
            },
        )
        self.assertIn("ProjectX", res.prompt)
        self.assertIn("General dashboard metadata info", res.prompt)

        # Confirm missing variable errors out
        with self.assertRaises(AIPromptTemplateError):
            self.engine.render("dashboard_summary", {"project_name": "Ghost"})

    def test_concurrent_registration(self) -> None:
        """Verifies thread-safety during concurrent registration runs."""
        engine = AIPromptEngine()
        templates = DashboardPromptTemplates(engine)

        def run_register():
            templates.register_all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_register) for _ in range(25)]
            for f in futures:
                f.result()

        self.assertEqual(len(engine.list_templates()), 4)


if __name__ == "__main__":
    unittest.main()
