import { ArchitectureStrength } from "@/types/ai-architecture-review-ui";
import { ShieldCheck } from "lucide-react";

interface ArchitectureStrengthsProps {
  strengths: ArchitectureStrength[];
}

export function ArchitectureStrengths({ strengths }: ArchitectureStrengthsProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center gap-2 mb-5">
        <ShieldCheck className="h-5 w-5 text-[#10B981]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Architecture Strengths</h3>
      </div>
      
      <div className="space-y-4">
        {strengths.map((str) => (
          <div key={str.id} className="group">
            <div className="flex items-center justify-between mb-1">
              <h4 className="text-sm font-bold text-[#F8FAFC] flex items-center gap-2">
                {str.title}
              </h4>
              <span className="text-xs font-bold text-[#10B981] bg-[#10B981]/10 px-2 py-0.5 rounded">
                {str.score}%
              </span>
            </div>
            <p className="text-xs text-[#94A3B8] mb-2">{str.explanation}</p>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[10px] text-[#64748B] uppercase font-semibold">Supporting:</span>
              {str.components.map(c => (
                <span key={c} className="text-[10px] text-[#CBD5E1] bg-[#141E2E] border border-[#1E293B] px-1.5 py-0.5 rounded font-mono">
                  {c}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
