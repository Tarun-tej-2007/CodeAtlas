export type ReportType = 
  | "REPOSITORY_ANALYSIS" 
  | "ARCHITECTURE" 
  | "DEPENDENCY" 
  | "GOVERNANCE" 
  | "EVOLUTION" 
  | "DECISION" 
  | "AI_ARCHITECTURE" 
  | "COMPREHENSIVE"
  | "SECURITY_BASELINE"
  | "TECHNICAL_DEBT"
  | "CODE_QUALITY"
  | "PERFORMANCE_ANALYSIS"
  | "EXECUTIVE_SUMMARY";

export type ReportStatus = "READY" | "GENERATING" | "COMPLETED" | "FAILED" | "SCHEDULED";
export type ReportFormat = "PDF" | "HTML" | "JSON";
export type ReportSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export interface ReportMetric {
  label: string;
  value: string | number;
  trend?: "UP" | "DOWN" | "FLAT";
}

export interface ReportFinding {
  id: string;
  title: string;
  severity: ReportSeverity;
  description: string;
  component: string;
}

export interface ReportSection {
  id: string;
  title: string;
  content: string;
  findings?: ReportFinding[];
  metrics?: ReportMetric[];
}

export interface Report {
  id: string;
  title: string;
  type: ReportType;
  status: ReportStatus;
  score: number;
  format: ReportFormat;
  generatedAt: string;
  duration?: string;
  coverage: number;
  summary: string;
  sections: ReportSection[];
  recommendations: string[];
  affectedComponents: string[];
  availableFormats: ReportFormat[];
  findingsCount: number;
}

export interface ReportSummary {
  title: string;
  score: number;
  summary: string;
  keyObservations: string[];
}

export interface ReportGenerationOptions {
  scope: string;
  includeFindings: boolean;
  includeRecommendations: boolean;
  includeArchitectureDiagram: boolean;
  includeGovernanceSummary: boolean;
  includeTechnicalDebt: boolean;
}

export interface ReportGenerationState {
  status: ReportStatus;
  step: string;
  progress: number;
}

export interface ReportFilterState {
  search: string;
  type: ReportType | "ALL";
  status: ReportStatus | "ALL";
  format: ReportFormat | "ALL";
  dateRange: "ALL" | "TODAY" | "LAST_7_DAYS" | "LAST_30_DAYS";
}

export interface ReportStats {
  total: number;
  completed: number;
  inProgress: number;
  scheduled: number;
  latestScore: number;
  coverage: number;
}

export interface ReportHistoryEntry {
  id: string;
  date: string;
  reportTitle: string;
  score: number;
  findings: number;
  status: ReportStatus;
}

export interface ReportActivity {
  id: string;
  date: string;
  event: string;
  reportTitle: string;
  status: ReportStatus;
}
