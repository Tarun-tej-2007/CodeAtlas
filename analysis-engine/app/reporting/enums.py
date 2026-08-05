"""Report Domain Enums Module."""

from enum import Enum


class ReportFormat(str, Enum):
    """Supported output formats for reports."""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class ReportSection(str, Enum):
    """Supported sections inside an AnalysisReport."""

    SUMMARY = "summary"
    ARCHITECTURE = "architecture"
    QUALITY = "quality"
    TECHNICAL_DEBT = "technical_debt"
    METRICS = "metrics"
    RECOMMENDATIONS = "recommendations"
