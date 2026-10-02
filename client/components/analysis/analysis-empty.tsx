import { FolderSearch } from "lucide-react";

interface AnalysisEmptyProps {
  onRunAnalysis: () => void;
}

export function AnalysisEmpty({ onRunAnalysis }: AnalysisEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[400px] border border-dashed border-[#1E293B] rounded-lg bg-[#0F1726]/50">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#141E2E] text-[#94A3B8] mb-4">
        <FolderSearch className="h-6 w-6" />
      </div>
      <h3 className="text-lg font-medium text-[#F8FAFC]">No Analysis Data</h3>
      <p className="text-sm text-[#94A3B8] text-center max-w-md mt-2 mb-6">
        This repository hasn&apos;t been analyzed yet. Run an analysis to generate architecture metrics, discover code smells, and review complexity.
      </p>
      <button
        onClick={onRunAnalysis}
        className="rounded-md bg-[#3B82F6] px-4 py-2 text-sm font-medium text-white hover:bg-[#2563EB] transition-colors focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:ring-offset-2 focus:ring-offset-[#080D18]"
      >
        Run Initial Analysis
      </button>
    </div>
  );
}
