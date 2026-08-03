"""Unit tests for the AIResponseProcessor component."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.ai_service.enums import ResponseStatus
from app.ai_service.exceptions import AIResponseError
from app.ai_service.models import AIResponse, AIUsage
from app.ai_service.response_processor import AIResponseProcessor


class TestAIResponseProcessor(unittest.TestCase):
    """Verifies DTO validation logic, code extraction accuracy, markdown stripping, and thread safety."""

    def setUp(self) -> None:
        self.processor = AIResponseProcessor()
        self.usage = AIUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        self.success_response = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content="Clean message text content",
            status=ResponseStatus.SUCCESS,
            usage=self.usage
        )

    def test_successful_validation(self) -> None:
        # Should execute without raising any errors
        self.processor.validate(self.success_response)

    def test_empty_response_rejection(self) -> None:
        empty_content_resp = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content="   ",
            status=ResponseStatus.SUCCESS,
            usage=None
        )
        with self.assertRaises(AIResponseError) as context:
            self.processor.validate(empty_content_resp)
        self.assertIn("content is empty", str(context.exception))

    def test_invalid_status_rejection(self) -> None:
        failed_resp = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content="Error details",
            status=ResponseStatus.FAILURE,
            usage=None
        )
        with self.assertRaises(AIResponseError) as context:
            self.processor.validate(failed_resp)
        self.assertIn("status is 'failure'", str(context.exception))

    def test_usage_inconsistency_rejection(self) -> None:
        bad_usage = AIUsage(prompt_tokens=100, completion_tokens=50, total_tokens=999)  # Inconsistent total
        bad_usage_resp = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content="Valid text",
            status=ResponseStatus.SUCCESS,
            usage=bad_usage
        )
        with self.assertRaises(AIResponseError) as context:
            self.processor.validate(bad_usage_resp)
        self.assertIn("usage tokens are inconsistent", str(context.exception))

    def test_process_returns_immutable_response_unchanged(self) -> None:
        processed = self.processor.process(self.success_response)
        # Should return the exact same reference copy
        self.assertEqual(processed, self.success_response)
        self.assertIs(processed, self.success_response)

    def test_code_block_extraction(self) -> None:
        content = (
            "Here is the code:\n"
            "```python\n"
            "def foo():\n"
            "    return True\n"
            "```\n"
            "And another one:\n"
            "```js\n"
            "const x = 1;\n"
            "```\n"
            "Goodbye."
        )
        resp = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content=content,
            status=ResponseStatus.SUCCESS,
            usage=None
        )

        blocks = self.processor.extract_code_blocks(resp)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0], "def foo():\n    return True")
        self.assertEqual(blocks[1], "const x = 1;")

    def test_strip_markdown_fences(self) -> None:
        content = (
            "Intro text\n"
            "```yaml\n"
            "key: val\n"
            "```\n"
            "Outro text"
        )
        resp = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content=content,
            status=ResponseStatus.SUCCESS,
            usage=None
        )

        stripped = self.processor.strip_markdown(resp)
        expected = "Intro text\nkey: val\nOutro text"
        self.assertEqual(stripped, expected)

    def test_concurrent_processing_safety(self) -> None:
        def run_proc():
            return self.processor.process(self.success_response)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_proc) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertIs(r, self.success_response)

    def test_deterministic_behavior(self) -> None:
        content = "```python\nprint(1)\n```"
        resp = AIResponse(
            id="resp-1",
            request_id="req-1",
            text_content=content,
            status=ResponseStatus.SUCCESS,
            usage=None
        )

        b1 = self.processor.extract_code_blocks(resp)
        b2 = self.processor.extract_code_blocks(resp)
        self.assertEqual(b1, b2)

        s1 = self.processor.strip_markdown(resp)
        s2 = self.processor.strip_markdown(resp)
        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
