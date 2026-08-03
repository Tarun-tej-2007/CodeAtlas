"""AI Service Domain Models module.

Defines immutable Pydantic v2 models representing configuration parameters, requests,
response payloads, and usage statistics.
"""

from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus


class AIUsage(BaseModel):
    """Represents token usage statistics for an AI request/response transaction."""

    prompt_tokens: int = Field(..., ge=0, description="Number of tokens in the input prompt.")
    completion_tokens: int = Field(..., ge=0, description="Number of tokens in the output completion.")
    total_tokens: int = Field(..., ge=0, description="Total tokens consumed.")

    model_config = ConfigDict(frozen=True)


class AIProviderConfig(BaseModel):
    """Configuration options for establishing communication with an AI provider."""

    provider: AIProvider = Field(..., description="Target AI provider brand.")
    api_key: str = Field(..., min_length=1, description="Authentication API key credentials.")
    endpoint: Optional[str] = Field(default=None, description="Optional custom connection proxy endpoint.")
    timeout_seconds: int = Field(default=30, ge=1, description="Maximum request duration timeout.")
    max_retries: int = Field(default=3, ge=0, description="Retry attempts count for failed requests.")
    extra_params: Dict[str, str] = Field(
        default_factory=dict, description="Additional custom configuration parameters."
    )

    model_config = ConfigDict(frozen=True)


class AIRequest(BaseModel):
    """Represents the parameters and content for requesting text generation from an AI model."""

    id: str = Field(..., description="Unique deterministic identifier for the request.")
    model_type: AIModelType = Field(..., description="Abstraction tier class of model to query.")
    prompt: str = Field(..., min_length=1, description="Instruction prompt content text.")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Model sampling temperature value.")
    max_output_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum generation token ceiling.")
    priority: RequestPriority = Field(default=RequestPriority.MEDIUM, description="Request scheduling priority.")

    model_config = ConfigDict(frozen=True)


class AIResponse(BaseModel):
    """Immutable model representing the text generation result from an AI request."""

    id: str = Field(..., description="Unique response transaction identifier.")
    request_id: str = Field(..., description="Identifier of the origin request model.")
    text_content: str = Field(..., description="Generated text completion content.")
    status: ResponseStatus = Field(..., description="outcome status of the transaction request.")
    usage: Optional[AIUsage] = Field(default=None, description="Detailed request token consumption.")
    error_message: Optional[str] = Field(default=None, description="Errors messages if execution failed.")

    model_config = ConfigDict(frozen=True)
