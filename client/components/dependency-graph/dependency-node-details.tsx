"use client";

import { DependencyGraphData } from "@/types/dependency-graph-ui";
import { X, Layers, FileCode } from "lucide-react";

interface DependencyNodeDetailsProps {
  nodeId: string;
  data: DependencyGraphData;
  onClose: () => void;
}

export function DependencyNodeDetails({ nodeId, data, onClose }: DependencyNodeDetailsProps) {
  const node = data.nodes.find(n => n.id === nodeId);
  
  if (!node) return null;

  const dependencies = data.edges.filter(e => e.source === nodeId).map(e => ({ edge: e, node: data.nodes.find(n => n.id === e.target)! }));
  const dependents = data.edges.filter(e => e.target === nodeId).map(e => ({ edge: e, node: data.nodes.find(n => n.id === e.source)! }));

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Critical": return "text-[#EF4444]";
      case "High": return "text-[#F97316]";
      case "Medium": return "text-[#EAB308]";
      case "Low": return "text-[#3B82F6]";
      default: return "text-[#94A3B8]";
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0F1726] border-l border-[#1E293B] w-full max-w-xs shrink-0 overflow-y-auto">
      <div className="flex items-center justify-between p-4 border-b border-[#1E293B] sticky top-0 bg-[#0F1726] z-10">
        <h3 className="text-sm font-semibold text-[#F8FAFC]">Node Details</h3>
        <button onClick={onClose} className="text-[#64748B] hover:text-[#CBD5E1] transition-colors rounded-sm hover:bg-[#1E293B] p-1">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-5 flex flex-col gap-6">
        <div>
          <div className="flex items-start gap-3 mb-2">
            <div className="mt-0.5 shrink-0"><Layers className="h-5 w-5 text-[#3B82F6]" /></div>
            <h2 className="text-base font-medium text-[#F8FAFC] leading-snug">{node.label}</h2>
          </div>
          
          <div className="flex flex-wrap gap-2 mt-3">
            <span className="text-[11px] font-medium px-2 py-0.5 rounded border border-[#1E293B] bg-[#141E2E] text-[#CBD5E1]">
              {node.type}
            </span>
            <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded border border-[#1E293B] bg-[#141E2E] text-[#94A3B8]">
              {node.layer}
            </span>
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded border border-[#1E293B] bg-[#141E2E] ${getRiskColor(node.risk)}`}>
              {node.risk} Risk
            </span>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Location</h4>
          <div className="flex items-center gap-2 bg-[#080D18] rounded-md border border-[#1E293B] p-2.5">
            <FileCode className="h-4 w-4 text-[#64748B]" />
            <p className="text-xs font-mono text-[#CBD5E1] truncate" title={node.path}>{node.path}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-[#080D18] border border-[#1E293B] rounded-md p-3 flex flex-col items-center justify-center">
            <span className="text-xl font-mono font-semibold text-[#F8FAFC]">{node.dependencyCount}</span>
            <span className="text-[10px] uppercase font-semibold text-[#64748B] tracking-wider mt-1">Dependencies</span>
          </div>
          <div className="bg-[#080D18] border border-[#1E293B] rounded-md p-3 flex flex-col items-center justify-center">
            <span className="text-xl font-mono font-semibold text-[#F8FAFC]">{node.dependentCount}</span>
            <span className="text-[10px] uppercase font-semibold text-[#64748B] tracking-wider mt-1">Dependents</span>
          </div>
          <div className="bg-[#080D18] border border-[#1E293B] rounded-md p-3 flex flex-col items-center justify-center">
            <span className="text-xl font-mono font-semibold text-[#F8FAFC]">{node.complexity}</span>
            <span className="text-[10px] uppercase font-semibold text-[#64748B] tracking-wider mt-1">Complexity</span>
          </div>
          <div className="bg-[#080D18] border border-[#1E293B] rounded-md p-3 flex flex-col items-center justify-center">
            <span className={`text-xl font-mono font-semibold ${node.issueCount > 0 ? "text-[#EF4444]" : "text-[#22C55E]"}`}>{node.issueCount}</span>
            <span className="text-[10px] uppercase font-semibold text-[#64748B] tracking-wider mt-1">Issues</span>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Dependencies</h4>
          {dependencies.length > 0 ? (
            <div className="space-y-2">
              {dependencies.map(({ node: depNode, edge }) => (
                <div key={edge.id} className="flex items-center justify-between bg-[#141E2E] rounded border border-[#1E293B] p-2">
                  <span className="text-xs font-medium text-[#CBD5E1] truncate">{depNode.label}</span>
                  <span className="text-[10px] font-mono text-[#64748B] shrink-0">{edge.relationship}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#64748B]">No dependencies.</p>
          )}
        </div>

        <div>
          <h4 className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider mb-2">Dependents</h4>
          {dependents.length > 0 ? (
            <div className="space-y-2">
              {dependents.map(({ node: depNode, edge }) => (
                <div key={edge.id} className="flex items-center justify-between bg-[#141E2E] rounded border border-[#1E293B] p-2">
                  <span className="text-xs font-medium text-[#CBD5E1] truncate">{depNode.label}</span>
                  <span className="text-[10px] font-mono text-[#64748B] shrink-0">{edge.relationship}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#64748B]">No dependents.</p>
          )}
        </div>

      </div>
    </div>
  );
}
