"""Architecture Analysis Domain Enums module.

Defines canonical types, categories, levels, and smell classifications.
"""

from enum import StrEnum


class LayerType(StrEnum):
    """Represents standard architectural layers in a system."""

    PRESENTATION = "presentation"
    APPLICATION = "application"
    DOMAIN = "domain"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    SERVICE = "service"
    API = "api"
    SHARED = "shared"
    UTILITY = "utility"
    UNKNOWN = "unknown"


class ArchitectureSmellType(StrEnum):
    """Represents common structural and design smells."""

    CYCLIC_DEPENDENCY = "cyclic_dependency"
    UNSTABLE_DEPENDENCY = "unstable_dependency"
    LAYER_VIOLATION = "layer_violation"
    HIGH_COUPLING = "high_coupling"
    LOW_COHESION = "low_cohesion"
    FEATURE_ENVY = "feature_envy"
    GOD_COMPONENT = "god_component"


class CouplingType(StrEnum):
    """Represents coupling direction types."""

    AFFERENT = "afferent"
    EFFERENT = "efferent"


class SeverityLevel(StrEnum):
    """Represents issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AnalysisCategory(StrEnum):
    """Represents category tags for issues and metrics."""

    LAYERING = "layering"
    COUPLING = "coupling"
    COHESION = "cohesion"
    DEPENDENCY = "dependency"
    METRICS = "metrics"
    SMELL = "smell"
    STRUCTURE = "structure"
    COMPLEXITY = "complexity"
