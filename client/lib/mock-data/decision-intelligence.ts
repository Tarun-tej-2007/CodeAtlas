import { DecisionMockData, DecisionRecommendation, ImpactEffortPoint, DecisionHistoryEntry, TechnicalDebtSummary, DecisionCategory } from "@/types/decision-intelligence-ui";

const generateRecommendations = (): DecisionRecommendation[] => {
  const baseRecs: Partial<DecisionRecommendation>[] = [
    {
      id: "rec-1",
      title: "Refactor Authentication Boundary",
      priority: "HIGH",
      category: "ARCHITECTURE",
      impact: "HIGH",
      effort: "MEDIUM",
      confidence: 94,
      status: "NEW",
      affectedComponents: ["AuthService", "UserService", "JWTService"],
      problem: "Authentication logic is shared across multiple application boundaries, increasing coupling between presentation and infrastructure layers.",
      evidence: "6 cross-layer dependencies detected across 3 services.",
      architectureImpact: "High coupling across domains.",
      riskImpact: "Changes to auth affect all downstream boundaries.",
      expectedBenefit: "Reduced coupling and clearer domain boundaries.",
      suggestedActions: ["Introduce authentication application boundary", "Move token validation behind domain-facing interface", "Remove direct infrastructure dependency"],
      date: "Oct 01, 2026",
    },
    {
      id: "rec-2",
      title: "Resolve Circular Dependency Cluster",
      priority: "CRITICAL",
      category: "DEPENDENCIES",
      impact: "HIGH",
      effort: "HIGH",
      confidence: 98,
      status: "NEW",
      affectedComponents: ["OrderService", "InventoryService", "BillingService"],
      problem: "Three core services have cyclical references preventing independent deployment.",
      evidence: "Cycle detected: Order -> Inventory -> Billing -> Order",
      architectureImpact: "Prevents service extraction.",
      riskImpact: "High risk of cascading failures.",
      expectedBenefit: "Independent deployability.",
      suggestedActions: ["Extract shared interface", "Use event-driven communication for Billing updates"],
      date: "Sep 28, 2026",
    },
    {
      id: "rec-3",
      title: "Isolate Repository Infrastructure",
      priority: "HIGH",
      category: "ARCHITECTURE",
      impact: "MEDIUM",
      effort: "MEDIUM",
      confidence: 85,
      status: "IN_PROGRESS",
      affectedComponents: ["PostgreSQLRepository", "MongoAdapter"],
      problem: "Domain layer directly references DB adapters.",
      evidence: "Import of 'pg' detected in 4 domain entities.",
      architectureImpact: "Violates Clean Architecture.",
      riskImpact: "Hard to unit test domain.",
      expectedBenefit: "Testability and separation of concerns.",
      suggestedActions: ["Implement repository interfaces in domain", "Inject adapters at runtime"],
      date: "Sep 26, 2026",
    },
    {
      id: "rec-4",
      title: "Reduce High-Complexity Modules",
      priority: "MEDIUM",
      category: "CODE_QUALITY",
      impact: "MEDIUM",
      effort: "LOW",
      confidence: 77,
      status: "NEW",
      affectedComponents: ["PaymentProcessor"],
      problem: "Cyclomatic complexity exceeds 25 in core payment loop.",
      evidence: "SonarQube metric: complexity 28.",
      architectureImpact: "Low.",
      riskImpact: "High risk of bugs during modification.",
      expectedBenefit: "Easier maintenance.",
      suggestedActions: ["Extract sub-methods", "Use strategy pattern"],
      date: "Oct 01, 2026",
    },
    {
      id: "rec-5",
      title: "Consolidate Duplicate Services",
      priority: "HIGH",
      category: "ARCHITECTURE",
      impact: "HIGH",
      effort: "HIGH",
      confidence: 91,
      status: "REVIEWED",
      affectedComponents: ["EmailSender", "NotificationService"],
      problem: "Two distinct services handle outbound messaging.",
      evidence: "80% code overlap in messaging templates.",
      architectureImpact: "Duplicated logic.",
      riskImpact: "Inconsistent message delivery.",
      expectedBenefit: "Single source of truth for communications.",
      suggestedActions: ["Merge EmailSender into NotificationService", "Standardize API"],
      date: "Sep 22, 2026",
    },
    {
      id: "rec-6",
      title: "Strengthen API Boundary",
      priority: "HIGH",
      category: "ARCHITECTURE",
      impact: "HIGH",
      effort: "MEDIUM",
      confidence: 89,
      status: "NEW",
      affectedComponents: ["PublicAPI", "InternalAPI"],
      problem: "Internal DTOs are leaking into public API responses.",
      evidence: "UserEntity exposed directly on /api/v1/users",
      architectureImpact: "Tight coupling between internal DB and external consumers.",
      riskImpact: "Data leakage and brittle contracts.",
      expectedBenefit: "Decoupled internal evolution.",
      suggestedActions: ["Create explicit Response DTOs", "Add mapping layer"],
      date: "Oct 01, 2026",
    },
    {
      id: "rec-7",
      title: "Reduce External Dependency Coupling",
      priority: "MEDIUM",
      category: "DEPENDENCIES",
      impact: "MEDIUM",
      effort: "MEDIUM",
      confidence: 82,
      status: "DISMISSED",
      affectedComponents: ["ThirdPartyAnalytics"],
      problem: "Direct calls to analytics SDK throughout the codebase.",
      evidence: "54 files import 'analytics-sdk'.",
      architectureImpact: "Vendor lock-in.",
      riskImpact: "Hard to replace analytics provider.",
      expectedBenefit: "Vendor independence.",
      suggestedActions: ["Create internal Analytics interface"],
      date: "Sep 15, 2026",
    },
    {
      id: "rec-8",
      title: "Improve Domain Isolation",
      priority: "MEDIUM",
      category: "ARCHITECTURE",
      impact: "LOW",
      effort: "HIGH",
      confidence: 76,
      status: "COMPLETED",
      affectedComponents: ["ProductDomain"],
      problem: "Product domain shares state with Pricing domain.",
      evidence: "Shared Redis cache instance.",
      architectureImpact: "Moderate coupling.",
      riskImpact: "Cache invalidation bugs.",
      expectedBenefit: "Clear boundary.",
      suggestedActions: ["Separate cache instances"],
      date: "Sep 10, 2026",
    },
  ];

  // Fill remaining 10 to reach 18
  const extraRecs: DecisionRecommendation[] = Array.from({ length: 10 }).map((_, i) => {
    const isArch = i < 2; // Make 2 more architecture risks (total 5 + 2 = 7 architecture recs)
    const category: DecisionCategory = isArch ? "ARCHITECTURE" : (i % 2 === 0 ? "SECURITY" : "PERFORMANCE");
    return {
      id: `rec-${i + 9}`,
      title: `Auto-generated Recommendation ${i + 9}`,
      priority: "LOW",
      category,
      impact: "LOW",
      effort: "LOW",
      confidence: 60 + i * 2,
      status: "NEW",
      affectedComponents: [`Component-${i}`],
      problem: "Generic problem detected by automated analysis.",
      evidence: "System heuristic match.",
      architectureImpact: "Minimal.",
      riskImpact: "Low risk.",
      expectedBenefit: "Minor improvement.",
      suggestedActions: ["Review configuration"],
      date: "Oct 01, 2026",
    };
  });

  return [...baseRecs, ...extraRecs] as DecisionRecommendation[];
};

