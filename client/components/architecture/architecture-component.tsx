"use client";

import { Handle, Position } from "@xyflow/react";
import { ArchitectureComponent } from "@/types/architecture-ui";
import { AlertTriangle, ShieldAlert } from "lucide-react";

interface ArchitectureComponentNodeProps {
  data: {
    component: ArchitectureComponent;
    isSelected: boolean;
    isDimmed: boolean;
  };
}

export function ArchitectureComponentNode({ data }: ArchitectureComponentNodeProps) {
  const { component, isSelected, isDimmed } = data;
  
  let borderColor = "border-[#1E293B]";
  let bgColor = "bg-[#141E2E]";
  
  if (isSelected) {
    borderColor = "border-[#3B82F6] ring-2 ring-[#3B82F6]/20";
    bgColor = "bg-[#1E293B]";
  } else if (component.risk === "Critical") {
    borderColor = "border-[#EF4444]";
  } else if (component.risk === "High") {
    borderColor = "border-[#F97316]";
  } else if (component.risk === "Medium") {
    borderColor = "border-[#F59E0B]";
  }

  return (
    <div 
      className={`w-[160px] h-[60px] rounded-md border ${borderColor} ${bgColor} p-2 flex flex-col justify-center transition-all duration-200 cursor-pointer shadow-sm
        ${isDimmed ? "opacity-20 grayscale" : "opacity-100 hover:border-[#475569]"}
      `}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 bg-[#475569] border-none" />
      
      <div className="flex items-start justify-between gap-1 w-full overflow-hidden">
        <div className="flex flex-col overflow-hidden">
          <span className="text-xs font-semibold text-[#E2E8F0] truncate">{component.name}</span>
          <span className="text-[10px] text-[#94A3B8] truncate mt-0.5">{component.type}</span>
        </div>
        
        {component.issueCount > 0 && (
          <div className="flex shrink-0">
            {component.risk === "Critical" ? (
              <ShieldAlert className="h-3 w-3 text-[#EF4444]" />
            ) : (
              <AlertTriangle className="h-3 w-3 text-[#F59E0B]" />
            )}
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-[#475569] border-none" />
    </div>
  );
}
