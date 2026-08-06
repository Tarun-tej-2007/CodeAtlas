"""Dashboard Exporters Module."""

import html
import json
from typing import Any

from app.dashboard.exceptions import DashboardValidationError
from app.dashboard.models import DashboardModel


class JSONDashboardExporter:
    """Exporter translating DashboardModel DTO instances into stable, sorted JSON string outputs."""

    def export(self, dashboard: DashboardModel) -> str:
        """Serializes the DashboardModel to a deterministic JSON string."""
        if dashboard is None:
            raise DashboardValidationError("dashboard input must not be None.")
        if not isinstance(dashboard, DashboardModel):
            raise DashboardValidationError("Input must be an instance of DashboardModel.")

        from types import MappingProxyType
        from enum import Enum
        import uuid
        from datetime import datetime

        def make_serializable(v: Any) -> Any:
            if isinstance(v, Enum):
                return v.value
            if isinstance(v, (dict, MappingProxyType)):
                resolved_dict = {}
                for k, val in v.items():
                    k_str = k.value if isinstance(k, Enum) else str(k)
                    resolved_dict[k_str] = make_serializable(val)
                return resolved_dict
            if isinstance(v, (list, tuple)):
                return [make_serializable(x) for x in v]
            if isinstance(v, uuid.UUID):
                return str(v)
            if isinstance(v, datetime):
                return v.isoformat()
            if hasattr(v, "model_dump") and callable(v.model_dump):
                return make_serializable(v.model_dump())
            return v

        serializable_data = make_serializable(dashboard)
        return json.dumps(serializable_data, sort_keys=True, indent=2)


class MarkdownDashboardExporter:
    """Exporter translating DashboardModel DTO instances into clean, structured Markdown."""

    def export(self, dashboard: DashboardModel) -> str:
        """Serializes the DashboardModel to a deterministic Markdown string."""
        if dashboard is None:
            raise DashboardValidationError("dashboard input must not be None.")
        if not isinstance(dashboard, DashboardModel):
            raise DashboardValidationError("Input must be an instance of DashboardModel.")

        lines = [
            f"# Dashboard: {dashboard.metadata.project_name}",
            "",
            "## Metadata",
            f"- **Dashboard ID**: {dashboard.id}",
            f"- **Created At**: {dashboard.metadata.created_at.isoformat()}",
            f"- **Status**: {dashboard.metadata.status.value}",
        ]

        for k, v in sorted(dashboard.metadata.extra_info.items()):
            lines.append(f"- **{k}**: {v}")

        lines.append("")

        # Widgets in deterministic order sorted by key
        for name, widget in sorted(dashboard.widgets.items()):
            lines.extend(
                [
                    f"## {widget.title} ({widget.type.value})",
                    str(widget.content),
                    "",
                ]
            )

        return "\n".join(lines).strip()


class HTMLDashboardExporter:
    """Exporter translating DashboardModel DTO instances into semantic HTML5 string outputs."""

    def export(self, dashboard: DashboardModel) -> str:
        """Serializes the DashboardModel to a deterministic, semantic HTML5 string."""
        if dashboard is None:
            raise DashboardValidationError("dashboard input must not be None.")
        if not isinstance(dashboard, DashboardModel):
            raise DashboardValidationError("Input must be an instance of DashboardModel.")

        proj_name_esc = html.escape(dashboard.metadata.project_name)

        html_lines = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '    <meta charset="UTF-8">',
            f"    <title>Dashboard - {proj_name_esc}</title>",
            "</head>",
            "<body>",
            f"    <h1>Dashboard: {proj_name_esc}</h1>",
            '    <section id="metadata">',
            "        <h2>Metadata</h2>",
            "        <ul>",
            f"            <li><strong>ID:</strong> {html.escape(str(dashboard.id))}</li>",
            f"            <li><strong>Created At:</strong> {html.escape(dashboard.metadata.created_at.isoformat())}</li>",
            f"            <li><strong>Status:</strong> {html.escape(dashboard.metadata.status.value)}</li>",
        ]

        for k, v in sorted(dashboard.metadata.extra_info.items()):
            html_lines.append(
                f"            <li><strong>{html.escape(k)}:</strong> {html.escape(str(v))}</li>"
            )

        html_lines.extend(
            [
                "        </ul>",
                "    </section>",
                '    <section id="widgets">',
            ]
        )

        for name, widget in sorted(dashboard.widgets.items()):
            widget_title_esc = html.escape(widget.title)
            widget_content_esc = html.escape(str(widget.content))
            widget_type_esc = html.escape(widget.type.value)
            html_lines.extend(
                [
                    f'        <article id="widget-{widget_type_esc}">',
                    f"            <h3>{widget_title_esc}</h3>",
                    f"            <pre>{widget_content_esc}</pre>",
                    "        </article>",
                ]
            )

        html_lines.extend(
            [
                "    </section>",
                "</body>",
                "</html>",
                "",
            ]
        )

        return "\n".join(html_lines)
