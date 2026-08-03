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
    # Models
    "AIUsage",
    "AIProviderConfig",
    "AIRequest",
    "AIResponse",
    # Provider Client Interface
    "AIProviderClient",
]
