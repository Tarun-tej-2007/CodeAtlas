export type FindingSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type FindingStatus = "OPEN" | "ACKNOWLEDGED" | "RESOLVED" | "DISMISSED";
export type ReviewCategory = "ARCHITECTURE" | "DEPENDENCIES" | "BOUNDARIES" | "SECURITY" | "SCALABILITY" | "MAINTAINABILITY" | "PERFORMANCE";
export type ReviewState = "IDLE" | "ANALYZING" | "COMPLETED" | "ERROR";

export interface ArchitectureReviewScore {
  overall: number;
  architecture: number;
  boundaries: number;
  dependencies: number;
  security: number;
  scalability: number;
  maintainability: number;
  performance: number;
}

export interface ArchitectureReviewFinding {
  id: string;
  title: string;
  severity: FindingSeverity;
  category: ReviewCategory;
  status: FindingStatus;
  confidence: number;
  affectedComponents: string[];
  description: string;
  whyItMatters: string;
  evidence: string;
  architectureImpact: string;
  risk: string;
  suggestedRemediation: string[];
}

export interface ArchitectureReviewRecommendation {
  id: string;
  title: string;
  priority: FindingSeverity; // Using same union as severity for simplicity
  confidence: number;
  problem: string;
  evidence: string;
  affectedComponents: string[];
  expectedArchitecture: string;
  currentArchitecture: string;
  expectedBenefit: string;
  estimatedEffort: "HIGH" | "MEDIUM" | "LOW";
  suggestedSteps: string[];
  status: FindingStatus;
}

export interface ArchitectureReviewCategory {
  category: ReviewCategory;
  score: number;
  explanation: string;
}

export interface ArchitectureReviewEvidence {
  id: string;
  type: string;
  description: string;
  findingId?: string;
  components: string[];
}

export interface ArchitectureReviewSummary {
  assessment: string;
  strengths: string[];
  concerns: string[];
}

export interface ArchitectureReviewHistory {
  id: string;
  date: string;
  score: number;
  findings: number;
  criticalFindings: number;
  recommendations: number;
  change: "UP" | "DOWN" | "FLAT";
}

export interface ArchitectureStrength {
  id: string;
  title: string;
  score: number;
  explanation: string;
  components: string[];
}

export interface ArchitectureReviewStats {
  score: number;
  confidence: number;
  totalFindings: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  recommendations: number;
}

export interface ArchitectureReview {
  stats: ArchitectureReviewStats;
  scoreBreakdown: ArchitectureReviewScore;
  summary: ArchitectureReviewSummary;
  findings: ArchitectureReviewFinding[];
  recommendations: ArchitectureReviewRecommendation[];
  evidence: ArchitectureReviewEvidence[];
  history: ArchitectureReviewHistory[];
  strengths: ArchitectureStrength[];
  categories: ArchitectureReviewCategory[];
}
