"use client";

import { AnalysisHistoryEntry } from "@/types/analysis-ui";
import { CheckCircle2, Clock, XCircle } from "lucide-react";
import { formatNumber } from "@/lib/utils";

interface AnalysisHistoryProps {
  history: AnalysisHistoryEntry[];
}

export function AnalysisHistory({ history }: AnalysisHistoryProps) {
  return (
    <div className="flex flex-col h-full bg-[#0F1726] overflow-y-auto custom-scrollbar p-6">
      <h3 className="text-sm font-semibold text-[#F8FAFC] mb-4">Analysis History</h3>
      
      <div className="space-y-4">
        {history.map((entry) => (
          <div key={entry.id} className="rounded-lg border border-[#1E293B] bg-[#141E2E] p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-colors hover:bg-[#1E293B]/50 cursor-pointer">
            <div className="flex items-start sm:items-center gap-4">
              <div className="mt-1 sm:mt-0 shrink-0">
                {entry.status === "Completed" && <CheckCircle2 className="h-5 w-5 text-[#22C55E]" />}
                {entry.status === "Failed" && <XCircle className="h-5 w-5 text-[#EF4444]" />}
                {entry.status === "Cancelled" && <XCircle className="h-5 w-5 text-[#94A3B8]" />}
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-[#F8FAFC]">{entry.timestamp}</h4>
                <div className="flex items-center gap-4 mt-1 text-xs text-[#94A3B8]">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {entry.duration}
                  </span>
                  <span>{formatNumber(entry.filesAnalyzed)} files</span>
                  <span className={entry.issuesFound > 0 ? "text-[#EAB308]" : ""}>{entry.issuesFound} issues</span>
                </div>
              </div>
            </div>
            
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${
              entry.status === "Completed" ? "bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20" :
              entry.status === "Failed" ? "bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20" :
              "bg-[#94A3B8]/10 text-[#CBD5E1] border border-[#94A3B8]/20"
            }`}>
              {entry.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
