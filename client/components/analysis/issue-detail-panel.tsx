"use client";

import { AnalysisIssue } from "@/types/analysis-ui";
import { X, Code2, ShieldAlert, AlertTriangle, Info } from "lucide-react";

interface IssueDetailPanelProps {
  issue: AnalysisIssue;
  onClose: () => void;
  onViewInCode: () => void;
}

export function IssueDetailPanel({ issue, onClose, onViewInCode }: IssueDetailPanelProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return <ShieldAlert className="h-5 w-5 text-[#EF4444]" />;
      case "HIGH": return <AlertTriangle className="h-5 w-5 text-[#F97316]" />;
      case "MEDIUM": return <AlertTriangle className="h-5 w-5 text-[#EAB308]" />;
      case "LOW": return <Info className="h-5 w-5 text-[#3B82F6]" />;
      default: return <Info className="h-5 w-5 text-[#94A3B8]" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "text-[#EF4444]";
      case "HIGH": return "text-[#F97316]";
      case "MEDIUM": return "text-[#EAB308]";
      case "LOW": return "text-[#3B82F6]";
      default: return "text-[#94A3B8]";
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0F1726] border-l border-[#1E293B] w-full max-w-sm shrink-0 overflow-y-auto">
      <div className="flex items-center justify-between p-4 border-b border-[#1E293B] sticky top-0 bg-[#0F1726] z-10">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Issue Details</h3>
        <button onClick={onClose} className="text-[#64748B] hover:text-[#CBD5E1] transition-colors rounded-sm hover:bg-[#1E293B] p-1">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-5 flex flex-col gap-6">
        {/* Header section */}
        <div>
          <div className="flex items-start gap-3 mb-2">
            <div className="mt-0.5 shrink-0">{getSeverityIcon(issue.severity)}</div>
            <h2 className="text-base font-medium text-[#F8FAFC] leading-snug">{issue.title}</h2>
          </div>
          
          <div className="flex flex-wrap gap-2 mt-3 pl-8">
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded border border-current bg-current/10 ${getSeverityColor(issue.severity)}`}>
              {issue.severity}
            </span>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded border border-[#1E293B] bg-[#141E2E] text-[#CBD5E1]">
              {issue.type}
            </span>
            <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded border border-[#1E293B] bg-[#141E2E] text-[#94A3B8]">
              {issue.rule}
            </span>
          </div>
        </div>

        <div className="h-px bg-[#1E293B] w-full" />

        {/* Location Section */}
        <div>
          <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Location</h4>
          <div className="bg-[#080D18] rounded-md border border-[#1E293B] p-3">
            <p className="text-sm font-mono text-[#CBD5E1] break-all mb-1">{issue.filePath}</p>
            <p className="text-xs font-mono text-[#64748B]">Line {issue.line}{issue.column ? ` : Col ${issue.column}` : ''}</p>
          </div>
          <button 
            onClick={onViewInCode}
            className="mt-3 flex items-center gap-1.5 text-sm font-medium text-[#3B82F6] hover:text-[#60A5FA] transition-colors"
          >
            <Code2 className="h-4 w-4" />
            View in Code
          </button>
        </div>

        {/* Description Section */}
        <div>
          <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Description</h4>
          <p className="text-sm text-[#CBD5E1] leading-relaxed">
            {issue.description}
          </p>
        </div>

        {/* Architecture details if available */}
        {(issue.detected || issue.expected) && (
          <div className="space-y-4">
            {issue.detected && (
              <div>
                <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Detected Relationship</h4>
                <div className="bg-[#EF4444]/5 border border-[#EF4444]/20 rounded-md p-3">
                  <pre className="text-xs font-mono text-[#EF4444] whitespace-pre-wrap">{issue.detected}</pre>
                </div>
              </div>
            )}
            
            {issue.expected && (
              <div>
                <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Expected Architecture</h4>
                <div className="bg-[#22C55E]/5 border border-[#22C55E]/20 rounded-md p-3">
                  <pre className="text-xs font-mono text-[#22C55E] whitespace-pre-wrap">{issue.expected}</pre>
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
