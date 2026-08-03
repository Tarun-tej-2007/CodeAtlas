"""AI Response Processor module.

Defines the AIResponseProcessor component responsible for validating, parsing,
extracting, and cleaning AI responses.
"""

import re
from typing import Tuple

from app.ai_service.enums import ResponseStatus
from app.ai_service.exceptions import AIResponseError
from app.ai_service.models import AIResponse


class AIResponseProcessor:
    """Stateless service processing and validating completed AIResponse DTO objects."""

    def validate(self, response: AIResponse) -> None:
        """Validates response completion status, content presence, and usage consistency."""
        # 1. Verify status success
        if response.status != ResponseStatus.SUCCESS:
            raise AIResponseError(
                f"Response validation failed: status is '{response.status.value}' (expected success)."
            )

        # 2. Verify non-empty content
        if not response.text_content or len(response.text_content.strip()) == 0:
            raise AIResponseError("Response validation failed: text content is empty.")

        # 3. Verify token usage consistency if present
        if response.usage is not None:
            expected_total = response.usage.prompt_tokens + response.usage.completion_tokens
            if response.usage.total_tokens != expected_total:
                raise AIResponseError(
                    f"Response validation failed: usage tokens are inconsistent. "
                    f"Prompt ({response.usage.prompt_tokens}) + Completion ({response.usage.completion_tokens}) "
                    f"does not equal Total ({response.usage.total_tokens})."
                )

    def process(self, response: AIResponse) -> AIResponse:
        """Validates the response and returns a validated reference copy (since DTO is frozen)."""
        self.validate(response)
        # Under current pipeline design, no further post-processing modifications are required,
        # so we return the input response object unchanged.
        return response

    def extract_code_blocks(self, response: AIResponse) -> Tuple[str, ...]:
        """Extracts fenced Markdown code block contents from the response text."""
        lines = response.text_content.splitlines()
        blocks = []
        current_block = []
        in_block = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                if in_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                    in_block = False
                else:
                    in_block = True
            elif in_block:
                current_block.append(line)

        return tuple(blocks)

    def strip_markdown(self, response: AIResponse) -> str:
        """Removes Markdown code fence delimiters while preserving internal text content."""
        lines = response.text_content.splitlines()
        filtered = [line for line in lines if not line.strip().startswith("```")]
        return "\n".join(filtered)
