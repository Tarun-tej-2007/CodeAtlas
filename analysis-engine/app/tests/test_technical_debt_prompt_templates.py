"""Unit tests for Technical Debt AI Prompt Templates."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.prompts import AIPromptEngine, AIPromptTemplateError
from app.technical_debt import TechnicalDebtPromptTemplates


class TestTechnicalDebtPromptTemplates(unittest.TestCase):
    """Verifies template registration idempotency, duplicate checks, layout determinism, and concurrency."""

    def setUp(self) -> None:
        self.engine = AIPromptEngine()
        self.templates = TechnicalDebtPromptTemplates(self.engine)

    def test_constructor_validation(self) -> None:
        """Verifies constructor validation rejects None prompt engine."""
        with self.assertRaises(ValueError):
            TechnicalDebtPromptTemplates(None)  # type: ignore

    def test_initial_registration(self) -> None:
        """Verifies templates can be registered on a clean engine."""
        self.assertEqual(len(self.engine.list_templates()), 0)

        self.templates.register_all()

        listed = self.engine.list_templates()
        self.assertEqual(len(listed), 4)

        names = [t.name for t in listed]
        self.assertIn("technical_debt_summary", names)
        self.assertIn("technical_debt_review", names)
        self.assertIn("technical_debt_recommendations", names)
        self.assertIn("technical_debt_prioritization", names)

    def test_duplicate_registration_and_idempotency(self) -> None:
        """Verifies registering multiple times has no side effects and does not raise errors."""
        self.templates.register_all()
        listed1 = self.engine.list_templates()

        # Re-register
        self.templates.register_all()
        listed2 = self.engine.list_templates()

        self.assertEqual(len(listed1), len(listed2))
        self.assertEqual([t.name for t in listed1], [t.name for t in listed2])

    def test_template_lookup_and_format_validation(self) -> None:
        """Verifies lookups get templates and they format successfully using standard variable blocks."""
        self.templates.register_all()

        t_summary = self.engine.get_template("technical_debt_summary")
        t_review = self.engine.get_template("technical_debt_review")
        t_recs = self.engine.get_template("technical_debt_recommendations")
        t_prior = self.engine.get_template("technical_debt_prioritization")

        # Test render calls mapping variables
        res_summary = self.engine.render(
            "technical_debt_summary",
            {
                "project_name": "TestProj",
                "Remediation Overview": "Total effort is 10 minutes",
                "Debt Categories": "Duplication: 1 items",
            },
        )
        self.assertIn("TestProj", res_summary.prompt)
        self.assertIn("Total effort is 10 minutes", res_summary.prompt)

        # Confirm missing variable raises AIPromptTemplateError
        with self.assertRaises(AIPromptTemplateError):
            self.engine.render("technical_debt_summary", {"project_name": "Ghost"})

    def test_engine_isolation(self) -> None:
        """Verifies separate engine instances maintain distinct sets of registered templates."""
        other_engine = AIPromptEngine()
        self.templates.register_all()

        self.assertEqual(len(self.engine.list_templates()), 4)
        self.assertEqual(len(other_engine.list_templates()), 0)

    def test_concurrent_registration(self) -> None:
        """Verifies thread safety under parallel registration race attempts."""
        engine = AIPromptEngine()
        templates = TechnicalDebtPromptTemplates(engine)

        def run_register():
            templates.register_all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_register) for _ in range(30)]
            for f in futures:
                f.result()

        self.assertEqual(len(engine.list_templates()), 4)


if __name__ == "__main__":
    unittest.main()
