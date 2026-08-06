"""CodeAtlas Incremental Analysis Domain Package."""

from app.incremental.enums import ChangeType, IncrementalStatus
from app.incremental.exceptions import (
    IncrementalAnalysisError,
    IncrementalAnalysisValidationError,
)
from app.incremental.models import (
    FileFingerprint,
    RepositorySnapshot,
    ChangedFile,
    IncrementalAnalysisMetadata,
    IncrementalAnalysisRequest,
    IncrementalAnalysisResult,
)
from app.incremental.interfaces import (
    FingerprintGenerator,
    SnapshotCalculator,
    SnapshotDifferenceEngine,
    IncrementalAnalysisPersistence,
)
from app.incremental.snapshot_service import RepositorySnapshotService
from app.incremental.fingerprint import SHA256FingerprintGenerator
from app.incremental.diff import SHA256SnapshotDifferenceEngine
from app.incremental.impact import DependencyImpactAnalyzer
from app.incremental.service import IncrementalAnalysisService
from app.incremental.persistence import (
    IncrementalAnalysisRepository,
    IncrementalAnalysisPersistenceService,
)

__all__ = [
    "ChangeType",
    "IncrementalStatus",
    "IncrementalAnalysisError",
    "IncrementalAnalysisValidationError",
    "FileFingerprint",
    "RepositorySnapshot",
    "ChangedFile",
    "IncrementalAnalysisMetadata",
    "IncrementalAnalysisRequest",
    "IncrementalAnalysisResult",
    "FingerprintGenerator",
    "SnapshotCalculator",
    "SnapshotDifferenceEngine",
    "IncrementalAnalysisPersistence",
    "RepositorySnapshotService",
    "SHA256FingerprintGenerator",
    "SHA256SnapshotDifferenceEngine",
    "DependencyImpactAnalyzer",
    "IncrementalAnalysisService",
    "IncrementalAnalysisRepository",
    "IncrementalAnalysisPersistenceService",
]
