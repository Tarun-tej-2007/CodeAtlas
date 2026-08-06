"""CodeAtlas Architecture Evolution Domain Subsystem Package."""

from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus
from app.evolution.exceptions import EvolutionError, EvolutionValidationError
from app.evolution.interfaces import (
    ArchitectureSnapshotCalculator,
    EvolutionDifferenceEngine,
    EvolutionPersistence,
    ArchitectureAnalysisProvider,
)
from app.evolution.models import (
    ArchitecturalChange,
    ArchitectureSnapshot,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionSummary,
)
from app.evolution.snapshot_builder import ArchitectureSnapshotService

__all__ = [
    "ArchitecturalChangeType",
    "EvolutionStatus",
    "EvolutionError",
    "EvolutionValidationError",
    "ArchitectureSnapshotCalculator",
    "EvolutionDifferenceEngine",
    "EvolutionPersistence",
    "ArchitectureAnalysisProvider",
    "ArchitecturalChange",
    "ArchitectureSnapshot",
    "EvolutionMetadata",
    "EvolutionRequest",
    "EvolutionResult",
    "EvolutionSummary",
    "ArchitectureSnapshotService",
]
