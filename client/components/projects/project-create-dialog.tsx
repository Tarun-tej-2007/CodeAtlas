import { X, Loader2 } from "lucide-react";
import { useState } from "react";
import { useCreateProject } from "@/lib/query/use-projects";
import { ProjectVisibility } from "@/types/project";

interface ProjectCreateDialogProps {
  onClose: () => void;
}

export function ProjectCreateDialog({ onClose }: ProjectCreateDialogProps) {
  const createMutation = useCreateProject();
  
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [visibility, setVisibility] = useState<ProjectVisibility>("private");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!name.trim()) {
      setError("Project name is required.");
      return;
    }
    
    if (name.length > 50) {
      setError("Project name must be 50 characters or fewer.");
      return;
    }
    
    try {
      await createMutation.mutateAsync({
        name: name.trim(),
        description: description.trim() || undefined,
        visibility,
      });
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create project.";
      setError(msg);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-[#0B1220]/80 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      
      <div className="relative w-full max-w-md rounded-lg border border-[#1E293B] bg-[#0F1726] p-6 shadow-xl z-10" role="dialog" aria-labelledby="create-project-title">
        <div className="flex items-center justify-between mb-5">
          <h2 id="create-project-title" className="text-lg font-semibold text-[#F8FAFC]">
            Create Project
          </h2>
          <button 
            onClick={onClose}
            className="text-[#64748B] hover:text-[#CBD5E1] transition-colors rounded p-1 hover:bg-[#1E293B]"
            aria-label="Close dialog"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {error && (
            <div className="rounded-md bg-[#EF4444]/10 border border-[#EF4444]/20 p-3 text-xs text-[#EF4444]">
              {error}
            </div>
          )}
          
          <div>
            <label htmlFor="name" className="block text-xs font-medium text-[#CBD5E1] mb-1.5">
              Project Name *
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="block w-full rounded-md border border-[#1E293B] bg-[#141E2E] py-2 px-3 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#3B82F6] focus:outline-hidden focus:ring-1 focus:ring-[#3B82F6]"
              placeholder="e.g. backend-api"
              autoFocus
            />
          </div>
          
          <div>
            <label htmlFor="description" className="block text-xs font-medium text-[#CBD5E1] mb-1.5">
              Description <span className="text-[#64748B]">(Optional)</span>
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="block w-full rounded-md border border-[#1E293B] bg-[#141E2E] py-2 px-3 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#3B82F6] focus:outline-hidden focus:ring-1 focus:ring-[#3B82F6] resize-none"
              placeholder="Briefly describe this project..."
            />
          </div>
          
          <div>
            <label htmlFor="visibility" className="block text-xs font-medium text-[#CBD5E1] mb-1.5">
              Visibility
            </label>
            <select
              id="visibility"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as ProjectVisibility)}
              className="block w-full rounded-md border border-[#1E293B] bg-[#141E2E] py-2 px-3 text-sm text-[#F8FAFC] focus:border-[#3B82F6] focus:outline-hidden focus:ring-1 focus:ring-[#3B82F6]"
            >
              <option value="private">Private (Only you)</option>
              <option value="internal">Internal (Team only)</option>
              <option value="public">Public (Anyone)</option>
            </select>
          </div>
          
          <div className="mt-4 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-[#1E293B] bg-transparent px-4 py-2 text-xs font-medium text-[#CBD5E1] hover:bg-[#1E293B] hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex items-center gap-2 rounded-md bg-[#3B82F6] px-4 py-2 text-xs font-medium text-white hover:bg-[#2563EB] transition-colors shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              <span>{createMutation.isPending ? "Creating..." : "Create Project"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
