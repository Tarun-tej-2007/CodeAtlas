"""CodeAtlas Dashboard Subsystem Domain Package."""

from app.dashboard.enums import DashboardWidgetType, DashboardStatus
from app.dashboard.exceptions import DashboardError, DashboardValidationError
from app.dashboard.models import DashboardMetadata, DashboardWidget, DashboardModel
from app.dashboard.dashboard import DashboardView
from app.dashboard.registry import DashboardWidgetRegistry

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
]
