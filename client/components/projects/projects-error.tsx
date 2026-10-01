import { AlertCircle, RefreshCw } from "lucide-react";

interface ProjectsErrorProps {
  message?: string;
  onRetry?: () => void;
}

export function ProjectsError({
  message = "Failed to load projects. Verify backend connection.",
  onRetry,
}: ProjectsErrorProps) {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border border-[#EF4444]/30 bg-[#0F1726] p-8 text-center"
      data-testid="projects-error"
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#EF4444]/10 text-[#EF4444] mb-3">
        <AlertCircle className="h-6 w-6" />
      </div>

      <h2 className="text-sm font-semibold text-[#F8FAFC]">
        Projects Unavailable
      </h2>
      <p className="mt-1 max-w-md text-xs text-[#94A3B8] font-mono leading-relaxed">
        {message}
      </p>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-2 rounded-md bg-[#141E2E] border border-[#1E293B] px-3 py-1.5 text-xs font-medium text-[#F8FAFC] hover:bg-[#182337] transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5 text-[#3B82F6]" />
          <span>Retry connection</span>
        </button>
      )}
    </div>
  );
}
