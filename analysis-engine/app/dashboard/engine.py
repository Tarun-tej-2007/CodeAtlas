"""Dashboard Aggregation Engine Module."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Union

from app.dashboard.enums import DashboardStatus, DashboardWidgetType
from app.dashboard.exceptions import DashboardValidationError
from app.dashboard.models import DashboardMetadata, DashboardModel, DashboardWidget
from app.dashboard.registry import DashboardWidgetRegistry
from app.dashboard.dashboard import DashboardView


class DashboardAggregationEngine(DashboardView):
    """Orchestration engine that executes widgets in registry and compiles a DashboardModel."""

    def __init__(self, registry: DashboardWidgetRegistry) -> None:
        """Initializes the engine with dependency-injected DashboardWidgetRegistry."""
        if registry is None:
            raise ValueError("DashboardWidgetRegistry dependency must not be None.")
        if not isinstance(registry, DashboardWidgetRegistry):
            raise TypeError("Dependency must be an instance of DashboardWidgetRegistry.")
        self.registry = registry

    def compile(self, *, project_name: str, context: Any) -> DashboardModel:
        """Executes registered widgets sequentially and compiles an immutable DashboardModel."""
        if project_name is None or not project_name.strip():
            raise DashboardValidationError("project_name must be a non-empty string.")
        if context is None:
            raise DashboardValidationError("context must not be None.")

        widgets_map: Dict[str, DashboardWidget] = {}
        extra_info: Dict[str, Any] = {}

        # Known widgets list for checking
        known_types = {
            DashboardWidgetType.SUMMARY,
            DashboardWidgetType.METRICS,
            DashboardWidgetType.ARCHITECTURE,
            DashboardWidgetType.QUALITY,
            DashboardWidgetType.TECHNICAL_DEBT,
            DashboardWidgetType.REPORT,
        }

        # Execute widgets sequentially, preserving registration order
        for name in [w.__class__.__name__ for w in self.registry.list_widgets()]:
            # Wait, the registry contains widgets by name. Let's get the widget and its name.
            # Wait, list_widgets returns a tuple of DashboardView instances.
            # But the registry uses name mapping internally! Let's get the registered names.
            pass

        # Let's iterate using registry's internal list if we can, or iterate list_widgets.
        # Wait, since list_widgets returns a tuple of DashboardView instances, we can check their type or registration name.
        # Wait, how do we know the registration name of each view in the tuple returned by list_widgets?
        # Actually, let's look at `DashboardWidgetRegistry.list_widgets()` implementation:
        # `return tuple(self._widgets.values())`
        # Since it returns the views, but not their names, let's write a helper to iterate them or look at `_widgets` items.
        # Since we have access to `self.registry._widgets`, we can safely acquire keys and values thread-safely:
        with self.registry._lock:
            registered_items = list(self.registry._widgets.items())

        for name, widget_view in registered_items:
            # Execute widget view by calling render(context). We pass context unchanged.
            # Do NOT wrap exceptions. Allow them to propagate.
            output = widget_view.render(context)

            # Resolve widget type
            widget_type = getattr(widget_view, "widget_type", None) or getattr(widget_view, "type", None)
            if isinstance(widget_type, str):
                try:
                    widget_type = DashboardWidgetType(widget_type.lower())
                except ValueError:
                    pass

            if widget_type in known_types:
                # Compile a DashboardWidget DTO
                if isinstance(output, DashboardWidget):
                    widget_dto = output
                else:
                    widget_dto = DashboardWidget(
                        type=widget_type,
                        title=getattr(widget_view, "title", name),
                        content=output,
                        metadata=getattr(widget_view, "metadata", {}),
                    )
                widgets_map[widget_type.value] = widget_dto
            else:
                # Store unknown or custom widget outputs in metadata extra_info
                extra_info[name] = output

        # Construct immutable DashboardMetadata
        metadata = DashboardMetadata(
            project_name=project_name,
            created_at=datetime.now(timezone.utc),
            status=DashboardStatus.READY,
            extra_info=extra_info,
        )

        # Return frozen DashboardModel DTO
        return DashboardModel(
            metadata=metadata,
            widgets=widgets_map,
        )

    def render(self, dashboard: DashboardModel) -> Any:
        """Renders the dashboard model as-is, implementing the DashboardView contract."""
        if dashboard is None:
            raise DashboardValidationError("dashboard must not be None.")
        if not isinstance(dashboard, DashboardModel):
            raise TypeError("dashboard must be an instance of DashboardModel.")
        return dashboard