export const MOCK_DECISION_RECOMMENDATIONS = generateRecommendations();

// Map recommendations to the matrix
export const MOCK_IMPACT_EFFORT_POINTS: ImpactEffortPoint[] = MOCK_DECISION_RECOMMENDATIONS.map((r, i) => {
  let impactScore = r.impact === "HIGH" ? 85 : r.impact === "MEDIUM" ? 50 : 20;
  let effortScore = r.effort === "HIGH" ? 85 : r.effort === "MEDIUM" ? 50 : 20;
  
  // Add some deterministic jitter
  impactScore += (i % 3) * 5 - 5;
  effortScore += (i % 4) * 4 - 6;

  return {
    id: `pt-${r.id}`,
    recommendationId: r.id,
    label: r.title.substring(0, 15) + "...",
    impactScore: Math.min(100, Math.max(0, impactScore)),
    effortScore: Math.min(100, Math.max(0, effortScore)),
    priority: r.priority,
  };
});

export const MOCK_TECHNICAL_DEBT: TechnicalDebtSummary = {
  total: 34,
  previousTotal: 38,
  trend: "DOWN",
  items: [
    { id: "td-1", category: "Architecture", count: 11 },
    { id: "td-2", category: "Dependencies", count: 8 },
    { id: "td-3", category: "Code Quality", count: 7 },
    { id: "td-4", category: "Infrastructure", count: 5 },
    { id: "td-5", category: "Security", count: 3 },
  ],
};

export const MOCK_DECISION_HISTORY: DecisionHistoryEntry[] = [
  { id: "ev-1", date: "Oct 01", event: "Dependency direction recommendation generated", category: "DEPENDENCIES", status: "SYSTEM", recommendationId: "rec-2" },
  { id: "ev-2", date: "Sep 29", event: "Authentication boundary recommendation reviewed", category: "ARCHITECTURE", status: "REVIEWED", recommendationId: "rec-1" },
  { id: "ev-3", date: "Sep 27", event: "Circular dependency recommendation created", category: "DEPENDENCIES", status: "NEW", recommendationId: "rec-2" },
  { id: "ev-4", date: "Sep 26", event: "Isolate Repository Infrastructure started", category: "ARCHITECTURE", status: "IN_PROGRESS", recommendationId: "rec-3" },
  { id: "ev-5", date: "Sep 24", event: "Technical debt analysis completed", category: "CODE_QUALITY", status: "SYSTEM" },
  { id: "ev-6", date: "Sep 22", event: "Consolidate Duplicate Services reviewed", category: "ARCHITECTURE", status: "REVIEWED", recommendationId: "rec-5" },
  { id: "ev-7", date: "Sep 21", event: "Architecture refactoring recommendation completed", category: "ARCHITECTURE", status: "COMPLETED", recommendationId: "rec-8" },
  { id: "ev-8", date: "Sep 15", event: "External dependency recommendation dismissed", category: "DEPENDENCIES", status: "DISMISSED", recommendationId: "rec-7" },
  { id: "ev-9", date: "Sep 10", event: "Improve Domain Isolation created", category: "ARCHITECTURE", status: "NEW", recommendationId: "rec-8" },
  { id: "ev-10", date: "Sep 01", event: "Initial baseline analysis", category: "ARCHITECTURE", status: "SYSTEM" },
];

// High Priority count = 5 (2 CRITICAL + 3 HIGH in baseRecs).
// Architecture Risks = 7 (5 in baseRecs with ARCHITECTURE + 2 in extraRecs).
// Total Recs = 18.
export const MOCK_DECISION_DATA: DecisionMockData = {
  stats: {
    health: {
      score: 82,
      recommendations: 18,
      highPriority: 5,
      architectureRisks: 7,
      technicalDebt: 34,
      potentialSavings: 21,
    },
    debt: MOCK_TECHNICAL_DEBT,
  },
  recommendations: MOCK_DECISION_RECOMMENDATIONS,
  matrixPoints: MOCK_IMPACT_EFFORT_POINTS,
  history: MOCK_DECISION_HISTORY,
};
