"use client";

import { ArchitectureRisk } from "@/types/architecture-ui";
import { AlertTriangle, ShieldAlert } from "lucide-react";

interface ArchitectureRisksProps {
  risks: ArchitectureRisk[];
}

export function ArchitectureRisks({ risks }: ArchitectureRisksProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Architecture Risks</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-2">
        {risks.map((risk) => (
          <div key={risk.id} className="bg-[#141E2E] border border-[#1E293B] rounded p-3 hover:border-[#334155] cursor-pointer transition-colors">
            <div className="flex items-start gap-2 mb-1">
              <div className="mt-0.5 shrink-0">
                {risk.severity === "Critical" ? (
                  <ShieldAlert className="h-4 w-4 text-[#EF4444]" />
                ) : risk.severity === "High" ? (
                  <AlertTriangle className="h-4 w-4 text-[#F97316]" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />
                )}
              </div>
              <h4 className="text-sm font-medium text-[#E2E8F0]">{risk.title}</h4>
            </div>
            <p className="text-xs text-[#94A3B8] ml-6">{risk.description}</p>
          </div>
        ))}
        {risks.length === 0 && (
          <div className="text-sm text-[#64748B] text-center py-4">No active risks.</div>
        )}
      </div>
    </div>
  );
}
