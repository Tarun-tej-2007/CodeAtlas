"""Quality Analysis Domain Enums module."""

from enum import StrEnum


class MetricCategory(StrEnum):
    """Supported software quality metric categories in CodeAtlas."""

    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    COUPLING = "coupling"
    COHESION = "cohesion"
    STABILITY = "stability"
    MODULARITY = "modularity"
    REUSABILITY = "reusability"
    TESTABILITY = "testability"


class QualityLevel(StrEnum):
    """Quality levels classification based on computed metrics scores."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
