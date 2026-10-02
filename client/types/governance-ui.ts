export type PolicyCategory = "Architecture" | "Security" | "Dependencies" | "Code Quality" | "Repository" | "Engineering";
export type PolicyStatus = "Passing" | "At Risk" | "Failing" | "Disabled";
export type Severity = "Critical" | "High" | "Medium" | "Low";
export type ViolationStatus = "Open" | "Resolved" | "Ignored";
export type ExceptionStatus = "Active" | "Expiring Soon" | "Expired";

export interface GovernanceHealth {
  score: number;
  compliance: number;
  openViolations: number;
  criticalViolations: number;
  policyCount: number;
  passingPolicies: number;
  atRiskPolicies: number;
  failingPolicies: number;
  resolvedViolations: number;
  activeExceptions: number;
}

export interface GovernanceRule {
  id: string;
  policyId: string;
  name: string;
  description: string;
  severity: Severity;
  status: PolicyStatus;
  violationCount: number;
}

export interface GovernancePolicy {
  id: string;
  name: string;
  category: PolicyCategory;
  description: string;
  status: PolicyStatus;
  compliance: number;
  ruleCount: number;
  violationCount: number;
  owner: string;
  lastEvaluated: string;
  rules: GovernanceRule[];
}

export interface CategoryCompliance {
  category: PolicyCategory;
  compliance: number;
  policyCount: number;
  violationCount: number;
}

export interface ComplianceTrendPoint {
  timestamp: string;
  compliance: number;
  health: number;
  openViolations: number;
  criticalViolations: number;
}

export interface GovernanceViolation {
  id: string;
  policyId: string;
  ruleId: string;
  severity: Severity;
  status: ViolationStatus;
  component: string;
  message: string;
  description: string;
  source?: string;
  target?: string;
  filePath?: string;
  line?: number;
  date: string;
}

export interface GovernanceException {
  id: string;
  policyId: string;
  component: string;
  reason: string;
  expiry: string;
  approvedBy: string;
  status: ExceptionStatus;
  scope: string;
}

export interface GovernanceActivity {
  id: string;
  type: string;
  date: string;
  message: string;
  actor: string;
  category: PolicyCategory;
  severity?: Severity;
}

export interface GovernanceStats {
  health: GovernanceHealth;
  categories: CategoryCompliance[];
  trend: ComplianceTrendPoint[];
}

export interface GovernanceMockData {
  policies: GovernancePolicy[];
  violations: GovernanceViolation[];
  exceptions: GovernanceException[];
  activities: GovernanceActivity[];
  stats: GovernanceStats;
}
