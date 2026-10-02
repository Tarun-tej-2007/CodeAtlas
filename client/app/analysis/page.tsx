"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { AnalysisHeader } from "@/components/analysis/analysis-header";
import { AnalysisMetricsGrid } from "@/components/analysis/analysis-metrics-grid";
import { AnalysisStatus } from "@/components/analysis/analysis-status";
import { FileTreeExplorer } from "@/components/analysis/file-tree-explorer";
import { AnalysisTabs, AnalysisTabType } from "@/components/analysis/analysis-tabs";
import { IssuesPanel } from "@/components/analysis/issues-panel";
import { IssueDetailPanel } from "@/components/analysis/issue-detail-panel";
import { ComplexityPanel } from "@/components/analysis/complexity-panel";
import { CodeViewPanel } from "@/components/analysis/code-view-panel";
import { AnalysisHistory } from "@/components/analysis/analysis-history";

import {
  MOCK_ANALYSIS_METRICS,
  MOCK_ANALYSIS_ISSUES,
  MOCK_FILE_TREE,
  MOCK_COMPLEXITY_DATA,
  MOCK_ANALYSIS_HISTORY,
  MOCK_FILE_CONTENTS,
} from "@/lib/mock-data/analysis";
import { FileNode, AnalysisIssue } from "@/types/analysis-ui";

export default function AnalysisPage() {
  const [status, setStatus] = useState<"idle" | "running" | "completed">("idle");
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [lastAnalysis, setLastAnalysis] = useState("12 minutes ago");
  
  const [activeTab, setActiveTab] = useState<AnalysisTabType>("issues");
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [selectedIssue, setSelectedIssue] = useState<AnalysisIssue | null>(null);

  // Mock Analysis Run Logic
  const handleRunAnalysis = () => {
    setStatus("running");
    setCurrentStageIndex(0);
    setActiveTab("issues");
    setSelectedIssue(null);
  };

  useEffect(() => {
    if (status === "running") {
      const interval = setInterval(() => {
        setCurrentStageIndex((prev) => {
          if (prev >= 7) {
            clearInterval(interval);
            setStatus("completed");
            setLastAnalysis("Just now");
            return prev;
          }
          return prev + 1;
        });
      }, 500); // Progress every 500ms
      return () => clearInterval(interval);
    }
  }, [status]);

  const handleIssueSelect = (issue: AnalysisIssue) => {
    setSelectedIssue(issue);
  };

  const handleViewInCode = () => {
    if (selectedIssue) {
      setActiveTab("code");
      // Find the file node matching the issue to select it in the tree
      // (Simplified search for mock data)
      const findNode = (nodes: FileNode[], path: string): FileNode | null => {
        for (const node of nodes) {
          if (node.path === path) return node;
          if (node.children) {
            const found = findNode(node.children, path);
            if (found) return found;
          }
        }
        return null;
      };
      
      const file = findNode(MOCK_FILE_TREE, selectedIssue.filePath);
      if (file) setSelectedFile(file);
    }
  };

  return (
    <AppShell breadcrumb="Repository Analysis">
      <div className="flex flex-col h-full space-y-6 overflow-hidden">
        
        <AnalysisHeader 
          status={status} 
          onRunAnalysis={handleRunAnalysis} 
          lastAnalysisTimestamp={lastAnalysis} 
        />
        
        <AnalysisMetricsGrid metrics={MOCK_ANALYSIS_METRICS} />
        
        {status !== "idle" && (
          <AnalysisStatus status={status} currentStageIndex={currentStageIndex} />
        )}
        
        <div className="flex-1 flex gap-4 min-h-[500px] overflow-hidden">
          {/* Left File Explorer */}
          <div className="w-64 shrink-0 hidden md:block">
            <FileTreeExplorer 
              tree={MOCK_FILE_TREE} 
              selectedFileId={selectedFile?.id || null} 
              onFileSelect={setSelectedFile} 
            />
          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#0F1726] border border-[#1E293B] rounded-lg shadow-xs overflow-hidden relative">
            <AnalysisTabs 
              activeTab={activeTab} 
              onTabChange={setActiveTab} 
              issueCount={MOCK_ANALYSIS_ISSUES.length} 
            />
            
            <div className="flex-1 overflow-hidden flex relative">
              <div className="flex-1 overflow-hidden">
                {activeTab === "issues" && (
                  <IssuesPanel 
                    issues={MOCK_ANALYSIS_ISSUES} 
                    selectedIssueId={selectedIssue?.id || null}
                    onIssueSelect={handleIssueSelect}
                  />
                )}
                
                {activeTab === "complexity" && (
                  <ComplexityPanel data={MOCK_COMPLEXITY_DATA} />
                )}
                
                {activeTab === "code" && (
                  <CodeViewPanel 
                    filePath={selectedFile?.path || (selectedIssue?.filePath) || ""} 
                    code={selectedFile?.path ? MOCK_FILE_CONTENTS[selectedFile.path] || "" : (selectedIssue?.filePath ? MOCK_FILE_CONTENTS[selectedIssue.filePath] || "" : "")} 
                    language={selectedFile?.language || "typescript"}
                    highlightLine={activeTab === "code" && selectedIssue && (selectedIssue.filePath === selectedFile?.path) ? selectedIssue.line : undefined}
                  />
                )}
                
                {activeTab === "history" && (
                  <AnalysisHistory history={MOCK_ANALYSIS_HISTORY} />
                )}
              </div>
              
              {/* Issue Details Drawer */}
              {selectedIssue && activeTab === "issues" && (
                <div className="absolute top-0 right-0 h-full bottom-0 z-20 shadow-[-4px_0_15px_rgba(0,0,0,0.5)]">
                  <IssueDetailPanel 
                    issue={selectedIssue} 
                    onClose={() => setSelectedIssue(null)} 
                    onViewInCode={handleViewInCode}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
