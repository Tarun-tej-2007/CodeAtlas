"""Report Exporters Module."""

import html
import json
from typing import Any

from app.reporting.enums import ReportSection
from app.reporting.exceptions import ReportGenerationError
from app.reporting.models import AnalysisReport


class JSONReportExporter:
    """Exporter translating AnalysisReport DTO instances into stable, sorted JSON string outputs."""

    def export(self, report: AnalysisReport) -> str:
        """Serializes the AnalysisReport to a deterministic JSON string."""
        if report is None:
            raise ReportGenerationError("report input must not be None.")
        if not isinstance(report, AnalysisReport):
            raise ReportGenerationError("Input must be an instance of AnalysisReport.")

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

        serializable_data = make_serializable(report)
        return json.dumps(serializable_data, sort_keys=True, indent=2)


class MarkdownReportExporter:
    """Exporter translating AnalysisReport DTO instances into clean, structured Markdown."""

    def export(self, report: AnalysisReport) -> str:
        """Serializes the AnalysisReport to a deterministic Markdown string."""
        if report is None:
            raise ReportGenerationError("report input must not be None.")
        if not isinstance(report, AnalysisReport):
            raise ReportGenerationError("Input must be an instance of AnalysisReport.")

        lines = [
            f"# Analysis Report: {report.metadata.project_name}",
            "",
            "## Metadata",
            f"- **Report ID**: {report.id}",
            f"- **Generated At**: {report.metadata.generated_at.isoformat()}",
            f"- **Format**: {report.metadata.format.value}",
        ]

        for k, v in sorted(report.metadata.extra_info.items()):
            lines.append(f"- **{k}**: {v}")

        lines.append("")

        # Sections in canonical ordering
        canonical_order = [
            ReportSection.SUMMARY,
            ReportSection.ARCHITECTURE,
            ReportSection.QUALITY,
            ReportSection.TECHNICAL_DEBT,
            ReportSection.METRICS,
            ReportSection.RECOMMENDATIONS,
        ]

        for sec in canonical_order:
            if sec in report.sections:
                sec_content = report.sections[sec]
                lines.extend(
                    [
                        f"## {sec_content.title}",
                        sec_content.content,
                        "",
                    ]
                )

        return "\n".join(lines).strip()


class HTMLReportExporter:
    """Exporter translating AnalysisReport DTO instances into semantic HTML5 string outputs."""

    def export(self, report: AnalysisReport) -> str:
        """Serializes the AnalysisReport to a deterministic, semantic HTML5 string."""
        if report is None:
            raise ReportGenerationError("report input must not be None.")
        if not isinstance(report, AnalysisReport):
            raise ReportGenerationError("Input must be an instance of AnalysisReport.")

        proj_name_esc = html.escape(report.metadata.project_name)

        html_lines = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '    <meta charset="UTF-8">',
            f"    <title>Analysis Report - {proj_name_esc}</title>",
            "</head>",
            "<body>",
            f"    <h1>Analysis Report: {proj_name_esc}</h1>",
            '    <section id="metadata">',
            "        <h2>Metadata</h2>",
            "        <ul>",
            f"            <li><strong>ID:</strong> {html.escape(str(report.id))}</li>",
            f"            <li><strong>Timestamp:</strong> {html.escape(report.metadata.generated_at.isoformat())}</li>",
            f"            <li><strong>Format:</strong> {html.escape(report.metadata.format.value)}</li>",
        ]

        for k, v in sorted(report.metadata.extra_info.items()):
            html_lines.append(
                f"            <li><strong>{html.escape(k)}:</strong> {html.escape(str(v))}</li>"
            )

        html_lines.extend(
            [
                "        </ul>",
                "    </section>",
                '    <section id="sections">',
            ]
        )

        # Sections in canonical ordering
        canonical_order = [
            ReportSection.SUMMARY,
            ReportSection.ARCHITECTURE,
            ReportSection.QUALITY,
            ReportSection.TECHNICAL_DEBT,
            ReportSection.METRICS,
            ReportSection.RECOMMENDATIONS,
        ]

        for sec in canonical_order:
            if sec in report.sections:
                sec_content = report.sections[sec]
                sec_title_esc = html.escape(sec_content.title)
                sec_body_esc = html.escape(sec_content.content)
                sec_val_esc = html.escape(sec.value)
                html_lines.extend(
                    [
                        f'        <article id="{sec_val_esc}">',
                        f"            <h3>{sec_title_esc}</h3>",
                        f"            <pre>{sec_body_esc}</pre>",
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
