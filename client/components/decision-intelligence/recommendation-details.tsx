import { X, ExternalLink } from "lucide-react";
import { DecisionRecommendation, RecommendationStatus } from "@/types/decision-intelligence-ui";

interface RecommendationDetailsProps {
  recommendation: DecisionRecommendation | null;
  onClose: () => void;
  onStatusChange: (id: string, status: RecommendationStatus) => void;
}

export function RecommendationDetails({ recommendation, onClose, onStatusChange }: RecommendationDetailsProps) {
  if (!recommendation) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full md:w-[600px] bg-[#0B1220] border-l border-[#1E293B] shadow-2xl flex flex-col transform transition-transform duration-300">
      <div className="flex items-center justify-between px-6 py-4 border-b border-[#1E293B]">
        <div>
          <div className="text-xs font-semibold text-[#64748B] tracking-wider uppercase mb-1">
            Recommendation Details
          </div>
          <h2 className="text-lg font-bold text-[#F8FAFC]">{recommendation.title}</h2>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-md text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#1E293B] transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold mb-1">Status</span>
            <span className="text-sm font-medium text-[#F8FAFC]">{recommendation.status.replace("_", " ")}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold mb-1">Priority</span>
            <span className="text-sm font-medium text-[#F8FAFC]">{recommendation.priority}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold mb-1">Impact</span>
            <span className="text-sm font-medium text-[#F8FAFC]">{recommendation.impact}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold mb-1">Effort</span>
            <span className="text-sm font-medium text-[#F8FAFC]">{recommendation.effort}</span>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Problem</h3>
          <p className="text-sm text-[#CBD5E1] bg-[#141E2E] p-3 rounded border border-[#1E293B]">
            {recommendation.problem}
          </p>
        </div>

        <div>
          <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Evidence</h3>
          <p className="text-sm text-[#94A3B8] font-mono bg-[#080D18] p-3 rounded border border-[#1E293B]">
            {recommendation.evidence}
          </p>
        </div>

        <div>
          <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Affected Components</h3>
          <div className="flex flex-wrap gap-2">
            {recommendation.affectedComponents.map((c, i) => (
              <span key={i} className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-[#1E293B] text-[#CBD5E1] border border-[#334155]">
                {c}
              </span>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Architecture Impact</h3>
            <p className="text-sm text-[#CBD5E1]">{recommendation.architectureImpact}</p>
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Risk Impact</h3>
            <p className="text-sm text-[#CBD5E1]">{recommendation.riskImpact}</p>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Expected Benefit</h3>
          <p className="text-sm text-[#CBD5E1]">{recommendation.expectedBenefit}</p>
        </div>

        <div>
          <h3 className="text-sm font-bold text-[#F8FAFC] mb-2">Suggested Actions</h3>
          <ul className="list-disc pl-5 space-y-1">
            {recommendation.suggestedActions.map((act, i) => (
              <li key={i} className="text-sm text-[#CBD5E1]">{act}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="p-6 border-t border-[#1E293B] bg-[#141E2E]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => onStatusChange(recommendation.id, "REVIEWED")}
              disabled={recommendation.status === "REVIEWED" || recommendation.status === "COMPLETED"}
              className="px-3 py-1.5 text-xs font-medium rounded bg-[#1E293B] text-[#F8FAFC] border border-[#334155] hover:bg-[#334155] disabled:opacity-50"
            >
              Mark Reviewed
            </button>
            <button
              onClick={() => onStatusChange(recommendation.id, "IN_PROGRESS")}
              disabled={recommendation.status === "IN_PROGRESS" || recommendation.status === "COMPLETED"}
              className="px-3 py-1.5 text-xs font-medium rounded bg-[#3B82F6] text-white hover:bg-[#2563EB] disabled:opacity-50"
            >
              Start Work
            </button>
            <button
              onClick={() => onStatusChange(recommendation.id, "COMPLETED")}
              disabled={recommendation.status === "COMPLETED"}
              className="px-3 py-1.5 text-xs font-medium rounded bg-[#10B981] text-white hover:bg-[#059669] disabled:opacity-50"
            >
              Mark Completed
            </button>
          </div>
          <button
            onClick={() => onStatusChange(recommendation.id, "DISMISSED")}
            disabled={recommendation.status === "DISMISSED"}
            className="px-3 py-1.5 text-xs font-medium rounded text-[#EF4444] hover:bg-[#EF4444]/10 disabled:opacity-50"
          >
            Dismiss
          </button>
        </div>
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-[#1E293B]">
          <button className="flex items-center gap-1.5 text-xs font-medium text-[#3B82F6] hover:text-[#60A5FA]">
            View Architecture <ExternalLink className="h-3 w-3" />
          </button>
          <button className="flex items-center gap-1.5 text-xs font-medium text-[#3B82F6] hover:text-[#60A5FA]">
            View Dependency Graph <ExternalLink className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  );
}
