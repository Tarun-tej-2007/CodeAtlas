import { ArchitectureReviewRecommendation } from "@/types/ai-architecture-review-ui";
import { Lightbulb, ArrowRight } from "lucide-react";

interface ReviewRecommendationsProps {
  recommendations: ArchitectureReviewRecommendation[];
  onSelect: (id: string) => void;
  selectedId: string | null;
}

export function ReviewRecommendations({ recommendations, onSelect, selectedId }: ReviewRecommendationsProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "CRITICAL": return "text-[#EF4444]";
      case "HIGH": return "text-[#F97316]";
      case "MEDIUM": return "text-[#F59E0B]";
      case "LOW": return "text-[#3B82F6]";
      default: return "text-[#64748B]";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "OPEN": return "text-[#3B82F6]";
      case "ACKNOWLEDGED": return "text-[#F59E0B]";
      case "RESOLVED": return "text-[#10B981]";
      case "DISMISSED": return "text-[#64748B]";
      default: return "text-[#94A3B8]";
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="h-5 w-5 text-[#8B5CF6]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Top Recommendations</h3>
      </div>
      
      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div 
            key={rec.id}
            onClick={() => onSelect(rec.id)}
            className={`group p-3 rounded border cursor-pointer transition-colors ${
              selectedId === rec.id
                ? "bg-[#141E2E] border-[#8B5CF6]/50"
                : "bg-[#080D18] border-[#1E293B] hover:border-[#8B5CF6]/30"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <h4 className="text-xs font-bold text-[#F8FAFC] mb-1">{rec.title}</h4>
                <p className="text-[11px] text-[#94A3B8] line-clamp-1">{rec.problem}</p>
              </div>
              <ArrowRight className="h-4 w-4 shrink-0 text-[#8B5CF6] opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            
            <div className="flex items-center gap-3 mt-3 text-[10px] font-mono">
              <div className="flex items-center gap-1">
                <span className="text-[#64748B]">PRIORITY:</span>
                <span className={getPriorityColor(rec.priority)}>{rec.priority}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-[#64748B]">EFFORT:</span>
                <span className="text-[#CBD5E1]">{rec.estimatedEffort}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-[#64748B]">STATUS:</span>
                <span className={getStatusColor(rec.status)}>{rec.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
