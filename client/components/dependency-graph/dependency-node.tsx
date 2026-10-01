"use client";

import { Handle, Position } from "@xyflow/react";
import { DependencyNode } from "@/types/dependency-graph-ui";
import { memo } from "react";
import { Layers, AlertTriangle, ShieldAlert } from "lucide-react";

interface DependencyNodeProps {
  data: DependencyNode & {
    isHighlighted: boolean;
    isDimmed: boolean;
    isSelected: boolean;
  };
}

export const DependencyGraphNode = memo(({ data }: DependencyNodeProps) => {
  const isHighRisk = data.risk === "High" || data.risk === "Critical";
  const hasIssues = data.issueCount > 0;

  const getLayerColor = (layer: string) => {
    switch (layer) {
      case "presentation": return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30";
      case "application": return "bg-[#8B5CF6]/10 text-[#8B5CF6] border-[#8B5CF6]/30";
      case "domain": return "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30";
      case "infrastructure": return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30";
      case "external": return "bg-[#64748B]/10 text-[#94A3B8] border-[#64748B]/30";
      default: return "bg-[#1E293B] text-[#94A3B8] border-[#334155]";
    }
  };

  return (
    <div
      className={`relative min-w-[200px] rounded-md border p-3 shadow-md transition-all duration-200 ${
        data.isSelected
          ? "bg-[#141E2E] border-[#3B82F6] shadow-[0_0_15px_rgba(59,130,246,0.3)] z-20 scale-105"
          : data.isHighlighted
          ? "bg-[#141E2E] border-[#94A3B8] z-10"
          : data.isDimmed
          ? "bg-[#080D18] border-[#1E293B] opacity-40 grayscale"
          : "bg-[#0F1726] border-[#1E293B] hover:border-[#475569]"
      }`}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-[#64748B] border-none" />
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-[#64748B] border-none" />

      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 flex-1 min-w-0">
          <Layers className={`h-3.5 w-3.5 shrink-0 ${data.layer === "external" ? "text-[#64748B]" : "text-[#94A3B8]"}`} />
          <span className="text-sm font-semibold text-[#F8FAFC] truncate">{data.label}</span>
        </div>
        {hasIssues && (
          <ShieldAlert className="h-3.5 w-3.5 text-[#EF4444] shrink-0" />
        )}
      </div>

      <div className="flex items-center gap-2 mb-3">
        <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${getLayerColor(data.layer)}`}>
          {data.layer}
        </span>
        {isHighRisk && (
          <span className="flex items-center gap-1 text-[10px] font-bold text-[#F97316] bg-[#F97316]/10 px-1.5 py-0.5 rounded border border-[#F97316]/20">
            <AlertTriangle className="h-3 w-3" />
            {data.risk}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-[11px] text-[#64748B] font-mono border-t border-[#1E293B] pt-2 mt-1">
        <span>deps {data.dependencyCount}</span>
        <span className="w-1 h-1 rounded-full bg-[#1E293B]"></span>
        <span>used by {data.dependentCount}</span>
      </div>
    </div>
  );
});

DependencyGraphNode.displayName = "DependencyGraphNode";
