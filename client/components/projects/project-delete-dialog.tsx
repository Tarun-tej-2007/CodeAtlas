import { Loader2 } from "lucide-react";
import { useState } from "react";
import { useDeleteProject } from "@/lib/query/use-projects";
import { ProjectResponse } from "@/types/project";

interface ProjectDeleteDialogProps {
  project: ProjectResponse;
  onClose: () => void;
}

export function ProjectDeleteDialog({ project, onClose }: ProjectDeleteDialogProps) {
  const deleteMutation = useDeleteProject();
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setError(null);
    try {
      await deleteMutation.mutateAsync(project.id);
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete project.";
      setError(msg);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-[#0B1220]/80 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      
      <div className="relative w-full max-w-sm rounded-lg border border-[#1E293B] bg-[#0F1726] p-6 shadow-xl z-10" role="dialog" aria-labelledby="delete-project-title">
        <h2 id="delete-project-title" className="text-lg font-semibold text-[#F8FAFC] mb-2">
          Delete Project?
        </h2>
        
        <div className="text-sm text-[#94A3B8] mb-6 space-y-2 leading-relaxed">
          <p>You are about to permanently delete:</p>
          <p className="font-mono font-medium text-[#F8FAFC] break-all border-l-2 border-[#EF4444] pl-2 py-0.5">
            {project.name}
          </p>
          <p>This action cannot be undone.</p>
        </div>
        
        {error && (
          <div className="mb-4 rounded-md bg-[#EF4444]/10 border border-[#EF4444]/20 p-3 text-xs text-[#EF4444]">
            {error}
          </div>
        )}
        
        <div className="flex flex-col sm:flex-row justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="w-full sm:w-auto rounded-md border border-[#1E293B] bg-transparent px-4 py-2 text-xs font-medium text-[#CBD5E1] hover:bg-[#1E293B] hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-md bg-[#EF4444] px-4 py-2 text-xs font-medium text-white hover:bg-[#DC2626] transition-colors shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {deleteMutation.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            <span>{deleteMutation.isPending ? "Deleting..." : "Delete Project"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
