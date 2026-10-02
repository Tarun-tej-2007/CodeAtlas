import {
  DependencyGraphData,
  DependencyGraphStats,
  DependencyIssue,
  DependencyNode,
  DependencyEdge,
  DependencyRelationship
} from "@/types/dependency-graph-ui";

const nodes: DependencyNode[] = [
  // Presentation (8)
  { id: "DashboardPage", label: "DashboardPage", path: "src/app/dashboard/page.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 3, issueCount: 0 },
  { id: "ProjectsPage", label: "ProjectsPage", path: "src/app/projects/page.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 4, issueCount: 0 },
  { id: "AnalysisPage", label: "AnalysisPage", path: "src/app/analysis/page.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 5, issueCount: 0 },
  { id: "ArchitecturePage", label: "ArchitecturePage", path: "src/app/architecture/page.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 4, issueCount: 0 },
  { id: "GovernancePage", label: "GovernancePage", path: "src/app/governance/page.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 2, issueCount: 0 },
  { id: "ReportsPage", label: "ReportsPage", path: "src/app/reports/page.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 3, issueCount: 0 },
  { id: "LoginPage", label: "LoginPage", path: "src/app/auth/login.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 2, issueCount: 0 },
  { id: "HeaderNav", label: "HeaderNav", path: "src/components/layout/header.tsx", type: "React Component", layer: "presentation", language: "tsx", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 2, issueCount: 0 },
  
  // Application (Highly Coupled node: ProjectService) (8)
  { id: "ProjectService", label: "ProjectService", path: "src/services/project-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Medium", complexity: 18, issueCount: 2 },
  { id: "AnalysisService", label: "AnalysisService", path: "src/services/analysis-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "High", complexity: 12, issueCount: 1 },
  { id: "ArchitectureService", label: "ArchitectureService", path: "src/services/architecture-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "High", complexity: 14, issueCount: 1 },
  { id: "GovernanceService", label: "GovernanceService", path: "src/services/governance-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Medium", complexity: 9, issueCount: 0 },
  { id: "AuthService", label: "AuthService", path: "src/services/auth-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 5, issueCount: 0 },
  { id: "ReportService", label: "ReportService", path: "src/services/report-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 4, issueCount: 0 },
  { id: "NotificationService", label: "NotificationService", path: "src/services/notification-service.ts", type: "Service", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 6, issueCount: 0 },
  { id: "ScannerController", label: "ScannerController", path: "src/services/scanner-controller.ts", type: "Controller", layer: "application", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Medium", complexity: 8, issueCount: 0 },
  
  // Domain (7)
  { id: "Project", label: "Project", path: "src/domain/project.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 1, issueCount: 0 },
  { id: "Analysis", label: "Analysis", path: "src/domain/analysis.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 1, issueCount: 0 },
  { id: "Architecture", label: "Architecture", path: "src/domain/architecture.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 2, issueCount: 0 },
  { id: "GovernancePolicy", label: "GovernancePolicy", path: "src/domain/policy.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 3, issueCount: 0 },
  { id: "User", label: "User", path: "src/domain/user.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 1, issueCount: 0 },
  { id: "Report", label: "Report", path: "src/domain/report.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 1, issueCount: 0 },
  { id: "Notification", label: "Notification", path: "src/domain/notification.ts", type: "Model", layer: "domain", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 1, issueCount: 0 },
  
  // Infrastructure (8)
  { id: "PostgreSQLRepository", label: "PostgreSQLRepository", path: "src/infrastructure/database.ts", type: "Repository", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 6, issueCount: 0 },
  { id: "RedisCache", label: "RedisCache", path: "src/infrastructure/redis.ts", type: "Cache", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 4, issueCount: 0 },
  { id: "RepositoryScanner", label: "RepositoryScanner", path: "src/infrastructure/scanner.ts", type: "Utility", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Medium", complexity: 12, issueCount: 0 },
  { id: "GraphBuilder", label: "GraphBuilder", path: "src/infrastructure/graph-builder.ts", type: "Utility", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 9, issueCount: 0 },
  { id: "TreeSitterParser", label: "TreeSitterParser", path: "src/infrastructure/parser.ts", type: "Utility", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 15, issueCount: 0 },
  { id: "EmailSender", label: "EmailSender", path: "src/infrastructure/email.ts", type: "Utility", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 3, issueCount: 0 },
  { id: "JWTService", label: "JWTService", path: "src/infrastructure/jwt.ts", type: "Utility", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 2, issueCount: 0 },
  { id: "Logger", label: "Logger", path: "src/infrastructure/logger.ts", type: "Utility", layer: "infrastructure", language: "ts", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 1, issueCount: 0 },
  
  // External (6)
  { id: "PostgreSQL", label: "PostgreSQL", path: "external", type: "Database", layer: "external", language: "sql", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 0, issueCount: 0 },
  { id: "Redis", label: "Redis", path: "external", type: "Database", layer: "external", language: "nosql", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 0, issueCount: 0 },
  { id: "GitHubAPI", label: "GitHub API", path: "external", type: "API", layer: "external", language: "json", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 0, issueCount: 0 },
  { id: "OpenAIAPI", label: "OpenAI API", path: "external", type: "API", layer: "external", language: "json", dependencyCount: 0, dependentCount: 0, risk: "Medium", complexity: 0, issueCount: 0 },
  { id: "SendGridAPI", label: "SendGrid API", path: "external", type: "API", layer: "external", language: "json", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 0, issueCount: 0 },
  { id: "S3Storage", label: "S3 Storage", path: "external", type: "Cloud", layer: "external", language: "api", dependencyCount: 0, dependentCount: 0, risk: "Low", complexity: 0, issueCount: 0 },
];

const edgesRaw: { source: string; target: string; relationship: DependencyRelationship; isCircular?: boolean }[] = [
  // Presentation -> Application
  { source: "DashboardPage", target: "ProjectService", relationship: "imports" },
  { source: "DashboardPage", target: "AnalysisService", relationship: "imports" },
  { source: "DashboardPage", target: "ReportService", relationship: "imports" },
  { source: "ProjectsPage", target: "ProjectService", relationship: "imports" },
  { source: "ProjectsPage", target: "AnalysisService", relationship: "imports" },
  { source: "AnalysisPage", target: "AnalysisService", relationship: "imports" },
  { source: "AnalysisPage", target: "ArchitectureService", relationship: "imports" },
  { source: "ArchitecturePage", target: "ArchitectureService", relationship: "imports" },
  { source: "GovernancePage", target: "GovernanceService", relationship: "imports" },
  { source: "ReportsPage", target: "ReportService", relationship: "imports" },
  { source: "LoginPage", target: "AuthService", relationship: "imports" },
  { source: "HeaderNav", target: "AuthService", relationship: "imports" },
  { source: "HeaderNav", target: "NotificationService", relationship: "imports" },
  
  // Application -> Application (Circular Dependency)
  { source: "ProjectService", target: "AnalysisService", relationship: "calls", isCircular: true },
  { source: "AnalysisService", target: "ArchitectureService", relationship: "calls", isCircular: true },
  { source: "ArchitectureService", target: "ProjectService", relationship: "calls", isCircular: true },
  
  // Application -> Application (Normal)
  { source: "GovernanceService", target: "ProjectService", relationship: "calls" },
  { source: "ReportService", target: "ProjectService", relationship: "calls" },
  { source: "ReportService", target: "AnalysisService", relationship: "calls" },
  { source: "ScannerController", target: "ProjectService", relationship: "calls" },
  { source: "ScannerController", target: "AnalysisService", relationship: "calls" },
  { source: "AuthService", target: "NotificationService", relationship: "calls" },
  
  // Application -> Domain
  { source: "ProjectService", target: "Project", relationship: "imports" },
  { source: "AnalysisService", target: "Analysis", relationship: "imports" },
  { source: "AnalysisService", target: "Project", relationship: "imports" },
  { source: "ArchitectureService", target: "Architecture", relationship: "imports" },
  { source: "ArchitectureService", target: "Project", relationship: "imports" },
  { source: "GovernanceService", target: "GovernancePolicy", relationship: "imports" },
  { source: "GovernanceService", target: "Project", relationship: "imports" },
  { source: "ReportService", target: "Report", relationship: "imports" },
  { source: "AuthService", target: "User", relationship: "imports" },
  { source: "NotificationService", target: "Notification", relationship: "imports" },
  
  // Application -> Infrastructure
  { source: "ProjectService", target: "PostgreSQLRepository", relationship: "uses" },
  { source: "ProjectService", target: "RedisCache", relationship: "uses" },
  { source: "ProjectService", target: "Logger", relationship: "uses" },
  { source: "AnalysisService", target: "RepositoryScanner", relationship: "uses" },
  { source: "AnalysisService", target: "PostgreSQLRepository", relationship: "uses" },
  { source: "ArchitectureService", target: "GraphBuilder", relationship: "uses" },
  { source: "ArchitectureService", target: "PostgreSQLRepository", relationship: "uses" },
  { source: "ScannerController", target: "TreeSitterParser", relationship: "uses" },
  { source: "GovernanceService", target: "PostgreSQLRepository", relationship: "uses" },
  { source: "AuthService", target: "JWTService", relationship: "uses" },
  { source: "AuthService", target: "PostgreSQLRepository", relationship: "uses" },
  { source: "NotificationService", target: "EmailSender", relationship: "uses" },
  { source: "ReportService", target: "Logger", relationship: "uses" },
  
  // Domain -> Infrastructure (Boundary Violation)
  { source: "Project", target: "PostgreSQLRepository", relationship: "imports" },
  
  // Infrastructure -> Infrastructure
  { source: "GraphBuilder", target: "TreeSitterParser", relationship: "calls" },
  { source: "RepositoryScanner", target: "TreeSitterParser", relationship: "calls" },
  { source: "PostgreSQLRepository", target: "Logger", relationship: "uses" },
  { source: "RedisCache", target: "Logger", relationship: "uses" },
  
  // Application -> External
  { source: "ScannerController", target: "GitHubAPI", relationship: "calls" },
  { source: "ArchitectureService", target: "OpenAIAPI", relationship: "calls" },
  
  // Infrastructure -> External
  { source: "PostgreSQLRepository", target: "PostgreSQL", relationship: "depends_on" },
  { source: "RedisCache", target: "Redis", relationship: "depends_on" },
  { source: "RepositoryScanner", target: "GitHubAPI", relationship: "calls" },
  { source: "EmailSender", target: "SendGridAPI", relationship: "calls" },
  { source: "ReportService", target: "S3Storage", relationship: "calls" }, // application -> external
  { source: "Logger", target: "S3Storage", relationship: "calls" },
];

const edges: DependencyEdge[] = edgesRaw.map((e, i) => ({
  id: "e" + (i + 1),
  source: e.source,
  target: e.target,
  relationship: e.relationship,
  weight: 1,
  isCircular: e.isCircular
}));

// Pre-calculate dependencies/dependents for correct metrics
nodes.forEach(n => {
  n.dependencyCount = edges.filter(e => e.source === n.id).length;
  n.dependentCount = edges.filter(e => e.target === n.id).length;
});

export const MOCK_GRAPH_DATA: DependencyGraphData = { nodes, edges };

export const MOCK_GRAPH_STATS: DependencyGraphStats = {
  totalNodes: nodes.length,
  totalEdges: edges.length,
  internalDependencies: edges.filter(e => !nodes.find(n => n.id === e.target)?.layer.includes("external")).length,
  externalDependencies: edges.filter(e => nodes.find(n => n.id === e.target)?.layer === "external").length,
  circularDependencies: 1,
  averageDependencies: Number((edges.length / nodes.length).toFixed(1)),
  highestCouplingNode: "ProjectService",
};

export const MOCK_GRAPH_ISSUES: DependencyIssue[] = [
  {
    id: "iss-1",
    type: "Circular Dependency",
    severity: "High",
    title: "Circular dependency detected",
    description: "These components form a dependency cycle that reduces architectural modularity.",
    affectedNodes: ["ProjectService", "AnalysisService", "ArchitectureService"]
  },
  {
    id: "iss-2",
    type: "High Coupling",
    severity: "Medium",
    title: "Highly coupled component",
    description: "Component has an excessive number of dependencies and dependents, making it hard to maintain.",
    affectedNodes: ["ProjectService"]
  },
  {
    id: "iss-3",
    type: "Boundary Violation",
    severity: "High",
    title: "Domain layer depends on infrastructure",
    description: "Domain entities should not directly import infrastructure components.",
    affectedNodes: ["Project", "PostgreSQLRepository"]
  }
];
