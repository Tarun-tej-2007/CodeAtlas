"use client";

import { useState } from "react";
import { AnalysisIssue, AnalysisSeverity, AnalysisIssueType } from "@/types/analysis-ui";
import { ShieldAlert, AlertTriangle, Info, Search, Filter } from "lucide-react";

interface IssuesPanelProps {
  issues: AnalysisIssue[];
  onIssueSelect: (issue: AnalysisIssue) => void;
  selectedIssueId: string | null;
}

export function IssuesPanel({ issues, onIssueSelect, selectedIssueId }: IssuesPanelProps) {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<AnalysisSeverity | "ALL">("ALL");
  const [typeFilter, setTypeFilter] = useState<AnalysisIssueType | "ALL">("ALL");

  const filteredIssues = issues.filter(issue => {
    if (severityFilter !== "ALL" && issue.severity !== severityFilter) return false;
    if (typeFilter !== "ALL" && issue.type !== typeFilter) return false;
    if (search && !issue.title.toLowerCase().includes(search.toLowerCase()) && !issue.filePath.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const getSeverityIcon = (severity: AnalysisSeverity) => {
    switch (severity) {
      case "CRITICAL": return <ShieldAlert className="h-4 w-4 text-[#EF4444]" />;
      case "HIGH": return <AlertTriangle className="h-4 w-4 text-[#F97316]" />;
      case "MEDIUM": return <AlertTriangle className="h-4 w-4 text-[#EAB308]" />;
      case "LOW": return <Info className="h-4 w-4 text-[#3B82F6]" />;
    }
  };

  const getSeverityBadge = (severity: AnalysisSeverity) => {
    switch (severity) {
      case "CRITICAL": return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
      case "HIGH": return "bg-[#F97316]/10 text-[#F97316] border-[#F97316]/20";
      case "MEDIUM": return "bg-[#EAB308]/10 text-[#EAB308] border-[#EAB308]/20";
      case "LOW": return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20";
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0F1726]">
      {/* Filters Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 p-4 border-b border-[#1E293B] bg-[#0F1726]">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#64748B]" />
          <input
            type="text"
            placeholder="Search issues by title or file..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md py-2 pl-9 pr-3 text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:ring-1 focus:ring-[#3B82F6]"
          />
        </div>
        
        <div className="flex gap-3">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-[#64748B]" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as AnalysisSeverity | "ALL")}
              className="bg-[#080D18] border border-[#1E293B] rounded-md py-2 px-3 text-sm text-[#CBD5E1] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] appearance-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
          
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as AnalysisIssueType | "ALL")}
            className="bg-[#080D18] border border-[#1E293B] rounded-md py-2 px-3 text-sm text-[#CBD5E1] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] appearance-none"
          >
            <option value="ALL">All Types</option>
            <option value="Architecture">Architecture</option>
            <option value="Complexity">Complexity</option>
            <option value="Security">Security</option>
            <option value="Code Smell">Code Smell</option>
            <option value="Duplication">Duplication</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-[#141E2E] sticky top-0 z-10 shadow-xs">
            <tr>
              <th className="py-3 px-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider font-mono border-b border-[#1E293B]">Severity</th>
              <th className="py-3 px-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider font-mono border-b border-[#1E293B]">Type</th>
              <th className="py-3 px-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider font-mono border-b border-[#1E293B]">Issue</th>
              <th className="py-3 px-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider font-mono border-b border-[#1E293B]">File</th>
              <th className="py-3 px-4 text-xs font-semibold text-[#94A3B8] uppercase tracking-wider font-mono border-b border-[#1E293B]">Line</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B]">
            {filteredIssues.length > 0 ? (
              filteredIssues.map((issue) => (
                <tr 
                  key={issue.id}
                  onClick={() => onIssueSelect(issue)}
                  className={`cursor-pointer transition-colors hover:bg-[#1E293B]/50 ${selectedIssueId === issue.id ? 'bg-[#1E293B]/80' : ''}`}
                >
                  <td className="py-3 px-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(issue.severity)}
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${getSeverityBadge(issue.severity)}`}>
                        {issue.severity}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-sm text-[#CBD5E1]">{issue.type}</td>
                  <td className="py-3 px-4 text-sm font-medium text-[#F8FAFC] max-w-xs truncate" title={issue.title}>
                    {issue.title}
                  </td>
                  <td className="py-3 px-4 text-sm text-[#94A3B8] font-mono max-w-[200px] truncate" title={issue.filePath}>
                    {issue.filePath}
                  </td>
                  <td className="py-3 px-4 text-sm text-[#94A3B8] font-mono whitespace-nowrap">
                    {issue.line}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="py-8 text-center text-sm text-[#64748B]">
                  No issues found matching the criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
