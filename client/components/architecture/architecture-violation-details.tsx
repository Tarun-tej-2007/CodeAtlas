"use client";

import { ArchitectureViolation } from "@/types/architecture-ui";
import { X, ExternalLink } from "lucide-react";
import Link from "next/link";

interface ArchitectureViolationDetailsProps {
  violationId: string;
  violations: ArchitectureViolation[];
  onClose: () => void;
}

export function ArchitectureViolationDetails({ violationId, violations, onClose }: ArchitectureViolationDetailsProps) {
  const violation = violations.find(v => v.id === violationId);
  if (!violation) return null;

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case "Critical": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      case "High": return "text-[#F97316] bg-[#F97316]/10 border-[#F97316]/20";
      case "Medium": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20";
      default: return "text-[#22C55E] bg-[#22C55E]/10 border-[#22C55E]/20";
    }
  };

  return (
    <div className="w-80 h-full bg-[#0F1726] border-l border-[#1E293B] flex flex-col shadow-xl z-20">
      <div className="p-4 border-b border-[#1E293B] flex items-center justify-between sticky top-0 bg-[#0F1726]">
        <h2 className="font-semibold text-[#F8FAFC]">Violation Details</h2>
        <button onClick={onClose} className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-4 overflow-y-auto custom-scrollbar flex-1">
        <div className="mb-6">
          <div className="flex items-start justify-between gap-2 mb-2">
            <span className={`shrink-0 text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded border ${getSeverityColor(violation.severity)}`}>
              {violation.severity}
            </span>
            <span className="shrink-0 text-[10px] text-[#64748B] uppercase tracking-wider font-semibold border border-[#334155] rounded px-1.5 py-0.5">{violation.rule}</span>
          </div>
          <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">{violation.title}</h3>
          <p className="text-sm text-[#94A3B8]">{violation.description}</p>
        </div>

        <div className="mb-6 space-y-4">
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-[#141E2E] border border-[#1E293B] p-2 rounded">
              <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold block mb-1">Source</span>
              <span className="text-sm text-[#E2E8F0] break-all">{violation.source}</span>
              <span className="text-xs text-[#94A3B8] block mt-0.5">{violation.sourceLayer}</span>
            </div>
            <div className="bg-[#141E2E] border border-[#1E293B] p-2 rounded">
              <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold block mb-1">Target</span>
              <span className="text-sm text-[#E2E8F0] break-all">{violation.target}</span>
              <span className="text-xs text-[#94A3B8] block mt-0.5">{violation.targetLayer}</span>
            </div>
          </div>

          <div>
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold block mb-1">Location</span>
            <div className="bg-[#141E2E] border border-[#1E293B] p-2 rounded font-mono text-sm text-[#E2E8F0] break-all">
              {violation.filePath}:{violation.line}
            </div>
          </div>
        </div>

        <div className="mb-6 space-y-4 bg-[#EF4444]/5 border border-[#EF4444]/20 p-3 rounded text-sm">
          <div>
            <span className="font-semibold text-[#EF4444] block mb-1">Detected:</span>
            <span className="text-[#E2E8F0]">{violation.sourceLayer} → {violation.targetLayer}</span>
          </div>
        </div>

        <div className="space-y-2">
          <button className="w-full bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium py-2 rounded transition-colors flex items-center justify-center gap-2 border border-[#334155]">
            View Component
          </button>
          <Link 
            href="/graph" 
            className="w-full bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium py-2 rounded transition-colors flex items-center justify-center gap-2 border border-[#334155]"
          >
            View Dependency <ExternalLink className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
