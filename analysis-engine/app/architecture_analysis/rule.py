"""Architecture Rule Contract Module."""

from abc import ABC, abstractmethod
from typing import Tuple

from app.architecture_analysis.enums import ArchitectureRuleType, ArchitectureSeverity
from app.architecture_analysis.models import ArchitectureIssue


class ArchitectureRule(ABC):
    """Abstract Base Class defining the contract for architecture validation rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this architecture rule."""
        pass

    @property
    @abstractmethod
    def rule_type(self) -> ArchitectureRuleType:
        """The category classification for this architecture rule."""
        pass

    @property
    @abstractmethod
    def severity(self) -> ArchitectureSeverity:
        """The default severity level assigned to issues raised by this rule."""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Short readable title of this architecture rule."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Long description of what this architecture rule checks or enforces."""
        pass

    @abstractmethod
    def evaluate(self, *args, **kwargs) -> Tuple[ArchitectureIssue, ...]:
        """Evaluates the codebase structure against the rule's criteria.

        Must return a tuple of identified ArchitectureIssue instances.
        """
        pass
