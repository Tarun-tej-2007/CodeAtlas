"""Report AI Context Builder Module."""

from typing import List

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.reporting.enums import ReportSection
from app.reporting.models import AnalysisReport


class ReportAIContextBuilder:
    """Builder component translating AnalysisReport instances into structured AIContext."""

    def __init__(self, ai_context_manager: AIContextManager) -> None:
        """Initializes the builder with dependency-injected AIContextManager."""
        if ai_context_manager is None:
            raise ValueError("AIContextManager dependency must not be None.")
        self.ai_context_manager = ai_context_manager

    def build_context(self, report: AnalysisReport) -> AIContext:
        """Translates an AnalysisReport into an immutable, structured AIContext."""
        if report is None:
            raise ValueError("AnalysisReport input must not be None.")
        if not isinstance(report, AnalysisReport):
            raise TypeError("Input must be an instance of AnalysisReport.")

        # 1. Compile Metadata Map
        metadata = {
            "project_name": report.metadata.project_name,
            "generated_at": report.metadata.generated_at.isoformat(),
            "format": report.metadata.format.value,
        }
        # Add metadata keys deterministically
        for k, v in sorted(report.metadata.extra_info.items()):
            metadata[f"meta_{k}"] = str(v)

        # 2. Build Sections deterministically
        sections: List[ContextSection] = []

        # Section 1: Executive Summary Input
        sections.append(
            ContextSection(
                name="Executive Summary Input",
                content=f"Requesting AI executive summary compilation for project {report.metadata.project_name}.",
            )
        )

        # Section 2: Report Metadata
        meta_lines = [
            f"Project Name: {report.metadata.project_name}",
            f"Report ID: {report.id}",
            f"Generated Timestamp: {report.metadata.generated_at.isoformat()}",
            f"Format Layout: {report.metadata.format.value}",
        ]
        for k, v in sorted(report.metadata.extra_info.items()):
            meta_lines.append(f"- {k}: {v}")
        sections.append(
            ContextSection(name="Report Metadata", content="\n".join(meta_lines))
        )

        # Section 3: Report Sections
        sec_lines = []
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
                sec_lines.extend(
                    [
                        f"### {sec_content.title} ({sec_content.section.value})",
                        sec_content.content,
                        "",
                    ]
                )
        if not sec_lines:
            sec_lines.append("No report sections available.")
        sections.append(
            ContextSection(name="Report Sections", content="\n".join(sec_lines).strip())
        )

        # Section 4: Recommendations Input
        sections.append(
            ContextSection(
                name="Recommendations Input",
                content=f"Compile final summary recommendations for analyzed project {report.metadata.project_name}.",
            )
        )

        # 3. Delegate Context Construction to AIContextManager
        return self.ai_context_manager.create_context(
            title=f"Report AI Context: {report.metadata.project_name}",
            description=f"Structured context generated from AnalysisReport on {report.metadata.generated_at.isoformat()}.",
            metadata=metadata,
            sections=tuple(sections),
        )
