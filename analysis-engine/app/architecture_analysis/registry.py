"""Architecture Rule Registry Module."""

import threading
from typing import Dict, Tuple

from app.architecture_analysis.exceptions import ArchitectureRegistryError
from app.architecture_analysis.rule import ArchitectureRule


class ArchitectureRuleRegistry:
    """Thread-safe, isolated registry for managing and ordering architecture rules."""

    def __init__(self) -> None:
        """Initializes an empty registry with a thread lock and storage."""
        self._lock = threading.Lock()
        self._rules: Dict[str, ArchitectureRule] = {}

    def register(self, rule: ArchitectureRule) -> None:
        """Registers a new architecture rule.

        Raises ArchitectureRegistryError if a rule with the same ID already exists.
        """
        with self._lock:
            if rule.rule_id in self._rules:
                raise ArchitectureRegistryError(
                    f"Rule with ID '{rule.rule_id}' is already registered."
                )
            self._rules[rule.rule_id] = rule

    def remove(self, rule_id: str) -> None:
        """Removes a rule by its ID.

        Raises ArchitectureRegistryError if the rule is not found.
        """
        with self._lock:
            if rule_id not in self._rules:
                raise ArchitectureRegistryError(f"Rule with ID '{rule_id}' is not registered.")
            del self._rules[rule_id]

    def get(self, rule_id: str) -> ArchitectureRule:
        """Retrieves a rule by its ID.

        Raises ArchitectureRegistryError if the rule is not found.
        """
        with self._lock:
            if rule_id not in self._rules:
                raise ArchitectureRegistryError(f"Rule with ID '{rule_id}' is not registered.")
            return self._rules[rule_id]

    def list_rules(self) -> Tuple[ArchitectureRule, ...]:
        """Returns all registered rules, preserving their deterministic insertion order."""
        with self._lock:
            return tuple(self._rules.values())

    def clear(self) -> None:
        """Clears all rules from the registry."""
        with self._lock:
            self._rules.clear()

    def contains(self, rule_id: str) -> bool:
        """Checks if a rule is registered."""
        with self._lock:
            return rule_id in self._rules

    def __len__(self) -> int:
        """Returns the number of registered rules."""
        with self._lock:
            return len(self._rules)
