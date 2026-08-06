"""Immutable domain models and DTOs for Architecture Governance."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.governance.enums import GovernanceStatus, PolicyCategory, RuleType, ViolationSeverity


class PolicyMetadata(BaseModel):
    """Immutable metadata tracking descriptor for governance policies."""

    policy_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique policy identifier.")
    name: str = Field(..., min_length=1, description="Unique descriptive name of the policy.")
    version: str = Field(..., min_length=1, description="Version string identifier.")
    category: PolicyCategory = Field(..., description="Governance domain category classification.")
    created_at: datetime = Field(..., description="Time when policy metadata was created.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("name", "version", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that string values are not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v

    @field_validator("created_at", mode="after")
    @classmethod
    def validate_created_at_timezone(cls, v: datetime) -> datetime:
        """Ensures creation timestamp is timezone-aware UTC."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("created_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable view protection on extra_info mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(extra_info)


class PolicyRule(BaseModel):
    """Immutable rule declaration containing enforcement conditions."""

    rule_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique rule identifier.")
    name: str = Field(..., min_length=1, description="Unique descriptive name of the rule.")
    rule_type: RuleType = Field(..., description="Enforcement rule category type.")
    severity: ViolationSeverity = Field(..., description="Risk severity tier if violated.")
    configuration: Mapping[str, Any] = Field(
        default_factory=dict, description="Rule evaluation condition mapping values."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("name", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that string values are not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v

    @field_validator("configuration", mode="after")
    @classmethod
    def freeze_configuration(cls, v: Any) -> Any:
        """Enforces immutable view protection on configuration mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("configuration")
    def serialize_configuration(self, configuration: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(configuration)


class GovernancePolicy(BaseModel):
    """Immutable collection of rules enforced to govern architecture characteristics."""

    policy_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique policy identifier.")
    metadata: PolicyMetadata = Field(..., description="Descriptive metadata for policy.")
    rules: Tuple[PolicyRule, ...] = Field(default_factory=tuple, description="Set of rules in this policy.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class PolicyViolation(BaseModel):
    """Immutable record detailing a single rule violation finding."""

    violation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique violation tracking ID.")
    rule_id: uuid.UUID = Field(..., description="Associated policy rule identifier.")
    rule_name: str = Field(..., min_length=1, description="Associated policy rule name.")
    severity: ViolationSeverity = Field(..., description="Risk severity of this violation.")
    message: str = Field(..., min_length=1, description="Detail text description of the violation.")
    details: Mapping[str, Any] = Field(
        default_factory=dict, description="Metadata dictionary mapping details of violation."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("rule_name", "message", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that string values are not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v

    @field_validator("details", mode="after")
    @classmethod
    def freeze_details(cls, v: Any) -> Any:
        """Enforces immutable view protection on details mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("details")
    def serialize_details(self, details: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(details)


class GovernanceSummary(BaseModel):
    """Immutable statistics summarising a single governance run."""

    passed_count: int = Field(default=0, ge=0, description="Total rules passed successfully.")
    failed_count: int = Field(default=0, ge=0, description="Total rules failing with ERROR severity.")
    warning_count: int = Field(default=0, ge=0, description="Total rules failing with WARNING/INFO severity.")
    total_rules: int = Field(default=0, ge=0, description="Total evaluated policy rules.")

    model_config = ConfigDict(frozen=True)


class GovernanceRequest(BaseModel):
    """Immutable DTO payload requesting architecture governance verification."""

    project_id: uuid.UUID = Field(..., description="Unique tracking identifier of project scope.")
    project_name: str = Field(..., min_length=1, description="Associated codebase project identifier name.")
    commit_id: str = Field(..., min_length=1, description="Baseline target commit hash.")
    policies: Tuple[GovernancePolicy, ...] = Field(
        default_factory=tuple, description="Set of policies to evaluate."
    )
    correlation_id: Optional[str] = Field(default=None, description="Optional tracking identifier.")

    model_config = ConfigDict(frozen=True)

    @field_validator("project_name", "commit_id", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that string values are not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v


class GovernanceResult(BaseModel):
    """Immutable resulting domain object of a governance policies run."""

    result_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique result run tracking ID.")
    project_id: uuid.UUID = Field(..., description="Associated project identifier.")
    commit_id: str = Field(..., min_length=1, description="Associated commit hash.")
    status: GovernanceStatus = Field(..., description="Result run status category classification.")
    violations: Tuple[PolicyViolation, ...] = Field(
        default_factory=tuple, description="Immutable tuple collection of policy violations."
    )
    summary: GovernanceSummary = Field(..., description="Summary statistics of governance run.")
    created_at: datetime = Field(..., description="Time when governance result was generated.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that string values are not empty or only whitespace."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v

    @field_validator("created_at", mode="after")
    @classmethod
    def validate_created_at_timezone(cls, v: datetime) -> datetime:
        """Ensures creation timestamp is timezone-aware UTC."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("created_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable view protection on extra_info mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(extra_info)
