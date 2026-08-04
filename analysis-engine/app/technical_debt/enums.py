"""Technical Debt Domain Enums module."""

from enum import StrEnum


class TechnicalDebtSeverity(StrEnum):
    """Severity classification tiers for technical debt items."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TechnicalDebtCategory(StrEnum):
    """Categorized technical debt indicators for rule grouping assessments."""

    CODE_SMELL = "code_smell"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    COMPLEXITY = "complexity"
    DEAD_CODE = "dead_code"
    DUPLICATION = "duplication"
    DEPRECATED_USAGE = "deprecated_usage"
    DESIGN_DEBT = "design_debt"
