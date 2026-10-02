import { FolderGit2, Plus } from "lucide-react";

interface ProjectsEmptyProps {
  onCreateProject: () => void;
}

export function ProjectsEmpty({ onCreateProject }: ProjectsEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-[#1E293B] bg-[#0F1726] p-12 text-center my-8">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#3B82F6]/10 text-[#3B82F6] mb-4">
        <FolderGit2 className="h-6 w-6" />
      </div>
      <h2 className="text-base font-semibold text-[#F8FAFC]">
        No projects yet
      </h2>
      <p className="mt-1 max-w-md text-xs text-[#94A3B8] leading-relaxed">
        Create your first project to start analyzing your software architecture.
      </p>
      <div className="mt-6">
        <button
          type="button"
          onClick={onCreateProject}
          className="inline-flex items-center gap-2 rounded-md bg-[#3B82F6] px-3.5 py-1.5 text-xs font-medium text-white hover:bg-[#2563EB] transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>Create Project</span>
        </button>
      </div>
    </div>
  );
}

export function ProjectsNoResults({ onClearFilters }: { onClearFilters: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-[#1E293B] bg-[#0F1726] p-12 text-center my-8">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#141E2E] text-[#64748B] mb-4 border border-[#1E293B]">
        <FolderGit2 className="h-6 w-6" />
      </div>
      <h2 className="text-base font-semibold text-[#F8FAFC]">
        No matching projects
      </h2>
      <p className="mt-1 max-w-md text-xs text-[#94A3B8] leading-relaxed">
        Try changing your search or filters.
      </p>
      <div className="mt-6">
        <button
          type="button"
          onClick={onClearFilters}
          className="inline-flex items-center gap-2 rounded-md border border-[#1E293B] bg-[#141E2E] px-3.5 py-1.5 text-xs font-medium text-[#F8FAFC] hover:bg-[#1E293B] transition-colors"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
