import { DecisionHistoryEntry } from "@/types/decision-intelligence-ui";
import { CheckCircle2, Circle, Clock, Target, Info } from "lucide-react";

interface DecisionHistoryProps {
  history: DecisionHistoryEntry[];
}

export function DecisionHistory({ history }: DecisionHistoryProps) {
  const getIcon = (status: string) => {
    switch (status) {
      case "COMPLETED": return <CheckCircle2 className="h-4 w-4 text-[#10B981]" />;
      case "IN_PROGRESS": return <Clock className="h-4 w-4 text-[#8B5CF6]" />;
      case "REVIEWED": return <Target className="h-4 w-4 text-[#F59E0B]" />;
      case "NEW": return <Circle className="h-4 w-4 text-[#3B82F6]" />;
      default: return <Info className="h-4 w-4 text-[#64748B]" />;
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-bold text-[#F8FAFC] mb-4 uppercase tracking-wider">Decision History</h3>
      <div className="space-y-4">
        {history.map((event, i) => (
          <div key={event.id} className="relative flex gap-4">
            {/* Timeline line */}
            {i !== history.length - 1 && (
              <div className="absolute left-2 top-6 bottom-[-16px] w-px bg-[#1E293B]" />
            )}
            
            <div className="relative z-10 flex h-5 w-5 shrink-0 items-center justify-center mt-0.5 bg-[#0F1726]">
              {getIcon(event.status)}
            </div>
            
            <div className="flex flex-col pb-1">
              <span className="text-sm text-[#F8FAFC]">{event.event}</span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-xs text-[#64748B] font-mono">{event.date}</span>
                <span className="text-[10px] uppercase font-semibold text-[#94A3B8] tracking-wider px-1.5 py-0.5 rounded bg-[#1E293B]">
                  {event.category.replace("_", " ")}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
