"""AI Analysis Report Builder module.

Implements a stateless, extensible report builder that formats code analysis results
into structured, immutable report sections using modular section formatters.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import hashlib

from pydantic import BaseModel, ConfigDict, Field
from app.analysis.models import AnalysisResult


# --- Report Models ---


class ReportSection(BaseModel):
    """Represents a structured, markdown-compatible section of the analysis report."""

    id: str = Field(..., description="Unique deterministic identifier for the section.")
    title: str = Field(..., description="Human-readable title of the section.")
    content: str = Field(..., description="Markdown content body.")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Extensible section properties."
    )

    model_config = ConfigDict(frozen=True)


class AnalysisReport(BaseModel):
    """Container representing the complete, immutable code analysis report."""

    id: str = Field(..., description="Unique deterministic report identifier.")
    result_id: str = Field(..., description="Identifier of the origin AnalysisResult DTO.")
    sections: List[ReportSection] = Field(
        default_factory=list, description="Ordered report sections."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Extensible report configuration."
    )

    model_config = ConfigDict(frozen=True)


# --- Section Builders ---


class ReportSectionBuilder(ABC):
    """Abstract interface for constructing a specific section of the analysis report."""

    @abstractmethod
    def build_section(self, result: AnalysisResult) -> Optional[ReportSection]:
        """Constructs a ReportSection from the given AnalysisResult, or returns None."""
        pass


class SummarySectionBuilder(ReportSectionBuilder):
    """Formats the high-level summary overview of the analysis run."""

    def build_section(self, result: AnalysisResult) -> Optional[ReportSection]:
        summary = result.summary
        lines = [
            f"# Analysis Summary for Run '{result.id}'",
            "",
            f"- **Total Findings**: {summary.total_findings}",
        ]
        
        if summary.findings_by_severity:
            lines.append("- **Findings by Severity**:")
            for sev, count in sorted(summary.findings_by_severity.items()):
                lines.append(f"  - *{sev.upper()}*: {count}")

        # Extract other metadata metrics
        for key in sorted(summary.metadata.keys()):
            val = summary.metadata[key]
            lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        content = "\n".join(lines)
        return ReportSection(
            id="sec-summary",
            title="Analysis Summary",
            content=content,
            metadata={"type": "summary"},
        )


class FindingsSectionBuilder(ReportSectionBuilder):
    """Formats the specific list of code quality findings."""

    def build_section(self, result: AnalysisResult) -> Optional[ReportSection]:
        if not result.findings:
            return None

        lines = [
            "# Detected Code Findings",
            "",
            "The following quality, performance, or design issues were discovered:",
            "",
        ]

        for idx, f in enumerate(result.findings, start=1):
            rule_part = f" [{f.rule_id}]" if f.rule_id else ""
            lines.extend(
                [
                    f"## {idx}. {f.title}{rule_part}",
                    f"- **File**: `{f.file_path}` (Lines {f.start_line}-{f.end_line})",
                    f"- **Severity**: **{f.severity.upper()}**",
                    f"- **Description**: {f.description}",
                    "",
                ]
            )

        content = "\n".join(lines).strip()
        return ReportSection(
            id="sec-findings",
            title="Detected Code Findings",
            content=content,
            metadata={"type": "findings", "count": str(len(result.findings))},
        )


class RecommendationsSectionBuilder(ReportSectionBuilder):
    """Formats the remediation recommendations."""

    def build_section(self, result: AnalysisResult) -> Optional[ReportSection]:
        if not result.recommendations:
            return None

        lines = [
            "# Remediation Recommendations",
            "",
            "The following fixes are suggested to address the codebase findings:",
            "",
        ]

        for idx, r in enumerate(result.recommendations, start=1):
            priority = r.metadata.get("priority", "medium").upper()
            lines.extend(
                [
                    f"## Recommendation {idx} (Priority: {priority})",
                    f"- **Remediation Strategy**: {r.remediation}",
                    f"- **Target Finding**: {r.finding_id}",
                ]
            )
            if r.suggested_code:
                lines.extend(
                    [
                        "- **Suggested Fix**:",
                        "```python",
                        r.suggested_code,
                        "```",
                    ]
                )
            lines.append("")

        content = "\n".join(lines).strip()
        return ReportSection(
            id="sec-recommendations",
            title="Remediation Recommendations",
            content=content,
            metadata={"type": "recommendations", "count": str(len(result.recommendations))},
        )


class DiagnosticsSectionBuilder(ReportSectionBuilder):
    """Formats the analyzer diagnostics run logs."""

    def build_section(self, result: AnalysisResult) -> Optional[ReportSection]:
        if not result.diagnostics:
            return None

        lines = [
            "# Execution Diagnostics Log",
            "",
            "```text",
        ]
        for log in result.diagnostics:
            lines.append(log)
        lines.extend(["```"])

        content = "\n".join(lines)
        return ReportSection(
            id="sec-diagnostics",
            title="Diagnostics Log",
            content=content,
            metadata={"type": "diagnostics"},
        )


# --- Report Builder Core ---


class ReportBuilder:
    """Stateless generator that transforms AnalysisResult payloads into markdown reports."""

    def __init__(self, builders: Optional[List[ReportSectionBuilder]] = None) -> None:
        """Initializes the builder with custom or default section formatters."""
        self.builders = builders if builders is not None else self._get_default_builders()

    def _get_default_builders(self) -> List[ReportSectionBuilder]:
        return [
            SummarySectionBuilder(),
            FindingsSectionBuilder(),
            RecommendationsSectionBuilder(),
            DiagnosticsSectionBuilder(),
        ]

    def build_report(self, result: AnalysisResult) -> AnalysisReport:
        """Constructs an immutable AnalysisReport DTO from the given AnalysisResult.

        Ensures deterministic section order, stable hash-based report IDs, and thread-safety.
        """
        sections: List[ReportSection] = []

        for builder in self.builders:
            section = builder.build_section(result)
            if section:
                sections.append(section)

        # Generate stable content-derived hash for report ID
        sections_content = "".join(s.content for s in sections)
        h = hashlib.sha256(sections_content.encode("utf-8")).hexdigest()[:12]
        report_id = f"report-{result.id}-{h}"

        return AnalysisReport(
            id=report_id,
            result_id=result.id,
            sections=sections,
            metadata={"origin_analysis_type": result.analysis_type.value},
        )
