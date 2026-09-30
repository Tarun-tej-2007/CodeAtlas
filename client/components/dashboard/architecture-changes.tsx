"use client";

import { GitCommit, PlusCircle, Edit3, Camera, FolderPlus, Clock } from "lucide-react";
import { ArchitectureChangeItem, ChangeType } from "@/types/dashboard";

interface ArchitectureChangesProps {
  changes: ArchitectureChangeItem[];
}

function getChangeIcon(type: ChangeType) {
  switch (type) {
    case "Dependency added":
      return { icon: PlusCircle, color: "text-[#22D3EE]" };
    case "Component modified":
      return { icon: Edit3, color: "text-[#3B82F6]" };
    case "Architecture snapshot created":
      return { icon: Camera, color: "text-[#22C55E]" };
    case "New module detected":
      return { icon: FolderPlus, color: "text-[#F59E0B]" };
    default:
      return { icon: GitCommit, color: "text-[#94A3B8]" };
  }
}

export function ArchitectureChanges({ changes }: ArchitectureChangesProps) {
  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs">
      <div className="flex items-center justify-between pb-2.5 border-b border-[#1E293B]">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-[#F8FAFC]">
            Recent Architecture Changes
          </h2>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            Chronological technical activity log
          </p>
        </div>
      </div>

      <div className="divide-y divide-[#1E293B]">
        {changes.map((change) => {
          const { icon: Icon, color } = getChangeIcon(change.type);
          return (
            <div
              key={change.id}
              className="py-3 first:pt-3.5 last:pb-0 flex items-center justify-between gap-3 group"
            >
              <div className="flex items-start gap-3 min-w-0">
                <div className={`mt-0.5 shrink-0 ${color}`}>
                  <Icon className="h-4 w-4" />
                </div>

                <div className="min-w-0">
                  <div className="text-xs font-medium text-[#F8FAFC]">
                    {change.type}
                  </div>
                  <div className="text-xs font-mono text-[#94A3B8] mt-0.5 truncate">
                    {change.identifier}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1 text-[11px] font-mono text-[#64748B] shrink-0">
                <Clock className="h-3 w-3" />
                <span>{change.timestamp}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
