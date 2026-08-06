"""Enums describing architecture governance attributes."""

from enum import Enum


class PolicyCategory(str, Enum):
    """Classification categories for governance policies."""

    DEPENDENCY = "dependency"
    LAYER = "layer"
    METRIC = "metric"
    QUALITY = "quality"


class RuleType(str, Enum):
    """Classification of rule types applied in policies."""

    FORBIDDEN_DEPENDENCY = "forbidden_dependency"
    REQUIRED_DEPENDENCY = "required_dependency"
    LAYER_ORDERING = "layer_ordering"
    THRESHOLD = "threshold"


class ViolationSeverity(str, Enum):
    """Severity classification tiers for rules violations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class GovernanceStatus(str, Enum):
    """Governance verification run execution status classifications."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"
