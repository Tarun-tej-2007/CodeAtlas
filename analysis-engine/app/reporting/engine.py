"""Report Compilation Engine Module."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.reporting.enums import ReportFormat, ReportSection
from app.reporting.exceptions import ReportGenerationError
from app.reporting.generator import ReportGenerator
from app.reporting.models import AnalysisReport, ReportMetadata, ReportSectionContent


class ReportCompilationEngine(ReportGenerator):
    """Core report compilation engine producing immutable AnalysisReports from precomputed outputs."""

    def generate(
        self, *, project_name: str, context: Any, format: ReportFormat, **kwargs
    ) -> AnalysisReport:
        """Assembles and compiles an AnalysisReport from the precomputed analysis context."""
        # 1. Defensive Validations
        if not project_name or not project_name.strip():
            raise ReportGenerationError("project_name must be a non-empty string.")
        if context is None:
            raise ReportGenerationError("analysis context must not be None.")
        if format is None or not isinstance(format, ReportFormat):
            raise ReportGenerationError("format must be a valid ReportFormat enum value.")

        # Extract subsystem fields dynamically from context (object or dictionary)
        scan_res = self._get_attr(context, "scan_result")
        parse_res = self._get_attr(context, "parse_result")
        arch_res = self._get_attr(context, "architecture_result")
        qual_res = self._get_attr(context, "quality_result")
        tech_res = self._get_attr(context, "technical_debt_result")
        extra_meta = self._get_attr(context, "metadata") or {}

        # 2. Compile Report Sections Deterministically (Strict Section Ordering)
        sections: Dict[ReportSection, ReportSectionContent] = {}

        # Section 1: SUMMARY
        summary_lines = [
            f"Project Name: {project_name}",
            f"Compilation Format: {format.value}",
            f"Context Type: {type(context).__name__}",
        ]
        sections[ReportSection.SUMMARY] = ReportSectionContent(
            section=ReportSection.SUMMARY,
            title="Summary Section",
            content="\n".join(summary_lines),
            metadata={"type": "summary_aggregate"},
        )

        # Section 2: ARCHITECTURE
        sections[ReportSection.ARCHITECTURE] = ReportSectionContent(
            section=ReportSection.ARCHITECTURE,
            title="Architecture Section",
            content=self._format_value(arch_res),
            metadata={"type": "architecture_details"},
        )

        # Section 3: QUALITY
        sections[ReportSection.QUALITY] = ReportSectionContent(
            section=ReportSection.QUALITY,
            title="Quality Section",
            content=self._format_value(qual_res),
            metadata={"type": "quality_details"},
        )

        # Section 4: TECHNICAL_DEBT
        sections[ReportSection.TECHNICAL_DEBT] = ReportSectionContent(
            section=ReportSection.TECHNICAL_DEBT,
            title="Technical Debt Section",
            content=self._format_value(tech_res),
            metadata={"type": "technical_debt_details"},
        )

        # Section 5: METRICS
        metrics_lines = [
            "Scan Metrics:",
            self._format_value(scan_res),
            "",
            "Parse Metrics:",
            self._format_value(parse_res),
        ]
        sections[ReportSection.METRICS] = ReportSectionContent(
            section=ReportSection.METRICS,
            title="Metrics Section",
            content="\n".join(metrics_lines),
            metadata={"type": "scan_parse_metrics"},
        )

        # Section 6: RECOMMENDATIONS
        # Extracts recommendations from context, metadata, or provides placeholder
        recs = self._get_attr(context, "recommendations") or extra_meta.get("recommendations")
        sections[ReportSection.RECOMMENDATIONS] = ReportSectionContent(
            section=ReportSection.RECOMMENDATIONS,
            title="Recommendations Section",
            content=self._format_value(recs),
            metadata={"type": "recommendations_details"},
        )

        # 3. Construct ReportMetadata with timezone-aware UTC timestamp
        metadata = ReportMetadata(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            format=format,
            extra_info={k: str(v) for k, v in sorted(extra_meta.items())},
        )

        # 4. Return Frozen AnalysisReport DTO
        return AnalysisReport(
            metadata=metadata,
            sections=sections,
        )

    def _get_attr(self, obj: Any, name: str) -> Any:
        """Retrieves attribute or dictionary key safely."""
        if isinstance(obj, dict):
            return obj.get(name)
        return getattr(obj, name, None)

    def _format_value(self, val: Any) -> str:
        """Deterministic formatter translating optional structures into sorted strings."""
        if val is None:
            return "No data available."

        if hasattr(val, "model_dump") and callable(val.model_dump):
            data = val.model_dump()
        elif hasattr(val, "dict") and callable(val.dict):
            data = val.dict()
        elif isinstance(val, dict):
            data = val
        else:
            return str(val)

        if not isinstance(data, dict):
            return str(data)

        lines: List[str] = []
        for k, v in sorted(data.items()):
            lines.append(f"{k}: {self._format_nested(v)}")
        return "\n".join(lines)

    def _format_nested(self, val: Any) -> str:
        """Formats inner collection components deterministically."""
        if isinstance(val, (list, tuple)):
            items = []
            for x in val:
                if hasattr(x, "model_dump") and callable(x.model_dump):
                    items.append(str(x.model_dump()))
                else:
                    items.append(str(x))
            return "[" + ", ".join(sorted(items)) + "]"
        if isinstance(val, dict):
            pairs = []
            for k, v in sorted(val.items()):
                pairs.append(f"{k}: {v}")
            return "{" + ", ".join(pairs) + "}"
        return str(val)
