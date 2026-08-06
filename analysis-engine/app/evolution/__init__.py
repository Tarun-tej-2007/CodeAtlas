"""CodeAtlas Architecture Evolution Domain Subsystem Package."""

from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus, RiskSeverity
from app.evolution.exceptions import EvolutionError, EvolutionValidationError
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
)
from app.evolution.snapshot_builder import ArchitectureSnapshotService
from app.evolution.diff_engine import ArchitectureEvolutionDifferenceEngine
from app.evolution.trend_analyzer import ArchitecturalTrendAnalyzer
from app.evolution.risk_analyzer import CodeAtlasArchitecturalRiskAnalyzer

__all__ = [
    "ArchitecturalChangeType",
    "EvolutionStatus",
    "RiskSeverity",
    "EvolutionError",
    "EvolutionValidationError",
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
    "ArchitectureSnapshotService",
    "ArchitectureEvolutionDifferenceEngine",
    "ArchitecturalTrendAnalyzer",
    "CodeAtlasArchitecturalRiskAnalyzer",
]
