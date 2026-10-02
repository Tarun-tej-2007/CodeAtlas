import { ArchitectureData } from "@/types/architecture-ui";

export const MOCK_ARCHITECTURE_DATA: ArchitectureData = {
  overview: {
    healthScore: 84,
    trend: 3.2,
    componentCount: 84,
    serviceCount: 21,
    moduleCount: 63,
    externalDependencyCount: 17,
    violationCount: 7,
    criticalViolationCount: 2,
    lastAnalysis: "12 minutes ago",
  },
  layers: [
    {
      id: "presentation",
      name: "Presentation",
      description: "User interface, API routes, and controllers.",
      order: 1,
      components: [
        { id: "DashboardController", name: "DashboardController", type: "Controller", layerId: "presentation", path: "src/api/dashboard/controller.ts", description: "Handles dashboard data requests.", dependencyCount: 4, dependentCount: 0, complexity: 5, health: 90, risk: "Low", issueCount: 0 },
        { id: "ProjectController", name: "ProjectController", type: "Controller", layerId: "presentation", path: "src/api/projects/controller.ts", description: "Handles project requests.", dependencyCount: 5, dependentCount: 0, complexity: 8, health: 75, risk: "Medium", issueCount: 1 },
        { id: "AnalysisController", name: "AnalysisController", type: "Controller", layerId: "presentation", path: "src/api/analysis/controller.ts", description: "Handles analysis requests.", dependencyCount: 3, dependentCount: 0, complexity: 4, health: 95, risk: "Low", issueCount: 0 },
        { id: "ArchitectureController", name: "ArchitectureController", type: "Controller", layerId: "presentation", path: "src/api/architecture/controller.ts", description: "Handles architecture requests.", dependencyCount: 3, dependentCount: 0, complexity: 3, health: 90, risk: "Low", issueCount: 0 },
        { id: "GovernanceController", name: "GovernanceController", type: "Controller", layerId: "presentation", path: "src/api/governance/controller.ts", description: "Handles governance requests.", dependencyCount: 2, dependentCount: 0, complexity: 3, health: 100, risk: "Low", issueCount: 0 },
        { id: "APIRoutes", name: "API Routes", type: "Router", layerId: "presentation", path: "src/app/api", description: "Next.js API route definitions.", dependencyCount: 12, dependentCount: 0, complexity: 15, health: 85, risk: "Medium", issueCount: 0 },
        { id: "UIComponents", name: "UI Components", type: "View", layerId: "presentation", path: "src/components", description: "React UI components.", dependencyCount: 20, dependentCount: 0, complexity: 25, health: 88, risk: "Low", issueCount: 0 }
      ]
    },
    {
      id: "application",
      name: "Application",
      description: "Business orchestration and use-case coordination.",
      order: 2,
      components: [
        { id: "ProjectService", name: "ProjectService", type: "Service", layerId: "application", path: "src/services/project-service.ts", description: "Coordinates project lifecycle operations.", dependencyCount: 8, dependentCount: 12, complexity: 14, health: 82, risk: "High", issueCount: 2 },
        { id: "AnalysisService", name: "AnalysisService", type: "Service", layerId: "application", path: "src/services/analysis-service.ts", description: "Coordinates analysis runs.", dependencyCount: 6, dependentCount: 4, complexity: 12, health: 85, risk: "Medium", issueCount: 1 },
        { id: "ArchitectureService", name: "ArchitectureService", type: "Service", layerId: "application", path: "src/services/architecture-service.ts", description: "Analyzes system architecture.", dependencyCount: 5, dependentCount: 3, complexity: 18, health: 70, risk: "Medium", issueCount: 0 },
        { id: "GovernanceService", name: "GovernanceService", type: "Service", layerId: "application", path: "src/services/governance-service.ts", description: "Enforces policies.", dependencyCount: 4, dependentCount: 2, complexity: 8, health: 95, risk: "Low", issueCount: 0 },
        { id: "DecisionService", name: "DecisionService", type: "Service", layerId: "application", path: "src/services/decision-service.ts", description: "Manages architecture decisions.", dependencyCount: 3, dependentCount: 1, complexity: 5, health: 90, risk: "Low", issueCount: 0 }
      ]
    },
    {
      id: "domain",
      name: "Domain",
      description: "Core business logic and entities.",
      order: 3,
      components: [
        { id: "ProjectDomain", name: "Project", type: "Entity", layerId: "domain", path: "src/domain/project.ts", description: "Project entity logic.", dependencyCount: 2, dependentCount: 15, complexity: 4, health: 65, risk: "Critical", issueCount: 2 },
        { id: "AnalysisDomain", name: "Analysis", type: "Entity", layerId: "domain", path: "src/domain/analysis.ts", description: "Analysis entity logic.", dependencyCount: 0, dependentCount: 8, complexity: 3, health: 100, risk: "Low", issueCount: 0 },
        { id: "ArchitectureDomain", name: "Architecture", type: "Entity", layerId: "domain", path: "src/domain/architecture.ts", description: "Architecture entity logic.", dependencyCount: 0, dependentCount: 6, complexity: 5, health: 90, risk: "Low", issueCount: 0 },
        { id: "GovernancePolicyDomain", name: "GovernancePolicy", type: "Entity", layerId: "domain", path: "src/domain/policy.ts", description: "Policy entity logic.", dependencyCount: 0, dependentCount: 4, complexity: 2, health: 95, risk: "Low", issueCount: 0 },
        { id: "ArchitectureDecisionDomain", name: "ArchitectureDecision", type: "Entity", layerId: "domain", path: "src/domain/decision.ts", description: "Decision entity logic.", dependencyCount: 0, dependentCount: 3, complexity: 1, health: 100, risk: "Low", issueCount: 0 },
        { id: "DependencyDomain", name: "Dependency", type: "Entity", layerId: "domain", path: "src/domain/dependency.ts", description: "Dependency entity logic.", dependencyCount: 0, dependentCount: 7, complexity: 2, health: 100, risk: "Low", issueCount: 0 },
        { id: "SymbolDomain", name: "Symbol", type: "Entity", layerId: "domain", path: "src/domain/symbol.ts", description: "Code symbol entity logic.", dependencyCount: 0, dependentCount: 5, complexity: 2, health: 100, risk: "Low", issueCount: 0 }
      ]
    },
    {
      id: "infrastructure",
      name: "Infrastructure",
      description: "Database, external adapters, and technical details.",
      order: 4,
      components: [
        { id: "PostgreSQLRepository", name: "PostgreSQLRepository", type: "Repository", layerId: "infrastructure", path: "src/infrastructure/database.ts", description: "Database access.", dependencyCount: 1, dependentCount: 25, complexity: 15, health: 85, risk: "Low", issueCount: 0 },
        { id: "RedisCache", name: "RedisCache", type: "Cache", layerId: "infrastructure", path: "src/infrastructure/redis.ts", description: "Caching layer.", dependencyCount: 1, dependentCount: 10, complexity: 6, health: 95, risk: "Low", issueCount: 0 },
        { id: "RepositoryScanner", name: "RepositoryScanner", type: "Adapter", layerId: "infrastructure", path: "src/infrastructure/scanner.ts", description: "Scans code repositories.", dependencyCount: 2, dependentCount: 4, complexity: 22, health: 80, risk: "Medium", issueCount: 0 },
        { id: "TreeSitterParser", name: "TreeSitterParser", type: "Adapter", layerId: "infrastructure", path: "src/infrastructure/parser.ts", description: "Parses ASTs.", dependencyCount: 0, dependentCount: 3, complexity: 30, health: 75, risk: "Medium", issueCount: 0 },
        { id: "GraphBuilder", name: "GraphBuilder", type: "Adapter", layerId: "infrastructure", path: "src/infrastructure/graph-builder.ts", description: "Builds graphs.", dependencyCount: 1, dependentCount: 2, complexity: 18, health: 88, risk: "Low", issueCount: 0 },
        { id: "GitHubAdapter", name: "GitHubAdapter", type: "Adapter", layerId: "infrastructure", path: "src/infrastructure/github.ts", description: "GitHub API client.", dependencyCount: 1, dependentCount: 2, complexity: 10, health: 92, risk: "Low", issueCount: 0 }
      ]
    },
    {
      id: "external",
      name: "External",
      description: "Third-party systems and APIs.",
      order: 5,
      components: [
        { id: "PostgreSQL", name: "PostgreSQL", type: "Database", layerId: "external", path: "external", description: "Relational database.", dependencyCount: 0, dependentCount: 1, complexity: 0, health: 100, risk: "Low", issueCount: 0 },
        { id: "Redis", name: "Redis", type: "Database", layerId: "external", path: "external", description: "In-memory datastore.", dependencyCount: 0, dependentCount: 1, complexity: 0, health: 100, risk: "Low", issueCount: 0 },
        { id: "GitHubAPI", name: "GitHub API", type: "API", layerId: "external", path: "external", description: "Version control host.", dependencyCount: 0, dependentCount: 1, complexity: 0, health: 100, risk: "Low", issueCount: 0 },
        { id: "OpenAIAPI", name: "OpenAI API", type: "API", layerId: "external", path: "external", description: "LLM provider.", dependencyCount: 0, dependentCount: 1, complexity: 0, health: 100, risk: "Low", issueCount: 0 }
      ]
    }
  ],
  boundaries: [
    { id: "b1", sourceLayer: "Presentation", targetLayer: "Application", allowed: true, dependencyCount: 45, violationCount: 0 },
    { id: "b2", sourceLayer: "Application", targetLayer: "Domain", allowed: true, dependencyCount: 68, violationCount: 0 },
    { id: "b3", sourceLayer: "Application", targetLayer: "Infrastructure", allowed: true, dependencyCount: 32, violationCount: 0 },
    { id: "b4", sourceLayer: "Domain", targetLayer: "Infrastructure", allowed: false, dependencyCount: 4, violationCount: 2 },
    { id: "b5", sourceLayer: "Domain", targetLayer: "Presentation", allowed: false, dependencyCount: 0, violationCount: 0 },
    { id: "b6", sourceLayer: "Infrastructure", targetLayer: "Application", allowed: false, dependencyCount: 2, violationCount: 1 },
    { id: "b7", sourceLayer: "Presentation", targetLayer: "Infrastructure", allowed: false, dependencyCount: 8, violationCount: 4 }
  ],
  violations: [
    {
      id: "v1",
      severity: "Critical",
      title: "Domain layer directly accesses infrastructure",
      description: "Domain entities must be independent of technical details.",
      source: "ProjectDomain",
      target: "PostgreSQLRepository",
      sourceLayer: "Domain",
      targetLayer: "Infrastructure",
      rule: "ARCH-001",
      filePath: "src/domain/project.ts",
      line: 84
    },
    {
      id: "v2",
      severity: "Critical",
      title: "Domain layer depends on Redis Cache",
      description: "Caching should be handled by application or infrastructure layers.",
      source: "ProjectDomain",
      target: "RedisCache",
      sourceLayer: "Domain",
      targetLayer: "Infrastructure",
      rule: "ARCH-001",
      filePath: "src/domain/project.ts",
      line: 42
    },
    {
      id: "v3",
      severity: "High",
      title: "Controller directly accesses repository",
      description: "Controllers should coordinate via Application Services.",
      source: "ProjectController",
      target: "PostgreSQLRepository",
      sourceLayer: "Presentation",
      targetLayer: "Infrastructure",
      rule: "ARCH-002",
      filePath: "src/api/projects/controller.ts",
      line: 42
    },
    {
      id: "v4",
      severity: "Medium",
      title: "Service exceeds coupling threshold",
      description: "Component has too many outgoing dependencies.",
      source: "ProjectService",
      target: "Multiple",
      sourceLayer: "Application",
      targetLayer: "Multiple",
      rule: "ARCH-003",
      filePath: "src/services/project-service.ts",
      line: 1
    },
    {
      id: "v5",
      severity: "Medium",
      title: "Service exceeds coupling threshold",
      description: "Component has too many incoming dependents.",
      source: "ProjectService",
      target: "Multiple",
      sourceLayer: "Application",
      targetLayer: "Multiple",
      rule: "ARCH-004",
      filePath: "src/services/project-service.ts",
      line: 1
    },
    {
      id: "v6",
      severity: "High",
      title: "Infrastructure depends on Application",
      description: "Infrastructure should not depend inwards.",
      source: "RepositoryScanner",
      target: "AnalysisService",
      sourceLayer: "Infrastructure",
      targetLayer: "Application",
      rule: "ARCH-005",
      filePath: "src/infrastructure/scanner.ts",
      line: 112
    },
    {
      id: "v7",
      severity: "High",
      title: "Controller directly accesses repository",
      description: "Controllers should coordinate via Application Services.",
      source: "DashboardController",
      target: "PostgreSQLRepository",
      sourceLayer: "Presentation",
      targetLayer: "Infrastructure",
      rule: "ARCH-002",
      filePath: "src/api/dashboard/controller.ts",
      line: 25
    }
  ],
  risks: [
    {
      id: "r1",
      severity: "High",
      title: "High Coupling",
      description: "ProjectService has unusually high dependency count.",
      affectedComponents: ["ProjectService"]
    },
    {
      id: "r2",
      severity: "High",
      title: "Circular Dependency",
      description: "Three components form a dependency cycle.",
      affectedComponents: ["ProjectService", "AnalysisService", "ArchitectureService"]
    },
    {
      id: "r3",
      severity: "Critical",
      title: "Boundary Violation",
      description: "Domain layer accesses infrastructure directly.",
      affectedComponents: ["ProjectDomain", "PostgreSQLRepository"]
    },
    {
      id: "r4",
      severity: "Medium",
      title: "Architecture Drift",
      description: "Recent changes increased cross-layer dependencies.",
      affectedComponents: ["Presentation", "Infrastructure"]
    }
  ],
  stats: {
    components: 84,
    services: 21,
    modules: 63,
    externalDependencies: 17,
    boundaries: 7,
    violations: 7
  },
  history: [
    { id: "h1", timestamp: "Oct 01", healthScore: 84, componentCount: 84, violationCount: 7, status: "Healthy" },
    { id: "h2", timestamp: "Sep 30", healthScore: 81, componentCount: 84, violationCount: 9, status: "Warning" },
    { id: "h3", timestamp: "Sep 28", healthScore: 82, componentCount: 81, violationCount: 8, status: "Healthy" },
    { id: "h4", timestamp: "Sep 24", healthScore: 79, componentCount: 79, violationCount: 11, status: "Warning" }
  ],
  healthBreakdown: {
    boundaryCompliance: 91,
    dependencyHealth: 84,
    modularity: 82,
    coupling: 78,
    architectureDrift: 86,
    overall: 84
  }
};
