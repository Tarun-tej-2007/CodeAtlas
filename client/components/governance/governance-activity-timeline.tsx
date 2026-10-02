import { GovernanceActivity } from "@/types/governance-ui";
import { Activity, Edit, CheckCircle2, ShieldCheck, Tag } from "lucide-react";

interface GovernanceActivityTimelineProps {
  activities: GovernanceActivity[];
}

export function GovernanceActivityTimeline({ activities }: GovernanceActivityTimelineProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case "evaluation": return <Activity className="w-4 h-4 text-[#3B82F6]" />;
      case "policy_update": return <Edit className="w-4 h-4 text-[#8B5CF6]" />;
      case "violation_resolved": return <CheckCircle2 className="w-4 h-4 text-[#10B981]" />;
      case "policy_enabled": return <ShieldCheck className="w-4 h-4 text-[#22C55E]" />;
      default: return <Activity className="w-4 h-4 text-[#94A3B8]" />;
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Governance Activity</h2>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 relative">
        <div className="absolute left-3 top-0 bottom-0 w-px bg-[#1E293B]" />
        
        <div className="flex flex-col gap-6 relative">
          {activities.map((act) => (
            <div key={act.id} className="flex gap-4 relative group">
              <div className="w-6 h-6 shrink-0 rounded-full flex items-center justify-center border border-[#1E293B] bg-[#0F1726] relative z-10">
                {getIcon(act.type)}
              </div>
              <div className="flex-1 pb-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-[#F8FAFC]">{act.date}</span>
                  <span className="text-[10px] text-[#94A3B8] px-1.5 py-0.5 rounded border border-[#1E293B] bg-[#080D18]">
                    {act.actor}
                  </span>
                </div>
                <h3 className="text-sm text-[#CBD5E1] mb-1">{act.message}</h3>
                <div className="flex items-center gap-2">
                  <Tag className="w-3 h-3 text-[#64748B]" />
                  <span className="text-[10px] text-[#64748B] uppercase">{act.category}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
