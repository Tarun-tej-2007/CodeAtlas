"""Execution-scoped caching utilities for Architecture Evolution."""

import contextvars
from typing import Any, Dict, Optional

# ContextVar storing a thread-local, execution-scoped cache dictionary.
# Local to the current execution thread/task context.
execution_cache: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "evolution_execution_cache", default=None
)
