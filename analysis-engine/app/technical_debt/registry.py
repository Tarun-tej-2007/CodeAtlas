"""Technical Debt Rule Registry Module."""

import threading
from typing import Dict, Tuple

from app.technical_debt.exceptions import TechnicalDebtRuleError
from app.technical_debt.rule import TechnicalDebtRule


class TechnicalDebtRuleRegistry:
    """Thread-safe, instance-scoped registry for managing and ordering TechnicalDebtRules."""

    def __init__(self) -> None:
        """Initializes the registry with a thread lock and empty lookup storage."""
        self._lock = threading.Lock()
        self._rules: Dict[str, TechnicalDebtRule] = {}

    def register(self, rule: TechnicalDebtRule) -> None:
        """Registers a new technical debt rule.

        Raises TechnicalDebtRuleError if the rule is None, lacks id, or is already registered.
        """
        if rule is None:
            raise TechnicalDebtRuleError("Cannot register None rule.")
        if not hasattr(rule, "rule_id") or not rule.rule_id:
            raise TechnicalDebtRuleError("Rule must possess a non-empty 'rule_id'.")

        with self._lock:
            rule_id = rule.rule_id
            if rule_id in self._rules:
                raise TechnicalDebtRuleError(f"Technical debt rule '{rule_id}' is already registered.")
            self._rules[rule_id] = rule

    def unregister(self, rule_id: str) -> None:
        """Removes a registered rule by rule_id.

        Raises TechnicalDebtRuleError if the rule is not found.
        """
        if not rule_id:
            raise TechnicalDebtRuleError("Rule ID must be a non-empty string.")

        with self._lock:
            if rule_id not in self._rules:
                raise TechnicalDebtRuleError(f"Technical debt rule '{rule_id}' is not registered.")
            del self._rules[rule_id]

    def get(self, rule_id: str) -> TechnicalDebtRule:
        """Retrieves a registered rule by rule_id.

        Raises TechnicalDebtRuleError if the rule is not found.
        """
        if not rule_id:
            raise TechnicalDebtRuleError("Rule ID must be a non-empty string.")

        with self._lock:
            rule = self._rules.get(rule_id)
            if rule is None:
                raise TechnicalDebtRuleError(f"Technical debt rule '{rule_id}' is not registered.")
            return rule

    def contains(self, rule_id: str) -> bool:
        """Checks if a rule is registered under the given rule_id."""
        if not rule_id:
            return False

        with self._lock:
            return rule_id in self._rules

    def clear(self) -> None:
        """Clears all rules from the registry."""
        with self._lock:
            self._rules.clear()

    def list_rules(self) -> Tuple[TechnicalDebtRule, ...]:
        """Returns all registered rules, preserving their deterministic insertion order."""
        with self._lock:
            return tuple(self._rules.values())

    def __len__(self) -> int:
        """Returns the number of registered rules."""
        with self._lock:
            return len(self._rules)
