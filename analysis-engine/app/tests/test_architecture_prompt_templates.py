"""Unit tests for the ArchitecturePromptTemplates component."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.prompts import AIPromptEngine
from app.architecture_analysis import ArchitecturePromptTemplates


class TestArchitecturePromptTemplates(unittest.TestCase):
    """Verifies template registrations, duplicate checks, retrieval properties, and concurrent safety."""

    def setUp(self) -> None:
        self.prompt_engine = AIPromptEngine()
        self.templates = ArchitecturePromptTemplates(self.prompt_engine)

    def test_template_registration_and_retrieval(self) -> None:
        """Verifies initial registration and checking templates existence inside engine."""
        self.assertEqual(len(self.prompt_engine), 0)

        # Act: Register all predefined architecture templates
        self.templates.register_all()

        # Assert all 4 are registered
        self.assertEqual(len(self.prompt_engine), 4)

        # Retrieve a target template to verify its parameters
        tmpl = self.prompt_engine.get_template("architecture_summary")
        self.assertEqual(tmpl.name, "architecture_summary")
        self.assertIn("project_name", tmpl.template)
        self.assertIn("CRITICAL", tmpl.template)

    def test_duplicate_registration_idempotency(self) -> None:
        """Verifies duplicate registration runs do not raise errors or duplicate records."""
        self.templates.register_all()
        self.assertEqual(len(self.prompt_engine), 4)

        # Run registration a second time (idempotency test)
        # Should complete cleanly without raising AIPromptTemplateError
        self.templates.register_all()
        self.assertEqual(len(self.prompt_engine), 4)

    def test_deterministic_template_definitions(self) -> None:
        """Verifies template raw format strings do not change between instances."""
        tmpl_manager_1 = ArchitecturePromptTemplates(self.prompt_engine)
        tmpl_manager_2 = ArchitecturePromptTemplates(self.prompt_engine)

        self.assertEqual(len(tmpl_manager_1.TEMPLATES), len(tmpl_manager_2.TEMPLATES))
        for t1, t2 in zip(tmpl_manager_1.TEMPLATES, tmpl_manager_2.TEMPLATES):
            self.assertEqual(t1.name, t2.name)
            self.assertEqual(t1.template, t2.template)

    def test_multiple_instances_isolation(self) -> None:
        """Verifies multiple prompt engine registries remain isolated."""
        engine2 = AIPromptEngine()
        templates2 = ArchitecturePromptTemplates(engine2)

        self.templates.register_all()
        self.assertEqual(len(self.prompt_engine), 4)
        self.assertEqual(len(engine2), 0)

        templates2.register_all()
        self.assertEqual(len(engine2), 4)

    def test_concurrent_registrations(self) -> None:
        """Verifies concurrent registrations execute safely without racing or throwing errors."""
        def run_registration():
            self.templates.register_all()

        # Run registration concurrently across multiple threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_registration) for _ in range(25)]
            # Ensure none of the threads crashed
            for f in futures:
                f.result()

        self.assertEqual(len(self.prompt_engine), 4)


if __name__ == "__main__":
    unittest.main()
