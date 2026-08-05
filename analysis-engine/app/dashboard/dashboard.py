"""Dashboard Views and Abstract Interfaces Module."""

from abc import ABC, abstractmethod
from typing import Any

from app.dashboard.models import DashboardModel


class DashboardView(ABC):
    """Pure abstract domain interface declaring methods to render Dashboard representations."""

    @abstractmethod
    def render(self, dashboard: DashboardModel) -> Any:
        """Renders the dashboard model representation.

        Args:
            dashboard: The immutable DashboardModel.

        Returns:
            The rendered dashboard representation.
        """
        pass
