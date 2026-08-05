"""Dashboard AI Context Builder Module."""

from typing import List

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.dashboard.models import DashboardModel
from app.dashboard.exceptions import DashboardValidationError


class DashboardAIContextBuilder:
    """Builder component translating DashboardModel instances into structured AIContext."""

    def __init__(self, ai_context_manager: AIContextManager) -> None:
        """Initializes the builder with dependency-injected AIContextManager."""
        if ai_context_manager is None:
            raise ValueError("AIContextManager dependency must not be None.")
        self.ai_context_manager = ai_context_manager

    def build_context(self, dashboard: DashboardModel) -> AIContext:
        """Translates a DashboardModel into an immutable, structured AIContext."""
        if dashboard is None:
            raise DashboardValidationError("DashboardModel input must not be None.")
        if not isinstance(dashboard, DashboardModel):
            raise TypeError("Input must be an instance of DashboardModel.")

        # 1. Compile Metadata Map
        metadata = {
            "project_name": dashboard.metadata.project_name,
            "created_at": dashboard.metadata.created_at.isoformat(),
            "status": dashboard.metadata.status.value,
        }
        # Add metadata keys deterministically
        for k, v in sorted(dashboard.metadata.extra_info.items()):
            metadata[f"meta_{k}"] = str(v)

        # 2. Build Sections deterministically
        sections: List[ContextSection] = []

        # Section 1: Dashboard Overview
        overview_lines = [
            f"Project Name: {dashboard.metadata.project_name}",
            f"Dashboard ID: {dashboard.id}",
            f"Created Timestamp: {dashboard.metadata.created_at.isoformat()}",
            f"Compilation Status: {dashboard.metadata.status.value}",
        ]
        for k, v in sorted(dashboard.metadata.extra_info.items()):
            overview_lines.append(f"- {k}: {v}")
        sections.append(
            ContextSection(name="Dashboard Overview", content="\n".join(overview_lines))
        )

        # Section 2: Dashboard Widgets (Deterministic Ordering by key name)
        widget_lines = []
        for name, widget in sorted(dashboard.widgets.items()):
            widget_lines.extend(
                [
                    f"### Widget: {widget.title} ({widget.type.value})",
                    str(widget.content),
                    "",
                ]
            )
        if not widget_lines:
            widget_lines.append("No dashboard widgets available.")
        sections.append(
            ContextSection(name="Dashboard Widgets", content="\n".join(widget_lines).strip())
        )

        # Section 3: Dashboard Recommendations
        sections.append(
            ContextSection(
                name="Dashboard Recommendations",
                content=f"Synthesize dashboard visual widget cards recommendations for project {dashboard.metadata.project_name}.",
            )
        )

        # 3. Delegate Context Construction to AIContextManager
        return self.ai_context_manager.create_context(
            title=f"Dashboard AI Context: {dashboard.metadata.project_name}",
            description=f"Structured context generated from DashboardModel on {dashboard.metadata.created_at.isoformat()}.",
            metadata=metadata,
            sections=tuple(sections),
        )
