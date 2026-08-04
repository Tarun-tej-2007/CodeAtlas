"""OpenAI AI Provider implementation.

Implements the AIProviderClient interface wrapping the official OpenAI Python SDK.
"""

import threading
from typing import Dict, Optional

from app.ai_service.enums import AIModelType, AIProvider, ResponseStatus
from app.ai_service.exceptions import AIProviderError
from app.ai_service.models import AIProviderConfig, AIRequest, AIResponse, AIUsage
from app.ai_service.provider import AIProviderClient


class OpenAIProvider(AIProviderClient):
    """OpenAI implementation of the AIProviderClient contract.

    Manages lazy initialization of the SDK client and maps internal requests/responses.
    """

    MODEL_MAPPING: Dict[AIModelType, str] = {
        AIModelType.FAST: "gpt-4o-mini",
        AIModelType.BALANCED: "gpt-4o",
        AIModelType.POWERFUL: "gpt-4-turbo",
    }

    def __init__(self, config: AIProviderConfig) -> None:
        """Initializes the provider. Creation of the client is lazy."""
        self.config = config
        self._client = None
        self._lock = threading.Lock()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validates configuration properties."""
        if not self.config.api_key or len(self.config.api_key.strip()) == 0:
            raise AIProviderError("OpenAI API key must be provided and non-empty.")
        if self.config.max_retries != 0:
            # We explicitly override or ensure retries are handled at orchestration layers,
            # but we preserve config integrity.
            pass

    def _get_client(self):
        """Lazy thread-safe initialization of the OpenAI SDK client."""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    try:
                        from openai import OpenAI
                        # Initialize client. The provider must NOT retry requests internally.
                        self._client = OpenAI(
                            api_key=self.config.api_key,
                            base_url=self.config.endpoint,
                            timeout=self.config.timeout_seconds,
                            max_retries=0,
                        )
                    except Exception as e:
                        raise AIProviderError(f"Failed to initialize OpenAI SDK client: {e}") from e
        return self._client

    def _resolve_model(self, model_type: AIModelType) -> str:
        """Resolves the concrete model name using configuration overrides first, then falling back to defaults."""
        param_key = f"model_{model_type.value}"
        if self.config.extra_params and param_key in self.config.extra_params:
            return self.config.extra_params[param_key]
        return self.MODEL_MAPPING.get(model_type, "gpt-4o-mini")

    def send_request(self, request: AIRequest) -> AIResponse:
        """Sends a structured request completion query to OpenAI."""
        client = self._get_client()

        model_name = self._resolve_model(request.model_type)

        # Prepare parameters
        messages = [{"role": "user", "content": request.prompt}]
        params = {
            "model": model_name,
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_output_tokens is not None:
            params["max_tokens"] = request.max_output_tokens

        try:
            # Execute SDK completion request
            completion = client.chat.completions.create(**params)
        except Exception as e:
            # Shield SDK exceptions, raise clean AIProviderError with chain mapping
            raise AIProviderError(f"OpenAI service completion request failed: {e}") from e

        # Extract contents and construct usage DTO
        text_content = ""
        if completion.choices and len(completion.choices) > 0:
            text_content = completion.choices[0].message.content or ""

        usage_dto: Optional[AIUsage] = None
        if completion.usage:
            usage_dto = AIUsage(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens,
            )

        # Generate a deterministic response transaction identifier
        resp_id = f"openai-resp-{completion.id if hasattr(completion, 'id') else request.id}"

        return AIResponse(
            id=resp_id,
            request_id=request.id,
            text_content=text_content,
            status=ResponseStatus.SUCCESS,
            usage=usage_dto,
        )

    def validate_configuration(self, config: AIProviderConfig) -> bool:
        """Validates provider setup configuration parameters."""
        if not config.api_key or len(config.api_key.strip()) == 0:
            raise AIProviderError("Configuration validation failed: missing OpenAI API key.")
        return True

    def health_check(self) -> bool:
        """Verifies connectivity by conducting a shallow client query."""
        try:
            client = self._get_client()
            # Perform a fast list model models to confirm API reachability
            client.models.list()
            return True
        except Exception:
            return False
