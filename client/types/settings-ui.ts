export type Theme = "LIGHT" | "DARK" | "SYSTEM";
export type AnalysisDepth = "QUICK" | "STANDARD" | "DEEP";
export type AIProvider = "OPENAI" | "LOCAL" | "DISABLED";
export type GovernanceEnforcement = "WARNING" | "BLOCKING";
export type LogLevel = "ERROR" | "WARN" | "INFO" | "DEBUG";
export type ExceptionDuration = "7 days" | "14 days" | "30 days" | "90 days";
export type NotificationFrequency = "Immediate" | "Daily" | "Weekly" | "Disabled";
export type InterfaceDensity = "COMPACT" | "COMFORTABLE";
export type SeverityLevel = "INFO" | "WARNING" | "BLOCKING";
export type ViolationSeverity = "WARNING" | "BLOCKING" | "IGNORE";

export interface GeneralSettings {
  workspaceName: string;
  workspaceDescription: string;
  defaultProject: string;
  defaultBranch: string;
  repositoryRoot: string;
}

export interface AnalysisSettings {
  defaultAnalysisDepth: AnalysisDepth;
  automaticAnalysis: boolean;
  analyzeDependencies: boolean;
  analyzeArchitecture: boolean;
  analyzeSecurity: boolean;
  incrementalAnalysis: boolean;
  maximumAnalysisFiles: number;
  analysisTimeout: number;
}

export interface ArchitectureSettings {
  layerBoundaryDetection: boolean;
  circularDependencyDetection: boolean;
  architectureDriftDetection: boolean;
  crossLayerDependencyDetection: boolean;
  complexityThreshold: number;
  dependencyThreshold: number;
  architectureViolationSeverity: SeverityLevel;
  showArchitectureSuggestions: boolean;
}

export interface AISettings {
  aiAssistance: boolean;
  provider: AIProvider;
  architectureReview: boolean;
  recommendationGeneration: boolean;
  confidenceThreshold: number;
  maximumContextFiles: number;
  includeArchitectureContext: boolean;
  includeGovernanceContext: boolean;
  includeDependencyContext: boolean;
}

export interface GovernanceSettings {
  policyEnforcement: GovernanceEnforcement;
  automaticGovernanceEvaluation: boolean;
  evaluateArchitecture: boolean;
  evaluateDependencies: boolean;
  evaluateSecurity: boolean;
  criticalViolations: GovernanceEnforcement;
  highViolations: ViolationSeverity;
  requireExceptionForViolations: boolean;
  defaultExceptionDuration: ExceptionDuration;
}

export interface NotificationSettings {
  analysisCompleted: boolean;
  criticalViolations: boolean;
  architectureDrift: boolean;
  governanceChanges: boolean;
  aiReviewCompleted: boolean;
  weeklyEngineeringSummary: boolean;
  notificationFrequency: NotificationFrequency;
}

export interface AppearanceSettings {
  theme: Theme;
  compactMode: boolean;
  animations: boolean;
  reduceMotion: boolean;
  showGridBackground: boolean;
  interfaceDensity: InterfaceDensity;
}

export interface DeveloperSettings {
  showDebugInformation: boolean;
  logLevel: LogLevel;
  showPerformanceMetrics: boolean;
  showExperimentalFeatures: boolean;
  enableDevelopmentDiagnostics: boolean;
}

export interface SettingsState {
  general: GeneralSettings;
  analysis: AnalysisSettings;
  architecture: ArchitectureSettings;
  ai: AISettings;
  governance: GovernanceSettings;
  notifications: NotificationSettings;
  appearance: AppearanceSettings;
  developer: DeveloperSettings;
}

export type SettingsSection = 
  | "General"
  | "Analysis"
  | "Architecture"
  | "AI"
  | "Governance"
  | "Notifications"
  | "Appearance"
  | "Developer";
