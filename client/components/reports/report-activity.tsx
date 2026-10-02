import { ReportActivity as ReportActivityType } from "@/types/reports-ui";
import { Activity } from "lucide-react";

interface ReportActivityProps {
  activity: ReportActivityType[];
}

export function ReportActivity({ activity }: ReportActivityProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center gap-2 mb-5">
        <Activity className="h-5 w-5 text-[#8B5CF6]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Recent Activity</h3>
      </div>
      
      <div className="relative pl-3 border-l border-[#1E293B] space-y-4 ml-2">
        {activity.map((item, i) => (
          <div key={item.id} className="relative">
            <div className={`absolute -left-[17px] top-1.5 h-2 w-2 rounded-full ${i === 0 ? "bg-[#3B82F6]" : "bg-[#64748B]"}`} />
            <div className="text-xs font-bold text-[#CBD5E1] mb-1">{item.date}</div>
            <div className="text-sm text-[#F8FAFC] mb-0.5">{item.event}</div>
            <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">
              {item.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
