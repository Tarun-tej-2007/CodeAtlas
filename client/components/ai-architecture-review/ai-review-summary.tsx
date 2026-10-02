import { ArchitectureReviewSummary } from "@/types/ai-architecture-review-ui";
import { Sparkles, CheckCircle2, AlertTriangle } from "lucide-react";

interface AIReviewSummaryProps {
  summary: ArchitectureReviewSummary;
}

export function AIReviewSummary({ summary }: AIReviewSummaryProps) {
  return (
    <div className="bg-gradient-to-br from-[#0F1726] to-[#0B1220] border border-[#3B82F6]/20 rounded-lg p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Sparkles className="h-24 w-24 text-[#3B82F6]" />
      </div>
      
      <div className="flex items-center gap-2 mb-4 relative z-10">
        <Sparkles className="h-5 w-5 text-[#3B82F6]" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">AI Review Summary</h3>
      </div>
      
      <div className="relative z-10 mb-6">
        <p className="text-sm text-[#CBD5E1] leading-relaxed">
          {summary.assessment}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
        <div className="bg-[#141E2E]/50 border border-[#1E293B] rounded-md p-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle2 className="h-4 w-4 text-[#10B981]" />
            <h4 className="text-sm font-semibold text-[#F8FAFC]">Strengths</h4>
          </div>
          <ul className="space-y-2">
            {summary.strengths.map((s, i) => (
              <li key={i} className="text-xs text-[#CBD5E1] flex items-start gap-2">
                <span className="text-[#10B981] mt-0.5">•</span> {s}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="bg-[#141E2E]/50 border border-[#1E293B] rounded-md p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />
            <h4 className="text-sm font-semibold text-[#F8FAFC]">Concerns</h4>
          </div>
          <ul className="space-y-2">
            {summary.concerns.map((c, i) => (
              <li key={i} className="text-xs text-[#CBD5E1] flex items-start gap-2">
                <span className="text-[#F59E0B] mt-0.5">•</span> {c}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
