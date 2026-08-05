"""CodeAtlas Analysis Reporting Domain Package."""

from app.reporting.enums import ReportFormat, ReportSection
from app.reporting.exceptions import ReportingError, ReportGenerationError
from app.reporting.models import ReportSectionContent, ReportMetadata, AnalysisReport
from app.reporting.generator import ReportGenerator
from app.reporting.registry import ReportGeneratorRegistry
from app.reporting.engine import ReportCompilationEngine
from app.reporting.exporters import JSONReportExporter, MarkdownReportExporter, HTMLReportExporter
from app.reporting.comparison import ReportSectionDifference, ReportComparison, ReportComparisonEngine
from app.reporting.context_builder import ReportAIContextBuilder
from app.reporting.prompt_templates import ReportingPromptTemplates
from app.reporting.ai_analyzer import AIReportAnalysisResult, AIReportAnalyzer
from app.reporting.repository import ReportRepository
from app.reporting.persistence import ReportPersistenceService

__all__ = [
    "ReportFormat",
    "ReportSection",
    "ReportingError",
    "ReportGenerationError",
    "ReportSectionContent",
    "ReportMetadata",
    "AnalysisReport",
    "ReportGenerator",
    "ReportGeneratorRegistry",
    "ReportCompilationEngine",
    "JSONReportExporter",
    "MarkdownReportExporter",
    "HTMLReportExporter",
    "ReportSectionDifference",
    "ReportComparison",
    "ReportComparisonEngine",
    "ReportAIContextBuilder",
    "ReportingPromptTemplates",
    "AIReportAnalysisResult",
    "AIReportAnalyzer",
    "ReportRepository",
    "ReportPersistenceService",
]
