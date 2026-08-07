"""AI Context Aggregation Service aggregating subsystem outputs into a single AIContext."""

import uuid
from typing import Any, List, Optional, Tuple

from app.ai.exceptions import AIValidationError
from app.ai.interfaces import AIContextBuilder
from app.ai.models import AIContext


class AIContextAggregationService(AIContextBuilder):
    """Concrete AIContextBuilder aggregating information from completed CodeAtlas subsystems."""

    def __init__(self) -> None:
        """Initializes the context aggregation service."""
        pass

    def build_context(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
        decisions: Optional[Tuple[Any, ...]] = None,
        **kwargs: Any,
    ) -> AIContext:
        """Aggregates all available completed analysis subsystem outputs.

        Args:
            project_id: Unique project scoping ID.
            commit_id: Target Git commit hash.
            dependency_graph: Optional dependency graph output.
            arch_result: Optional architecture layer/issue analysis result.
            governance_result: Optional governance compliance check result.
            evolution_result: Optional evolution trend result.
            decisions: Optional collection of architecture decisions.
            **kwargs: Extensible arbitrary subsystem results.

        Returns:
            The compiled immutable AIContext instance.

        Raises:
            AIValidationError: For invalid request or parameter failures.
        """
        # Fail-fast validation
        if project_id is None:
            raise AIValidationError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise AIValidationError("commit_id must be a non-empty string.")

        commit_id_normalized = commit_id.strip()

        # 1. Process Dependency Graph
        dep_graph_lines: List[str] = []
        files_set = set()

        if dependency_graph is not None:
            # Nodes extraction
            nodes = getattr(dependency_graph, "nodes", None) or ()
            node_strings = []
            for n in nodes:
                n_id = getattr(n, "id", "")
                if not n_id:
                    continue
                # Normalize windows paths to forward slashes
                n_id_norm = n_id.replace("\\", "/")
                n_type = getattr(n, "type", None)
                n_type_val = n_type.value if hasattr(n_type, "value") else str(n_type)
                node_strings.append(f"Node: {n_id_norm} ({n_type_val})")

                # Count files (nodes representing modules/files or containing file extension)
                if n_type_val == "module" or any(n_id_norm.endswith(ext) for ext in (".py", ".js", ".ts", ".json", ".md")):
                    files_set.add(n_id_norm)

            # Deduplicate and sort nodes
            node_strings = sorted(list(set(node_strings)))
            dep_graph_lines.extend(node_strings)

            # Edges extraction
            edges = getattr(dependency_graph, "edges", None) or ()
            edge_strings = []
            for e in edges:
                src = getattr(e, "source_id", "")
                tgt = getattr(e, "target_id", "")
                if not src or not tgt:
                    continue
                src_norm = src.replace("\\", "/")
                tgt_norm = tgt.replace("\\", "/")
                e_type = getattr(e, "type", None)
                e_type_val = e_type.value if hasattr(e_type, "value") else str(e_type)
                edge_strings.append(f"Edge: {src_norm} -> {tgt_norm} ({e_type_val})")

            # Deduplicate and sort edges
            edge_strings = sorted(list(set(edge_strings)))
            dep_graph_lines.extend(edge_strings)

        dependency_graph_summary = "\n".join(dep_graph_lines) if dep_graph_lines else None
        files_count = len(files_set)

        # 2. Process Architecture Issues, Layers and Metrics
        architecture_issues_list: List[str] = []
        layers_summary: List[str] = []
        metrics_summary: List[str] = []

        if arch_result is not None:
            # Issues
            issues = getattr(arch_result, "issues", None) or ()
            for issue in issues:
                cat = getattr(issue, "category", None)
                cat_val = cat.value if hasattr(cat, "value") else str(cat)
                sev = getattr(issue, "severity", None)
                sev_val = sev.value if hasattr(sev, "value") else str(sev)
                title = getattr(issue, "title", "")
                desc = getattr(issue, "description", "")
                loc = getattr(issue, "location", "") or "N/A"
                loc_norm = str(loc).replace("\\", "/")

                issue_str = f"{cat_val} [{sev_val}]: {title} - {desc} (Location: {loc_norm})"
                architecture_issues_list.append(issue_str)

            # Layers
            layers = getattr(arch_result, "layers", None) or ()
            for layer in layers:
                l_name = getattr(layer, "name", "")
                l_type = getattr(layer, "layer_type", None)
                l_type_val = l_type.value if hasattr(l_type, "value") else str(l_type)
                node_ids = getattr(layer, "node_ids", ()) or ()
                node_ids_norm = sorted([str(n).replace("\\", "/") for n in node_ids])
                layers_summary.append(f"Layer {l_name} ({l_type_val}): {', '.join(node_ids_norm)}")

            # Metrics
            metrics = getattr(arch_result, "metrics", None) or ()
            for metric in metrics:
                m_name = getattr(metric, "name", "")
                m_val = getattr(metric, "value", 0.0)
                m_unit = getattr(metric, "unit", "")
                metrics_summary.append(f"Metric {m_name}: {m_val} {m_unit}")

        architecture_issues = tuple(sorted(list(set(architecture_issues_list))))
        layers_summary_sorted = tuple(sorted(list(set(layers_summary))))
        metrics_summary_sorted = tuple(sorted(list(set(metrics_summary))))

        # 3. Process Governance violations
        governance_violations_list: List[str] = []
        if governance_result is not None:
            violations = getattr(governance_result, "violations", None) or ()
            for v in violations:
                rule = getattr(v, "rule_name", "")
                sev = getattr(v, "severity", None)
                sev_val = sev.value if hasattr(sev, "value") else str(sev)
                msg = getattr(v, "message", "")
                msg_norm = msg.replace("\\", "/")
                viol_str = f"{rule} [{sev_val}]: {msg_norm}"
                governance_violations_list.append(viol_str)

        governance_violations = tuple(sorted(list(set(governance_violations_list))))

        # 4. Process Decisions summary
        decisions_summary_list: List[str] = []
        if decisions is not None:
            for dec in decisions:
                title = getattr(dec, "title", "")
                cat = getattr(dec, "category", None)
                cat_val = cat.value if hasattr(cat, "value") else str(cat)
                status = getattr(dec, "status", None)
                status_val = status.value if hasattr(status, "value") else str(status)
                priority = getattr(dec, "priority", None)
                priority_val = priority.value if hasattr(priority, "value") else str(priority)

                dec_str = f"{title} ({cat_val}) - Status: {status_val}, Priority: {priority_val}"
                decisions_summary_list.append(dec_str)

        decisions_summary = tuple(sorted(list(set(decisions_summary_list))))

        # 5. Compile extra context (including evolution, visualization, unified, incremental)
        extra_context_dict = {}

        # Layers and Metrics
        if layers_summary_sorted:
            extra_context_dict["layers"] = layers_summary_sorted
        if metrics_summary_sorted:
            extra_context_dict["metrics"] = metrics_summary_sorted

        # Evolution Result
        if evolution_result is not None:
            evol_lines = []
            # Check for changes list
            changes = getattr(evolution_result, "changes", None)
            if changes:
                change_strings = []
                for c in changes:
                    comp = getattr(c, "component_name", "")
                    c_type = getattr(c, "change_type", None)
                    c_type_val = c_type.value if hasattr(c_type, "value") else str(c_type)
                    change_strings.append(f"Change: {comp} ({c_type_val})")
                evol_lines.append(f"Changes: {', '.join(sorted(list(set(change_strings))))}")

            # Check for trends
            for trend_attr in ("coupling_trend", "complexity_trend", "tech_debt_trend", "quality_trend", "layer_stability", "module_growth"):
                trend_val = getattr(evolution_result, trend_attr, None)
                if trend_val is not None:
                    evol_lines.append(f"{trend_attr.replace('_', ' ').title()}: {list(trend_val)}")

            # Check for summary dictionary
            summary = getattr(evolution_result, "summary", None)
            if summary:
                evol_lines.append(f"Summary delta: {dict(summary)}")

            extra_context_dict["evolution"] = "\n".join(evol_lines) if evol_lines else str(evolution_result)

        # Forward any kwargs into extra_context
        for k, v in kwargs.items():
            extra_context_dict[k] = v

        return AIContext(
            project_id=project_id,
            commit_id=commit_id_normalized,
            dependency_graph_summary=dependency_graph_summary,
            architecture_issues=architecture_issues,
            governance_violations=governance_violations,
            decisions_summary=decisions_summary,
            files_count=files_count,
            extra_context=extra_context_dict,
        )
