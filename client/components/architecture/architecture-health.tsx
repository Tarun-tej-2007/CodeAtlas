"use client";

import { ArchitectureHealthBreakdown, ArchitectureOverview } from "@/types/architecture-ui";

interface ArchitectureHealthProps {
  breakdown: ArchitectureHealthBreakdown;
  overview: ArchitectureOverview;
}

export function ArchitectureHealth({ breakdown, overview }: ArchitectureHealthProps) {
  const metrics = [
    { label: "Boundary Compliance", value: breakdown.boundaryCompliance },
    { label: "Dependency Health", value: breakdown.dependencyHealth },
    { label: "Modularity", value: breakdown.modularity },
    { label: "Coupling", value: breakdown.coupling },
    { label: "Architecture Drift", value: breakdown.architectureDrift },
  ];

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <div className="mb-6 flex justify-between items-start">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Health Breakdown</h3>
        <div className="text-right">
          <span className="text-2xl font-semibold text-[#F8FAFC]">{overview.healthScore} <span className="text-sm text-[#64748B]">/ 100</span></span>
        </div>
      </div>
      
      <div className="space-y-4 flex-1">
        {metrics.map((m) => (
          <div key={m.label}>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-[#94A3B8] font-medium">{m.label}</span>
              <span className="text-[#F8FAFC]">{m.value}%</span>
            </div>
            <div className="w-full bg-[#1E293B] rounded-full h-1.5">
              <div 
                className={`h-1.5 rounded-full ${m.value >= 90 ? 'bg-[#22C55E]' : m.value >= 80 ? 'bg-[#3B82F6]' : m.value >= 70 ? 'bg-[#F59E0B]' : 'bg-[#EF4444]'}`} 
                style={{ width: `${m.value}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
