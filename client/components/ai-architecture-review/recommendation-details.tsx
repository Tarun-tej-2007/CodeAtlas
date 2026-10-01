import { ArchitectureReviewRecommendation, FindingStatus } from "@/types/ai-architecture-review-ui";
import { X, PlayCircle, ShieldOff, LayoutTemplate, Zap, Hammer, AlertOctagon } from "lucide-react";
import { useEffect } from "react";

interface RecommendationDetailsProps {
  recommendation: ArchitectureReviewRecommendation | null;
  onClose: () => void;
  onStatusChange: (id: string, status: FindingStatus) => void;
}

export function RecommendationDetails({ recommendation, onClose, onStatusChange }: RecommendationDetailsProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!recommendation) return null;

  return (
    <>
      <div 
        className="fixed inset-0 z-40 bg-[#080D18]/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-[#0B1220] border-l border-[#1E293B] shadow-2xl flex flex-col transform transition-transform duration-300">
        <div className="flex items-start justify-between p-5 border-b border-[#1E293B]">
          <div className="pr-4">
            <div className="text-xs font-semibold text-[#8B5CF6] tracking-wider uppercase mb-1">
              Architecture Recommendation
            </div>
            <h2 className="text-lg font-bold text-[#F8FAFC]">{recommendation.title}</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Priority</div>
              <div className="text-sm font-bold text-[#F8FAFC]">{recommendation.priority}</div>
            </div>
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Effort</div>
              <div className="text-sm font-bold text-[#F8FAFC]">{recommendation.estimatedEffort}</div>
            </div>
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Confidence</div>
              <div className="text-sm font-bold text-[#F8FAFC]">{recommendation.confidence}%</div>
            </div>
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Status</div>
              <div className="text-sm font-bold text-[#F8FAFC]">{recommendation.status}</div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <AlertOctagon className="h-4 w-4 text-[#EF4444]" /> The Problem
            </h3>
            <p className="text-sm text-[#CBD5E1] bg-[#EF4444]/5 border border-[#EF4444]/10 p-3 rounded-md">
              {recommendation.problem}
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-2">Current Architecture</h4>
              <div className="bg-[#0F1726] border border-[#1E293B] rounded p-3 text-xs font-mono text-[#F59E0B]">
                {recommendation.currentArchitecture}
              </div>
            </div>
            
            <div className="flex justify-center">
              <LayoutTemplate className="h-5 w-5 text-[#3B82F6]" />
            </div>

            <div>
              <h4 className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-2">Expected Architecture</h4>
              <div className="bg-[#0F1726] border border-[#1E293B] rounded p-3 text-xs font-mono text-[#10B981]">
                {recommendation.expectedArchitecture}
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <Zap className="h-4 w-4 text-[#F59E0B]" /> Expected Benefit
            </h3>
            <p className="text-sm text-[#94A3B8]">{recommendation.expectedBenefit}</p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <Hammer className="h-4 w-4 text-[#3B82F6]" /> Suggested Implementation Steps
            </h3>
            <ol className="list-decimal pl-5 space-y-2 text-sm text-[#CBD5E1]">
              {recommendation.suggestedSteps.map((step, i) => (
                <li key={i} className="pl-1">{step}</li>
              ))}
            </ol>
          </div>
        </div>

        <div className="p-5 border-t border-[#1E293B] bg-[#080D18]">
          <div className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-3">Actions</div>
          <div className="flex flex-wrap gap-2">
            {recommendation.status !== "ACKNOWLEDGED" && (
              <button
                onClick={() => onStatusChange(recommendation.id, "ACKNOWLEDGED")}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F59E0B]/10 hover:bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30 rounded text-xs font-medium transition-colors"
              >
                Mark Reviewed
              </button>
            )}
            {recommendation.status !== "RESOLVED" && (
              <button
                onClick={() => onStatusChange(recommendation.id, "RESOLVED")}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#3B82F6]/10 hover:bg-[#3B82F6]/20 text-[#3B82F6] border border-[#3B82F6]/30 rounded text-xs font-medium transition-colors"
              >
                <PlayCircle className="h-3.5 w-3.5" /> Start Work
              </button>
            )}
            {recommendation.status !== "DISMISSED" && (
              <button
                onClick={() => onStatusChange(recommendation.id, "DISMISSED")}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1E293B] hover:bg-[#334155] text-[#CBD5E1] border border-[#334155] rounded text-xs font-medium transition-colors"
              >
                <ShieldOff className="h-3.5 w-3.5" /> Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
// Adding AlertOctagon import since it's used

