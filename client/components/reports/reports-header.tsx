import { FileText, Settings, Play } from "lucide-react";

interface ReportsHeaderProps {
  latestReport: string;
  generatedAgo: string;
  onGenerate: () => void;
  onSettings: () => void;
}

export function ReportsHeader({ latestReport, generatedAgo, onGenerate, onSettings }: ReportsHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <FileText className="h-5 w-5 text-[#3B82F6]" />
          <h1 className="text-2xl font-bold tracking-tight text-[#F8FAFC]">Reports</h1>
        </div>
        <p className="text-sm text-[#94A3B8]">
          Generate, review, and export engineering intelligence from your CodeAtlas analysis.
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex flex-col items-end mr-4 hidden sm:flex">
          <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Latest Report</span>
          <div className="text-sm font-bold text-[#F8FAFC]">{latestReport}</div>
          <div className="text-[10px] text-[#94A3B8]">{generatedAgo}</div>
        </div>
        
        <button 
          onClick={onSettings}
          className="p-2 bg-[#0F1726] border border-[#1E293B] text-[#CBD5E1] rounded-md hover:bg-[#1E293B] transition-colors"
          aria-label="Report Settings"
        >
          <Settings className="h-4 w-4" />
        </button>
        
        <button
          onClick={onGenerate}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-[#3B82F6] px-4 py-2 text-sm font-medium text-white shadow hover:bg-[#2563EB] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#3B82F6] transition-colors"
        >
          <Play className="h-4 w-4" fill="currentColor" />
          Generate Report
        </button>
      </div>
    </div>
  );
}
