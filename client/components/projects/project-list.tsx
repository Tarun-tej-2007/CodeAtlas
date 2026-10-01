import { ProjectResponse } from "@/types/project";
import { ProjectCard } from "./project-card";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface ProjectListProps {
  projects: ProjectResponse[];
  onEdit: (project: ProjectResponse) => void;
  onDelete: (project: ProjectResponse) => void;
  page: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  onPageChange: (page: number) => void;
}

export function ProjectList({
  projects,
  onEdit,
  onDelete,
  page,
  totalPages,
  hasNext,
  hasPrevious,
  onPageChange,
}: ProjectListProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4.5">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-[#1E293B] pt-4 mt-2">
          <div className="text-xs text-[#94A3B8]">
            Page <span className="font-medium text-[#F8FAFC]">{page}</span> of{" "}
            <span className="font-medium text-[#F8FAFC]">{totalPages}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => onPageChange(page - 1)}
              disabled={!hasPrevious}
              className="flex items-center gap-1 rounded-md border border-[#1E293B] bg-[#0F1726] px-3 py-1.5 text-xs font-medium text-[#CBD5E1] hover:bg-[#141E2E] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </button>
            <button
              type="button"
              onClick={() => onPageChange(page + 1)}
              disabled={!hasNext}
              className="flex items-center gap-1 rounded-md border border-[#1E293B] bg-[#0F1726] px-3 py-1.5 text-xs font-medium text-[#CBD5E1] hover:bg-[#141E2E] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Next</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
