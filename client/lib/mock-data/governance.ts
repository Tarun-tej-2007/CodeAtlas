import { GovernanceMockData, GovernancePolicy, GovernanceViolation, GovernanceException, GovernanceActivity, CategoryCompliance, ComplianceTrendPoint, Severity, ViolationStatus } from "@/types/governance-ui";

const policies: GovernancePolicy[] = [
  { id: "pol-1", name: "Architecture Layering", category: "Architecture", description: "Enforce correct boundaries between Domain, Application, and Infrastructure layers.", status: "Passing", compliance: 96, ruleCount: 4, violationCount: 1, owner: "Architecture Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-2", name: "Dependency Direction", category: "Dependencies", description: "Dependencies must follow approved architectural boundaries.", status: "At Risk", compliance: 82, ruleCount: 5, violationCount: 5, owner: "Architecture Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-3", name: "Domain Isolation", category: "Architecture", description: "Domain logic must not depend on external frameworks or infrastructure.", status: "Failing", compliance: 74, ruleCount: 4, violationCount: 7, owner: "Architecture Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-4", name: "Security Baseline", category: "Security", description: "All services must implement base security requirements.", status: "Passing", compliance: 100, ruleCount: 6, violationCount: 0, owner: "Security Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-5", name: "API Boundary Policy", category: "Architecture", description: "Internal services should not be directly exposed to public interfaces.", status: "Passing", compliance: 92, ruleCount: 3, violationCount: 2, owner: "Architecture Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-6", name: "Repository Access Policy", category: "Repository", description: "Only Infrastructure layer may implement repositories.", status: "Passing", compliance: 94, ruleCount: 2, violationCount: 1, owner: "Platform Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-7", name: "Circular Dependency Policy", category: "Dependencies", description: "No circular dependencies permitted between modules.", status: "At Risk", compliance: 85, ruleCount: 2, violationCount: 3, owner: "Architecture Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-8", name: "External Dependency Policy", category: "Dependencies", description: "External libraries must be vetted and approved.", status: "Passing", compliance: 98, ruleCount: 3, violationCount: 0, owner: "Security Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-9", name: "Code Complexity Policy", category: "Code Quality", description: "Cyclomatic complexity must remain below thresholds.", status: "Passing", compliance: 88, ruleCount: 2, violationCount: 2, owner: "Engineering Ops", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-10", name: "Secret Management", category: "Security", description: "No hardcoded secrets in source code.", status: "Passing", compliance: 95, ruleCount: 1, violationCount: 1, owner: "Security Team", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-11", name: "Testing Coverage", category: "Code Quality", description: "Minimum 80% test coverage for domain logic.", status: "Passing", compliance: 94, ruleCount: 2, violationCount: 1, owner: "Engineering Ops", lastEvaluated: "12 mins ago", rules: [] },
  { id: "pol-12", name: "Repository Hygiene", category: "Repository", description: "Clean repository structure and PR standards.", status: "Passing", compliance: 95, ruleCount: 1, violationCount: 0, owner: "Platform Team", lastEvaluated: "12 mins ago", rules: [] },
];

const violations: GovernanceViolation[] = [
  { id: "v-1", policyId: "pol-1", ruleId: "r-1", severity: "Critical", status: "Open", component: "Domain", message: "Domain directly accesses PostgreSQLRepository", description: "Expected: Domain -> Application -> Infrastructure. Detected: Domain -> PostgreSQLRepository", date: "Oct 01" },
  { id: "v-2", policyId: "pol-1", ruleId: "r-2", severity: "High", status: "Open", component: "Controller", message: "Controller bypasses application service", description: "Detected direct repository access", date: "Sep 29" },
  { id: "v-3", policyId: "pol-7", ruleId: "r-3", severity: "High", status: "Open", component: "AuthModule", message: "Circular dependency detected", description: "AuthModule -> UserModule -> AuthModule", date: "Sep 28" },
  { id: "v-4", policyId: "pol-2", ruleId: "r-4", severity: "Medium", status: "Open", component: "PaymentService", message: "Service exceeds dependency threshold", description: "Service has too many incoming dependencies.", date: "Sep 27" },
  { id: "v-5", policyId: "pol-11", ruleId: "r-5", severity: "Low", status: "Open", component: "EmailService", message: "Missing test coverage", description: "Coverage is at 76%.", date: "Sep 26" },
  // Adding more open violations to reach 23 total open
  ...Array.from({ length: 18 }).map((_, i) => ({
    id: `v-open-${i+6}`,
    policyId: "pol-3",
    ruleId: "r-gen",
    severity: (i % 5 === 0 ? "High" : i % 2 === 0 ? "Medium" : "Low") as Severity,
    status: "Open" as ViolationStatus,
    component: `Component-${i}`,
    message: "Generic violation message",
    description: "Detailed generic violation explanation.",
    date: "Sep 25"
  })),
  // 11 Resolved violations
  ...Array.from({ length: 11 }).map((_, i) => ({
    id: `v-res-${i+1}`,
    policyId: "pol-4",
    ruleId: "r-gen",
    severity: "Medium" as Severity,
    status: "Resolved" as ViolationStatus,
    component: `ResolvedComp-${i}`,
    message: "Resolved security violation",
    description: "Was previously failing.",
    date: "Sep 20"
  }))
];

