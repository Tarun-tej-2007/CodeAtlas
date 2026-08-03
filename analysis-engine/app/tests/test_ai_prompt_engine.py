"""Unit tests for the AIPromptEngine component."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.prompts import (
    AIPromptTemplateError,
    PromptTemplate,
    RenderedPrompt,
    AIPromptEngine,
)


class TestAIPromptEngine(unittest.TestCase):
    """Verifies template registrations, safe formatting renders, duplicates trapping, and concurrent isolation."""

    def setUp(self) -> None:
        self.engine = AIPromptEngine()
        self.temp_a = PromptTemplate(
            name="a-temp",
            description="First template",
            template="Hello {name}, welcome to {place}."
        )
        self.temp_b = PromptTemplate(
            name="b-temp",
            description="Second template",
            template="Result: {status}."
        )

    def test_successful_registration_and_retrieval(self) -> None:
        self.engine.register_template(self.temp_a)
        
        # Retrieval
        retrieved = self.engine.get_template("a-temp")
        self.assertEqual(retrieved, self.temp_a)

    def test_duplicate_registration_raises_error(self) -> None:
        self.engine.register_template(self.temp_a)
        with self.assertRaises(AIPromptTemplateError):
            self.engine.register_template(self.temp_a)

    def test_unknown_template_raises_error(self) -> None:
        with self.assertRaises(AIPromptTemplateError):
            self.engine.get_template("non-existent")

        with self.assertRaises(AIPromptTemplateError):
            self.engine.remove_template("non-existent")

    def test_successful_rendering(self) -> None:
        self.engine.register_template(self.temp_a)
        vars_map = {"name": "Alice", "place": "CodeAtlas"}
        
        rendered = self.engine.render("a-temp", vars_map)
        self.assertEqual(rendered.template_name, "a-temp")
        self.assertEqual(rendered.prompt, "Hello Alice, welcome to CodeAtlas.")

    def test_missing_variables_raises_error(self) -> None:
        self.engine.register_template(self.temp_a)
        vars_map = {"name": "Alice"}  # Missing "place"
        
        with self.assertRaises(AIPromptTemplateError) as context:
            self.engine.render("a-temp", vars_map)
        
        self.assertIn("missing required variable", str(context.exception))

    def test_deterministic_ordering(self) -> None:
        # Register in unsorted sequence
        self.engine.register_template(self.temp_b)
        self.engine.register_template(self.temp_a)

        templates = self.engine.list_templates()
        self.assertEqual(len(templates), 2)
        # Should be sorted alphabetically (a-temp, b-temp)
        self.assertEqual(templates[0].name, "a-temp")
        self.assertEqual(templates[1].name, "b-temp")

    def test_removal_and_clear(self) -> None:
        self.engine.register_template(self.temp_a)
        self.engine.register_template(self.temp_b)
        self.assertEqual(len(self.engine), 2)

        self.engine.remove_template("a-temp")
        self.assertEqual(len(self.engine), 1)
        self.assertFalse("a-temp" in self.engine)

        self.engine.clear()
        self.assertEqual(len(self.engine), 0)

    def test_contains_and_len(self) -> None:
        self.assertFalse("a-temp" in self.engine)
        self.assertEqual(len(self.engine), 0)

        self.engine.register_template(self.temp_a)
        self.assertTrue("a-temp" in self.engine)
        self.assertEqual(len(self.engine), 1)

    def test_engine_instances_isolation(self) -> None:
        engine1 = AIPromptEngine()
        engine2 = AIPromptEngine()

        engine1.register_template(self.temp_a)
        self.assertEqual(len(engine1), 1)
        self.assertEqual(len(engine2), 0)

    def test_concurrent_rendering_safety(self) -> None:
        self.engine.register_template(self.temp_a)
        vars_map = {"name": "Bob", "place": "Dev Staging"}

        def run_render():
            return self.engine.render("a-temp", vars_map)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_render) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.prompt, "Hello Bob, welcome to Dev Staging.")
            self.assertEqual(r.template_name, "a-temp")


if __name__ == "__main__":
    unittest.main()
