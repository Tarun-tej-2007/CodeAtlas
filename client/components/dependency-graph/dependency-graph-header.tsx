"use client";

import { DependencyGraphStats } from "@/types/dependency-graph-ui";

interface DependencyGraphHeaderProps {
  stats: DependencyGraphStats;
}

export function DependencyGraphHeader({ stats }: DependencyGraphHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
      <div>
        <h1 className="text-2xl font-semibold text-[#F8FAFC]">Dependency Graph</h1>
        <p className="text-sm text-[#94A3B8] mt-1">Explore dependencies, relationships, and architecture boundaries across your codebase.</p>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex flex-col">
          <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Nodes</span>
          <span className="text-sm text-[#F8FAFC] font-mono">{stats.totalNodes}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Edges</span>
          <span className="text-sm text-[#F8FAFC] font-mono">{stats.totalEdges}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Circular</span>
          <span className={`text-sm font-mono ${stats.circularDependencies > 0 ? "text-[#EF4444]" : "text-[#22C55E]"}`}>
            {stats.circularDependencies}
          </span>
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">External</span>
          <span className="text-sm text-[#F8FAFC] font-mono">{stats.externalDependencies}</span>
        </div>
      </div>
    </div>
  );
}
