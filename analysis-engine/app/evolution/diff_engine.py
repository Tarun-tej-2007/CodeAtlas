"""Concrete implementation of EvolutionDifferenceEngine."""

import uuid
from typing import Any, Dict, List, Set, Tuple

from app.evolution.enums import ArchitecturalChangeType
from app.evolution.exceptions import EvolutionValidationError
from app.evolution.interfaces import EvolutionDifferenceEngine
from app.evolution.models import ArchitecturalChange, ArchitectureSnapshot


class ArchitectureEvolutionDifferenceEngine(EvolutionDifferenceEngine):
    """Concrete difference engine comparing snapshots and generating detailed architectural change logs."""

    def diff_snapshots(
        self, old_snapshot: ArchitectureSnapshot, new_snapshot: ArchitectureSnapshot
    ) -> Tuple[ArchitecturalChange, ...]:
        """Compares baseline and target snapshots, resolving component modifications.

        Args:
            old_snapshot: Reference baseline snapshot state.
            new_snapshot: Updated snapshot comparison state.

        Returns:
            Immutable collection tuple of ArchitecturalChange items.

        Raises:
            EvolutionValidationError: If snapshot formatting is invalid or inputs are missing.
        """
        if old_snapshot is None or new_snapshot is None:
            raise EvolutionValidationError("Both old_snapshot and new_snapshot parameters must be provided.")
        if not isinstance(old_snapshot, ArchitectureSnapshot) or not isinstance(new_snapshot, ArchitectureSnapshot):
            raise EvolutionValidationError("Snapshots must be valid ArchitectureSnapshot instances.")

        changes: List[ArchitecturalChange] = []

        # 1. Compare modules inventory
        old_mods = old_snapshot.components.get("modules", [])
        new_mods = new_snapshot.components.get("modules", [])

        if not isinstance(old_mods, list) or not isinstance(new_mods, list):
            raise EvolutionValidationError("Snapshot modules metadata is corrupt or invalid format.")

        old_mods_set = set(old_mods)
        new_mods_set = set(new_mods)

        for path in new_mods_set - old_mods_set:
            changes.append(
                ArchitecturalChange(
                    component_name=f"module:{path}",
                    change_type=ArchitecturalChangeType.ADDED,
                    description=f"Module '{path}' was added to inventory.",
                )
            )
        for path in old_mods_set - new_mods_set:
            changes.append(
                ArchitecturalChange(
                    component_name=f"module:{path}",
                    change_type=ArchitecturalChangeType.REMOVED,
                    description=f"Module '{path}' was removed from inventory.",
                )
            )
        for path in old_mods_set & new_mods_set:
            changes.append(
                ArchitecturalChange(
                    component_name=f"module:{path}",
                    change_type=ArchitecturalChangeType.UNCHANGED,
                    description=f"Module '{path}' is unchanged.",
                )
            )

        # 2. Compare layers
        old_layers_set = set(old_snapshot.layers)
        new_layers_set = set(new_snapshot.layers)

        for layer in new_layers_set - old_layers_set:
            changes.append(
                ArchitecturalChange(
                    component_name=f"layer:{layer}",
                    change_type=ArchitecturalChangeType.ADDED,
                    description=f"Architectural layer '{layer}' was defined.",
                )
            )
        for layer in old_layers_set - new_layers_set:
            changes.append(
                ArchitecturalChange(
                    component_name=f"layer:{layer}",
                    change_type=ArchitecturalChangeType.REMOVED,
                    description=f"Architectural layer '{layer}' was removed.",
                )
            )
        for layer in old_layers_set & new_layers_set:
            changes.append(
                ArchitecturalChange(
                    component_name=f"layer:{layer}",
                    change_type=ArchitecturalChangeType.UNCHANGED,
                    description=f"Architectural layer '{layer}' is unchanged.",
                )
            )

        # 3. Compare dependency graph metadata
        old_g = old_snapshot.components.get("dependency_graph_metadata", {})
        new_g = new_snapshot.components.get("dependency_graph_metadata", {})

        old_nodes = old_g.get("node_count", 0)
        new_nodes = new_g.get("node_count", 0)
        old_edges = old_g.get("edge_count", 0)
        new_edges = new_g.get("edge_count", 0)

        if old_nodes != new_nodes or old_edges != new_edges:
            changes.append(
                ArchitecturalChange(
                    component_name="dependency_graph",
                    change_type=ArchitecturalChangeType.MODIFIED,
                    description=f"Dependency graph changed: nodes {old_nodes}->{new_nodes}, edges {old_edges}->{new_edges}.",
                )
            )
        else:
            changes.append(
                ArchitecturalChange(
                    component_name="dependency_graph",
                    change_type=ArchitecturalChangeType.UNCHANGED,
                    description=f"Dependency graph structure is unchanged (nodes={new_nodes}, edges={new_edges}).",
                )
            )

        # 4. Compare architectural metrics
        old_metrics_list = old_snapshot.components.get("architectural_metrics", [])
        new_metrics_list = new_snapshot.components.get("architectural_metrics", [])

        old_metrics = {m["name"]: m for m in old_metrics_list if "name" in m}
        new_metrics = {m["name"]: m for m in new_metrics_list if "name" in m}

        for m_name in set(new_metrics.keys()) - set(old_metrics.keys()):
            changes.append(
                ArchitecturalChange(
                    component_name=f"architectural_metric:{m_name}",
                    change_type=ArchitecturalChangeType.ADDED,
                    description=f"Architectural metric '{m_name}' was introduced.",
                    metadata=new_metrics[m_name],
                )
            )
        for m_name in set(old_metrics.keys()) - set(new_metrics.keys()):
            changes.append(
                ArchitecturalChange(
                    component_name=f"architectural_metric:{m_name}",
                    change_type=ArchitecturalChangeType.REMOVED,
                    description=f"Architectural metric '{m_name}' was deleted.",
                    metadata=old_metrics[m_name],
                )
            )
        for m_name in set(old_metrics.keys()) & set(new_metrics.keys()):
            old_val = old_metrics[m_name].get("value")
            new_val = new_metrics[m_name].get("value")
            if old_val != new_val:
                changes.append(
                    ArchitecturalChange(
                        component_name=f"architectural_metric:{m_name}",
                        change_type=ArchitecturalChangeType.MODIFIED,
                        description=f"Architectural metric '{m_name}' value changed from {old_val} to {new_val}.",
                        metadata=new_metrics[m_name],
                    )
                )
            else:
                changes.append(
                    ArchitecturalChange(
                        component_name=f"architectural_metric:{m_name}",
                        change_type=ArchitecturalChangeType.UNCHANGED,
                        description=f"Architectural metric '{m_name}' is unchanged.",
                        metadata=new_metrics[m_name],
                    )
                )

        # 5. Compare quality metrics
        old_qm = old_snapshot.components.get("quality_metrics", {})
        new_qm = new_snapshot.components.get("quality_metrics", {})

        old_score = old_qm.get("overall_score", 0.0)
        new_score = new_qm.get("overall_score", 0.0)
        old_level = old_qm.get("overall_level", "unknown")
        new_level = new_qm.get("overall_level", "unknown")

        if old_score != new_score or old_level != new_level:
            changes.append(
                ArchitecturalChange(
                    component_name="quality_metrics:summary",
                    change_type=ArchitecturalChangeType.MODIFIED,
                    description=f"Quality score shifted from {old_score} ({old_level}) to {new_score} ({new_level}).",
                    metadata={"overall_score": new_score, "overall_level": new_level},
                )
            )
        else:
            changes.append(
                ArchitecturalChange(
                    component_name="quality_metrics:summary",
                    change_type=ArchitecturalChangeType.UNCHANGED,
                    description=f"Quality summary score is unchanged at {new_score}.",
                    metadata={"overall_score": new_score, "overall_level": new_level},
                )
            )

        # Individual quality metrics
        old_qm_m = {m["name"]: m for m in old_qm.get("metrics", []) if "name" in m}
        new_qm_m = {m["name"]: m for m in new_qm.get("metrics", []) if "name" in m}

        for q_name in set(new_qm_m.keys()) - set(old_qm_m.keys()):
            changes.append(
                ArchitecturalChange(
                    component_name=f"quality_metric:{q_name}",
                    change_type=ArchitecturalChangeType.ADDED,
                    description=f"Quality metric '{q_name}' was introduced.",
                )
            )
        for q_name in set(old_qm_m.keys()) - set(new_qm_m.keys()):
            changes.append(
                ArchitecturalChange(
                    component_name=f"quality_metric:{q_name}",
                    change_type=ArchitecturalChangeType.REMOVED,
                    description=f"Quality metric '{q_name}' was deleted.",
                )
            )
        for q_name in set(old_qm_m.keys()) & set(new_qm_m.keys()):
            o_val = old_qm_m[q_name].get("value")
            n_val = new_qm_m[q_name].get("value")
            if o_val != n_val:
                changes.append(
                    ArchitecturalChange(
                        component_name=f"quality_metric:{q_name}",
                        change_type=ArchitecturalChangeType.MODIFIED,
                        description=f"Quality metric '{q_name}' value changed from {o_val} to {n_val}.",
                    )
                )
            else:
                changes.append(
                    ArchitecturalChange(
                        component_name=f"quality_metric:{q_name}",
                        change_type=ArchitecturalChangeType.UNCHANGED,
                        description=f"Quality metric '{q_name}' is unchanged.",
                    )
                )

        # 6. Compare technical debt findings
        old_td = old_snapshot.components.get("technical_debt_metrics", {})
        new_td = new_snapshot.components.get("technical_debt_metrics", {})

        old_items_count = old_td.get("total_items", 0)
        new_items_count = new_td.get("total_items", 0)
        old_effort = old_td.get("total_effort_minutes", 0)
        new_effort = new_td.get("total_effort_minutes", 0)

        if old_items_count != new_items_count or old_effort != new_effort:
            changes.append(
                ArchitecturalChange(
                    component_name="technical_debt:summary",
                    change_type=ArchitecturalChangeType.MODIFIED,
                    description=f"Technical debt metrics changed: items {old_items_count}->{new_items_count}, effort {old_effort}->{new_effort} mins.",
                    metadata={"total_items": new_items_count, "total_effort_minutes": new_effort},
                )
            )
        else:
            changes.append(
                ArchitecturalChange(
                    component_name="technical_debt:summary",
                    change_type=ArchitecturalChangeType.UNCHANGED,
                    description=f"Technical debt summary is unchanged (items={new_items_count}, effort={new_effort} mins).",
                    metadata={"total_items": new_items_count, "total_effort_minutes": new_effort},
                )
            )

        # Individual technical debt items comparison
        old_td_items = {item["id"]: item for item in old_td.get("items", []) if "id" in item}
        new_td_items = {item["id"]: item for item in new_td.get("items", []) if "id" in item}

        for item_id in set(new_td_items.keys()) - set(old_td_items.keys()):
            changes.append(
                ArchitecturalChange(
                    component_name=f"technical_debt_item:{item_id}",
                    change_type=ArchitecturalChangeType.ADDED,
                    description=f"Technical debt finding '{new_td_items[item_id].get('title')}' was reported.",
                )
            )
        for item_id in set(old_td_items.keys()) - set(new_td_items.keys()):
            changes.append(
                ArchitecturalChange(
                    component_name=f"technical_debt_item:{item_id}",
                    change_type=ArchitecturalChangeType.REMOVED,
                    description=f"Technical debt finding '{old_td_items[item_id].get('title')}' was resolved.",
                )
            )
        for item_id in set(old_td_items.keys()) & set(new_td_items.keys()):
            o_eff = old_td_items[item_id].get("effort_minutes")
            n_eff = new_td_items[item_id].get("effort_minutes")
            if o_eff != n_eff:
                changes.append(
                    ArchitecturalChange(
                        component_name=f"technical_debt_item:{item_id}",
                        change_type=ArchitecturalChangeType.MODIFIED,
                        description=f"Technical debt finding '{new_td_items[item_id].get('title')}' effort changed: {o_eff}->{n_eff} mins.",
                    )
                )
            else:
                changes.append(
                    ArchitecturalChange(
                        component_name=f"technical_debt_item:{item_id}",
                        change_type=ArchitecturalChangeType.UNCHANGED,
                        description=f"Technical debt finding '{new_td_items[item_id].get('title')}' is unchanged.",
                    )
                )

        # 7. Sort changes alphabetically by component_name and change_type value for absolute determinism
        changes.sort(key=lambda c: (c.component_name, c.change_type.value))

        return tuple(changes)
