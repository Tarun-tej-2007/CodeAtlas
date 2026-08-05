"""Dashboard Widget View Registry Module."""

import threading
from typing import Dict, Tuple

from app.dashboard.dashboard import DashboardView
from app.dashboard.exceptions import DashboardValidationError


class DashboardWidgetRegistry:
    """Thread-safe, insertion-order preserving registry for managing dashboard widget views."""

    def __init__(self) -> None:
        """Initializes the registry with instance-scoped lock and widget views container."""
        self._lock = threading.Lock()
        self._widgets: Dict[str, DashboardView] = {}

    def register(self, name: str, view: DashboardView) -> None:
        """Registers a dashboard widget view under a unique name.

        Args:
            name: Unique widget name.
            view: The DashboardView instance.

        Raises:
            DashboardValidationError if validation fails or name already exists.
        """
        if not name or not name.strip():
            raise DashboardValidationError("Widget name must not be empty or whitespace-only.")
        if view is None:
            raise DashboardValidationError("Cannot register None widget view.")
        if not isinstance(view, DashboardView):
            raise DashboardValidationError("Widget view must inherit from DashboardView abstract interface.")

        with self._lock:
            if name in self._widgets:
                raise DashboardValidationError(f"Widget view with name '{name}' is already registered.")
            self._widgets[name] = view

    def unregister(self, name: str) -> None:
        """Unregisters a widget view by name.

        Args:
            name: Widget name to remove.

        Raises:
            DashboardValidationError if not found.
        """
        if not name or not name.strip():
            raise DashboardValidationError("Widget name must not be empty or whitespace-only.")

        with self._lock:
            if name not in self._widgets:
                raise DashboardValidationError(f"Widget view with name '{name}' is not registered.")
            del self._widgets[name]

    def contains(self, name: str) -> bool:
        """Checks if a widget view is registered under the given name."""
        if not name or not name.strip():
            return False
        with self._lock:
            return name in self._widgets

    def get(self, name: str) -> DashboardView:
        """Retrieves a registered widget view by name.

        Args:
            name: Registered widget name.

        Returns:
            The registered DashboardView instance.

        Raises:
            DashboardValidationError if not found.
        """
        if not name or not name.strip():
            raise DashboardValidationError("Widget name must not be empty or whitespace-only.")

        with self._lock:
            view = self._widgets.get(name)
            if view is None:
                raise DashboardValidationError(f"Widget view with name '{name}' is not registered.")
            return view

    def list_widgets(self) -> Tuple[DashboardView, ...]:
        """Returns all registered widget views, preserving registration order.

        Returns:
            An immutable tuple of registered DashboardView instances.
        """
        with self._lock:
            return tuple(self._widgets.values())

    def clear(self) -> None:
        """Clears all widget views from the registry."""
        with self._lock:
            self._widgets.clear()

    def __len__(self) -> int:
        """Returns the number of registered widget views."""
        with self._lock:
            return len(self._widgets)
