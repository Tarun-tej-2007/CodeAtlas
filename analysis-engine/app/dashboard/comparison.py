"""Dashboard Comparison Module."""

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field

from app.dashboard.enums import DashboardWidgetType
from app.dashboard.exceptions import DashboardValidationError
from app.dashboard.models import DashboardModel


class DashboardWidgetDifference(BaseModel):
    """Immutable DTO mapping differences between two individual dashboard widgets."""

    widget_type: DashboardWidgetType = Field(..., description="The widget type configuration.")
    title_changed: bool = Field(..., description="True if titles differ.")
    content_changed: bool = Field(..., description="True if widget body content differs.")
    metadata_changes: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Detailed changed metadata map: {key: {old: v, new: v}}"
    )

    model_config = ConfigDict(frozen=True)


class DashboardComparison(BaseModel):
    """Immutable DTO holding consolidated differences between two DashboardModel configurations."""

    added_widgets: List[str] = Field(..., description="Keys of widgets present only in new dashboard.")
    removed_widgets: List[str] = Field(..., description="Keys of widgets present only in old dashboard.")
    modified_widgets: List[str] = Field(..., description="Keys of modified widgets.")
    unchanged_widgets: List[str] = Field(..., description="Keys of identical widgets.")
    widget_differences: Dict[str, DashboardWidgetDifference] = Field(
        ..., description="Difference details for modified widgets."
    )
    metadata_changes: Dict[str, Dict[str, Any]] = Field(
        ..., description="Differences in top-level dashboard metadata parameters."
    )

    model_config = ConfigDict(frozen=True)


class DashboardComparisonEngine:
    """Orchestrates comparing two DashboardModels to generate a DashboardComparison."""

    def compare(self, old_dashboard: DashboardModel, new_dashboard: DashboardModel) -> DashboardComparison:
        """Compares two DashboardModels and returns a deterministic, sorted DashboardComparison."""
        if old_dashboard is None or new_dashboard is None:
            raise DashboardValidationError("Both old_dashboard and new_dashboard must not be None.")
        if not isinstance(old_dashboard, DashboardModel) or not isinstance(new_dashboard, DashboardModel):
            raise DashboardValidationError("Inputs must be instances of DashboardModel.")

        # 1. Compare Top-Level Metadata
        meta_changes: Dict[str, Dict[str, Any]] = {}
        old_meta = old_dashboard.metadata
        new_meta = new_dashboard.metadata

        if old_meta.project_name != new_meta.project_name:
            meta_changes["project_name"] = {"old": old_meta.project_name, "new": new_meta.project_name}
        if old_meta.status != new_meta.status:
            meta_changes["status"] = {"old": old_meta.status.value, "new": new_meta.status.value}

        # Compare metadata extra_info
        all_meta_keys = set(old_meta.extra_info.keys()) | set(new_meta.extra_info.keys())
        for k in all_meta_keys:
            old_val = old_meta.extra_info.get(k)
            new_val = new_meta.extra_info.get(k)
            if old_val != new_val:
                meta_changes[k] = {"old": old_val, "new": new_val}

        # 2. Compare Widgets
        old_keys = set(old_dashboard.widgets.keys())
        new_keys = set(new_dashboard.widgets.keys())

        added_widgets = sorted(list(new_keys - old_keys))
        removed_widgets = sorted(list(old_keys - new_keys))

        modified_widgets: List[str] = []
        unchanged_widgets: List[str] = []
        widget_differences: Dict[str, DashboardWidgetDifference] = {}

        common_keys = old_keys & new_keys
        for k in sorted(list(common_keys)):
            old_w = old_dashboard.widgets[k]
            new_w = new_dashboard.widgets[k]

            title_changed = old_w.title != new_w.title
            content_changed = old_w.content != new_w.content

            # Compare widget metadata
            w_meta_changes: Dict[str, Dict[str, Any]] = {}
            all_w_meta_keys = set(old_w.metadata.keys()) | set(new_w.metadata.keys())
            for mk in all_w_meta_keys:
                old_mv = old_w.metadata.get(mk)
                new_mv = new_w.metadata.get(mk)
                if old_mv != new_mv:
                    w_meta_changes[mk] = {"old": old_mv, "new": new_mv}

            if title_changed or content_changed or w_meta_changes:
                modified_widgets.append(k)
                widget_differences[k] = DashboardWidgetDifference(
                    widget_type=new_w.type,
                    title_changed=title_changed,
                    content_changed=content_changed,
                    metadata_changes=w_meta_changes,
                )
            else:
                unchanged_widgets.append(k)

        # Ensure all collections are deterministically sorted
        return DashboardComparison(
            added_widgets=added_widgets,
            removed_widgets=removed_widgets,
            modified_widgets=sorted(modified_widgets),
            unchanged_widgets=sorted(unchanged_widgets),
            widget_differences=widget_differences,
            metadata_changes=meta_changes,
        )
