"""Report Persistence Service Module."""

import uuid
from typing import Any, Tuple

from app.reporting.exceptions import ReportGenerationError
from app.reporting.models import AnalysisReport
from app.reporting.repository import ReportRepository


class ReportPersistenceService:
    """Service layer managing the lifecycle and persistence operations of AnalysisReports."""

    def __init__(self, repository: ReportRepository) -> None:
        """Initializes the service with dependency-injected ReportRepository."""
        if repository is None:
            raise ValueError("ReportRepository dependency must not be None.")
        if not isinstance(repository, ReportRepository):
            raise TypeError("Dependency must inherit from ReportRepository base contract.")
        self.repository = repository

    def save_report(self, report: Any) -> None:
        """Validates and persists an AnalysisReport or AIReportAnalysisResult."""
        if report is None:
            raise ReportGenerationError("report input must not be None.")

        # Resolves report_id dynamically to support AIReportAnalysisResult without hard dependency coupling
        report_id = None
        if isinstance(report, AnalysisReport):
            report_id = report.id
        elif hasattr(report, "report") and isinstance(getattr(report, "report"), AnalysisReport):
            report_id = getattr(report, "report").id
        else:
            raise ReportGenerationError("Object must be of type AnalysisReport or AIReportAnalysisResult.")

        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise ReportGenerationError("Unable to resolve valid UUID report identifier.")

        self.repository.save(report_id, report)

    def get_report(self, report_id: uuid.UUID) -> Any:
        """Retrieves a persisted report by UUID."""
        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise ReportGenerationError("report_id must be a valid UUID.")
        return self.repository.get(report_id)

    def list_reports(self) -> Tuple[Any, ...]:
        """Lists all persisted reports in deterministic order."""
        res = self.repository.list_reports()
        if not isinstance(res, tuple):
            raise ReportGenerationError("Repository returned invalid non-tuple collection.")
        return res

    def delete_report(self, report_id: uuid.UUID) -> None:
        """Removes a persisted report by UUID."""
        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise ReportGenerationError("report_id must be a valid UUID.")
        self.repository.delete(report_id)
