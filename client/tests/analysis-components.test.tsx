import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { AnalysisHeader } from "@/components/analysis/analysis-header";
import { AnalysisMetricsGrid } from "@/components/analysis/analysis-metrics-grid";
import { AnalysisStatus } from "@/components/analysis/analysis-status";
import { FileTreeExplorer } from "@/components/analysis/file-tree-explorer";
import { AnalysisTabs } from "@/components/analysis/analysis-tabs";
import { IssuesPanel } from "@/components/analysis/issues-panel";
import { IssueDetailPanel } from "@/components/analysis/issue-detail-panel";
import { ComplexityPanel } from "@/components/analysis/complexity-panel";
import { CodeViewPanel } from "@/components/analysis/code-view-panel";
import { AnalysisHistory } from "@/components/analysis/analysis-history";
import { AnalysisSkeleton } from "@/components/analysis/analysis-skeleton";

import {
  MOCK_ANALYSIS_METRICS,
  MOCK_ANALYSIS_ISSUES,
  MOCK_FILE_TREE,
  MOCK_COMPLEXITY_DATA,
  MOCK_ANALYSIS_HISTORY,
  MOCK_FILE_CONTENTS,
} from "@/lib/mock-data/analysis";

describe("Analysis Components", () => {
  it("renders AnalysisHeader correctly", () => {
    const onRun = vi.fn();
    render(<AnalysisHeader status="idle" onRunAnalysis={onRun} lastAnalysisTimestamp="12 minutes ago" />);
    
    expect(screen.getByText("Repository Analysis")).toBeInTheDocument();
    expect(screen.getByText("12 minutes ago")).toBeInTheDocument();
    
    const runBtn = screen.getByText("Run Analysis");
    fireEvent.click(runBtn);
    expect(onRun).toHaveBeenCalled();
  });

  it("renders AnalysisMetricsGrid correctly", () => {
    render(<AnalysisMetricsGrid metrics={MOCK_ANALYSIS_METRICS} />);
    // Format numbers could have commas, e.g., 48,291
    expect(screen.getByText("48,291")).toBeInTheDocument();
    expect(screen.getByText("347")).toBeInTheDocument();
  });

  it("renders AnalysisStatus correctly when running", () => {
    render(<AnalysisStatus status="running" currentStageIndex={3} />);
    expect(screen.getByText("Analysis Progress")).toBeInTheDocument();
    expect(screen.getByText("Repository Discovery")).toBeInTheDocument();
    expect(screen.getByText("Semantic Analysis")).toBeInTheDocument();
  });

  it("renders FileTreeExplorer and supports interaction", () => {
    const onSelect = vi.fn();
    render(<FileTreeExplorer tree={MOCK_FILE_TREE} onFileSelect={onSelect} selectedFileId={null} />);
    
    expect(screen.getByText("src")).toBeInTheDocument();
    expect(screen.getByText("app")).toBeInTheDocument();
    expect(screen.getByText("project-service.ts")).toBeInTheDocument();

    fireEvent.click(screen.getByText("project-service.ts"));
    expect(onSelect).toHaveBeenCalled();
  });

  it("renders AnalysisTabs correctly", () => {
    const onChange = vi.fn();
    render(<AnalysisTabs activeTab="issues" onTabChange={onChange} issueCount={5} />);
    
    expect(screen.getByText("Issues")).toBeInTheDocument();
    expect(screen.getByText("Complexity")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Complexity"));
    expect(onChange).toHaveBeenCalledWith("complexity");
  });

  it("renders IssuesPanel and supports filtering", () => {
    const onSelect = vi.fn();
    render(<IssuesPanel issues={MOCK_ANALYSIS_ISSUES} selectedIssueId={null} onIssueSelect={onSelect} />);
    
    expect(screen.getByText("Controller directly accesses repository")).toBeInTheDocument();
    
    // Select an issue
    fireEvent.click(screen.getByText("Controller directly accesses repository"));
    expect(onSelect).toHaveBeenCalledWith(MOCK_ANALYSIS_ISSUES[0]);
    
    // Search filter
    const searchInput = screen.getByPlaceholderText("Search issues by title or file...");
    fireEvent.change(searchInput, { target: { value: "Controller directly" } });
    expect(screen.getByText("Controller directly accesses repository")).toBeInTheDocument();
  });

  it("renders IssueDetailPanel correctly", () => {
    const onClose = vi.fn();
    const onViewCode = vi.fn();
    render(
      <IssueDetailPanel 
        issue={MOCK_ANALYSIS_ISSUES[0]} 
        onClose={onClose} 
        onViewInCode={onViewCode} 
      />
    );
    
    expect(screen.getByText("Issue Details")).toBeInTheDocument();
    expect(screen.getByText("Controller directly accesses repository")).toBeInTheDocument();
    expect(screen.getByText("ARCH-001")).toBeInTheDocument();

    fireEvent.click(screen.getByText("View in Code"));
    expect(onViewCode).toHaveBeenCalled();
  });

  it("renders ComplexityPanel correctly", () => {
    render(<ComplexityPanel data={MOCK_COMPLEXITY_DATA} />);
    expect(screen.getByText("Avg Complexity")).toBeInTheDocument();
    expect(screen.getByText("analysis-service.ts")).toBeInTheDocument();
  });

  it("renders CodeViewPanel correctly", () => {
    render(
      <CodeViewPanel 
        filePath="src/api/projects/controller.ts" 
        code={MOCK_FILE_CONTENTS["src/api/projects/controller.ts"]}
        highlightLine={42}
      />
    );
    
    expect(screen.getByText("src/api/projects/controller.ts")).toBeInTheDocument();
    // Using string matching since code viewer splits lines and applies syntax highlighting HTML
    const lineElements = screen.getAllByText("42");
    expect(lineElements.length).toBeGreaterThan(0);
  });

  it("renders AnalysisHistory correctly", () => {
    render(<AnalysisHistory history={MOCK_ANALYSIS_HISTORY} />);
    expect(screen.getByText("Oct 01, 2026")).toBeInTheDocument();
    expect(screen.getByText("42.8s")).toBeInTheDocument();
  });

  it("renders AnalysisSkeleton correctly", () => {
    render(<AnalysisSkeleton />);
    expect(screen.getByTestId("analysis-skeleton")).toBeInTheDocument();
  });
});
