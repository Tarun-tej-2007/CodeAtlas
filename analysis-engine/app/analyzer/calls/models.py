"""Call analysis domain data models module.

Defines immutable Pydantic v2 models representing function, method, constructor,
and static method invocations alongside aggregated CallAnalysisResult objects.
"""

from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class CallKind(StrEnum):
    """Supported call invocation kinds."""

    FUNCTION = "function"
    METHOD = "method"
    CONSTRUCTOR = "constructor"
    STATIC_METHOD = "static_method"


class CallReference(BaseModel):
    """Represents a single function, method, constructor, or static call invocation."""

    id: str = Field(..., description="Deterministic unique identifier for the call invocation.")
    caller_symbol_id: str | None = Field(default=None, description="Symbol ID of the enclosing caller function/method.")
    callee_name: str = Field(..., description="Name of the function/method being called.")
    callee_symbol_id: str | None = Field(default=None, description="Symbol ID of the resolved callee declaration, if found.")
    kind: CallKind = Field(..., description="Kind of call invocation.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    line: int = Field(..., ge=1, description="1-indexed line number of the call invocation.")
    column: int = Field(..., ge=0, description="0-indexed column offset of the call invocation.")
    resolved: bool = Field(..., description="True if callee declaration was resolved in current file, False otherwise.")

    model_config = ConfigDict(frozen=True)


class CallAnalysisResult(BaseModel):
    """Represents aggregated results from intra-file call invocation analysis."""

    calls: list[CallReference] = Field(default_factory=list, description="Ordered list of detected call references.")
    call_count: int = Field(default=0, ge=0, description="Total count of detected call references.")
    resolved_calls: int = Field(default=0, ge=0, description="Count of successfully resolved call references.")
    unresolved_calls: int = Field(default=0, ge=0, description="Count of unresolved call references.")

    model_config = ConfigDict(frozen=True)
