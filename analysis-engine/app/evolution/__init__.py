"""CodeAtlas Architecture Evolution Domain Subsystem Package."""

from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus, RiskSeverity
from app.evolution.exceptions import EvolutionError, EvolutionValidationError, EvolutionPersistenceError
from app.evolution.interfaces import (
    ArchitectureSnapshotCalculator,
    EvolutionDifferenceEngine,
    EvolutionPersistence,
    ArchitectureAnalysisProvider,
    TrendAnalyzer,
    RiskAnalyzer,
)
from app.evolution.models import (
    ArchitecturalChange,
    ArchitectureSnapshot,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionSummary,
    EvolutionTrendResult,
    ArchitecturalRisk,
    ArchitecturalRiskReport,
    ArchitectureEvolutionResult,
)
from app.evolution.snapshot_builder import ArchitectureSnapshotService
from app.evolution.diff_engine import ArchitectureEvolutionDifferenceEngine
from app.evolution.trend_analyzer import ArchitecturalTrendAnalyzer
from app.evolution.risk_analyzer import CodeAtlasArchitecturalRiskAnalyzer
from app.evolution.service import ArchitectureEvolutionService
from app.evolution.persistence import (
    ArchitectureEvolutionRepository,
    ArchitectureEvolutionPersistenceService,
)
from app.evolution.cache import execution_cache

__all__ = [
    "ArchitecturalChangeType",
    "EvolutionStatus",
    "RiskSeverity",
    "EvolutionError",
    "EvolutionValidationError",
    "EvolutionPersistenceError",
    "ArchitectureSnapshotCalculator",
    "EvolutionDifferenceEngine",
    "EvolutionPersistence",
    "ArchitectureAnalysisProvider",
    "TrendAnalyzer",
    "RiskAnalyzer",
    "ArchitecturalChange",
    "ArchitectureSnapshot",
    "EvolutionMetadata",
    "EvolutionRequest",
    "EvolutionResult",
    "EvolutionSummary",
    "EvolutionTrendResult",
    "ArchitecturalRisk",
    "ArchitecturalRiskReport",
    "ArchitectureEvolutionResult",
    "ArchitectureSnapshotService",
    "ArchitectureEvolutionDifferenceEngine",
    "ArchitecturalTrendAnalyzer",
    "CodeAtlasArchitecturalRiskAnalyzer",
    "ArchitectureEvolutionService",
    "ArchitectureEvolutionRepository",
    "ArchitectureEvolutionPersistenceService",
    "execution_cache",
]
