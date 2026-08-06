"""Unit tests for the Architecture Governance Domain Foundation components."""

import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from pydantic import ValidationError

from app.governance import (
    GovernanceStatus,
    PolicyCategory,
    RuleType,
    ViolationSeverity,
    GovernanceError,
    GovernanceValidationError,
    GovernancePersistenceError,
    PolicyEvaluationError,
    PolicyMetadata,
    PolicyRule,
    GovernancePolicy,
    PolicyViolation,
    GovernanceSummary,
    GovernanceRequest,
    GovernanceResult,
)


class TestGovernanceDomain(unittest.TestCase):
    """Verifies validations, immutability, serialization, and exceptions in governance package."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
        self.project_id = uuid.uuid4()
        self.policy_id = uuid.uuid4()
        self.rule_id = uuid.uuid4()

    def test_enums_attributes(self) -> None:
        """Verifies enum value mappings."""
        self.assertEqual(PolicyCategory.DEPENDENCY.value, "dependency")
        self.assertEqual(RuleType.FORBIDDEN_DEPENDENCY.value, "forbidden_dependency")
        self.assertEqual(ViolationSeverity.ERROR.value, "error")
        self.assertEqual(GovernanceStatus.PASSED.value, "passed")

    def test_exceptions_inheritance(self) -> None:
        """Verifies domain exceptions inherit correctly from GovernanceError."""
        self.assertTrue(issubclass(GovernanceValidationError, GovernanceError))
        self.assertTrue(issubclass(GovernancePersistenceError, GovernanceError))
        self.assertTrue(issubclass(PolicyEvaluationError, GovernanceError))

    def test_policy_metadata_validation_success(self) -> None:
        """Verifies successful instantiation of PolicyMetadata with valid fields."""
        meta = PolicyMetadata(
            policy_id=self.policy_id,
            name="No Cyclic Deps",
            version="1.0.0",
            category=PolicyCategory.DEPENDENCY,
            created_at=self.time_utc,
            extra_info={"created_by": "admin"},
        )
        self.assertEqual(meta.policy_id, self.policy_id)
        self.assertEqual(meta.name, "No Cyclic Deps")
        self.assertIsInstance(meta.extra_info, MappingProxyType)
        self.assertEqual(meta.extra_info["created_by"], "admin")

    def test_policy_metadata_validation_failures(self) -> None:
        """Verifies PolicyMetadata validation rejects empty strings and naive datetimes."""
        # Empty name
        with self.assertRaises(ValidationError):
            PolicyMetadata(
                name="  ",
                version="1.0.0",
                category=PolicyCategory.DEPENDENCY,
                created_at=self.time_utc,
            )

        # Naive datetime
        with self.assertRaises(ValidationError):
            PolicyMetadata(
                name="No Cyclic Deps",
                version="1.0.0",
                category=PolicyCategory.DEPENDENCY,
                created_at=datetime.now(),
            )

    def test_policy_metadata_immutability(self) -> None:
        """Verifies metadata properties cannot be mutated once instantiated."""
        meta = PolicyMetadata(
            name="No Cyclic Deps",
            version="1.0.0",
            category=PolicyCategory.DEPENDENCY,
            created_at=self.time_utc,
        )
        with self.assertRaises(ValidationError):
            # pydantic frozen model raises ValidationError when attempting to mutate
            meta.name = "New Name"

    def test_policy_rule_configuration_freeze(self) -> None:
        """Verifies configuration dictionary becomes MappingProxyType."""
        rule = PolicyRule(
            name="Forbidden Import Rule",
            rule_type=RuleType.FORBIDDEN_DEPENDENCY,
            severity=ViolationSeverity.ERROR,
            configuration={"forbidden_pattern": "app.legacy.*"},
        )
        self.assertIsInstance(rule.configuration, MappingProxyType)
        with self.assertRaises(TypeError):
            # Attempt to mutate mapping proxy raises TypeError
            rule.configuration["forbidden_pattern"] = "app.other.*"

    def test_policy_rule_empty_name(self) -> None:
        """Verifies rules reject empty names."""
        with self.assertRaises(ValidationError):
            PolicyRule(
                name="",
                rule_type=RuleType.FORBIDDEN_DEPENDENCY,
                severity=ViolationSeverity.ERROR,
            )

    def test_governance_policy_nested_components(self) -> None:
        """Verifies policy composition of metadata and rules."""
        meta = PolicyMetadata(
            name="Standard Architecture",
            version="2.0.0",
            category=PolicyCategory.LAYER,
            created_at=self.time_utc,
        )
        rule = PolicyRule(
            name="Forbidden Import Rule",
            rule_type=RuleType.FORBIDDEN_DEPENDENCY,
            severity=ViolationSeverity.ERROR,
        )
        policy = GovernancePolicy(
            policy_id=self.policy_id,
            metadata=meta,
            rules=(rule,),
        )
        self.assertEqual(policy.policy_id, self.policy_id)
        self.assertEqual(len(policy.rules), 1)
        self.assertEqual(policy.rules[0].name, "Forbidden Import Rule")

    def test_policy_violation_validations(self) -> None:
        """Verifies PolicyViolation fields mapping and checks."""
        v = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="Forbidden Import Rule",
            severity=ViolationSeverity.ERROR,
            message="Import of app.legacy is forbidden.",
            details={"source": "app/main.py", "line": 15},
        )
        self.assertEqual(v.rule_name, "Forbidden Import Rule")
        self.assertIsInstance(v.details, MappingProxyType)

        # Empty message check
        with self.assertRaises(ValidationError):
            PolicyViolation(
                rule_id=self.rule_id,
                rule_name="Forbidden Import Rule",
                severity=ViolationSeverity.ERROR,
                message=" ",
            )

    def test_governance_summary_limits(self) -> None:
        """Verifies GovernanceSummary rejects negative counts."""
        with self.assertRaises(ValidationError):
            GovernanceSummary(passed_count=-1, failed_count=0)

    def test_governance_request_inputs(self) -> None:
        """Verifies request fields validation."""
        req = GovernanceRequest(
            project_id=self.project_id,
            project_name="Atlas",
            commit_id="commit-abc-123",
            policies=(),
            correlation_id="corr-abc-123",
        )
        self.assertEqual(req.project_name, "Atlas")
        self.assertEqual(req.correlation_id, "corr-abc-123")

        # Empty project name
        with self.assertRaises(ValidationError):
            GovernanceRequest(
                project_id=self.project_id,
                project_name=" ",
                commit_id="commit-abc-123",
            )

    def test_governance_result_immutability_and_serialization(self) -> None:
        """Verifies GovernanceResult fields freeze, serialization, and immutability."""
        summary = GovernanceSummary(passed_count=2, failed_count=0, warning_count=0, total_rules=2)
        res = GovernanceResult(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            status=GovernanceStatus.PASSED,
            summary=summary,
            created_at=self.time_utc,
            extra_info={"duration_ms": 120.0},
        )
        self.assertEqual(res.status, GovernanceStatus.PASSED)
        self.assertIsInstance(res.extra_info, MappingProxyType)

        # Test Pydantic serialization
        serialized = res.model_dump()
        self.assertEqual(serialized["commit_id"], "commit-abc-123")
        self.assertEqual(serialized["status"], "passed")
        self.assertEqual(serialized["extra_info"]["duration_ms"], 120.0)


if __name__ == "__main__":
    unittest.main()
