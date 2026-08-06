"""Supporting enums for the Architecture Evolution subsystem."""

from enum import Enum


class EvolutionStatus(str, Enum):
    """Represents the lifecycle execution status of an architecture evolution query."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ArchitecturalChangeType(str, Enum):
    """Represents the classification of delta modifications detected in architectural components."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class RiskSeverity(str, Enum):
    """Represents the severity level classification of an identified architectural risk."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
