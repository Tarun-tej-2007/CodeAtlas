import { SettingsState } from "@/types/settings-ui";

export const DEFAULT_SETTINGS: SettingsState = {
  general: {
    workspaceName: "CodeAtlas Workspace",
    workspaceDescription: "Engineering architecture intelligence workspace",
    defaultProject: "Core Services",
    defaultBranch: "main",
    repositoryRoot: "/"
  },
  analysis: {
    defaultAnalysisDepth: "STANDARD",
    automaticAnalysis: true,
    analyzeDependencies: true,
    analyzeArchitecture: true,
    analyzeSecurity: true,
    incrementalAnalysis: true,
    maximumAnalysisFiles: 10000,
    analysisTimeout: 120
  },
  architecture: {
    layerBoundaryDetection: true,
    circularDependencyDetection: true,
    architectureDriftDetection: true,
    crossLayerDependencyDetection: true,
    complexityThreshold: 15,
    dependencyThreshold: 20,
    architectureViolationSeverity: "WARNING",
    showArchitectureSuggestions: true
  },
  ai: {
    aiAssistance: true,
    provider: "OPENAI",
    architectureReview: true,
    recommendationGeneration: true,
    confidenceThreshold: 80,
    maximumContextFiles: 50,
    includeArchitectureContext: true,
    includeGovernanceContext: true,
    includeDependencyContext: true
  },
  governance: {
    policyEnforcement: "WARNING",
    automaticGovernanceEvaluation: true,
    evaluateArchitecture: true,
    evaluateDependencies: true,
    evaluateSecurity: true,
    criticalViolations: "BLOCKING",
    highViolations: "WARNING",
    requireExceptionForViolations: true,
    defaultExceptionDuration: "14 days"
  },
  notifications: {
    analysisCompleted: true,
    criticalViolations: true,
    architectureDrift: true,
    governanceChanges: false,
    aiReviewCompleted: true,
    weeklyEngineeringSummary: true,
    notificationFrequency: "Immediate"
  },
  appearance: {
    theme: "DARK",
    compactMode: true,
    animations: true,
    reduceMotion: false,
    showGridBackground: true,
    interfaceDensity: "COMPACT"
  },
  developer: {
    showDebugInformation: false,
    logLevel: "INFO",
    showPerformanceMetrics: false,
    showExperimentalFeatures: false,
    enableDevelopmentDiagnostics: false
  }
};
