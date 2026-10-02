import { ActivityStats } from "@/types/activity-ui";
import { Activity, Calendar, AlertTriangle, ShieldAlert, CheckCircle2, Bot } from "lucide-react";

interface Props {
  stats: ActivityStats;
}

export function ActivityOverview({ stats }: Props) {
  const metrics = [
    { label: "Total Events", value: stats.total, icon: Activity, color: "text-[#3B82F6]" },
    { label: "Today", value: stats.today, icon: Calendar, color: "text-[#F8FAFC]" },
    { label: "Warnings", value: stats.warnings, icon: AlertTriangle, color: "text-[#F59E0B]" },
    { label: "Critical", value: stats.critical, icon: ShieldAlert, color: "text-[#EF4444]" },
    { label: "Resolved", value: stats.resolved, icon: CheckCircle2, color: "text-[#10B981]" },
    { label: "Automated", value: stats.automated, icon: Bot, color: "text-[#8B5CF6]" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {metrics.map((m, i) => {
        const Icon = m.icon;
        return (
          <div key={i} className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col justify-between h-full">
            <div className="flex items-center gap-2 mb-3">
              <Icon className={`h-4 w-4 ${m.color}`} />
              <span className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">{m.label}</span>
            </div>
            <div className="text-2xl font-bold text-[#F8FAFC]">{m.value}</div>
          </div>
        );
      })}
    </div>
  );
}

