"""Dashboard Repository Abstract Class Module."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Tuple


class DashboardRepository(ABC):
    """Pure abstract contract base class establishing the persistence Repository wrapper for dashboards."""

    @abstractmethod
    def save(self, dashboard_id: uuid.UUID, dashboard: Any) -> None:
        """Persists the dashboard object details.

        Args:
            dashboard_id: Unique tracking UUID.
            dashboard: The dashboard DTO or model to store.
        """
        pass

    @abstractmethod
    def get(self, dashboard_id: uuid.UUID) -> Any:
        """Retrieves a persisted dashboard by identifier.

        Args:
            dashboard_id: Unique tracking UUID.

        Returns:
            The retrieved dashboard DTO or None.
        """
        pass

    @abstractmethod
    def list_dashboards(self) -> Tuple[Any, ...]:
        """Lists all registered dashboards inside storage.

        Returns:
            An immutable tuple of persisted dashboard DTOs.
        """
        pass

    @abstractmethod
    def delete(self, dashboard_id: uuid.UUID) -> None:
        """Removes a persisted dashboard by identifier.

        Args:
            dashboard_id: Unique tracking UUID.
        """
        pass
