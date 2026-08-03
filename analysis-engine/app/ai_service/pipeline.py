"""AI Request Pipeline module.

Defines the AIRequestPipeline component orchestrating prompt engine rendering,
context section merging, request building, and service dispatching.
"""

import hashlib
from typing import Any, Mapping, Optional

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.ai_service.models import AIRequest, AIResponse
from app.ai_service.context import AIContext, AIContextManager
from app.ai_service.prompts import AIPromptEngine
from app.ai_service.service import AIService


class AIRequestPipeline:
    """Orchestrates prompt assembly from structured contexts and dispatches AI execution requests."""

    def __init__(
        self,
        context_manager: AIContextManager,
        prompt_engine: AIPromptEngine,
        ai_service: AIService,
    ) -> None:
        """Initializes the pipeline with dependency-injected services."""
        self.context_manager = context_manager
        self.prompt_engine = prompt_engine
        self.ai_service = ai_service

    def execute(
        self,
        *,
        provider: AIProvider,
        model_type: AIModelType,
        template_name: str,
        context: AIContext,
        variables: Mapping[str, Any],
        priority: RequestPriority = RequestPriority.MEDIUM,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Orchestrates context merging, prompt rendering, request building, and query dispatching."""
        # 1. Merge variables and context sections into a single mapping for rendering
        merged_vars = dict(variables)
        for sec in context.sections:
            merged_vars[sec.name] = sec.content

        # 2. Render prompt using Prompt Engine
        rendered = self.prompt_engine.render(template_name, merged_vars)

        # 3. Generate a stable, deterministic request identifier
        hash_input = f"{template_name}:{context.title}:{rendered.prompt}"
        stable_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
        req_id = f"pipeline-req-{stable_hash}"

        # 4. Construct AIRequest DTO
        req_params = {
            "id": req_id,
            "model_type": model_type,
            "prompt": rendered.prompt,
            "priority": priority,
        }
        if temperature is not None:
            req_params["temperature"] = temperature
        if max_tokens is not None:
            req_params["max_output_tokens"] = max_tokens

        request = AIRequest(**req_params)

        # 5. Dispatch execution to AI Service
        return self.ai_service.send_request(provider, request)
