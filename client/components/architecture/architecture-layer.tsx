"use client";

import { Handle, Position } from "@xyflow/react";
import { ArchitectureLayer } from "@/types/architecture-ui";

interface ArchitectureLayerNodeProps {
  data: {
    layer: ArchitectureLayer;
    isSelected: boolean;
  };
}

export function ArchitectureLayerNode({ data }: ArchitectureLayerNodeProps) {
  const { layer, isSelected } = data;
  
  // Choose border color based on layer id for visual hierarchy
  let borderColor = "border-[#1E293B]";
  const headerBg = "bg-[#0F1726]";
  
  if (isSelected) {
    borderColor = "border-[#3B82F6] shadow-[0_0_15px_rgba(59,130,246,0.1)]";
  } else if (layer.id === "presentation") {
    borderColor = "border-[#1E293B] hover:border-[#3B82F6]/50";
  } else if (layer.id === "application") {
    borderColor = "border-[#1E293B] hover:border-[#8B5CF6]/50";
  } else if (layer.id === "domain") {
    borderColor = "border-[#1E293B] hover:border-[#10B981]/50";
  } else if (layer.id === "infrastructure") {
    borderColor = "border-[#1E293B] hover:border-[#F59E0B]/50";
  }

  return (
    <div className={`w-full h-full rounded-xl border-2 ${borderColor} bg-[#0F1726]/40 backdrop-blur-sm transition-all duration-200`}>
      <Handle type="target" position={Position.Top} className="opacity-0" />
      
      <div className={`px-6 py-4 rounded-t-xl border-b ${isSelected ? 'border-[#3B82F6]' : 'border-[#1E293B]'} flex items-center justify-between${headerBg}`}>
        <div>
          <h2 className={`text-lg font-bold tracking-wide uppercase ${isSelected ? 'text-[#3B82F6]' : 'text-[#F8FAFC]'}`}>
            {layer.name}
          </h2>
          <p className="text-sm text-[#94A3B8] mt-1">{layer.description}</p>
        </div>
        <div className="flex gap-4 text-xs font-medium text-[#64748B]">
          <div className="flex flex-col items-end">
            <span>Components</span>
            <span className="text-[#F8FAFC]">{layer.components.length}</span>
          </div>
        </div>
      </div>
      
      {/* Children components render here inside the group */}
      
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
}
