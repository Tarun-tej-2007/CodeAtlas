import { FolderGit2, Play, Pencil, Trash2, Globe, Lock, Shield, ExternalLink, Loader2, MoreVertical } from "lucide-react";
import { ProjectResponse } from "@/types/project";
import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { useTriggerAnalysis } from "@/lib/query/use-projects";

interface ProjectCardProps {
  project: ProjectResponse;
  onEdit: (project: ProjectResponse) => void;
  onDelete: (project: ProjectResponse) => void;
}

export function ProjectCard({ project, onEdit, onDelete }: ProjectCardProps) {
  const triggerMutation = useTriggerAnalysis();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [analysisStatus, setAnalysisStatus] = useState<{type: "success" | "error", text: string} | null>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleRunAnalysis = async () => {
    setDropdownOpen(false);
    try {
      setAnalysisStatus(null);
      const res = await triggerMutation.mutateAsync({ projectId: project.id });
      setAnalysisStatus({
        type: "success",
        text: `Analysis running (Job: ${res.job_id.slice(0, 8)})`,
      });
      setTimeout(() => setAnalysisStatus(null), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to trigger analysis";
      setAnalysisStatus({
        type: "error",
        text: msg,
      });
      setTimeout(() => setAnalysisStatus(null), 4000);
    }
  };

  const getVisibilityIcon = () => {
    switch(project.visibility) {
      case "public": return <Globe className="h-3 w-3" />;
      case "private": return <Lock className="h-3 w-3" />;
      case "internal": return <Shield className="h-3 w-3" />;
      default: return <Lock className="h-3 w-3" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="flex flex-col justify-between rounded-lg border border-[#1E293B] bg-[#0F1726] p-4.5 shadow-xs hover:border-[#3B82F6]/50 transition-colors group relative">
      <div>
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <FolderGit2 className="h-4.5 w-4.5 text-[#3B82F6] shrink-0" />
            <h3 className="text-sm font-semibold text-[#F8FAFC] truncate pr-4" title={project.name}>
              {project.name}
            </h3>
          </div>
          
          <div className="relative" ref={dropdownRef}>
            <button 
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="text-[#64748B] hover:text-[#CBD5E1] transition-colors p-1 rounded-md hover:bg-[#1E293B]"
              aria-label="More actions"
            >
              <MoreVertical className="h-4 w-4" />
            </button>
            {dropdownOpen && (
              <div className="absolute right-0 top-full mt-1 w-40 rounded-md border border-[#1E293B] bg-[#141E2E] py-1 shadow-lg z-20">
                <button 
                  onClick={handleRunAnalysis}
                  disabled={triggerMutation.isPending}
                  className="flex w-full items-center gap-2 px-3 py-1.5 text-xs text-[#CBD5E1] hover:bg-[#1E293B] hover:text-white transition-colors disabled:opacity-50"
                >
                  {triggerMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
                  <span>Run Analysis</span>
                </button>
                <button 
                  onClick={() => { setDropdownOpen(false); onEdit(project); }}
                  className="flex w-full items-center gap-2 px-3 py-1.5 text-xs text-[#CBD5E1] hover:bg-[#1E293B] hover:text-white transition-colors"
                >
                  <Pencil className="h-3.5 w-3.5" />
                  <span>Edit Project</span>
                </button>
                <button 
                  onClick={() => { setDropdownOpen(false); onDelete(project); }}
                  className="flex w-full items-center gap-2 px-3 py-1.5 text-xs text-[#EF4444] hover:bg-[#1E293B] hover:text-[#F87171] transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  <span>Delete Project</span>
                </button>
              </div>
            )}
          </div>
        </div>
        
        {project.description && (
          <p className="text-xs text-[#94A3B8] line-clamp-2 mb-4 leading-relaxed" title={project.description}>
            {project.description}
          </p>
        )}
        
        {analysisStatus && (
          <div className={`mb-3 px-2 py-1.5 text-[10px] rounded border flex items-center justify-center font-mono ${
              analysisStatus.type === "success"
                ? "bg-[#22C55E]/10 border-[#22C55E]/20 text-[#22C55E]"
                : "bg-[#EF4444]/10 border-[#EF4444]/20 text-[#EF4444]"
            }`}>
            {analysisStatus.text}
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-col gap-3">
        <div className="flex items-center gap-3 text-[11px] font-mono text-[#64748B]">
          <div className="flex items-center gap-1.5 rounded-full border border-[#1E293B] bg-[#141E2E] px-2 py-0.5">
            {getVisibilityIcon()}
            <span className="capitalize">{project.visibility}</span>
          </div>
          <span>Updated {formatDate(project.updated_at)}</span>
        </div>
        
        <Link 
          href={`/projects/${project.id}`}
          className="flex w-full items-center justify-center gap-1.5 rounded-md border border-[#1E293B] bg-[#141E2E] px-3 py-1.5 text-xs font-medium text-[#CBD5E1] hover:bg-[#1E293B] hover:text-white transition-colors"
        >
          <span>Open Project</span>
          <ExternalLink className="h-3 w-3" />
        </Link>
      </div>
    </div>
  );
}
