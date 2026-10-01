"use client";

import { ArchitectureStats } from "@/types/architecture-ui";
import { Boxes, Layers, Package, Link, AlertTriangle, ShieldAlert } from "lucide-react";

interface ArchitectureOverviewProps {
  stats: ArchitectureStats;
  criticalViolations: number;
}

export function ArchitectureOverviewMetrics({ stats, criticalViolations }: ArchitectureOverviewProps) {
  const metrics = [
    { label: "Components", value: stats.components, icon: Boxes, color: "text-[#3B82F6]" },
    { label: "Services", value: stats.services, icon: Layers, color: "text-[#8B5CF6]" },
    { label: "Modules", value: stats.modules, icon: Package, color: "text-[#10B981]" },
    { label: "External Deps", value: stats.externalDependencies, icon: Link, color: "text-[#94A3B8]" },
    { label: "Violations", value: stats.violations, icon: AlertTriangle, color: "text-[#F59E0B]" },
    { label: "Critical", value: criticalViolations, icon: ShieldAlert, color: "text-[#EF4444]" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div key={metric.label} className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-3 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold truncate">{metric.label}</span>
              <Icon className={`h-4 w-4 ${metric.color}`} />
            </div>
            <span className="text-xl font-mono font-semibold text-[#F8FAFC]">{metric.value}</span>
          </div>
        );
      })}
    </div>
  );
}
