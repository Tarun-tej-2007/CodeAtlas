"use client";

import { ComplexityDataPoint } from "@/types/analysis-ui";
import { GitMerge, AlertTriangle } from "lucide-react";

interface ComplexityPanelProps {
  data: ComplexityDataPoint[];
}

export function ComplexityPanel({ data }: ComplexityPanelProps) {
  const average = (data.reduce((acc, curr) => acc + curr.value, 0) / data.length).toFixed(1);
  const max = Math.max(...data.map(d => d.value));
  const overThreshold = data.filter(d => d.value > 15).length;
  
  // Maximum for bar chart scaling (make it slightly bigger than max to give headroom)
  const chartMax = Math.max(20, max + 2);

  return (
    <div className="flex flex-col h-full bg-[#0F1726] overflow-y-auto custom-scrollbar p-6">
      
      {/* Top metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="rounded-lg border border-[#1E293B] bg-[#141E2E] p-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <GitMerge className="h-4 w-4" />
            <span className="text-xs font-medium uppercase tracking-wider">Avg Complexity</span>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{average}</span>
          </div>
        </div>

        <div className="rounded-lg border border-[#1E293B] bg-[#141E2E] p-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <GitMerge className="h-4 w-4" />
            <span className="text-xs font-medium uppercase tracking-wider">Max Complexity</span>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{max}</span>
          </div>
        </div>

        <div className="rounded-lg border border-[#1E293B] bg-[#141E2E] p-4 flex flex-col justify-between">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <AlertTriangle className="h-4 w-4 text-[#EAB308]" />
            <span className="text-xs font-medium uppercase tracking-wider">Functions {'>'} 15</span>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{overThreshold}</span>
          </div>
        </div>
      </div>

      <div className="flex-1">
        <h3 className="text-sm font-semibold text-[#F8FAFC] mb-4">Cyclomatic Complexity by File</h3>
        
        <div className="space-y-4">
          {data.map((point) => {
            const width = `${(point.value / chartMax) * 100}%`;
            const isHigh = point.value > 15;
            const isWarning = point.value > 10 && point.value <= 15;
            
            return (
              <div key={point.label} className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#CBD5E1] font-mono">{point.label}</span>
                  <span className={`font-mono font-medium ${isHigh ? 'text-[#EF4444]' : isWarning ? 'text-[#EAB308]' : 'text-[#22C55E]'}`}>
                    {point.value}
                  </span>
                </div>
                <div className="w-full bg-[#1E293B] rounded-sm h-3 overflow-hidden flex">
                  <div 
                    className={`h-full rounded-sm ${isHigh ? 'bg-[#EF4444]' : isWarning ? 'bg-[#EAB308]' : 'bg-[#3B82F6]'}`}
                    style={{ width }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
