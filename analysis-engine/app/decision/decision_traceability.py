"""Decision traceability service implementation mapping decisions to codebase artifacts."""

import uuid
from typing import Dict, List, Tuple

from app.decision.exceptions import DecisionTraceabilityError, DecisionValidationError
from app.decision.interfaces import DecisionTraceabilityProvider
from app.decision.models import ArchitectureDecision, DecisionTraceGraph, DecisionTraceLink


class DecisionTraceabilityService(DecisionTraceabilityProvider):
    """Concrete DecisionTraceabilityProvider constructing immutable decision trace graphs."""

    def trace_decisions(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        decisions: Tuple[ArchitectureDecision, ...],
    ) -> DecisionTraceGraph:
        """Maps codebase file paths/modules back to associated decision identifiers and builds trace graph.

        Args:
            project_id: Unique project tracker.
            commit_id: Baseline target commit hash.
            decisions: Collection of decisions.

        Returns:
            The compiled immutable DecisionTraceGraph DTO.

        Raises:
            DecisionTraceabilityError: If traceability extraction fails.
        """
        if project_id is None:
            raise DecisionTraceabilityError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise DecisionTraceabilityError("commit_id must be a non-empty string.")
        if decisions is None:
            raise DecisionTraceabilityError("decisions collection must not be None.")

        links_list: List[DecisionTraceLink] = []

        # Parse target links from each decision's extra_info / metadata
        for dec in decisions:
            if not isinstance(dec, ArchitectureDecision):
                raise DecisionTraceabilityError("All items in decisions must be valid ArchitectureDecision instances.")

            extra = dec.metadata.extra_info
            targets = extra.get("targets") or ()
            if isinstance(targets, str):
                targets = (targets,)

            for tgt in targets:
                if not isinstance(tgt, str):
                    continue

                # Expected format: "type:value" (e.g. "file:src/app.py")
                if ":" not in tgt:
                    # Default target type if type not specified
                    target_type = "module"
                    target_id = tgt.strip()
                else:
                    parts = tgt.split(":", 1)
                    target_type = parts[0].strip().lower()
                    target_id = parts[1].strip()

                if not target_id:
                    continue

                # Normalize target identifier
                # Replace Windows backward slashes with standard forward slashes for files
                if target_type == "file" or "/" in target_id or "\\" in target_id:
                    target_id = target_id.replace("\\", "/")

                links_list.append(
                    DecisionTraceLink(
                        target_id=target_id,
                        target_type=target_type,
                        decision_id=dec.decision_id,
                    )
                )

        # Eliminate duplicate links
        unique_links_map = {}
        for link in links_list:
            key = (link.target_type, link.target_id, link.decision_id)
            unique_links_map[key] = link

        unique_links = list(unique_links_map.values())

        # Preserve deterministic ordering: sort by target_type, target_id, then decision_id (string)
        unique_links.sort(key=lambda x: (x.target_type, x.target_id.lower(), str(x.decision_id)))

        # Build indexes
        links_by_target: Dict[str, List[uuid.UUID]] = {}
        links_by_decision: Dict[str, List[str]] = {}

        for link in unique_links:
            # target indexing
            t_key = f"{link.target_type}:{link.target_id}"
            if t_key not in links_by_target:
                links_by_target[t_key] = []
            links_by_target[t_key].append(link.decision_id)

            # decision indexing
            d_key = str(link.decision_id)
            if d_key not in links_by_decision:
                links_by_decision[d_key] = []
            links_by_decision[d_key].append(t_key)

        # Sort values and keys in index mappings for absolute determinism
        sorted_by_target = {}
        for t_key in sorted(links_by_target.keys()):
            sorted_by_target[t_key] = tuple(sorted(links_by_target[t_key], key=str))

        sorted_by_decision = {}
        for d_key in sorted(links_by_decision.keys()):
            sorted_by_decision[d_key] = tuple(sorted(links_by_decision[d_key]))

        return DecisionTraceGraph(
            graph_id=uuid.uuid4(),
            project_id=project_id,
            commit_id=commit_id.strip(),
            links=tuple(unique_links),
            links_by_target=sorted_by_target,
            links_by_decision=sorted_by_decision,
        )
