import { Sparkles, Clock, History } from "lucide-react";

interface AIReviewHeaderProps {
  score: number;
  lastReviewTime: string;
  onRunReview: () => void;
  isRunning: boolean;
}

export function AIReviewHeader({ score, lastReviewTime, onRunReview, isRunning }: AIReviewHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="h-5 w-5 text-[#3B82F6]" />
          <h1 className="text-2xl font-bold tracking-tight text-[#F8FAFC]">AI Architecture Review</h1>
        </div>
        <p className="text-sm text-[#94A3B8]">
          Evaluate architecture quality, identify structural risks, and surface improvement opportunities.
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex flex-col items-end mr-4">
          <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Architecture Score</span>
          <div className="text-xl font-bold text-[#F8FAFC]">
            {score} <span className="text-sm text-[#94A3B8] font-normal">/ 100</span>
          </div>
        </div>
        <div className="flex flex-col items-end mr-2 hidden sm:flex">
          <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Last Review</span>
          <div className="flex items-center gap-1.5 text-sm font-medium text-[#CBD5E1]">
            <Clock className="h-3.5 w-3.5" />
            {lastReviewTime}
          </div>
        </div>
        
        <button className="hidden md:flex items-center gap-2 px-3 py-2 bg-[#0F1726] border border-[#1E293B] text-sm text-[#CBD5E1] rounded-md hover:bg-[#1E293B] transition-colors">
          <History className="h-4 w-4" />
          Review History
        </button>
        
        <button
          onClick={onRunReview}
          disabled={isRunning}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-[#3B82F6] px-4 py-2 text-sm font-medium text-white shadow hover:bg-[#2563EB] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#3B82F6] disabled:pointer-events-none disabled:opacity-50 transition-colors"
        >
          <Sparkles className={`h-4 w-4 ${isRunning ? "animate-pulse" : ""}`} />
          {isRunning ? "Running..." : "Run Architecture Review"}
        </button>
      </div>
    </div>
  );
}
