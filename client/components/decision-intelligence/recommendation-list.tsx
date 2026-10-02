import { DecisionRecommendation } from "@/types/decision-intelligence-ui";

interface RecommendationListProps {
  recommendations: DecisionRecommendation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function RecommendationList({ recommendations, selectedId, onSelect }: RecommendationListProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "CRITICAL": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      case "HIGH": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20";
      case "MEDIUM": return "text-[#3B82F6] bg-[#3B82F6]/10 border-[#3B82F6]/20";
      case "LOW": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20";
      default: return "text-[#94A3B8] bg-[#1E293B] border-[#334155]";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "NEW": return "text-[#3B82F6]";
      case "REVIEWED": return "text-[#F59E0B]";
      case "IN_PROGRESS": return "text-[#8B5CF6]";
      case "COMPLETED": return "text-[#10B981]";
      case "DISMISSED": return "text-[#64748B]";
      default: return "text-[#94A3B8]";
    }
  };

  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#0F1726] border border-[#1E293B] rounded-lg">
        <div className="text-[#64748B] text-sm">No recommendations match your filters.</div>
      </div>
    );
  }

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-[#CBD5E1]">
          <thead className="bg-[#141E2E] text-xs uppercase text-[#64748B] border-b border-[#1E293B]">
            <tr>
              <th className="px-4 py-3 font-semibold">Recommendation</th>
              <th className="px-4 py-3 font-semibold">Priority</th>
              <th className="px-4 py-3 font-semibold">Impact / Effort</th>
              <th className="px-4 py-3 font-semibold">Category</th>
              <th className="px-4 py-3 font-semibold">Confidence</th>
              <th className="px-4 py-3 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B]">
            {recommendations.map((rec) => (
              <tr 
                key={rec.id} 
                onClick={() => onSelect(rec.id)}
                data-testid="recommendation-row"
                className={`cursor-pointer transition-colors ${selectedId === rec.id ? "bg-[#1E293B]" : "hover:bg-[#141E2E]"}`}
              >
                <td className="px-4 py-3 font-medium text-[#F8FAFC]">
                  {rec.title}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border ${getPriorityColor(rec.priority)}`}>
                    {rec.priority}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1 text-xs">
                    <span className={rec.impact === "HIGH" ? "text-[#F8FAFC] font-medium" : "text-[#94A3B8]"}>{rec.impact}</span>
                    <span className="text-[#64748B]">/</span>
                    <span className={rec.effort === "HIGH" ? "text-[#F8FAFC] font-medium" : "text-[#94A3B8]"}>{rec.effort}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-xs text-[#94A3B8]">
                  {rec.category.replace("_", " ")}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-[#1E293B] rounded-full overflow-hidden">
                      <div className="h-full bg-[#3B82F6]" style={{ width: `${rec.confidence}%` }} />
                    </div>
                    <span className="text-xs text-[#64748B]">{rec.confidence}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium ${getStatusColor(rec.status)}`}>
                    {rec.status.replace("_", " ")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
