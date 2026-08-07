"""Decision builder service implementation constructing normalized, immutable decisions."""

import re
import uuid
from typing import Optional, Set, Tuple

from app.decision.enums import DecisionCategory, DecisionPriority, DecisionRelationshipType, DecisionStatus
from app.decision.exceptions import DecisionValidationError
from app.decision.interfaces import DecisionBuilder
from app.decision.models import ArchitectureDecision, DecisionMetadata, DecisionRelationship, DecisionRequest

# Semantic Version regex pattern (SemVer 2.0.0)
SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Valid status transitions map
VALID_TRANSITIONS = {
    DecisionStatus.DRAFT: {DecisionStatus.DRAFT, DecisionStatus.PROPOSED, DecisionStatus.ACCEPTED, DecisionStatus.REJECTED},
    DecisionStatus.PROPOSED: {DecisionStatus.PROPOSED, DecisionStatus.ACCEPTED, DecisionStatus.REJECTED},
    DecisionStatus.ACCEPTED: {DecisionStatus.ACCEPTED, DecisionStatus.SUPERSEDED, DecisionStatus.DEPRECATED},
    DecisionStatus.REJECTED: {DecisionStatus.REJECTED, DecisionStatus.DRAFT, DecisionStatus.PROPOSED},
    DecisionStatus.SUPERSEDED: {DecisionStatus.SUPERSEDED, DecisionStatus.DEPRECATED},
    DecisionStatus.DEPRECATED: {DecisionStatus.DEPRECATED},
}


class DecisionBuilderService(DecisionBuilder):
    """Concrete DecisionBuilder service executing normalization and constraint validations."""

    def build_from_request(self, request: DecisionRequest) -> ArchitectureDecision:
        """Constructs and normalizes an ArchitectureDecision from a DecisionRequest.

        Args:
            request: The decision registration request.

        Returns:
            The normalized immutable ArchitectureDecision.

        Raises:
            DecisionValidationError: If validation fails.
        """
        if request is None:
            raise DecisionValidationError("request must not be None.")
        if not isinstance(request, DecisionRequest):
            raise DecisionValidationError("request must be a valid DecisionRequest instance.")

        d = request.decision
        return self.build_decision(
            title=d.title,
            category=d.category,
            status=d.status,
            priority=d.priority,
            context=d.context,
            decision_text=d.decision_text,
            consequences=d.consequences,
            metadata=d.metadata,
            relationships=d.relationships,
            decision_id=d.decision_id,
        )

    def build_decision(
        self,
        title: str,
        category: DecisionCategory,
        status: DecisionStatus,
        priority: DecisionPriority,
        context: str,
        decision_text: str,
        consequences: str,
        metadata: DecisionMetadata,
        relationships: Tuple[DecisionRelationship, ...] = (),
        decision_id: Optional[uuid.UUID] = None,
    ) -> ArchitectureDecision:
        """Constructs, validates, and normalizes an immutable ArchitectureDecision instance.

        Args:
            title: Decision title.
            category: Domain classification category.
            status: Initial status phase.
            priority: Priority scale.
            context: Problem statement context.
            decision_text: Selected resolution strategy text.
            consequences: Resulting outcomes or trade-offs.
            metadata: Associated author metadata DTO.
            relationships: Set of linked decisions.
            decision_id: Optional existing decision tracking ID.

        Returns:
            The immutable ArchitectureDecision.

        Raises:
            DecisionValidationError: If validation checks fail.
        """
        # Fail-fast validations on non-empty string properties
        if not title or not title.strip():
            raise DecisionValidationError("title must be a non-empty string.")
        if not context or not context.strip():
            raise DecisionValidationError("context must be a non-empty string.")
        if not decision_text or not decision_text.strip():
            raise DecisionValidationError("decision_text must be a non-empty string.")
        if consequences is None:
            raise DecisionValidationError("consequences must not be None.")
        if metadata is None or not isinstance(metadata, DecisionMetadata):
            raise DecisionValidationError("metadata must be a valid DecisionMetadata instance.")
        if relationships is None:
            raise DecisionValidationError("relationships must not be None.")

        from app.decision.cache import execution_cache, make_hashable
        cache = execution_cache.get()
        cache_key = None
        if cache is not None:
            cache_key = make_hashable((
                "build_decision", title, category, status, priority, context,
                decision_text, consequences, metadata, relationships, decision_id
            ))
            if cache_key in cache:
                return cache[cache_key]

        # Normalize string values
        norm_title = title.strip()
        norm_context = context.strip()
        norm_decision_text = decision_text.strip()
        norm_consequences = consequences.strip()

        # Semantic version metadata validation
        extra = metadata.extra_info
        if extra and "version" in extra:
            ver = str(extra["version"]).strip()
            if not SEMVER_REGEX.match(ver):
                raise DecisionValidationError(f"Invalid semantic version format: '{ver}'")

        dec_id = decision_id or uuid.uuid4()

        # Normalize and validate relationships
        seen_rels: Set[Tuple[uuid.UUID, DecisionRelationshipType]] = set()
        normalized_rels = []

        for rel in relationships:
            if not isinstance(rel, DecisionRelationship):
                raise DecisionValidationError("All items in relationships must be valid DecisionRelationship instances.")

            # Validate target decision is not itself
            if rel.target_decision_id == dec_id:
                raise DecisionValidationError("A decision cannot define a relationship with itself.")

            rel_key = (rel.target_decision_id, rel.relationship_type)
            if rel_key in seen_rels:
                raise DecisionValidationError(
                    f"Duplicate relationship detected for target decision ID: '{rel.target_decision_id}' "
                    f"with type: '{rel.relationship_type}'"
                )
            seen_rels.add(rel_key)

            normalized_rels.append(rel)

        # Deterministic sorting of relationships: by target_decision_id, then by relationship_type
        normalized_rels.sort(key=lambda r: (str(r.target_decision_id), r.relationship_type.value))

        res = ArchitectureDecision(
            decision_id=dec_id,
            title=norm_title,
            category=category,
            status=status,
            priority=priority,
            context=norm_context,
            decision_text=norm_decision_text,
            consequences=norm_consequences,
            metadata=metadata,
            relationships=tuple(normalized_rels),
        )

        if cache is not None and cache_key is not None:
            cache[cache_key] = res

        return res

    def validate_transition(self, current: DecisionStatus, proposed: DecisionStatus) -> None:
        """Validates if a transition from current status to proposed status is allowed.

        Args:
            current: Current DecisionStatus state.
            proposed: Proposed target DecisionStatus state.

        Raises:
            DecisionValidationError: If the transition is not allowed under lifecycle rules.
        """
        if current not in VALID_TRANSITIONS or proposed not in VALID_TRANSITIONS[current]:
            raise DecisionValidationError(
                f"Invalid lifecycle transition from state '{current}' to state '{proposed}'."
            )
