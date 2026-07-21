"""Rule registry module.

Provides the RuleRegistry class for registering and retrieving Quality Rule instances.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.analyzer.rules.base import BaseRule


class RuleRegistry:
    """Registry managing quality rule instances."""

    def __init__(self) -> None:
        """Initializes an empty rule registry."""
        self._rules: list["BaseRule"] = []

    def register(self, rule: "BaseRule") -> None:
        """Registers a quality rule instance.

        Args:
            rule: Instance of BaseRule.
        """
        self._rules.append(rule)

    def get_all(self) -> list["BaseRule"]:
        """Returns all currently registered quality rules.

        Returns:
            List of BaseRule instances.
        """
        return list(self._rules)

    def clear(self) -> None:
        """Clears all registered quality rules."""
        self._rules.clear()