// Re-adjust critical count to ensure exactly 2 open critical violations
violations[0].severity = "Critical";
violations[10].severity = "Critical"; // one of the generated ones

const exceptions: GovernanceException[] = [
  { id: "exc-1", policyId: "pol-5", component: "Legacy API Boundary", reason: "Migration underway.", expiry: "Oct 15", approvedBy: "Architecture Team", status: "Active", scope: "Global" },
  { id: "exc-2", policyId: "pol-6", component: "Legacy Repository Access", reason: "Pending rewrite to new architecture pattern.", expiry: "Oct 08", approvedBy: "Platform Team", status: "Expiring Soon", scope: "Module" },
  { id: "exc-3", policyId: "pol-9", component: "Core Logic Complex Function", reason: "Mathematically complex domain logic, cannot be simplified.", expiry: "Dec 31", approvedBy: "Engineering Ops", status: "Active", scope: "Function" },
  { id: "exc-4", policyId: "pol-2", component: "Vendor SDK Integration", reason: "Vendor SDK dictates dependency pattern.", expiry: "Nov 30", approvedBy: "Architecture Team", status: "Active", scope: "Module" }
];

const activities: GovernanceActivity[] = [
  { id: "act-1", type: "evaluation", date: "Oct 01", message: "Governance check completed (Compliance: 91%)", actor: "System", category: "Architecture" },
  { id: "act-2", type: "policy_update", date: "Sep 29", message: "Dependency Direction policy updated", actor: "Architecture Team", category: "Dependencies" },
  { id: "act-3", type: "violation_resolved", date: "Sep 27", message: "Architecture Layering violation resolved", actor: "Dev Team", category: "Architecture", severity: "High" },
  { id: "act-4", type: "evaluation", date: "Sep 24", message: "Security Baseline evaluated", actor: "System", category: "Security" },
  { id: "act-5", type: "policy_enabled", date: "Sep 21", message: "Domain Isolation policy enabled", actor: "Architecture Team", category: "Architecture" },
];

const categories: CategoryCompliance[] = [
  { category: "Architecture", compliance: 88, policyCount: 3, violationCount: 10 },
  { category: "Security", compliance: 96, policyCount: 2, violationCount: 1 },
  { category: "Dependencies", compliance: 82, policyCount: 3, violationCount: 8 },
  { category: "Code Quality", compliance: 91, policyCount: 2, violationCount: 3 },
  { category: "Repository", compliance: 94, policyCount: 2, violationCount: 1 },
  { category: "Engineering", compliance: 89, policyCount: 0, violationCount: 0 },
];

const trend: ComplianceTrendPoint[] = [
  { timestamp: "Sep 05", compliance: 84, health: 80, openViolations: 30, criticalViolations: 5 },
  { timestamp: "Sep 10", compliance: 85, health: 81, openViolations: 28, criticalViolations: 4 },
  { timestamp: "Sep 14", compliance: 86, health: 82, openViolations: 27, criticalViolations: 4 },
  { timestamp: "Sep 18", compliance: 84, health: 80, openViolations: 29, criticalViolations: 5 },
  { timestamp: "Sep 21", compliance: 88, health: 84, openViolations: 25, criticalViolations: 3 },
  { timestamp: "Sep 24", compliance: 89, health: 85, openViolations: 24, criticalViolations: 3 },
  { timestamp: "Sep 27", compliance: 90, health: 86, openViolations: 23, criticalViolations: 2 },
  { timestamp: "Sep 29", compliance: 91, health: 87, openViolations: 23, criticalViolations: 2 },
  { timestamp: "Oct 01", compliance: 91, health: 87, openViolations: 23, criticalViolations: 2 },
];

export const MOCK_GOVERNANCE_DATA: GovernanceMockData = {
  policies,
  violations,
  exceptions,
  activities,
  stats: {
    health: {
      score: 87,
      compliance: 91,
      openViolations: 23,
      criticalViolations: 2,
      policyCount: 12,
      passingPolicies: 9,
      atRiskPolicies: 2,
      failingPolicies: 1,
      resolvedViolations: 11,
      activeExceptions: 4
    },
    categories,
    trend
  }
};
