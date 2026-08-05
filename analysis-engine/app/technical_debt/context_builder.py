"""Technical Debt AI Context Builder Module."""

from typing import List

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.technical_debt.models import TechnicalDebtReport


class TechnicalDebtAIContextBuilder:
    """Builder component that translates a TechnicalDebtReport into structured, machine-readable AIContext."""

    def __init__(self, ai_context_manager: AIContextManager) -> None:
        """Initializes the context builder with dependency-injected AIContextManager."""
        if ai_context_manager is None:
            raise ValueError("AIContextManager dependency must not be None.")
        self.ai_context_manager = ai_context_manager

    def build_context(self, report: TechnicalDebtReport) -> AIContext:
        """Translates a TechnicalDebtReport into an immutable, structured AIContext."""
        if report is None:
            raise ValueError("TechnicalDebtReport input must not be None.")

        # 1. Compile Metadata Map
        weighted_score = report.summary.metadata.get("weighted_overall_score", 0.0)

        metadata = {
            "project_name": report.project_name,
            "generated_at": report.generated_at.isoformat(),
            "total_items": report.summary.total_items,
            "total_effort_minutes": report.summary.total_effort_minutes,
            "weighted_overall_score": float(weighted_score),
        }

        # 2. Build Sections
        sections: List[ContextSection] = []

        # Section 1: Summary
        summary_lines = [
            f"Project: {report.project_name}",
            f"Generated At: {report.generated_at.isoformat()}",
            f"Total Technical Debt Items: {report.summary.total_items}",
            f"Total Remediation Effort (Minutes): {report.summary.total_effort_minutes}",
            f"Weighted Overall Score: {weighted_score:.2f}",
        ]
        sections.append(
            ContextSection(name="Summary", content="\n".join(summary_lines))
        )

        # Sort findings deterministically by file, line, and ID to maintain stable context format outputs
        sorted_items = sorted(
            report.items,
            key=lambda x: (x.location_file or "", x.location_line or 0, x.id),
        )

        # Section 2: Technical Debt Findings
        findings_lines = ["Technical Debt Findings Details:"]
        for item in sorted_items:
            findings_lines.extend(
                [
                    f"- ID: {item.id}",
                    f"  Category: {item.category.value}",
                    f"  Severity: {item.severity.value}",
                    f"  Title: {item.title}",
                    f"  Description: {item.description}",
                    f"  Effort (Minutes): {item.effort_minutes}",
                    f"  Location: {item.location_file or 'unknown'}:{item.location_line or 0}",
                    f"  Metadata: {dict(item.metadata)}",
                ]
            )
        sections.append(
            ContextSection(
                name="Technical Debt Findings", content="\n".join(findings_lines)
            )
        )

        # Section 3: Debt Categories
        cat_lines = ["Debt Categories Distribution:"]
        for cat, count in sorted(report.summary.items_by_category.items(), key=lambda x: x[0].value):
            cat_lines.append(f"- {cat.value}: {count} items")
        sections.append(
            ContextSection(name="Debt Categories", content="\n".join(cat_lines))
        )

        # Section 4: Remediation Overview
        remediation_lines = [
            "Remediation Overview Statistics:",
            f"Total Remediation Effort: {report.summary.total_effort_minutes} minutes",
            "Effort Distribution by Severity:",
        ]
        for sev, effort in sorted(report.summary.effort_by_severity.items(), key=lambda x: x[0].value):
            remediation_lines.append(f"  {sev.value.upper()}: {effort} minutes")
        sections.append(
            ContextSection(
                name="Remediation Overview", content="\n".join(remediation_lines)
            )
        )

        # Section 5: Recommendations Input
        rec_lines = [
            f"Technical debt recommendations input requested for overall score {weighted_score:.2f} "
            f"with {report.summary.total_items} items totaling {report.summary.total_effort_minutes} effort minutes "
            f"in project {report.project_name}."
        ]
        sections.append(
            ContextSection(
                name="Recommendations Input", content="\n".join(rec_lines)
            )
        )

        # 3. Delegate Context Construction to AIContextManager
        return self.ai_context_manager.create_context(
            title=f"Technical Debt Context: {report.project_name}",
            description=f"Structured context generated from technical debt report on {report.generated_at.isoformat()}.",
            metadata=metadata,
            sections=tuple(sections),
        )
