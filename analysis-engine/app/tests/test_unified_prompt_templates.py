"""Unit tests for Unified Analysis AI Prompt Templates."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.prompts import AIPromptEngine, AIPromptTemplateError
from app.unified_analysis import UnifiedAnalysisPromptTemplates


class TestUnifiedPromptTemplates(unittest.TestCase):
    """Verifies template registration idempotency, duplicate blocks checking, and registry isolation."""

    def setUp(self) -> None:
        self.engine = AIPromptEngine()
        self.templates = UnifiedAnalysisPromptTemplates(self.engine)

    def test_constructor_validation(self) -> None:
        """Verifies constructor rejects None prompt engine."""
        with self.assertRaises(ValueError):
            UnifiedAnalysisPromptTemplates(None)  # type: ignore

    def test_initial_registration(self) -> None:
        """Verifies registering all templates on a clean engine."""
        self.assertEqual(len(self.engine.list_templates()), 0)

        self.templates.register_all()

        listed = self.engine.list_templates()
        self.assertEqual(len(listed), 4)

        names = [t.name for t in listed]
        self.assertIn("unified_analysis_summary", names)
        self.assertIn("unified_analysis_review", names)
        self.assertIn("unified_analysis_recommendations", names)
        self.assertIn("unified_analysis_executive_summary", names)

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

        t_summary = self.engine.get_template("unified_analysis_summary")
        t_review = self.engine.get_template("unified_analysis_review")
        t_recs = self.engine.get_template("unified_analysis_recommendations")
        t_exec = self.engine.get_template("unified_analysis_executive_summary")

        # Verify render compiles correctly
        res_summary = self.engine.render(
            "unified_analysis_summary",
            {
                "project_name": "TestProj",
                "Repository Summary": "Summary info",
                "Scan Results": "Scan stats",
                "Parse Results": "Parse stats",
                "Quality Analysis": "Quality ok",
            },
        )
        self.assertIn("TestProj", res_summary.prompt)
        self.assertIn("Summary info", res_summary.prompt)

        # Confirm missing variable throws AIPromptTemplateError
        with self.assertRaises(AIPromptTemplateError):
            self.engine.render("unified_analysis_summary", {"project_name": "Ghost"})

    def test_engine_isolation(self) -> None:
        """Verifies separate engine instances maintain distinct templates registries."""
        other_engine = AIPromptEngine()
        self.templates.register_all()

        self.assertEqual(len(self.engine.list_templates()), 4)
        self.assertEqual(len(other_engine.list_templates()), 0)

    def test_concurrent_registration(self) -> None:
        """Verifies thread safety under parallel registration runs."""
        engine = AIPromptEngine()
        templates = UnifiedAnalysisPromptTemplates(engine)

        def run_register():
            templates.register_all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_register) for _ in range(30)]
            for f in futures:
                f.result()

        self.assertEqual(len(engine.list_templates()), 4)


if __name__ == "__main__":
    unittest.main()
