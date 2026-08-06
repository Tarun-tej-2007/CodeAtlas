"""Unit tests for the PolicyDefinitionService and policy construction validations."""

import unittest
from app.governance import (
    PolicyCategory,
    RuleType,
    ViolationSeverity,
    GovernanceValidationError,
    PolicyRule,
    PolicyDefinitionService,
)


class TestPolicyDefinition(unittest.TestCase):
    """Verifies rules normalization, ordering, category setups, and contradiction checks."""

    def setUp(self) -> None:
        self.service = PolicyDefinitionService()

    def test_empty_policy_rules(self) -> None:
        """Verifies policy can be created with empty rules tuple."""
        policy = self.service.create_policy(
            name="Empty Policy",
            version="1.0.0",
            category=PolicyCategory.QUALITY,
            rules=(),
        )
        self.assertEqual(policy.metadata.name, "Empty Policy")
        self.assertEqual(len(policy.rules), 0)

    def test_single_rule_policy(self) -> None:
        """Verifies policy with one rule builds successfully."""
        r = PolicyRule(
            name="SingleRule",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.WARNING,
        )
        policy = self.service.create_policy(
            name="Single Rule Policy",
            version="1.0.0",
            category=PolicyCategory.QUALITY,
            rules=(r,),
        )
        self.assertEqual(len(policy.rules), 1)
        self.assertEqual(policy.rules[0].name, "SingleRule")

    def test_naming_convention_policy(self) -> None:
        """Verifies naming rules build correctly."""
        r = PolicyRule(
            name="Naming_Rule",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.INFO,
            configuration={"pattern": "^test_.*"},
        )
        policy = self.service.create_policy(
            name="Naming Policy",
            version="1.1.0",
            category=PolicyCategory.QUALITY,
            rules=(r,),
        )
        self.assertEqual(policy.rules[0].configuration["pattern"], "^test_.*")

    def test_complexity_threshold_policy(self) -> None:
        """Verifies complexity limits rules can be constructed."""
        r = PolicyRule(
            name="Complexity_Limit",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 15},
        )
        policy = self.service.create_policy(
            name="Complexity Policy",
            version="1.0.0",
            category=PolicyCategory.METRIC,
            rules=(r,),
        )
        self.assertEqual(policy.rules[0].configuration["max_threshold"], 15)

    def test_coupling_limit_policy(self) -> None:
        """Verifies coupling limits rules creation."""
        r = PolicyRule(
            name="Coupling_Limit",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "coupling", "max_threshold": 10},
        )
        policy = self.service.create_policy(
            name="Coupling Policy",
            version="2.0.0",
            category=PolicyCategory.METRIC,
            rules=(r,),
        )
        self.assertEqual(policy.rules[0].configuration["max_threshold"], 10)

    def test_technical_debt_limit_policy(self) -> None:
        """Verifies technical debt limits rules creation."""
        r = PolicyRule(
            name="TechDebt_Limit",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "technical_debt", "max_threshold": 600},
        )
        policy = self.service.create_policy(
            name="Debt Policy",
            version="1.0.0",
            category=PolicyCategory.QUALITY,
            rules=(r,),
        )
        self.assertEqual(policy.rules[0].configuration["max_threshold"], 600)

    def test_deterministic_rule_ordering(self) -> None:
        """Verifies rules are stored in absolute alphabetical name order."""
        r1 = PolicyRule(name="ZRule", rule_type=RuleType.THRESHOLD, severity=ViolationSeverity.WARNING)
        r2 = PolicyRule(name="ARule", rule_type=RuleType.THRESHOLD, severity=ViolationSeverity.WARNING)
        r3 = PolicyRule(name="MRule", rule_type=RuleType.THRESHOLD, severity=ViolationSeverity.WARNING)

        policy = self.service.create_policy(
            name="Ordered Policy",
            version="1.0.0",
            category=PolicyCategory.QUALITY,
            rules=(r1, r2, r3),
        )

        names = [r.name for r in policy.rules]
        self.assertEqual(names, ["ARule", "MRule", "ZRule"])

    def test_contradictory_dependency_rules_validation(self) -> None:
        """Verifies validation failure if a module is both required and forbidden."""
        r1 = PolicyRule(
            name="Forbid_A",
            rule_type=RuleType.FORBIDDEN_DEPENDENCY,
            severity=ViolationSeverity.ERROR,
            configuration={"forbidden_modules": ("moduleA", "moduleB")},
        )
        r2 = PolicyRule(
            name="Require_A",
            rule_type=RuleType.REQUIRED_DEPENDENCY,
            severity=ViolationSeverity.ERROR,
            configuration={"required_modules": ("moduleA", "moduleC")},
        )

        with self.assertRaises(GovernanceValidationError) as ctx:
            self.service.create_policy(
                name="Contradictory Policy",
                version="1.0.0",
                category=PolicyCategory.DEPENDENCY,
                rules=(r1, r2),
            )
        self.assertIn("required and forbidden", str(ctx.exception))

    def test_contradictory_metric_thresholds_validation(self) -> None:
        """Verifies validation fails if min_threshold exceeds max_threshold for a metric."""
        r1 = PolicyRule(
            name="Threshold_Min",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "min_threshold": 25},
        )
        r2 = PolicyRule(
            name="Threshold_Max",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 20},
        )

        with self.assertRaises(GovernanceValidationError) as ctx:
            self.service.create_policy(
                name="Contradictory Thresholds",
                version="1.0.0",
                category=PolicyCategory.METRIC,
                rules=(r1, r2),
            )
        self.assertIn("minimum limit 25.0 exceeds maximum limit 20.0", str(ctx.exception))

    def test_validation_failures_invalid_params(self) -> None:
        """Verifies invalid parameters raise GovernanceValidationError."""
        # Empty name
        with self.assertRaises(GovernanceValidationError):
            self.service.create_policy(name=" ", version="1.0.0", category=PolicyCategory.QUALITY, rules=())

        # Empty version
        with self.assertRaises(GovernanceValidationError):
            self.service.create_policy(name="P", version="  ", category=PolicyCategory.QUALITY, rules=())

        # Duplicate rule name
        r1 = PolicyRule(name="Dup", rule_type=RuleType.THRESHOLD, severity=ViolationSeverity.INFO)
        r2 = PolicyRule(name="Dup", rule_type=RuleType.THRESHOLD, severity=ViolationSeverity.INFO)
        with self.assertRaises(GovernanceValidationError) as ctx:
            self.service.create_policy(name="P", version="1.0", category=PolicyCategory.QUALITY, rules=(r1, r2))
        self.assertIn("Duplicate rule name", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
