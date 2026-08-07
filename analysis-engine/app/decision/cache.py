"""Execution-scoped caching utilities for Architecture Decision Intelligence."""

import contextvars
from typing import Any, Dict, Optional

# ContextVar storing a thread-local, execution-scoped cache dictionary.
# Local to the current execution thread/task context.
execution_cache: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "decision_execution_cache", default=None
)


def make_hashable(val: Any) -> Any:
    """Recursively converts unhashable structures (dicts, lists, Pydantic models) into hashable tuples."""
    if val is None:
        return None
    if hasattr(val, "model_dump"):
        try:
            return (type(val).__name__, make_hashable(val.model_dump()))
        except Exception:
            pass
    if isinstance(val, dict) or hasattr(val, "items"):
        return tuple((str(k), make_hashable(v)) for k, v in sorted(val.items()))
    elif isinstance(val, (list, tuple, set)):
        return tuple(make_hashable(x) for x in val)
    return val
