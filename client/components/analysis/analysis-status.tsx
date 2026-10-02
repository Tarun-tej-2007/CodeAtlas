"use client";

import { Check, Circle, Loader2 } from "lucide-react";

interface AnalysisStatusProps {
  status: "idle" | "running" | "completed";
  currentStageIndex: number;
}

const STAGES = [
  "Repository Discovery",
  "File Scanning",
  "Parsing",
  "Semantic Analysis",
  "Dependency Analysis",
  "Architecture Analysis",
  "Governance",
  "AI Review"
];

export function AnalysisStatus({ status, currentStageIndex }: AnalysisStatusProps) {
  if (status === "idle") return null;

  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-5 shadow-xs mb-6">
      <h3 className="text-sm font-semibold text-[#F8FAFC] mb-4">Analysis Progress</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STAGES.map((stage, index) => {
          let stageStatus: "pending" | "running" | "completed" = "pending";
          
          if (status === "completed") {
            stageStatus = "completed";
          } else if (status === "running") {
            if (index < currentStageIndex) stageStatus = "completed";
            else if (index === currentStageIndex) stageStatus = "running";
            else stageStatus = "pending";
          }

          return (
            <div key={stage} className="flex items-center gap-3">
              {stageStatus === "completed" && (
                <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[#22C55E]/10 text-[#22C55E]">
                  <Check className="h-3.5 w-3.5" />
                </div>
              )}
              {stageStatus === "running" && (
                <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[#3B82F6]/10 text-[#3B82F6]">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                </div>
              )}
              {stageStatus === "pending" && (
                <div className="flex h-5 w-5 items-center justify-center rounded-full text-[#334155]">
                  <Circle className="h-3.5 w-3.5" />
                </div>
              )}
              <span className={`text-xs font-medium ${
                stageStatus === "completed" ? "text-[#CBD5E1]" :
                stageStatus === "running" ? "text-[#3B82F6]" : "text-[#64748B]"
              }`}>
                {stage}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
