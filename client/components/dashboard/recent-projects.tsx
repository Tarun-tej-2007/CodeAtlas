"use client";

import Link from "next/link";
import { FolderGit2, ArrowUpRight, ExternalLink } from "lucide-react";
import { ProjectResponse } from "@/types/project";
import { getHealthStatus } from "@/lib/utils";

interface RecentProjectsProps {
  projects: ProjectResponse[];
}

const BASELINE_FALLBACK_PROJECTS: Array<
  ProjectResponse & { mockScore: number; displayTime: string }
> = [
  {
    id: "proj-1",
    owner_id: "u1",
    name: "CodeAtlas",
    slug: "codeatlas",
    description: "AI software architecture intelligence platform",
    visibility: "private",
    created_at: "2026-09-04T00:00:00.000Z",
    updated_at: "2026-09-04T12:00:00.000Z",
    mockScore: 92,
    displayTime: "12m ago",
  },
  {
    id: "proj-2",
    owner_id: "u1",
    name: "SatQuery",
    slug: "satquery",
    description: "Distributed telemetry querying service",
    visibility: "private",
    created_at: "2026-09-04T00:00:00.000Z",
    updated_at: "2026-09-04T11:00:00.000Z",
    mockScore: 86,
    displayTime: "1h ago",
  },
  {
    id: "proj-3",
    owner_id: "u1",
    name: "Agridata Copilot",
    slug: "agridata-copilot",
    description: "Agricultural sensor data aggregation",
    visibility: "internal",
    created_at: "2026-09-04T00:00:00.000Z",
    updated_at: "2026-09-04T09:00:00.000Z",
    mockScore: 78,
    displayTime: "3h ago",
  },
];

export function RecentProjects({ projects }: RecentProjectsProps) {
  const displayItems =
    projects.length > 0
      ? projects.map((p, idx) => ({
          ...p,
          mockScore: idx === 0 ? 92 : idx === 1 ? 86 : 78,
          displayTime: "Recently",
        }))
      : BASELINE_FALLBACK_PROJECTS;

  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs">
      <div className="flex items-center justify-between pb-2.5 border-b border-[#1E293B]">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-[#F8FAFC]">
            Recent Projects
          </h2>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            Architecture status across tracked repositories
          </p>
        </div>

        <Link
          href="/projects"
          className="inline-flex items-center gap-1 text-xs font-medium text-[#3B82F6] hover:text-[#2563EB] transition-colors"
        >
          <span>View all</span>
          <ArrowUpRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* Table Container */}
      <div className="mt-1.5 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-[#1E293B] text-[11px] font-mono text-[#64748B]">
              <th className="py-2 font-medium">Project</th>
              <th className="py-2 font-medium">Architecture Health</th>
              <th className="py-2 font-medium">Last Analysis</th>
              <th className="py-2 font-medium">Status</th>
              <th className="py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B]">
            {displayItems.map((project) => {
              const score = project.mockScore;
              const statusInfo = getHealthStatus(score);

              return (
                <tr
                  key={project.id}
                  className="group hover:bg-[#141E2E]/50 transition-colors"
                >
                  <td className="py-2.5 font-medium text-[#F8FAFC]">
                    <div className="flex items-center gap-2">
                      <FolderGit2 className="h-4 w-4 text-[#64748B] group-hover:text-[#3B82F6] transition-colors shrink-0" />
                      <span className="font-mono text-xs">{project.name}</span>
                    </div>
                  </td>

                  <td className="py-2.5 font-mono font-medium">
                    <div className="flex items-center gap-2">
                      <span className="text-[#F8FAFC]">{score}</span>
                      <div className="h-1.5 w-16 rounded-full bg-[#1E293B] overflow-hidden hidden sm:block">
                        <div
                          style={{ width: `${score}%` }}
                          className={`h-full ${
                            score >= 80
                              ? "bg-[#22C55E]"
                              : score >= 60
                              ? "bg-[#F59E0B]"
                              : "bg-[#EF4444]"
                          }`}
                        />
                      </div>
                    </div>
                  </td>

                  <td className="py-2.5 font-mono text-[#94A3B8]">
                    {project.displayTime}
                  </td>

                  <td className="py-2.5">
                    <span
                      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium ${statusInfo.bgClass} ${statusInfo.borderClass} ${statusInfo.colorClass}`}
                    >
                      {statusInfo.label}
                    </span>
                  </td>

                  <td className="py-2.5 text-right">
                    <Link
                      href={`/projects/${project.id}`}
                      className="inline-flex items-center gap-1 text-[11px] text-[#64748B] hover:text-[#3B82F6] transition-colors"
                    >
                      <span>Explore</span>
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
