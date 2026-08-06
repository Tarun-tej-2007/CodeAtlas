"""Concrete implementation of TrendAnalyzer."""

from typing import Any, Dict, List, Optional, Set, Tuple

from app.evolution.enums import ArchitecturalChangeType
from app.evolution.exceptions import EvolutionValidationError
from app.evolution.interfaces import TrendAnalyzer
from app.evolution.models import EvolutionResult, EvolutionTrendResult


class ArchitecturalTrendAnalyzer(TrendAnalyzer):
    """Concrete trend analyzer compiling chronological codebase quality, complexity, debt and growth curves."""

    def analyze_trends(
        self, history: Tuple[EvolutionResult, ...], *, window_size: Optional[int] = None
    ) -> EvolutionTrendResult:
        """Analyzes chronological evolution history to extract trends.

        Args:
            history: Chronological collection of EvolutionResult items.
            window_size: Optional configurable trailing historical window size.

        Returns:
            The compiled EvolutionTrendResult.

        Raises:
            EvolutionValidationError: If chronological ordering is invalid or inputs are missing.
        """
        if history is None:
            raise EvolutionValidationError("History collection parameter must not be None.")

        from app.evolution.cache import execution_cache
        cache = execution_cache.get()
        if cache is not None:
            history_key = ",".join(res.metadata.target_commit for res in history if res is not None)
            cache_key = f"trends:{history_key}:{window_size}"
            if cache_key in cache:
                return cache[cache_key]

        # 1. Filter out adjacent duplicate target commits
        filtered_history: List[EvolutionResult] = []
        for res in history:
            if not isinstance(res, EvolutionResult):
                raise EvolutionValidationError("All historical items must be valid EvolutionResult instances.")
            if not filtered_history:
                filtered_history.append(res)
            elif res.metadata.target_commit != filtered_history[-1].metadata.target_commit:
                filtered_history.append(res)

        # 2. Validate chronological ordering
        for i in range(len(filtered_history) - 1):
            t1 = filtered_history[i].metadata.created_at
            t2 = filtered_history[i + 1].metadata.created_at
            if t1 > t2:
                raise EvolutionValidationError("Historical evolution results are not in chronological order.")

        # 3. Apply configurable trailing window
        if window_size is not None:
            if window_size <= 0:
                raise EvolutionValidationError("window_size must be a positive integer.")
            filtered_history = filtered_history[-window_size:]

        # If history is empty, return empty result
        if not filtered_history:
            return EvolutionTrendResult(
                coupling_trend=(),
                complexity_trend=(),
                tech_debt_trend=(),
                quality_trend=(),
                layer_stability=(),
                module_growth=(),
                summary={
                    "coupling_trend": "stable",
                    "complexity_trend": "stable",
                    "tech_debt_trend": "stable",
                    "quality_trend": "stable",
                    "layer_stability": "stable",
                    "module_growth": "stable",
                },
            )

        # Trace variables
        coupling_vals: List[float] = []
        complexity_vals: List[float] = []
        tech_debt_vals: List[int] = []
        quality_vals: List[float] = []
        layer_counts: List[float] = []
        module_counts: List[int] = []

        # Keep sets tracking active modules/layers at each step
        active_modules: Set[str] = set()
        active_layers: Set[str] = set()

        # Last known metric states
        current_coupling = 0.0
        current_complexity = 0.0
        current_tech_debt = 0
        current_quality = 100.0

        for step in filtered_history:
            # Process changes
            for change in step.changes:
                comp_name = change.component_name
                c_type = change.change_type

                # Module tracking
                if comp_name.startswith("module:"):
                    path = comp_name.split("module:", 1)[1]
                    if c_type in (ArchitecturalChangeType.ADDED, ArchitecturalChangeType.UNCHANGED):
                        active_modules.add(path)
                    elif c_type == ArchitecturalChangeType.REMOVED:
                        active_modules.discard(path)

                # Layer tracking
                elif comp_name.startswith("layer:"):
                    layer = comp_name.split("layer:", 1)[1]
                    if c_type in (ArchitecturalChangeType.ADDED, ArchitecturalChangeType.UNCHANGED):
                        active_layers.add(layer)
                    elif c_type == ArchitecturalChangeType.REMOVED:
                        active_layers.discard(layer)

                # Coupling and Complexity
                elif comp_name.startswith("architectural_metric:"):
                    m_name = comp_name.split("architectural_metric:", 1)[1]
                    if change.metadata and "value" in change.metadata:
                        val = float(change.metadata["value"])
                        if m_name.lower() == "coupling":
                            current_coupling = val
                        elif m_name.lower() == "complexity":
                            current_complexity = val

                # Quality Overall Score
                elif comp_name == "quality_metrics:summary":
                    if change.metadata and "overall_score" in change.metadata:
                        current_quality = float(change.metadata["overall_score"])

                # Tech Debt Total Items
                elif comp_name == "technical_debt:summary":
                    if change.metadata and "total_items" in change.metadata:
                        current_tech_debt = int(change.metadata["total_items"])

            # Append current status state values
            coupling_vals.append(current_coupling)
            complexity_vals.append(current_complexity)
            tech_debt_vals.append(current_tech_debt)
            quality_vals.append(current_quality)
            layer_counts.append(float(len(active_layers)))
            module_counts.append(len(active_modules))

        # Helper to compute direction slope
        def get_direction(vals: List[Any]) -> str:
            if len(vals) <= 1:
                return "stable"
            if vals[-1] > vals[0]:
                return "increasing"
            if vals[-1] < vals[0]:
                return "decreasing"
            return "stable"

        summary = {
            "coupling_trend": get_direction(coupling_vals),
            "complexity_trend": get_direction(complexity_vals),
            "tech_debt_trend": get_direction(tech_debt_vals),
            "quality_trend": get_direction(quality_vals),
            "layer_stability": get_direction(layer_counts),
            "module_growth": get_direction(module_counts),
        }

        trend_result = EvolutionTrendResult(
            coupling_trend=tuple(coupling_vals),
            complexity_trend=tuple(complexity_vals),
            tech_debt_trend=tuple(tech_debt_vals),
            quality_trend=tuple(quality_vals),
            layer_stability=tuple(layer_counts),
            module_growth=tuple(module_counts),
            summary=summary,
        )
        if cache is not None:
            history_key = ",".join(res.metadata.target_commit for res in history if res is not None)
            cache_key = f"trends:{history_key}:{window_size}"
            cache[cache_key] = trend_result
        return trend_result
