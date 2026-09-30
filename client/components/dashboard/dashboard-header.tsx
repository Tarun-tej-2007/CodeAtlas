"use client";

import { useState } from "react";
import { Play, Loader2, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { useTriggerAnalysis } from "@/lib/query/use-projects";
import { ProjectResponse } from "@/types/project";

interface DashboardHeaderProps {
  lastAnalysisTimestamp?: string;
  projects?: ProjectResponse[];
  onAnalysisTriggered?: () => void;
}

export function DashboardHeader({
  lastAnalysisTimestamp = "12m ago",
  projects = [],
  onAnalysisTriggered,
}: DashboardHeaderProps) {
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const triggerMutation = useTriggerAnalysis();

  const handleRunAnalysis = async () => {
    // Pick the first available project or selected project
    const targetProject = selectedProjectId
      ? projects.find((p) => p.id === selectedProjectId)
      : projects[0];

    if (!targetProject) {
      setStatusMessage({
        type: "error",
        text: "No active project available to analyze. Create a project first.",
      });
      setTimeout(() => setStatusMessage(null), 4000);
      return;
    }

    try {
      setStatusMessage(null);
      const res = await triggerMutation.mutateAsync({
        projectId: targetProject.id,
      });
      setStatusMessage({
        type: "success",
        text: `Analysis accepted for ${targetProject.name} (Job: ${res.job_id.slice(0, 8)})`,
      });
      onAnalysisTriggered?.();
      setTimeout(() => setStatusMessage(null), 5000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to trigger analysis";
      setStatusMessage({
        type: "error",
        text: msg,
      });
      setTimeout(() => setStatusMessage(null), 5000);
    }
  };

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-4.5 border-b border-[#1E293B]">
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold tracking-tight text-[#F8FAFC]">
          Dashboard
        </h1>
        <p className="text-xs sm:text-sm text-[#94A3B8] mt-0.5">
          Architecture intelligence across your projects.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2.5">
        {/* Status indicator popup if active */}
        {statusMessage && (
          <div
            className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium border ${
              statusMessage.type === "success"
                ? "bg-[#22C55E]/10 border-[#22C55E]/20 text-[#22C55E]"
                : "bg-[#EF4444]/10 border-[#EF4444]/20 text-[#EF4444]"
            }`}
          >
            {statusMessage.type === "success" ? (
              <CheckCircle2 className="h-3.5 w-3.5" />
            ) : (
              <AlertCircle className="h-3.5 w-3.5" />
            )}
            <span>{statusMessage.text}</span>
          </div>
        )}

        {/* Last analysis timestamp indicator */}
        <div className="flex items-center gap-1.5 rounded-md bg-[#0F1726] border border-[#1E293B] px-3 py-1.5 text-xs text-[#94A3B8]">
          <Clock className="h-3.5 w-3.5 text-[#64748B]" />
          <span>
            Last analysis:{" "}
            <span className="font-mono text-[#CBD5E1]">{lastAnalysisTimestamp}</span>
          </span>
        </div>

        {/* Project Selector dropdown if multiple projects exist */}
        {projects.length > 1 && (
          <select
            value={selectedProjectId || projects[0]?.id || ""}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="rounded-md bg-[#0F1726] border border-[#1E293B] px-2.5 py-1.5 text-xs text-[#CBD5E1] focus:border-[#3B82F6] focus:outline-hidden"
            aria-label="Select project to analyze"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id} className="bg-[#0F1726]">
                {p.name}
              </option>
            ))}
          </select>
        )}

        {/* Run analysis trigger button */}
        <button
          type="button"
          onClick={handleRunAnalysis}
          disabled={triggerMutation.isPending}
          className="flex items-center gap-2 rounded-md bg-[#3B82F6] hover:bg-[#2563EB] disabled:bg-[#3B82F6]/50 disabled:cursor-not-allowed px-3.5 py-1.5 text-xs font-medium text-white transition-colors shadow-xs"
        >
          {triggerMutation.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Play className="h-3.5 w-3.5 fill-current" />
          )}
          <span>{triggerMutation.isPending ? "Submitting..." : "Run analysis"}</span>
        </button>
      </div>
    </div>
  );
}
