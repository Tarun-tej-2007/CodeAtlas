"""Enums describing architecture decision properties, status, priorities, and relations."""

from enum import StrEnum


class DecisionStatus(StrEnum):
    """Execution and approval status classifications of an architecture decision."""

    DRAFT = "draft"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class DecisionPriority(StrEnum):
    """Urgency or importance weight level of an architecture decision."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionCategory(StrEnum):
    """Categorized domain scopes affected by an architecture decision."""

    ARCHITECTURE = "architecture"
    DESIGN = "design"
    TECHNOLOGY = "technology"
    PATTERN = "pattern"
    INTEGRATION = "integration"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


class DecisionRelationshipType(StrEnum):
    """Directed link classifications of relationships between distinct decisions."""

    SUPERSEDES = "supersedes"
    SUPERSEDED_BY = "superseded_by"
    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    REQUIRED_BY = "required_by"
