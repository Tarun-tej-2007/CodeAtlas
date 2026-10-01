"use client";

import { ArchitectureHistoryEntry } from "@/types/architecture-ui";

interface ArchitectureHistoryProps {
  history: ArchitectureHistoryEntry[];
}

export function ArchitectureHistory({ history }: ArchitectureHistoryProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Architecture Evolution</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-3">
        {history.map((entry, idx) => (
          <div key={entry.id} className="relative pl-4">
            {/* Timeline line */}
            {idx !== history.length - 1 && (
              <div className="absolute left-1.5 top-5 bottom-[-16px] w-px bg-[#1E293B]"></div>
            )}
            
            {/* Timeline dot */}
            <div className={`absolute left-0 top-1.5 w-3 h-3 rounded-full border-2 border-[#0F1726] ${
              entry.status === 'Healthy' ? 'bg-[#22C55E]' : 'bg-[#F59E0B]'
            }`}></div>
            
            <div className="bg-[#141E2E] border border-[#1E293B] rounded p-2 text-sm cursor-pointer hover:border-[#334155] transition-colors">
              <div className="flex justify-between items-center mb-1">
                <span className="font-semibold text-[#E2E8F0]">{entry.timestamp}</span>
                <span className={`font-semibold ${entry.healthScore >= 80 ? 'text-[#22C55E]' : 'text-[#F59E0B]'}`}>
                  {entry.healthScore}
                </span>
              </div>
              <div className="flex gap-3 text-xs text-[#94A3B8]">
                <span>{entry.componentCount} components</span>
                <span>{entry.violationCount} violations</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
