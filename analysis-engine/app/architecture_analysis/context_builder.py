"""Architecture AI Context Builder Module."""

from typing import List

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.architecture_analysis.models import ArchitectureReport


class ArchitectureAIContextBuilder:
    """Builder component that translates an ArchitectureReport into structured, machine-readable AIContext."""

    def __init__(self, ai_context_manager: AIContextManager) -> None:
        """Initializes the context builder with dependency-injected AIContextManager."""
        if ai_context_manager is None:
            raise ValueError("AIContextManager dependency must not be None.")
        self.ai_context_manager = ai_context_manager

    def build_context(self, report: ArchitectureReport) -> AIContext:
        """Translates an ArchitectureReport into an immutable, structured AIContext."""
        # 1. Compile Metadata Map
        metadata = {
            "project_name": report.project_name,
            "generated_at": report.generated_at.isoformat(),
            "total_issues": report.summary.total_issues,
            "info_count": report.summary.info_count,
            "low_count": report.summary.low_count,
            "medium_count": report.summary.medium_count,
            "high_count": report.summary.high_count,
            "critical_count": report.summary.critical_count,
        }

        # 2. Build Sections
        sections: List[ContextSection] = []

        # Section 1: Summary
        summary_lines = [
            f"Project: {report.project_name}",
            f"Generated At: {report.generated_at.isoformat()}",
            f"Total Issues: {report.summary.total_issues}",
            "Severity Counts:",
            f"  INFO: {report.summary.info_count}",
            f"  LOW: {report.summary.low_count}",
            f"  MEDIUM: {report.summary.medium_count}",
            f"  HIGH: {report.summary.high_count}",
            f"  CRITICAL: {report.summary.critical_count}",
        ]
        sections.append(
            ContextSection(name="Summary", content="\n".join(summary_lines))
        )

        # Sort issues deterministically by id to maintain stable context format outputs
        sorted_issues = sorted(report.issues, key=lambda x: x.id)

        # Section 2: Architecture Issues
        issue_lines = ["Architecture Issues Details:"]
        for issue in sorted_issues:
            issue_lines.extend(
                [
                    f"- ID: {issue.id}",
                    f"  Rule Type: {issue.rule_type.value}",
                    f"  Severity: {issue.severity.value}",
                    f"  Title: {issue.title}",
                    f"  Description: {issue.description}",
                    f"  Affected Symbols: {', '.join(issue.affected_symbols)}",
                    f"  Metadata: {dict(issue.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Architecture Issues", content="\n".join(issue_lines))
        )

        # Section 3: Dependency Analysis (circular dependencies and chain path issues)
        dep_issues = [
            iss
            for iss in sorted_issues
            if iss.rule_type.value in ("circular_dependency", "long_dependency_chain")
        ]
        dep_lines = ["Dependency Violation Analysis:"]
        for iss in dep_issues:
            dep_lines.extend(
                [
                    f"- ID: {iss.id}",
                    f"  Severity: {iss.severity.value}",
                    f"  Title: {iss.title}",
                    f"  Path Details: {iss.description}",
                    f"  Metadata: {dict(iss.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Dependency Analysis", content="\n".join(dep_lines))
        )

        # Section 4: Semantic Analysis (non-dependency code issues: scope, layer violations, smells, etc.)
        sem_issues = [
            iss
            for iss in sorted_issues
            if iss.rule_type.value not in ("circular_dependency", "long_dependency_chain")
        ]
        sem_lines = ["Semantic Code Analysis:"]
        for iss in sem_issues:
            sem_lines.extend(
                [
                    f"- ID: {iss.id}",
                    f"  Severity: {iss.severity.value}",
                    f"  Title: {iss.title}",
                    f"  Description: {iss.description}",
                    f"  Affected Symbols: {', '.join(iss.affected_symbols)}",
                    f"  Metadata: {dict(iss.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Semantic Analysis", content="\n".join(sem_lines))
        )

        # Section 5: Recommendations Input
        rec_lines = [
            f"Architectural recommendation input requested for {report.summary.total_issues} issues identified in {report.project_name}."
        ]
        sections.append(
            ContextSection(name="Recommendations Input", content="\n".join(rec_lines))
        )

        # 3. Delegate Context Construction to AIContextManager
        return self.ai_context_manager.create_context(
            title=f"Architecture Analysis Context: {report.project_name}",
            description=f"Structured context generated from architectural report on {report.generated_at.isoformat()}.",
            metadata=metadata,
            sections=sections,
        )
