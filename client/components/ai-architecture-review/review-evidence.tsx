import { ArchitectureReviewEvidence } from "@/types/ai-architecture-review-ui";
import { FileSearch } from "lucide-react";

interface ReviewEvidenceProps {
  evidence: ArchitectureReviewEvidence[];
}

export function ReviewEvidence({ evidence }: ReviewEvidenceProps) {
  // Only show first 5 for the sidebar to keep it compact
  const displayEvidence = evidence.slice(0, 5);

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <FileSearch className="h-5 w-5 text-[#3B82F6]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Supporting Evidence</h3>
      </div>
      
      <div className="space-y-3">
        {displayEvidence.map((ev) => (
          <div key={ev.id} className="p-3 bg-[#080D18] border border-[#1E293B] rounded">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#1E293B] text-[#CBD5E1] uppercase tracking-wider font-semibold">
                {ev.type}
              </span>
            </div>
            <p className="text-xs text-[#94A3B8] font-mono leading-relaxed mb-2">
              {ev.description}
            </p>
            <div className="flex flex-wrap gap-1">
              {ev.components.map(c => (
                <span key={c} className="text-[10px] text-[#64748B]">
                  {c}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {evidence.length > 5 && (
        <button className="w-full mt-4 text-xs font-medium text-[#3B82F6] hover:text-[#60A5FA] transition-colors">
          View all {evidence.length} evidence records
        </button>
      )}
    </div>
  );
}
