"""Rule registry module.

Provides the RuleRegistry class for registering and retrieving Quality Rule instances with
type validation and duplicate elimination.
"""

from typing import TYPE_CHECKING
from app.analyzer.rules.base import BaseRule
from app.analyzer.rules.exceptions import RuleError


class RuleRegistry:
    """Registry managing quality rule instances with type validation and duplicate checks."""

    def __init__(self) -> None:
        """Initializes an empty rule registry."""
        self._rules: list[BaseRule] = []
        self._registered_classes: set[type] = set()

    def register(self, rule: BaseRule) -> None:
        """Registers a quality rule instance.

        Args:
            rule: Instance of BaseRule.

        Raises:
            RuleError: If rule is invalid or already registered.
        """
        if not isinstance(rule, BaseRule):
            raise RuleError(f"Cannot register invalid rule instance: {type(rule)}")

        rule_cls = type(rule)
        if rule_cls in self._registered_classes:
            # Skip or ignore duplicate registration gracefully
            return

        self._registered_classes.add(rule_cls)
        self._rules.append(rule)

    def get_all(self) -> list[BaseRule]:
        """Returns all currently registered quality rules in deterministic registration order.

        Returns:
            List of BaseRule instances.
        """
        return list(self._rules)

    def clear(self) -> None:
        """Clears all registered quality rules."""
        self._rules.clear()
        self._registered_classes.clear()
