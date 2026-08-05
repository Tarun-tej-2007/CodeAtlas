"""Unified Analysis Engine Module."""

from datetime import datetime, timezone
from typing import Any, Dict

from app.unified_analysis.analyzer import UnifiedAnalysisAnalyzer
from app.unified_analysis.enums import AnalysisStatus
from app.unified_analysis.models import UnifiedAnalysisReport
from app.unified_analysis.registry import UnifiedAnalysisRegistry


class UnifiedAnalysisEngine(UnifiedAnalysisAnalyzer):
    """Orchestrates codebase unified analysis by executing registered contributors."""

    def __init__(self, registry: UnifiedAnalysisRegistry) -> None:
        """Initializes the engine with dependency-injected UnifiedAnalysisRegistry."""
        if registry is None:
            raise ValueError("UnifiedAnalysisRegistry dependency must not be None.")
        self.registry = registry

    def analyze(self, *, project_name: str, context: Any, **kwargs) -> UnifiedAnalysisReport:
        """Executes registered contributors sequentially and compiles a UnifiedAnalysisReport."""
        if project_name is None:
            raise ValueError("project_name must not be None.")
        if not isinstance(project_name, str):
            raise TypeError("project_name must be a string.")
        if not project_name.strip():
            raise ValueError("project_name must be a non-empty string.")
        if context is None:
            raise ValueError("context must not be None.")

        contributors = self.registry.list_contributors()
        results: Dict[str, Any] = {}

        # 1. Execute contributors sequentially in registration order (exceptions propagate)
        for contributor in contributors:
            res = contributor.contribute(context, **kwargs)
            results[contributor.contributor_type] = res

        # 2. Map results based on contributor types to compile UnifiedAnalysisReport
        scan_res = results.get("scan")
        parse_res = results.get("parse")
        arch_res = results.get("architecture")
        qual_res = results.get("quality")
        tech_res = results.get("technical_debt")

        # Compile any other results into metadata
        extra_metadata: Dict[str, Any] = {
            k: v
            for k, v in results.items()
            if k not in ("scan", "parse", "architecture", "quality", "technical_debt")
        }

        # 3. Construct UnifiedAnalysisReport with timezone-aware UTC datetime
        return UnifiedAnalysisReport(
            project_name=project_name,
            generated_at=datetime.now(timezone.utc),
            status=AnalysisStatus.SUCCESS,
            scan_result=scan_res,
            parse_result=parse_res,
            architecture_result=arch_res,
            quality_result=qual_res,
            technical_debt_result=tech_res,
            metadata=extra_metadata,
        )
