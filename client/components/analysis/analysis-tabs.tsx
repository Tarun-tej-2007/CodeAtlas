"use client";

import { ShieldAlert, GitMerge, FileCode, History } from "lucide-react";

export type AnalysisTabType = "issues" | "complexity" | "code" | "history";

interface AnalysisTabsProps {
  activeTab: AnalysisTabType;
  onTabChange: (tab: AnalysisTabType) => void;
  issueCount?: number;
}

export function AnalysisTabs({ activeTab, onTabChange, issueCount }: AnalysisTabsProps) {
  const tabs = [
    { id: "issues", label: "Issues", icon: ShieldAlert, badge: issueCount },
    { id: "complexity", label: "Complexity", icon: GitMerge, badge: undefined },
    { id: "code", label: "Code View", icon: FileCode, badge: undefined },
    { id: "history", label: "History", icon: History, badge: undefined },
  ] as const;

  return (
    <div className="flex items-center gap-1 border-b border-[#1E293B] bg-[#0F1726] px-2 pt-2">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;
        
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id as AnalysisTabType)}
            className={`group flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              isActive
                ? "border-[#3B82F6] text-[#F8FAFC]"
                : "border-transparent text-[#94A3B8] hover:text-[#CBD5E1] hover:border-[#1E293B]"
            }`}
          >
            <Icon className={`h-4 w-4 ${isActive ? "text-[#3B82F6]" : "text-[#64748B] group-hover:text-[#94A3B8]"}`} />
            {tab.label}
            {tab.badge !== undefined && tab.badge > 0 && (
              <span className={`ml-1.5 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${
                isActive ? "bg-[#3B82F6]/10 text-[#3B82F6]" : "bg-[#1E293B] text-[#94A3B8]"
              }`}>
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
