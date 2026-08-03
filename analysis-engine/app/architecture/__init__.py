"""CodeAtlas Architecture Analysis package.

Establishes structural model definitions, enums, exceptions,
and abstract analysis pipeline interfaces.
"""

from app.architecture.enums import (
    AnalysisCategory,
    ArchitectureSmellType,
    CouplingType,
    LayerType,
    SeverityLevel,
)
from app.architecture.exceptions import (
    ArchitectureAnalysisError,
    ArchitectureError,
    ArchitectureModelError,
    ArchitectureValidationError,
)
from app.architecture.models import (
    ArchitectureAnalysisResult,
    ArchitectureIssue,
    ArchitectureLayer,
    ArchitectureMetric,
)
from app.architecture.analyzer import ArchitectureAnalyzer
from app.architecture.layer_detector import LayerRule, LayerDetector
from app.architecture.layer_dependency import (
    LayerDependency,
    LayerDependencyResult,
    LayerDependencyAnalyzer,
)

__all__ = [
    # Enums
    "AnalysisCategory",
    "ArchitectureSmellType",
    "CouplingType",
    "LayerType",
    "SeverityLevel",
    # Exceptions
    "ArchitectureAnalysisError",
    "ArchitectureError",
    "ArchitectureModelError",
    "ArchitectureValidationError",
    # Models
    "ArchitectureAnalysisResult",
    "ArchitectureIssue",
    "ArchitectureLayer",
    "ArchitectureMetric",
    # Analyzer Interface
    "ArchitectureAnalyzer",
    # Layer Detector
    "LayerRule",
    "LayerDetector",
    # Layer Dependency
    "LayerDependency",
    "LayerDependencyResult",
    "LayerDependencyAnalyzer",
]
