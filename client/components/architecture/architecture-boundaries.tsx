"use client";

import { ArchitectureBoundary } from "@/types/architecture-ui";
import { CheckCircle2, XCircle } from "lucide-react";

interface ArchitectureBoundariesProps {
  boundaries: ArchitectureBoundary[];
}

export function ArchitectureBoundaries({ boundaries }: ArchitectureBoundariesProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Architecture Boundaries</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-2">
        {boundaries.map((boundary) => (
          <div 
            key={boundary.id} 
            className={`p-3 rounded-md border flex items-center justify-between ${
              boundary.allowed 
                ? "bg-[#141E2E] border-[#1E293B]" 
                : "bg-[#EF4444]/5 border-[#EF4444]/20"
            }`}
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium text-[#E2E8F0]">{boundary.sourceLayer}</span>
                <span className="text-[#64748B]">→</span>
                <span className="text-sm font-medium text-[#E2E8F0]">{boundary.targetLayer}</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-[#94A3B8]">
                <span>{boundary.dependencyCount} deps</span>
                {boundary.violationCount > 0 && (
                  <span className="text-[#EF4444]">{boundary.violationCount} violations</span>
                )}
              </div>
            </div>
            
            <div className="shrink-0 ml-4">
              {boundary.allowed ? (
                <div className="flex items-center gap-1.5 text-[#22C55E]">
                  <CheckCircle2 className="h-4 w-4" />
                  <span className="text-xs font-medium">Allowed</span>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 text-[#EF4444]">
                  <XCircle className="h-4 w-4" />
                  <span className="text-xs font-medium">Violation</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
