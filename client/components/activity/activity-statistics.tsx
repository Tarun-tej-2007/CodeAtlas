import { ActivityEvent } from "@/types/activity-ui";

interface Props {
  events: ActivityEvent[];
}

export function ActivityStatistics({ events }: Props) {
  // Calculate distribution
  const distribution: Record<string, number> = {};
  const actorStats = { automated: 0, user: 0, system: 0 };
  
  events.forEach(e => {
    distribution[e.type] = (distribution[e.type] || 0) + 1;
    
    if (e.actor.type === "AUTOMATION" || e.actor.type === "AI") {
      actorStats.automated++;
    } else if (e.actor.type === "USER") {
      actorStats.user++;
    } else if (e.actor.type === "SYSTEM") {
      actorStats.system++;
    }
  });
  
  // Sort types by count descending
  const sortedDistribution = Object.entries(distribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8); // Top 8 max
    
  const maxCount = Math.max(...sortedDistribution.map(d => d[1]), 1);

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-bold text-[#F8FAFC] mb-4">Event Statistics</h3>
      
      <div className="space-y-3 mb-6">
        {sortedDistribution.map(([type, count]) => (
          <div key={type}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-[#94A3B8] font-medium">{type.replace(/_/g, ' ')}</span>
              <span className="text-[#F8FAFC] font-bold">{count}</span>
            </div>
            <div className="h-1.5 w-full bg-[#1E293B] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#3B82F6] rounded-full" 
                style={{ width: `${(count / maxCount) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      
      <div className="pt-4 border-t border-[#1E293B]">
        <h4 className="text-[10px] font-semibold tracking-wider text-[#64748B] uppercase mb-3">Actor Breakdown</h4>
        <div className="flex items-center justify-between gap-2 text-xs">
          <div className="flex flex-col">
            <span className="text-[#94A3B8]">Automated</span>
            <span className="text-[#F8FAFC] font-bold text-sm">{actorStats.automated}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[#94A3B8]">User Initiated</span>
            <span className="text-[#F8FAFC] font-bold text-sm">{actorStats.user}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[#94A3B8]">System</span>
            <span className="text-[#F8FAFC] font-bold text-sm">{actorStats.system}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
