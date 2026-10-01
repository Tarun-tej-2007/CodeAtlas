"use client";

import { DependencyIssue } from "@/types/dependency-graph-ui";
import { AlertTriangle, ShieldAlert } from "lucide-react";

interface DependencyIssuesPanelProps {
  issues: DependencyIssue[];
  onIssueSelect: (nodeId: string) => void;
}

export function DependencyIssuesPanel({ issues, onIssueSelect }: DependencyIssuesPanelProps) {
  return (
    <div className="flex flex-col h-full bg-[#0F1726]">
      <div className="p-3 border-b border-[#1E293B] bg-[#141E2E] flex justify-between items-center sticky top-0">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Architecture Issues</h3>
        <div className="flex gap-1.5">
          <span className="text-[10px] bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20 px-1.5 py-0.5 rounded font-bold">1 HIGH</span>
          <span className="text-[10px] bg-[#EAB308]/10 text-[#EAB308] border border-[#EAB308]/20 px-1.5 py-0.5 rounded font-bold">1 MEDIUM</span>
        </div>
      </div>
      
      <div className="overflow-y-auto custom-scrollbar flex-1 p-2 space-y-2">
        {issues.map((issue) => (
          <div 
            key={issue.id} 
            className="p-2.5 rounded border border-[#1E293B] bg-[#080D18] hover:border-[#475569] transition-colors cursor-pointer group"
            onClick={() => onIssueSelect(issue.affectedNodes[0])}
          >
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-1.5">
                {issue.severity === "High" ? (
                  <ShieldAlert className="h-3.5 w-3.5 text-[#EF4444] shrink-0" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5 text-[#EAB308] shrink-0" />
                )}
                <span className="text-xs font-semibold text-[#F8FAFC]">{issue.title}</span>
              </div>
              <span className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded border ${
                issue.severity === "High" ? "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20" : "bg-[#EAB308]/10 text-[#EAB308] border-[#EAB308]/20"
              }`}>
                {issue.severity}
              </span>
            </div>
            
            <p className="text-[11px] text-[#94A3B8] leading-snug mb-2">
              {issue.description}
            </p>
            
            <div className="flex flex-wrap gap-1">
              {issue.affectedNodes.map(node => (
                <span key={node} className="text-[10px] font-mono text-[#CBD5E1] bg-[#141E2E] px-1.5 py-0.5 rounded border border-[#1E293B]">
                  {node}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
