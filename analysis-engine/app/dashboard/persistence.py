"""Dashboard Persistence Service Module."""

import uuid
from typing import Any, Tuple

from app.dashboard.exceptions import DashboardValidationError
from app.dashboard.models import DashboardModel
from app.dashboard.repository import DashboardRepository


class DashboardPersistenceService:
    """Service layer managing the lifecycle and persistence operations of DashboardModels."""

    def __init__(self, repository: DashboardRepository) -> None:
        """Initializes the service with dependency-injected DashboardRepository."""
        if repository is None:
            raise ValueError("DashboardRepository dependency must not be None.")
        if not isinstance(repository, DashboardRepository):
            raise TypeError("Dependency must inherit from DashboardRepository base contract.")
        self.repository = repository

    def save_dashboard(self, dashboard: Any) -> None:
        """Validates and persists a DashboardModel or AIDashboardAnalysisResult."""
        if dashboard is None:
            raise DashboardValidationError("dashboard input must not be None.")

        # Resolves dashboard_id dynamically to support AIDashboardAnalysisResult without hard dependency coupling
        dashboard_id = None
        if isinstance(dashboard, DashboardModel):
            dashboard_id = dashboard.id
        elif hasattr(dashboard, "dashboard") and isinstance(getattr(dashboard, "dashboard"), DashboardModel):
            dashboard_id = getattr(dashboard, "dashboard").id
        else:
            raise DashboardValidationError("Object must be of type DashboardModel or AIDashboardAnalysisResult.")

        if dashboard_id is None or not isinstance(dashboard_id, uuid.UUID):
            raise DashboardValidationError("Unable to resolve valid UUID dashboard identifier.")

        self.repository.save(dashboard_id, dashboard)

    def get_dashboard(self, dashboard_id: uuid.UUID) -> Any:
        """Retrieves a persisted dashboard by UUID."""
        if dashboard_id is None or not isinstance(dashboard_id, uuid.UUID):
            raise DashboardValidationError("dashboard_id must be a valid UUID.")
        return self.repository.get(dashboard_id)

    def list_dashboards(self) -> Tuple[Any, ...]:
        """Lists all persisted dashboards in storage."""
        res = self.repository.list_dashboards()
        if not isinstance(res, tuple):
            raise DashboardValidationError("Repository returned invalid non-tuple collection.")
        return res

    def delete_dashboard(self, dashboard_id: uuid.UUID) -> None:
        """Removes a persisted dashboard by UUID."""
        if dashboard_id is None or not isinstance(dashboard_id, uuid.UUID):
            raise DashboardValidationError("dashboard_id must be a valid UUID.")
        self.repository.delete(dashboard_id)
