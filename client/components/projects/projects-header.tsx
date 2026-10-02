import { Plus } from "lucide-react";

interface ProjectsHeaderProps {
  onCreateProject: () => void;
}

export function ProjectsHeader({ onCreateProject }: ProjectsHeaderProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-4.5 border-b border-[#1E293B]">
      <div>
        <h1 className="text-xl sm:text-2xl font-semibold tracking-tight text-[#F8FAFC]">
          Projects
        </h1>
        <p className="text-xs sm:text-sm text-[#94A3B8] mt-0.5">
          Manage your software projects and architecture analysis.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2.5">
        <button
          type="button"
          onClick={onCreateProject}
          className="flex items-center gap-2 rounded-md bg-[#3B82F6] hover:bg-[#2563EB] px-3.5 py-1.5 text-xs font-medium text-white transition-colors shadow-xs"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>New Project</span>
        </button>
      </div>
    </div>
  );
}
