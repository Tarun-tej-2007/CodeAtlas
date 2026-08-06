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
]
