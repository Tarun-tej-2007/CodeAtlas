"""CodeAtlas AI Service domain package.

Establishes core StrEnums, custom exceptions, model definitions, and provider
interfaces for AI model transactions.
"""

from app.ai_service.enums import (
    AIProvider,
    AIModelType,
    RequestPriority,
    ResponseStatus,
)
from app.ai_service.exceptions import (
    AIServiceError,
    AIProviderError,
    AIRequestError,
    AIResponseError,
)
from app.ai_service.models import (
    AIUsage,
    AIProviderConfig,
    AIRequest,
    AIResponse,
)
from app.ai_service.provider import AIProviderClient
from app.ai_service.registry import AIProviderRegistry
from app.ai_service.providers.openai_provider import OpenAIProvider
from app.ai_service.service import AIService
from app.ai_service.health import ProviderHealthStatus, HealthSummary, AIHealthMonitor
from app.ai_service.prompts import (
    AIPromptTemplateError,
    PromptTemplate,
    RenderedPrompt,
    AIPromptEngine,
)
from app.ai_service.context import (
    AIContextError,
    ContextSection,
    AIContext,
    AIContextManager,
)

__all__ = [
    # Enums
    "AIProvider",
    "AIModelType",
    "RequestPriority",
    "ResponseStatus",
    # Exceptions
    "AIServiceError",
    "AIProviderError",
    "AIRequestError",
    "AIResponseError",
    "AIPromptTemplateError",
    "AIContextError",
    # Models
    "AIUsage",
    "AIProviderConfig",
    "AIRequest",
    "AIResponse",
    # Provider Client Interface
    "AIProviderClient",
    # Provider Registry
    "AIProviderRegistry",
    # Concrete Providers
    "OpenAIProvider",
    # AI Service Facade
    "AIService",
    # Health Monitoring
    "ProviderHealthStatus",
    "HealthSummary",
    "AIHealthMonitor",
    # Prompt Engine
    "PromptTemplate",
    "RenderedPrompt",
    "AIPromptEngine",
    # Context Manager
    "ContextSection",
    "AIContext",
    "AIContextManager",
]
