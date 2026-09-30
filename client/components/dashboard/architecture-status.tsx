"use client";

import { ArchitectureStatusCounts } from "@/types/dashboard";

interface ArchitectureStatusProps {
  status: ArchitectureStatusCounts;
}

export function ArchitectureStatus({ status }: ArchitectureStatusProps) {
  const totalTracked = status.healthyCount + status.warningCount + status.criticalCount;
  const healthyPct = Math.round((status.healthyCount / totalTracked) * 100);
  const warningPct = Math.round((status.warningCount / totalTracked) * 100);
  const criticalPct = 100 - healthyPct - warningPct;

  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center justify-between pb-2 border-b border-[#1E293B]">
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-[#F8FAFC]">
              Architecture Status
            </h2>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              Entity breakdown & component health
            </p>
          </div>
        </div>

        {/* Structural Counts Grid - 2x2 layout with comfortable spacing */}
        <div className="mt-3.5 grid grid-cols-2 gap-2.5">
          <div className="rounded-md border border-[#1E293B] bg-[#0B1220] p-3 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-[#94A3B8]">Components</span>
            <div className="mt-1 text-xl font-bold font-mono text-[#F8FAFC]">
              {status.components}
            </div>
          </div>

          <div className="rounded-md border border-[#1E293B] bg-[#0B1220] p-3 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-[#94A3B8]">Services</span>
            <div className="mt-1 text-xl font-bold font-mono text-[#F8FAFC]">
              {status.services}
            </div>
          </div>

          <div className="rounded-md border border-[#1E293B] bg-[#0B1220] p-3 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-[#94A3B8]">Modules</span>
            <div className="mt-1 text-xl font-bold font-mono text-[#F8FAFC]">
              {status.modules}
            </div>
          </div>

          <div className="rounded-md border border-[#1E293B] bg-[#0B1220] p-3 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-[#94A3B8]">External Deps</span>
            <div className="mt-1 text-xl font-bold font-mono text-[#F8FAFC]">
              {status.externalDependencies}
            </div>
          </div>
        </div>
      </div>

      {/* Health Distribution Meter */}
      <div className="mt-4 pt-3.5 border-t border-[#1E293B]">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-[#94A3B8] font-medium">Status Distribution</span>
          <span className="text-[#64748B] font-mono text-[11px]">{totalTracked} components</span>
        </div>

        {/* Proportional Segment Bar */}
        <div className="h-2 w-full rounded-full bg-[#1E293B] overflow-hidden flex">
          <div
            style={{ width: `${healthyPct}%` }}
            className="bg-[#22C55E] h-full transition-all"
            title={`Healthy: ${status.healthyCount} (${healthyPct}%)`}
          />
          <div
            style={{ width: `${warningPct}%` }}
            className="bg-[#F59E0B] h-full transition-all"
            title={`Warning: ${status.warningCount} (${warningPct}%)`}
          />
          <div
            style={{ width: `${criticalPct}%` }}
            className="bg-[#EF4444] h-full transition-all"
            title={`Critical: ${status.criticalCount} (${criticalPct}%)`}
          />
        </div>

        {/* Legend */}
        <div className="mt-2.5 flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#22C55E]" />
            <span className="text-[#94A3B8] text-[11px]">Healthy</span>
            <span className="font-mono text-[#F8FAFC] font-semibold text-[11px]">{status.healthyCount}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#F59E0B]" />
            <span className="text-[#94A3B8] text-[11px]">Warning</span>
            <span className="font-mono text-[#F8FAFC] font-semibold text-[11px]">{status.warningCount}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#EF4444]" />
            <span className="text-[#94A3B8] text-[11px]">Critical</span>
            <span className="font-mono text-[#F8FAFC] font-semibold text-[11px]">{status.criticalCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
