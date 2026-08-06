"""CodeAtlas Dashboard Subsystem Domain Package."""

from app.dashboard.enums import DashboardWidgetType, DashboardStatus
from app.dashboard.exceptions import DashboardError, DashboardValidationError
from app.dashboard.models import DashboardMetadata, DashboardWidget, DashboardModel
from app.dashboard.dashboard import DashboardView
from app.dashboard.registry import DashboardWidgetRegistry
from app.dashboard.engine import DashboardAggregationEngine
from app.dashboard.context_builder import DashboardAIContextBuilder
from app.dashboard.prompt_templates import DashboardPromptTemplates
from app.dashboard.ai_analyzer import AIDashboardAnalysisResult, AIDashboardAnalyzer
from app.dashboard.repository import DashboardRepository
from app.dashboard.persistence import DashboardPersistenceService
from app.dashboard.exporters import JSONDashboardExporter, MarkdownDashboardExporter, HTMLDashboardExporter

__all__ = [
    "DashboardWidgetType",
    "DashboardStatus",
    "DashboardError",
    "DashboardValidationError",
    "DashboardMetadata",
    "DashboardWidget",
    "DashboardModel",
    "DashboardView",
    "DashboardWidgetRegistry",
    "DashboardAggregationEngine",
    "DashboardAIContextBuilder",
    "DashboardPromptTemplates",
    "AIDashboardAnalysisResult",
    "AIDashboardAnalyzer",
    "DashboardRepository",
    "DashboardPersistenceService",
    "JSONDashboardExporter",
    "MarkdownDashboardExporter",
    "HTMLDashboardExporter",
]
