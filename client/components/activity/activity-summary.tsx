import { ActivitySummary as ActivitySummaryType } from "@/types/activity-ui";
import { Zap } from "lucide-react";

interface Props {
  summary: ActivitySummaryType;
}

export function ActivitySummary({ summary }: Props) {
  return (
    <div className="bg-[#0B1220] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center gap-2 mb-3">
        <Zap className="h-4 w-4 text-[#3B82F6]" />
        <h3 className="text-sm font-bold text-[#F8FAFC]">AI Summary</h3>
      </div>
      
      <p className="text-sm text-[#CBD5E1] leading-relaxed mb-4">
        {summary.description}
      </p>
      
      <div className="space-y-2">
        <h4 className="text-[10px] font-semibold tracking-wider text-[#64748B] uppercase mb-2">Recent Highlights</h4>
        <ul className="space-y-2">
          {summary.highlights.map((highlight, idx) => (
            <li key={idx} className="flex items-start gap-2 text-xs text-[#94A3B8]">
              <span className="text-[#3B82F6] mt-0.5">•</span>
              <span>{highlight}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
