"""Unified AI Context Builder Module."""

from typing import Any, List

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.unified_analysis.models import UnifiedAnalysisReport


class UnifiedAIContextBuilder:
    """Builder component translating UnifiedAnalysisReport instances into structured AIContext."""

    def __init__(self, ai_context_manager: AIContextManager) -> None:
        """Initializes the builder with dependency-injected AIContextManager."""
        if ai_context_manager is None:
            raise ValueError("AIContextManager dependency must not be None.")
        self.ai_context_manager = ai_context_manager

    def build_context(self, report: UnifiedAnalysisReport) -> AIContext:
        """Translates a UnifiedAnalysisReport into an immutable, structured AIContext."""
        if report is None:
            raise ValueError("UnifiedAnalysisReport input must not be None.")
        if not isinstance(report, UnifiedAnalysisReport):
            raise TypeError("Input must be an instance of UnifiedAnalysisReport.")

        # 1. Compile Metadata Map
        metadata = {
            "project_name": report.project_name,
            "generated_at": report.generated_at.isoformat(),
            "status": report.status.value,
        }
        # Add metadata keys deterministically
        for k, v in sorted(report.metadata.items()):
            metadata[f"meta_{k}"] = str(v)

        # 2. Build Sections deterministically
        sections: List[ContextSection] = []

        # Section 1: Repository Summary
        summary_lines = [
            f"Project Name: {report.project_name}",
            f"Analysis Timestamp: {report.generated_at.isoformat()}",
            f"Status: {report.status.value}",
        ]
        sections.append(
            ContextSection(name="Repository Summary", content="\n".join(summary_lines))
        )

        # Section 2: Scan Results
        sections.append(
            ContextSection(
                name="Scan Results",
                content=self._format_result(report.scan_result),
            )
        )

        # Section 3: Parse Results
        sections.append(
            ContextSection(
                name="Parse Results",
                content=self._format_result(report.parse_result),
            )
        )

        # Section 4: Architecture Analysis
        sections.append(
            ContextSection(
                name="Architecture Analysis",
                content=self._format_result(report.architecture_result),
            )
        )

        # Section 5: Quality Analysis
        sections.append(
            ContextSection(
                name="Quality Analysis",
                content=self._format_result(report.quality_result),
            )
        )

        # Section 6: Technical Debt Analysis
        sections.append(
            ContextSection(
                name="Technical Debt Analysis",
                content=self._format_result(report.technical_debt_result),
            )
        )

        # Section 7: Metadata
        meta_lines = ["Repository Metadata:"]
        for k, v in sorted(report.metadata.items()):
            meta_lines.append(f"- {k}: {v}")
        if len(meta_lines) == 1:
            meta_lines.append("No additional metadata available.")
        sections.append(
            ContextSection(name="Metadata", content="\n".join(meta_lines))
        )

        # Section 8: Recommendations Input
        rec_lines = [
            f"Unified repository analysis review requested for project {report.project_name} "
            f"with execution status {report.status.value}."
        ]
        sections.append(
            ContextSection(name="Recommendations Input", content="\n".join(rec_lines))
        )

        # 3. Delegate Context Construction to AIContextManager
        return self.ai_context_manager.create_context(
            title=f"Unified Analysis Context: {report.project_name}",
            description=f"Structured aggregate context generated from unified analysis report on {report.generated_at.isoformat()}.",
            metadata=metadata,
            sections=tuple(sections),
        )

    def _format_result(self, result: Any) -> str:
        """Helper to format optional result objects deterministically."""
        if result is None:
            return "No data available."

        if hasattr(result, "model_dump") and callable(result.model_dump):
            data = result.model_dump()
        elif hasattr(result, "dict") and callable(result.dict):
            data = result.dict()
        elif isinstance(result, dict):
            data = result
        else:
            # Fallback to string representing raw data
            return str(result)

        if not isinstance(data, dict):
            return str(data)

        lines: List[str] = []
        for k, v in sorted(data.items()):
            lines.append(f"{k}: {self._format_value(v)}")
        return "\n".join(lines)

    def _format_value(self, val: Any) -> str:
        """Helper to format nested data structures deterministically."""
        if isinstance(val, (list, tuple)):
            # Formats collections or items lists
            formatted_items = []
            for item in val:
                if hasattr(item, "model_dump") and callable(item.model_dump):
                    formatted_items.append(str(item.model_dump()))
                else:
                    formatted_items.append(str(item))
            return "[" + ", ".join(sorted(formatted_items)) + "]"
        if isinstance(val, dict):
            formatted_pairs = []
            for k, v in sorted(val.items()):
                formatted_pairs.append(f"{k}: {v}")
            return "{" + ", ".join(formatted_pairs) + "}"
        return str(val)
