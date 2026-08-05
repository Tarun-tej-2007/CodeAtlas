"""Dashboard Domain Enums Module."""

from enum import Enum


class DashboardWidgetType(str, Enum):
    """Enumeration of possible dashboard widget component types."""

    SUMMARY = "summary"
    METRICS = "metrics"
    ARCHITECTURE = "architecture"
    QUALITY = "quality"
    TECHNICAL_DEBT = "technical_debt"
    REPORT = "report"


class DashboardStatus(str, Enum):
    """Enumeration of possible dashboard states."""

    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"
