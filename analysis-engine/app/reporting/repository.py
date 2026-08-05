"""Report Repository Abstract Class Module."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Tuple


class ReportRepository(ABC):
    """Pure abstract contract base class establishing the persistence Repository wrapper."""

    @abstractmethod
    def save(self, report_id: uuid.UUID, report: Any) -> None:
        """Persists the report object details.

        Args:
            report_id: Unique tracking UUID.
            report: The report DTO or model to store.
        """
        pass

    @abstractmethod
    def get(self, report_id: uuid.UUID) -> Any:
        """Retrieves a persisted report by identifier.

        Args:
            report_id: Unique tracking UUID.

        Returns:
            The retrieved report DTO or None.
        """
        pass

    @abstractmethod
    def list_reports(self) -> Tuple[Any, ...]:
        """Lists all registered reports inside storage.

        Returns:
            An immutable tuple of persisted report DTOs.
        """
        pass

    @abstractmethod
    def delete(self, report_id: uuid.UUID) -> None:
        """Removes a persisted report by identifier.

        Args:
            report_id: Unique tracking UUID.
        """
        pass
