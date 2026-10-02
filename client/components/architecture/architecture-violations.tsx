"use client";

import { ArchitectureViolation } from "@/types/architecture-ui";
import { ShieldAlert, AlertTriangle } from "lucide-react";

interface ArchitectureViolationsProps {
  violations: ArchitectureViolation[];
  onSelect: (id: string) => void;
  selectedId: string | null;
}

export function ArchitectureViolations({ violations, onSelect, selectedId }: ArchitectureViolationsProps) {
  const criticalCount = violations.filter(v => v.severity === "Critical").length;
  const highCount = violations.filter(v => v.severity === "High").length;
  const mediumCount = violations.filter(v => v.severity === "Medium").length;

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Architecture Violations</h3>
        <div className="flex gap-3 text-xs font-medium">
          <span className="text-[#EF4444]">{criticalCount} Critical</span>
          <span className="text-[#F97316]">{highCount} High</span>
          <span className="text-[#F59E0B]">{mediumCount} Medium</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-2">
        {violations.map((v) => (
          <div 
            key={v.id} 
            onClick={() => onSelect(v.id)}
            className={`p-3 rounded-md border cursor-pointer transition-colors ${
              selectedId === v.id
                ? "bg-[#1E293B] border-[#475569]"
                : "bg-[#141E2E] border-[#1E293B] hover:border-[#334155]"
            }`}
          >
            <div className="flex items-start gap-2">
              <div className="mt-0.5 shrink-0">
                {v.severity === "Critical" ? (
                  <ShieldAlert className="h-4 w-4 text-[#EF4444]" />
                ) : v.severity === "High" ? (
                  <AlertTriangle className="h-4 w-4 text-[#F97316]" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <h4 className="text-sm font-medium text-[#E2E8F0] truncate">{v.title}</h4>
                  <span className="shrink-0 text-[10px] text-[#64748B] uppercase tracking-wider font-semibold border border-[#334155] rounded px-1">{v.rule}</span>
                </div>
                <p className="text-xs text-[#94A3B8] truncate">{v.description}</p>
              </div>
            </div>
          </div>
        ))}
        {violations.length === 0 && (
          <div className="text-sm text-[#64748B] text-center py-4">No violations found.</div>
        )}
      </div>
    </div>
  );
}
