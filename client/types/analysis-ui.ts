export interface AnalysisMetrics {
  totalFiles: number;
  linesOfCode: number;
  technicalDebtRatio: number;
  issues: number;
  codeSmells: number;
  duplicatedLines: number;
  testCoverage: number;
}

export type AnalysisSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type AnalysisIssueType = "Architecture" | "Complexity" | "Security" | "Code Smell" | "Duplication";

export interface AnalysisIssue {
  id: string;
  severity: AnalysisSeverity;
  type: AnalysisIssueType;
  title: string;
  description: string;
  filePath: string;
  line: number;
  column?: number;
  rule: string;
  status: "Open" | "Resolved" | "Ignored";
  expected?: string;
  detected?: string;
}

export interface FileNode {
  id: string;
  name: string;
  type: "file" | "directory";
  path: string;
  children?: FileNode[];
  language?: string;
  issueCount?: number;
}

export interface ComplexityDataPoint {
  label: string;
  value: number;
}

export interface AnalysisHistoryEntry {
  id: string;
  timestamp: string;
  duration: string; 
  filesAnalyzed: number;
  issuesFound: number;
  status: "Completed" | "Failed" | "Cancelled";
}
