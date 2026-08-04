"""Architecture Analysis Domain Enums."""

from enum import StrEnum


class ArchitectureSeverity(StrEnum):
    """Severity levels for architecture issues."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ArchitectureRuleType(StrEnum):
    """Rule types for architecture analysis rules."""

    CIRCULAR_DEPENDENCY = "circular_dependency"
    LAYER_VIOLATION = "layer_violation"
    HIGH_COMPLEXITY = "high_complexity"
    GOD_CLASS = "god_class"
    GOD_MODULE = "god_module"
    UNUSED_MODULE = "unused_module"
    UNUSED_SYMBOL = "unused_symbol"
    DEAD_CODE = "dead_code"
    EXCESSIVE_COUPLING = "excessive_coupling"
    LOW_COHESION = "low_cohesion"
    LONG_DEPENDENCY_CHAIN = "long_dependency_chain"
    ARCHITECTURAL_SMELL = "architectural_smell"
