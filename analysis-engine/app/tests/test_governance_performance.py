"""Unit and performance integration tests for the Architecture Governance caching layers."""

import threading
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.governance.cache import execution_cache
from app.governance import (
    PolicyCategory,
    RuleType,
    ViolationSeverity,
    PolicyRule,
    PolicyDefinitionService,
    PolicyEvaluationService,
    GovernanceViolationAnalyzer,
    ComplianceScoringService,
    GovernancePolicy,
    PolicyMetadata,
    PolicyViolation,
    GovernanceViolationReport,
    GovernanceRequest,
    GovernanceService,
)
from app.evolution.interfaces import ArchitectureAnalysisProvider
from app.graph.dependency_graph import DependencyGraph


class TestGovernancePerformance(unittest.TestCase):
    """Verifies governance execution-scoped cache hits, thread safety, and resource cleanups."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 7, 9, 0, 0, tzinfo=timezone.utc)
        self.project_id = uuid.uuid4()
        self.rule_id = uuid.uuid4()
        self.token = execution_cache.set(None)

    def tearDown(self) -> None:
        execution_cache.reset(self.token)

    def test_policy_normalization_cache_reuse(self) -> None:
        """Verifies policy definition service caches policy DTO objects on identical rules list."""
        service = PolicyDefinitionService()
        r = PolicyRule(
            name="RuleA",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"max_threshold": 10},
        )

        token = execution_cache.set({})
        try:
            p1 = service.create_policy(
                name="PolicyName",
                version="1.0.0",
                category=PolicyCategory.QUALITY,
                rules=(r,),
            )
            p2 = service.create_policy(
                name="PolicyName",
                version="1.0.0",
                category=PolicyCategory.QUALITY,
                rules=(r,),
            )
            # They must be the identical object reference
            self.assertIs(p1, p2)
        finally:
            execution_cache.reset(token)

    def test_policy_evaluation_cache_reuse(self) -> None:
        """Verifies duplicate rules evaluation requests fetch precalculated violations list from cache."""
        provider = MagicMock(spec=ArchitectureAnalysisProvider)
        provider.get_dependency_graph.return_value = DependencyGraph(nodes=[], edges=[])
        provider.get_architecture_result.return_value = None
        provider.get_quality_report.return_value = None
        provider.get_technical_debt_report.return_value = None

        service = PolicyEvaluationService(provider)
        r = PolicyRule(
            name="ThresholdRule",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 10},
        )

        token = execution_cache.set({})
        try:
            res1 = service.evaluate_rule("commit_target", r)
            res2 = service.evaluate_rule("commit_target", r)

            self.assertIs(res1, res2)
            # The mock provider was queried only once
            self.assertEqual(provider.get_dependency_graph.call_count, 1)
        finally:
            execution_cache.reset(token)

    def test_violation_analysis_cache_reuse(self) -> None:
        """Verifies duplicate raw violations analyze requests return cached report directly."""
        analyzer = GovernanceViolationAnalyzer()
        v = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="coupling_rule",
            severity=ViolationSeverity.ERROR,
            message="High coupling.",
            details={},
        )
        violations = (v,)

        token = execution_cache.set({})
        try:
            rep1 = analyzer.analyze_violations(self.project_id, "commit1", violations)
            rep2 = analyzer.analyze_violations(self.project_id, "commit1", violations)
            self.assertIs(rep1, rep2)
        finally:
            execution_cache.reset(token)

    def test_compliance_scoring_cache_reuse(self) -> None:
        """Verifies duplicate compliance scoring requests retrieve cached reports."""
        scorer = ComplianceScoringService()
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit1",
            generated_at=self.time_utc,
            violations=(),
            violations_by_rule={},
            violations_by_severity={},
        )

        token = execution_cache.set({})
        try:
            c1 = scorer.calculate_compliance(violation_report)
            c2 = scorer.calculate_compliance(violation_report)
            self.assertIs(c1, c2)
        finally:
            execution_cache.reset(token)

    def test_context_isolation_between_requests(self) -> None:
        """Verifies cache does not leak across different runs/requests contexts."""
        provider = MagicMock(spec=ArchitectureAnalysisProvider)
        provider.get_dependency_graph.return_value = DependencyGraph(nodes=[], edges=[])
        provider.get_architecture_result.return_value = None
        provider.get_quality_report.return_value = None
        provider.get_technical_debt_report.return_value = None

        service = PolicyEvaluationService(provider)
        r = PolicyRule(
            name="ThresholdRule",
            rule_type=RuleType.THRESHOLD,
            severity=ViolationSeverity.ERROR,
            configuration={"metric_name": "complexity", "max_threshold": 10},
        )

        # First context run
        token1 = execution_cache.set({})
        try:
            service.evaluate_rule("commit1", r)
        finally:
            execution_cache.reset(token1)

        # Second context run - should query provider again
        token2 = execution_cache.set({})
        try:
            service.evaluate_rule("commit1", r)
        finally:
            execution_cache.reset(token2)

        self.assertEqual(provider.get_dependency_graph.call_count, 2)

    def test_thread_safety_isolation(self) -> None:
        """Verifies distinct threads carry isolated cache contexts preventing cross-thread leaks."""
        results = []

        def run_thread(thread_val):
            # Each thread initializes its own execution cache
            token = execution_cache.set({})
            try:
                cache = execution_cache.get()
                cache["thread_specific_key"] = thread_val
                # Sleep briefly to verify no interleaving overrides from other threads
                import time
                time.sleep(0.01)
                results.append(execution_cache.get()["thread_specific_key"])
            finally:
                execution_cache.reset(token)

        t1 = threading.Thread(target=run_thread, args=("A",))
        t2 = threading.Thread(target=run_thread, args=("B",))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Both threads retrieved their own correct context value
        self.assertIn("A", results)
        self.assertIn("B", results)


if __name__ == "__main__":
    unittest.main()
