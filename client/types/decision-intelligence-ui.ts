export type RecommendationStatus = "NEW" | "REVIEWED" | "IN_PROGRESS" | "COMPLETED" | "DISMISSED";
export type RecommendationPriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type DecisionCategory = "ARCHITECTURE" | "DEPENDENCIES" | "SECURITY" | "CODE_QUALITY" | "PERFORMANCE" | "MAINTAINABILITY";
export type ImpactLevel = "HIGH" | "MEDIUM" | "LOW";
export type EffortLevel = "HIGH" | "MEDIUM" | "LOW";
export type DecisionAnalysisState = "Ready" | "Analyzing Architecture" | "Analyzing Dependencies" | "Analyzing Governance" | "Analyzing Technical Debt" | "Calculating Impact" | "Generating Recommendations" | "Complete";

export interface DecisionHealth {
  score: number;
  recommendations: number;
  highPriority: number;
  architectureRisks: number;
  technicalDebt: number;
  potentialSavings: number; // percentage
}

export interface DecisionRecommendation {
  id: string;
  title: string;
  priority: RecommendationPriority;
  category: DecisionCategory;
  impact: ImpactLevel;
  effort: EffortLevel;
  confidence: number;
  status: RecommendationStatus;
  affectedComponents: string[];
  problem: string;
  evidence: string;
  architectureImpact: string;
  riskImpact: string;
  expectedBenefit: string;
  suggestedActions: string[];
  date: string;
}

export interface ImpactEffortPoint {
  id: string;
  label: string;
  impactScore: number; // 0-100
  effortScore: number; // 0-100
  priority: RecommendationPriority;
  recommendationId: string;
}

export interface TechnicalDebtItem {
  id: string;
  category: string;
  count: number;
}

export interface TechnicalDebtSummary {
  total: number;
  previousTotal: number;
  items: TechnicalDebtItem[];
  trend: "UP" | "DOWN" | "FLAT";
}

export interface DecisionHistoryEntry {
  id: string;
  date: string;
  event: string;
  category: DecisionCategory;
  status: RecommendationStatus | "SYSTEM";
  recommendationId?: string;
}

export interface DecisionCategoryStats {
  category: DecisionCategory;
  recommendations: number;
  highPriority: number;
  riskCount: number;
  averageConfidence: number;
}

export interface DecisionAnalysisStats {
  health: DecisionHealth;
  debt: TechnicalDebtSummary;
}

export interface DecisionMockData {
  stats: DecisionAnalysisStats;
  recommendations: DecisionRecommendation[];
  matrixPoints: ImpactEffortPoint[];
  history: DecisionHistoryEntry[];
}
