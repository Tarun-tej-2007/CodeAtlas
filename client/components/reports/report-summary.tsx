import { ReportSummary as ReportSummaryType } from "@/types/reports-ui";
import { Sparkles, FileText, CheckCircle2 } from "lucide-react";

interface ReportSummaryProps {
  summary: ReportSummaryType;
}

export function ReportSummary({ summary }: ReportSummaryProps) {
  return (
    <div className="bg-gradient-to-br from-[#0F1726] to-[#0B1220] border border-[#3B82F6]/20 rounded-lg p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Sparkles className="h-24 w-24 text-[#3B82F6]" />
      </div>
      
      <div className="flex items-center gap-2 mb-2 relative z-10">
        <FileText className="h-5 w-5 text-[#3B82F6]" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">Latest Report Summary</h3>
      </div>
      <div className="text-sm font-semibold text-[#3B82F6] mb-4 relative z-10">
        {summary.title}
      </div>
      
      <div className="relative z-10 mb-6">
        <p className="text-sm text-[#CBD5E1] leading-relaxed">
          {summary.summary}
        </p>
      </div>

      <div className="bg-[#141E2E]/50 border border-[#1E293B] rounded-md p-4 relative z-10">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle2 className="h-4 w-4 text-[#10B981]" />
          <h4 className="text-sm font-semibold text-[#F8FAFC]">Key Observations</h4>
        </div>
        <ul className="space-y-2">
          {summary.keyObservations.map((obs, i) => (
            <li key={i} className="text-xs text-[#CBD5E1] flex items-start gap-2">
              <span className="text-[#3B82F6] mt-0.5">•</span> {obs}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
